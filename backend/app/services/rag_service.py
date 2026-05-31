import logging

from datetime import datetime
from uuid import uuid4

from app.api.v1.schemas import ChatRequest, ChatResponse, GroundingStats, RetrievalStats, SourceSpan
from app.document_processing.extractive import ExtractiveTextSummarizer
from app.rag.confidence import confidence_from_evidence, unsupported_claim_risk
from app.rag.generator import GroundedGenerator
from app.rag.grounding_validator import GroundingValidator
from app.services.dependencies import get_embedder, get_retriever
from app.services.session_memory import SessionMemoryStore, ConversationTurn, ConversationContext

logger = logging.getLogger(__name__)


class RagService:
    """Retrieval-augmented generation service enforcing retrieval-before-generation."""

    def __init__(self) -> None:
        self.generator = GroundedGenerator()
        self.grounding_validator = GroundingValidator(get_embedder())
        self.session_store = SessionMemoryStore()
        self.local_extractor = ExtractiveTextSummarizer()

    def _requires_synthesis(self, question: str) -> bool:
        synthesis_words = ["compare", "summarize", "synthesize", "evaluate", "why", "how", "explain", "difference"]
        return any(w in question.lower() for w in synthesis_words)

    def _has_strong_evidence(self, evidence: list[tuple]) -> bool:
        if not evidence:
            return False
        scores = [score for _, score in evidence]
        return max(scores) >= 0.45

    def answer_question(self, request: ChatRequest) -> ChatResponse:
        """Synchronous retrieval-first answer flow.

        Steps:
        - Run retrieval (FAISS + BM25 hybrid)
        - If no evidence -> return explicit no-evidence message
        - If local-first (high confidence, no synthesis) -> return extractive summary
        - Else attempt LLM synthesis with evidence; on failure fallback to extractive summary
        - Validate grounding and return structured response with sources and stats
        """
        retriever = get_retriever()
        evidence = retriever.retrieve(
            request.question,
            request.top_k,
            request.paper_ids,
            retrieval_mode=getattr(request, "retrieval_mode", "hybrid"),
        )

        # If evidence is weak, treat it as absent to avoid unsupported claims
        if not self._has_strong_evidence(evidence):
            evidence = []

        # Confidence from retrieval evidence (0-1)
        confidence = confidence_from_evidence(evidence)

        # Build source spans from retrieved chunks (may be empty)
        sources = [
            SourceSpan(
                paper_id=chunk.paper_id,
                title=chunk.title,
                page=chunk.page,
                chunk_id=chunk.chunk_id,
                score=round(score, 4),
                text=chunk.text,
            )
            for chunk, score in evidence
        ]

        # Retrieval stats (from hybrid retriever)
        retrieval_stats = None
        last_stats = retriever.get_retrieval_stats()
        if last_stats:
            retrieval_stats = RetrievalStats(
                semantic_score=last_stats.semantic_score if last_stats.semantic_score > 0 else None,
                bm25_score=last_stats.bm25_score if last_stats.bm25_score > 0 else None,
                final_score=last_stats.final_score,
                retrieval_mode=last_stats.retrieval_mode,
            )

        # Session context
        session = None
        context_str = ""
        if getattr(request, "session_id", None):
            session = self.session_store.load_session(request.session_id)
            if not session:
                session = self.session_store.create_session(request.session_id, title="Research Session")
            context_str = ConversationContext(session).get_recent_context(num_turns=3)

        full_question = request.question
        if context_str:
            full_question = f"Previous context:\n{context_str}\n\nCurrent question: {request.question}"

        requires_synthesis = self._requires_synthesis(request.question) or len(request.paper_ids or []) > 1
        is_local_first = not requires_synthesis and confidence >= 0.75

        used_provider_meta = None

        # No evidence -> explicit safe response
        if not evidence:
            answer_text = "I could not find supporting evidence in the indexed papers."
        else:
            # Local extractive answer when appropriate
            if is_local_first:
                evidence_text = " ".join(chunk.text for chunk, _ in evidence)
                extracted = self.local_extractor.summarize(evidence_text, num_sentences=4)
                answer_text = f"*[Local Extractive Answer]*\n\n{extracted}"
            else:
                # Synthesis path: call LLM provider with evidence; fallback to extractive on errors
                try:
                    answer_text = self.generator.answer(full_question, evidence)
                    used_provider_meta = getattr(self.generator.provider, "last_request_info", None)
                except Exception:
                    logger.exception("LLM provider failed; falling back to extractive answer")
                    evidence_text = " ".join(chunk.text for chunk, _ in evidence)
                    extracted = self.local_extractor.summarize(evidence_text, num_sentences=4)
                    answer_text = f"*[Fallback Extractive Answer — provider unavailable]*\n\n{extracted}"
                    used_provider_meta = None

        # Validate grounding
        grounding_result = self.grounding_validator.validate_answer(
            answer_text,
            evidence,
            answer_type="research",
        )

        grounding_stats = GroundingStats(
            groundedness_score=grounding_result.groundedness_score,
            hallucination_risk=grounding_result.hallucination_risk,
            risk_level=grounding_result.risk_level,
            supported_claims=grounding_result.supported_claims,
            total_claims=grounding_result.total_claims,
        )

        # Persist session turn
        if session:
            turn = ConversationTurn(
                turn_id=uuid4().hex,
                timestamp=datetime.now(),
                question=request.question,
                answer=answer_text,
                sources=[s.model_dump() for s in sources],
                grounding_score=grounding_stats.groundedness_score,
                papers_cited=list({s.paper_id for s in sources}),
            )
            self.session_store.add_turn(session.session_id, turn)

        return ChatResponse(
            answer=answer_text,
            confidence=confidence,
            unsupported_claim_risk=unsupported_claim_risk(confidence),
            sources=sources,
            provider_metadata=used_provider_meta,
            retrieval_stats=retrieval_stats,
            grounding_stats=grounding_stats,
        )

    async def answer_question_stream(self, request: ChatRequest):
        """Asynchronous streaming retrieval-first flow for SSE endpoints.

        Emits:
        - metadata event with retrieval stats and sources
        - content events streaming the answer text
        - grounding event with grounding stats
        - end event
        """
        import json

        try:
            retriever = get_retriever()
            evidence = retriever.retrieve(
                request.question,
                request.top_k,
                request.paper_ids,
                retrieval_mode=getattr(request, "retrieval_mode", "hybrid"),
            )

            if not self._has_strong_evidence(evidence):
                evidence = []

            confidence = confidence_from_evidence(evidence)
            sources = [
                SourceSpan(
                    paper_id=chunk.paper_id,
                    title=chunk.title,
                    page=chunk.page,
                    chunk_id=chunk.chunk_id,
                    score=round(score, 4),
                    text=chunk.text,
                )
                for chunk, score in evidence
            ]

            # Retrieval stats
            retrieval_stats = None
            last_stats = retriever.get_retrieval_stats()
            if last_stats:
                retrieval_stats = RetrievalStats(
                    semantic_score=last_stats.semantic_score if last_stats.semantic_score > 0 else None,
                    bm25_score=last_stats.bm25_score if last_stats.bm25_score > 0 else None,
                    final_score=last_stats.final_score,
                    retrieval_mode=last_stats.retrieval_mode,
                )

            # Emit initial metadata (provider metadata will be populated after generation if available)
            metadata = {
                "confidence": confidence,
                "unsupported_claim_risk": unsupported_claim_risk(confidence),
                "sources": [s.model_dump() for s in sources],
                "provider_metadata": None,
                "retrieval_stats": retrieval_stats.model_dump() if retrieval_stats else None,
            }
            yield {"event": "metadata", "data": json.dumps(metadata)}

            # Session context
            session = None
            context_str = ""
            if getattr(request, "session_id", None):
                session = self.session_store.load_session(request.session_id)
                if not session:
                    session = self.session_store.create_session(request.session_id, title="Research Session")
                context_str = ConversationContext(session).get_recent_context(num_turns=3)

            full_question = request.question
            if context_str:
                full_question = f"Previous context:\n{context_str}\n\nCurrent question: {request.question}"

            requires_synthesis = self._requires_synthesis(request.question) or len(request.paper_ids or []) > 1
            is_local_first = not requires_synthesis and confidence >= 0.75

            full_answer = ""
            provider_meta = None

            if not evidence:
                msg = "I could not find supporting evidence in the indexed papers."
                full_answer = msg
                yield {"event": "content", "data": json.dumps({"text": msg})}
            else:
                if is_local_first:
                    evidence_text = " ".join(chunk.text for chunk, _ in evidence)
                    extracted = f"*[Local Extractive Answer]*\n\n{self.local_extractor.summarize(evidence_text, num_sentences=4)}"
                    for token in extracted.split(" "):
                        chunk_text = token + " "
                        full_answer += chunk_text
                        yield {"event": "content", "data": json.dumps({"text": chunk_text})}
                else:
                    try:
                        async for piece in self.generator.answer_stream(full_question, evidence):
                            full_answer += piece
                            yield {"event": "content", "data": json.dumps({"text": piece})}
                        provider_meta = getattr(self.generator.provider, "last_request_info", None)
                    except Exception:
                        logger.exception("LLM streaming failed; falling back to extractive answer")
                        evidence_text = " ".join(chunk.text for chunk, _ in evidence)
                        extracted = f"*[Fallback Extractive Answer — provider unavailable]*\n\n{self.local_extractor.summarize(evidence_text, num_sentences=4)}"
                        for token in extracted.split(" "):
                            chunk_text = token + " "
                            full_answer += chunk_text
                            yield {"event": "content", "data": json.dumps({"text": chunk_text})}

            # Validate grounding
            grounding_result = self.grounding_validator.validate_answer(
                full_answer,
                evidence,
                answer_type="research",
            )

            grounding_stats = GroundingStats(
                groundedness_score=grounding_result.groundedness_score,
                hallucination_risk=grounding_result.hallucination_risk,
                risk_level=grounding_result.risk_level,
                supported_claims=grounding_result.supported_claims,
                total_claims=grounding_result.total_claims,
            )

            # Persist session turn
            if session:
                turn = ConversationTurn(
                    turn_id=uuid4().hex,
                    timestamp=datetime.now(),
                    question=request.question,
                    answer=full_answer,
                    sources=[s.model_dump() for s in sources],
                    grounding_score=grounding_stats.groundedness_score,
                    papers_cited=list({s.paper_id for s in sources}),
                )
                self.session_store.add_turn(session.session_id, turn)

            # Emit grounding stats and final provider metadata if available
            yield {"event": "grounding", "data": json.dumps(grounding_stats.model_dump())}
            yield {"event": "provider", "data": json.dumps(provider_meta or {})}

        except Exception:
            logger.exception("Error during SSE chat stream")
            yield {"event": "error", "data": json.dumps({"message": "An internal error occurred while streaming the answer."})}
        finally:
            yield {"event": "end", "data": "{}"}


rag_service = RagService()
