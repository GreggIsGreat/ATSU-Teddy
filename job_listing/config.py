from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Job Listing API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8001  # Different port from Django (8000)

    # CORS - Allow Django app
    ALLOWED_ORIGINS: str = "http://localhost:8000,http://127.0.0.1:8000"

    # Django App Integration
    DJANGO_APP_URL: str = "http://localhost:8000"
    DJANGO_API_KEY: Optional[str] = None

    # RapidAPI
    RAPIDAPI_KEY: str = ""

    # API Hosts
    LINKEDIN_API_HOST: str = "linkedin-jobs-search.p.rapidapi.com"
    JSEARCH_API_HOST: str = "jsearch.p.rapidapi.com"

    # Redis (optional caching)
    REDIS_URL: Optional[str] = None
    CACHE_TTL: int = 1800  # 30 minutes

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 30
    REQUEST_DELAY: float = 1.0

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()