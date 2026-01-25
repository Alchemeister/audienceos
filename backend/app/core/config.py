"""Application configuration using Pydantic Settings."""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # App
    APP_ENV: Literal["development", "staging", "production"] = "development"
    APP_URL: str = "http://localhost:3000"
    API_URL: str = "http://localhost:8000"
    SECRET_KEY: str = "change-me-in-production"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./audienceos.db"

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # AI Services
    ANTHROPIC_API_KEY: str = ""
    DEEPSEEK_API_KEY: str = ""  # Primary cheap tier (88.5% MMLU, best cost with caching)
    OPENAI_API_KEY: str = ""  # Fallback cheap tier (GPT-4o-mini)

    # Reddit API
    REDDIT_CLIENT_ID: str = ""
    REDDIT_CLIENT_SECRET: str = ""
    REDDIT_USER_AGENT: str = "audienceos/1.0"

    # Twitter/X API (optional)
    TWITTER_BEARER_TOKEN: str = ""

    # GitHub API (optional)
    GITHUB_TOKEN: str = ""

    # Email (Resend)
    RESEND_API_KEY: str = ""

    # Error tracking
    SENTRY_DSN: str = ""

    # Stripe
    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    STRIPE_PRICE_INDIE: str = ""
    STRIPE_PRICE_PRO: str = ""
    STRIPE_PRICE_AGENCY: str = ""

    # Feature flags
    ENABLE_TWITTER: bool = False
    ENABLE_GITHUB: bool = False

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"

    @property
    def database_url_async(self) -> str:
        """Convert sync database URL to async if needed."""
        url = self.DATABASE_URL
        if url.startswith("postgresql://"):
            return url.replace("postgresql://", "postgresql+asyncpg://", 1)
        if url.startswith("sqlite://"):
            return url.replace("sqlite://", "sqlite+aiosqlite://", 1)
        return url


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
