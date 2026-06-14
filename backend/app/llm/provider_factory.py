from app.core.config import settings
from app.llm.base_provider import LLMProvider


def get_llm_provider() -> LLMProvider:
    provider_name = settings.llm_provider.lower()
    if provider_name == "openrouter":
        from app.llm.openrouter_provider import OpenRouterProvider

        return OpenRouterProvider()
    if provider_name == "openai":
        from app.llm.openai_provider import OpenAIProvider

        return OpenAIProvider()
    if provider_name == "gemini":
        from app.llm.gemini_provider import GeminiProvider

        return GeminiProvider()
    if provider_name == "mock":
        from app.llm.mock_provider import MockProvider

        return MockProvider()
    if provider_name == "bedrock":
        from app.llm.bedrock_provider import BedrockLLM

        return BedrockLLM()
    raise ValueError(
        f"Unsupported llm_provider '{settings.llm_provider}'. "
        "Supported providers are: openrouter, openai, gemini, bedrock, mock."
    )
