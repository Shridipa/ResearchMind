from typing import Any

from app.api.v1.schemas import SourceSpan
from app.llm.prompt_templates import LITERATURE_REVIEW_SYSTEM_PROMPT
from app.llm.provider_factory import get_llm_provider
from app.rag.confidence import confidence_from_evidence, unsupported_claim_risk
from app.services.dependencies import get_retriever


class LiteratureService:
    def __init__(self) -> None:
        self.provider = get_llm_provider()

    def generate_review(self, topic: str, paper_ids: list[str] | None = None) -> dict[str, Any]:
        # Retrieve evidence across papers
        evidence = get_retriever().retrieve(topic, top_k=15, paper_ids=paper_ids)
        
        if not evidence:
            return {
                "review": "No evidence found to generate a literature review.",
                "confidence": 0,
                "sources": []
            }
            
        formatted_evidence = "\n\n".join(
            f"[{chunk.title}, page {chunk.page}, id: {chunk.chunk_id}]\n{chunk.text}"
            for chunk, _ in evidence
        )
        
        system_prompt = LITERATURE_REVIEW_SYSTEM_PROMPT.format(evidence=formatted_evidence)
        
        try:
            # We don't stream literature review for now, just generate the full markdown report
            review_md = self.provider.generate(system_prompt, f"Generate a literature review on: {topic}", model="anthropic/claude-3.5-sonnet")
        except Exception as e:
            review_md = f"Error generating literature review: {e}"

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
        
        return {
            "topic": topic,
            "review": review_md,
            "confidence": confidence,
            "unsupported_claim_risk": unsupported_claim_risk(confidence),
            "sources": sources
        }


literature_service = LiteratureService()
