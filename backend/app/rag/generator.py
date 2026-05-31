import json
import logging
from typing import AsyncGenerator

from app.llm.prompt_templates import QA_SYSTEM_PROMPT, SUMMARY_SYSTEM_PROMPT
from app.llm.provider_factory import get_llm_provider
from app.rag.chunking import DocumentChunk

logger = logging.getLogger(__name__)

class GroundedGenerator:
    def __init__(self) -> None:
        try:
            self.provider = get_llm_provider()
        except Exception as exc:
            logger.warning("LLM provider unavailable, falling back to local-only generation: %s", exc)
            self.provider = None

    def _format_evidence(self, evidence: list[tuple[DocumentChunk, float]]) -> str:
        return "\n\n".join(
            f"[{chunk.title}, page {chunk.page}, id: {chunk.chunk_id}]\n{chunk.text}"
            for chunk, _ in evidence
        )

    def answer(self, question: str, evidence: list[tuple[DocumentChunk, float]]) -> str:
        if not evidence:
            return "I could not find enough evidence in the indexed papers to answer this question."
        if self.provider is None:
            raise RuntimeError("LLM provider unavailable")

        system_prompt = QA_SYSTEM_PROMPT.format(evidence=self._format_evidence(evidence))
        try:
            return self.provider.generate(system_prompt, question)
        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            raise

    async def answer_stream(self, question: str, evidence: list[tuple[DocumentChunk, float]]) -> AsyncGenerator[str, None]:
        if not evidence:
            yield "I could not find enough evidence in the indexed papers to answer this question."
            return
        if self.provider is None:
            raise RuntimeError("LLM provider unavailable")

        system_prompt = QA_SYSTEM_PROMPT.format(evidence=self._format_evidence(evidence))
        try:
            async for chunk in self.provider.generate_stream(system_prompt, question):
                yield chunk
        except Exception as e:
            logger.error(f"Error streaming answer: {e}")
            raise

    def summarize(self, evidence: list[tuple[DocumentChunk, float]]) -> dict[str, str | list[str]]:
        if not evidence:
            return {
                "abstract": "No indexed evidence found.",
                "contributions": [],
                "methods": "No evidence.",
                "findings": "No evidence.",
                "limitations": [],
            }
        if self.provider is None:
            logger.warning("LLM provider unavailable; returning fallback summary structure.")
            return {
                "abstract": "LLM provider unavailable; summary could not be generated.",
                "contributions": [],
                "methods": "LLM provider unavailable.",
                "findings": "LLM provider unavailable.",
                "limitations": [],
            }

        system_prompt = SUMMARY_SYSTEM_PROMPT.format(evidence=self._format_evidence(evidence))
        try:
            response_text = self.provider.generate(system_prompt, "Generate the summary.")

            # Simple cleanup in case the model wraps JSON in markdown blocks
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]

            return json.loads(response_text.strip())
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return {
                "abstract": "Failed to generate summary.",
                "contributions": [],
                "methods": f"Error: {e}",
                "findings": "",
                "limitations": [],
            }
