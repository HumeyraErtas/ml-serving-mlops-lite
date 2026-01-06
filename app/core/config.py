from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    SERVICE_NAME: str = "ml-serving-mlops-lite"
    SERVICE_VERSION: str = "1.0.0"
    ENV: str = "local"

    ENABLE_DOCS: bool = True

    MODEL_DIR: str = "models"
    MODEL_VERSION: str = "1.0.0"

    LOG_LEVEL: str = "INFO"


settings = Settings()
