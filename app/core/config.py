from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, List
from functools import lru_cache

class Settings(BaseSettings):
    APP_NAME: str = "MarketHub API"
    APP_VERSION: str = "1.0.0"

    DATABASE_URL: str
    DB_ECHO: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()