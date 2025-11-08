from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    APP_NAME: str = "Bookshelf API"
    API_VERSION: str = "v1"
    ALLOWED_ORIGINS: List[str] = ["*"]  # In production, replace with specific domains
    SECRET_KEY: str = "TESTKEY"  # Should be set via environment variable in production
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 1


settings = Settings()