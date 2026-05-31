import time
from typing import AsyncGenerator

from app.llm.base_provider import LLMProvider


class MockProvider(LLMProvider):
    """Local deterministic provider for demos, tests, and offline development."""

    def __init__(self) -> None:
        self.last_request_info: dict[str, object] | None = None

    def _record(self, start_time: float) -> None:
        self.last_request_info = {
            "selected_model": "local-mock-grounded-generator",
            "attempted_models": ["local-mock-grounded-generator"],
            "retry_count": 0,
            "fallback_triggered": False,
            "latency_ms": round((time.monotonic() - start_time) * 1000, 2),
            "error": None,
        }

    def generate(self, system_prompt: str, user_prompt: str, model: str | None = None) -> str:
        start_time = time.monotonic()
        self._record(start_time)
        return (
            "ResearchMind AI is running in local demo mode. I can answer with retrieved source "
            "evidence after you upload and index research papers. Current question: "
            f"{user_prompt}"
        )

    async def generate_stream(
        self, system_prompt: str, user_prompt: str, model: str | None = None
    ) -> AsyncGenerator[str, None]:
        response = self.generate(system_prompt, user_prompt, model)
        for token in response.split(" "):
            yield token + " "
