"""Application configuration loaded from the environment."""

from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings; provider credentials are consumed directly by LiteLLM."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    models: list[str] = Field(
        default_factory=lambda: [
            "gpt-4o-mini",
            "claude-3-5-haiku-latest",
            "gemini/gemini-1.5-flash",
        ]
    )
    judge_model: str | None = None
    request_timeout_seconds: float = Field(default=30, gt=0, le=120)
    max_prompt_characters: int = Field(default=8_000, gt=0, le=100_000)

    @field_validator("models", mode="before")
    @classmethod
    def split_models(cls, value: object) -> object:
        """Accept a comma-separated MODELS value as well as a native list."""
        if isinstance(value, str):
            return [model.strip() for model in value.split(",") if model.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    """Return the cached process-level settings instance."""
    return Settings()
