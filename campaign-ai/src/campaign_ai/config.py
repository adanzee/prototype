from functools import lru_cache
from pathlib import Path

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        extra="ignore",
    )

    model: str = "openai/gpt-4o-mini"
    fallback_models: list[str] = Field(default_factory=list)

    openai_api_key: SecretStr = SecretStr("")
    anthropic_api_key: SecretStr = SecretStr("")
    gemini_api_key: SecretStr = SecretStr("")
    openrouter_api_key: SecretStr = SecretStr("")

    database_url: SecretStr = SecretStr("")
    demo_mode: bool = False

    max_brief_chars: int = Field(
        default=30000,
        ge=1,
        le=1000000,
    )

    llm_timeout_seconds: float = Field(default=45, gt=0)
    llm_attempts: int = Field(default=2, ge=1, le=3)


@lru_cache
def get_settings() -> Settings:
    return Settings()