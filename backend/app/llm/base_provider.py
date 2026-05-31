from abc import ABC, abstractmethod
from typing import AsyncGenerator


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    def generate(self, system_prompt: str, user_prompt: str, model: str | None = None) -> str:
        """Generate a complete string response."""
        pass

    @abstractmethod
    async def generate_stream(
        self, system_prompt: str, user_prompt: str, model: str | None = None
    ) -> AsyncGenerator[str, None]:
        """Generate a streamed response, yielding chunks of text."""
        pass
