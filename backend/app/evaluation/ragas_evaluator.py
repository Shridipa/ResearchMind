import asyncio
from typing import Any

from openai import AsyncOpenAI
from pydantic import BaseModel
from ragas.llms import llm_factory
from ragas.metrics import DiscreteMetric

from app.core.config import settings


class EvaluationResult(BaseModel):
    score: str | None
    reason: str | None


class RagasEvaluator:
    def __init__(self) -> None:
        if not settings.openrouter_api_key:
            raise ValueError("openrouter_api_key is required for Ragas evaluation.")
            
        self.client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=settings.openrouter_api_key,
        )
        # We use a default fast model for evaluation
        self.llm = llm_factory(settings.default_llm_model, client=self.client)

        self.faithfulness_metric = DiscreteMetric(
            name="faithfulness",
            allowed_values=["faithful", "unfaithful"],
            prompt="""Evaluate if the generated answer is strictly faithful to the provided context.
If it contains ANY claims not supported by the context, it is 'unfaithful'.

Context: {context}
Answer: {response}

Answer with only 'faithful' or 'unfaithful'."""
        )
        
        self.relevancy_metric = DiscreteMetric(
            name="answer_relevancy",
            allowed_values=["relevant", "irrelevant"],
            prompt="""Evaluate if the generated answer directly addresses the user's question.

Question: {question}
Answer: {response}

Answer with only 'relevant' or 'irrelevant'."""
        )

    async def evaluate_faithfulness(self, response: str, context: str) -> EvaluationResult:
        try:
            # We must pass the variables defined in the prompt string
            score_result = await self.faithfulness_metric.ascore(
                llm=self.llm,
                response=response,
                context=context
            )
            return EvaluationResult(score=score_result.value, reason=score_result.reason)
        except Exception as e:
            return EvaluationResult(score=None, reason=str(e))

    async def evaluate_relevancy(self, question: str, response: str) -> EvaluationResult:
        try:
            score_result = await self.relevancy_metric.ascore(
                llm=self.llm,
                response=response,
                question=question
            )
            return EvaluationResult(score=score_result.value, reason=score_result.reason)
        except Exception as e:
            return EvaluationResult(score=None, reason=str(e))

    async def evaluate_rag_pipeline(self, question: str, response: str, contexts: list[str]) -> dict[str, Any]:
        context_str = "\n".join(contexts)
        
        # Run evaluations concurrently
        f_task = asyncio.create_task(self.evaluate_faithfulness(response, context_str))
        r_task = asyncio.create_task(self.evaluate_relevancy(question, response))
        
        f_result, r_result = await asyncio.gather(f_task, r_task)
        
        return {
            "faithfulness": f_result.score,
            "faithfulness_reason": f_result.reason,
            "answer_relevancy": r_result.score,
            "relevancy_reason": r_result.reason,
        }

ragas_evaluator = RagasEvaluator()
