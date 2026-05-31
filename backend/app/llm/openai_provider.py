from typing import AsyncGenerator

from openai import AsyncOpenAI, OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import settings
from app.llm.base_provider import LLMProvider


class OpenAIProvider(LLMProvider):
    def __init__(self) -> None:
        api_key = settings.openai_api_key
        if not api_key:
            raise ValueError("OPENAI_API_KEY must be set to use OpenAI.")

        self.sync_client = OpenAI(api_key=api_key)
        self.async_client = AsyncOpenAI(api_key=api_key)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    def generate(self, system_prompt: str, user_prompt: str, model: str | None = None) -> str:
        model = model or settings.openai_default_model
        response = self.sync_client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
        )
        return response.choices[0].message.content or ""

    async def generate_stream(
        self, system_prompt: str, user_prompt: str, model: str | None = None
    ) -> AsyncGenerator[str, None]:
        model = model or settings.openai_default_model
        response = await self.async_client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
            stream=True,
        )
        async for chunk in response:
            content = None
            if chunk.choices and chunk.choices[0].delta:
                content = chunk.choices[0].delta.get("content")
            if content:
                yield content
