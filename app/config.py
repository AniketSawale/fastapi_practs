from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings, loaded from environment variables or a .env file.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Connected Lighting Telemetry API"
    log_level: str = "INFO"
    max_readings_per_device: int = 1000

    # LLM config -used in Phase 3
    llm_provider: str = "mock"
    llm_api_key: str | None = None
    llm_model: str = "gpt-4o-mini"


@lru_cache
def get_settings() -> Settings:
    """
    Cached settings instance. Suitable for use as a FastAPI depenedency.
    """
    return Settings()
