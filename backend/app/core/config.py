from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Resolve repo root from backend/app/core/config.py
REPO_ROOT = Path(__file__).resolve().parents[3]
DATA_ROOT = REPO_ROOT / "data"
INDEXES_ROOT = DATA_ROOT / "indexes"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = Field(default="ResearchMind AI")
    environment: str = Field(default="development")
    debug: bool = Field(default=False)
    backend_cors_origins: str = "http://localhost:3000"
    database_url: str = Field(default="postgresql+asyncpg://researchmind:password@localhost:5432/researchmind")
    redis_url: str = Field(default="redis://localhost:6379/0")
    enable_telemetry: bool = Field(default=False)
    data_dir: Path = DATA_ROOT
    indexes_path: Path = INDEXES_ROOT
    summary_cache_path: Path = DATA_ROOT / "cache" / "summaries"
    faiss_index_path: Path = INDEXES_ROOT / "researchmind.faiss"
    metadata_path: Path = INDEXES_ROOT / "metadata.json"
    use_local_summarization: bool = Field(default=True)
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    llm_provider: str = Field(default="openrouter")
    openai_api_key: str | None = Field(default=None, repr=False)
    openrouter_api_key: str | None = Field(default=None, repr=False)
    gemini_api_key: str | None = Field(default=None, repr=False)
    gemini_model: str = Field(default="gemini-1.5-flash")
    openrouter_base_url: str = Field(default="https://openrouter.ai/api/v1")
    openrouter_model: str = Field(default="deepseek/deepseek-v4-flash:free")
    openrouter_fallback_models: str = Field(
        default="deepseek/deepseek-v4-flash:free,google/gemini-2.0-flash-exp:free,qwen/qwen-2.5-72b-instruct:free,openrouter/free",
        env="OPENROUTER_FALLBACK_MODELS",
        repr=False,
    )
    openai_default_model: str = "gpt-4o-mini"
    default_llm_model: str = "deepseek/deepseek-v4-flash:free"
    
    # AWS Bedrock settings
    aws_access_key_id: str | None = Field(default=None)
    aws_secret_access_key: str | None = Field(default=None)
    aws_region_name: str = Field(default="us-east-1")
    bedrock_default_model: str = "anthropic.claude-3-sonnet-20240229-v1:0"

    log_level: str = "INFO"
    top_k: int = 3
    chunk_size: int = 900
    chunk_overlap: int = 160
    request_timeout: int = 30

    @property
    def openrouter_default_model(self) -> str:
        return self.openrouter_model

    @property
    def openrouter_fallback_model_list(self) -> list[str]:
        return [
            model.strip()
            for model in self.openrouter_fallback_models.split(",")
            if model.strip()
        ]

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.backend_cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
