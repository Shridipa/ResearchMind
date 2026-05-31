import logging
import os
from typing import AsyncGenerator

import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import settings
from app.llm.base_provider import LLMProvider


logger = logging.getLogger(__name__)


class GeminiProvider(LLMProvider):
    def __init__(self) -> None:
        api_key = settings.gemini_api_key or os.environ.get("GEMINI_API_KEY")
        if not api_key or api_key.strip() == "" or api_key.strip().lower() == "your_gemini_key_here":
            raise ValueError(
                "GEMINI_API_KEY must be set to use Google Gemini. "
                "Set it in backend/.env or export GEMINI_API_KEY."
            )

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(settings.gemini_model)
        self.default_model = settings.gemini_model

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    def generate(self, system_prompt: str, user_prompt: str, model: str | None = None) -> str:
        """Generate a complete response using Gemini."""
        try:
            # Combine system prompt and user prompt
            full_prompt = f"{system_prompt}\n\n{user_prompt}"
            
            response = self.model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.1,
                    top_p=0.8,
                    top_k=32,
                    max_output_tokens=1024,
                ),
            )
            
            if response.text:
                return response.text
            else:
                logger.warning("Empty response from Gemini API")
                return ""
                
        except Exception as exc:
            logger.error(f"Error generating content with Gemini: {exc}")
            raise

    async def generate_stream(
        self, system_prompt: str, user_prompt: str, model: str | None = None
    ) -> AsyncGenerator[str, None]:
        """Generate a streamed response using Gemini."""
        try:
            # Combine system prompt and user prompt
            full_prompt = f"{system_prompt}\n\n{user_prompt}"
            
            # Use streaming for faster delivery of responses
            response = self.model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.1,
                    top_p=0.8,
                    top_k=32,
                    max_output_tokens=1024,
                ),
                stream=True,
            )
            
            for chunk in response:
                if chunk.text:
                    yield chunk.text
                    
        except Exception as exc:
            logger.error(f"Error streaming content with Gemini: {exc}")
            raise
