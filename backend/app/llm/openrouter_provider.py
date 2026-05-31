import logging
import os
import time
from typing import AsyncGenerator

from openai import AsyncOpenAI, OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import settings
from app.llm.base_provider import LLMProvider


logger = logging.getLogger(__name__)


class OpenRouterProvider(LLMProvider):
    def __init__(self) -> None:
        api_key = settings.openrouter_api_key or os.environ.get("OPENROUTER_API_KEY")
        if not api_key or api_key.strip() == "" or api_key.strip().lower() == "your_openrouter_key_here":
            raise ValueError(
                "OPENROUTER_API_KEY must be set to use OpenRouter. "
                "Set it in backend/.env or export OPENROUTER_API_KEY."
            )

        # Configure clients with timeout
        self.sync_client = OpenAI(
            base_url=settings.openrouter_base_url, 
            api_key=api_key,
            timeout=30.0  # 30 second timeout for faster failures
        )
        self.async_client = AsyncOpenAI(
            base_url=settings.openrouter_base_url, 
            api_key=api_key,
            timeout=30.0  # 30 second timeout for faster failures
        )
        self.primary_model = settings.openrouter_model
        self.fallback_models = [
            model
            for model in settings.openrouter_fallback_model_list
            if model and model != self.primary_model
        ]
        self.last_request_info: dict[str, object] | None = None
        logger.info(f"OpenRouter provider initialized with primary model: {self.primary_model}")
        logger.info(f"Fallback models: {self.fallback_models}")

    def _is_retryable(self, error: Exception) -> bool:
        text = str(error).lower()
        return any(
            keyword in text
            for keyword in [
                "insufficient credits",
                "no credit",
                "rate limit",
                "rate_limit",
                "too many requests",
                "timeout",
                "502",
                "503",
                "504",
                "busy",
                "unavailable",
                "temporarily",
            ]
        )

    def _record_request(
        self,
        selected_model: str,
        attempted_models: list[str],
        retry_count: int,
        start_time: float,
        error: Exception | None = None,
    ) -> None:
        self.last_request_info = {
            "selected_model": selected_model,
            "attempted_models": attempted_models,
            "retry_count": retry_count,
            "fallback_triggered": retry_count > 0,
            "latency_ms": round((time.monotonic() - start_time) * 1000, 2),
            "error": str(error) if error else None,
        }

    def _build_model_sequence(self, explicit_model: str | None) -> list[str]:
        if explicit_model:
            return [explicit_model] + [m for m in self.fallback_models if m != explicit_model]
        return [self.primary_model] + self.fallback_models

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    def generate(self, system_prompt: str, user_prompt: str, model: str | None = None) -> str:
        models = self._build_model_sequence(model)
        last_error: Exception | None = None

        for retry_count, candidate_model in enumerate(models):
            attempted_models = models[: retry_count + 1]
            start_time = time.monotonic()
            try:
                response = self.sync_client.chat.completions.create(
                    model=candidate_model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=0.1,
                    max_tokens=1024,
                )
                self._record_request(candidate_model, attempted_models, retry_count, start_time)
                return response.choices[0].message.content or ""
            except Exception as exc:
                self._record_request(candidate_model, attempted_models, retry_count, start_time, exc)
                last_error = exc
                if retry_count == len(models) - 1 or not self._is_retryable(exc):
                    logger.exception(
                        "OpenRouter request failed for model %s after %s attempts",
                        candidate_model,
                        retry_count + 1,
                    )
                    raise
                logger.warning(
                    "OpenRouter model %s failed (attempt %s/%s); falling back to next model",
                    candidate_model,
                    retry_count + 1,
                    len(models),
                )
                continue

        raise last_error or RuntimeError("OpenRouter failed to generate a response.")

    async def generate_stream(
        self, system_prompt: str, user_prompt: str, model: str | None = None
    ) -> AsyncGenerator[str, None]:
        models = self._build_model_sequence(model)
        last_error: Exception | None = None

        for retry_count, candidate_model in enumerate(models):
            attempted_models = models[: retry_count + 1]
            start_time = time.monotonic()
            try:
                logger.info(f"Attempting OpenRouter streaming with model: {candidate_model}")
                response = await self.async_client.chat.completions.create(
                    model=candidate_model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=0.1,
                    max_tokens=1024,
                    stream=True,
                )
                self._record_request(candidate_model, attempted_models, retry_count, start_time)
                async for chunk in response:
                    try:
                        content = None
                        if chunk.choices and chunk.choices[0].delta:
                            # delta is an object with attributes, not a dict
                            delta = chunk.choices[0].delta
                            content = getattr(delta, "content", None)
                        if content:
                            yield content
                    except Exception as chunk_error:
                        logger.warning(f"Error processing chunk from {candidate_model}: {chunk_error}")
                        continue
                logger.info(f"Successfully completed streaming with {candidate_model}")
                return
            except Exception as exc:
                self._record_request(candidate_model, attempted_models, retry_count, start_time, exc)
                last_error = exc
                logger.warning(
                    f"OpenRouter streaming error with {candidate_model} (attempt {retry_count + 1}/{len(models)}): {exc}",
                    exc_info=True,
                )
                if retry_count == len(models) - 1 or not self._is_retryable(exc):
                    logger.exception(
                        "OpenRouter streaming failed for model %s after %s attempts",
                        candidate_model,
                        retry_count + 1,
                    )
                    raise
                logger.warning(
                    "OpenRouter streaming model %s failed; falling back to next model",
                    candidate_model,
                )
                continue

        raise last_error or RuntimeError("OpenRouter failed to stream a response.")
