"""
Shelf Life Estimator — Application Configuration
=================================================
Loads settings from environment variables with sensible defaults.
Uses pydantic-settings for type-safe configuration.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # --- Application ---
    app_name: str = "Shelf Life Estimator"
    app_version: str = "1.0.0"
    debug: bool = True

    # --- Database ---
    database_url: str = "sqlite+aiosqlite:///./shelf_life.db"

    # --- CORS ---
    allowed_origins: str = "http://localhost:3000,http://127.0.0.1:3000"

    # --- Security ---
    secret_key: str = "dev-secret-key-change-in-production"
    access_token_expire_minutes: int = 30

    # --- File Uploads ---
    upload_dir: str = "uploads"
    max_upload_size_mb: int = 10

    # --- AI Models ---
    classifier_model_path: str = "models/food_classifier.h5"
    freshness_model_path: str = "models/freshness_assessor.h5"

    @property
    def cors_origins(self) -> list[str]:
        """Parse comma-separated CORS origins into a list."""
        return [origin.strip() for origin in self.allowed_origins.split(",")]


@lru_cache
def get_settings() -> Settings:
    """
    Get cached application settings.
    Uses lru_cache so .env is only read once.
    """
    return Settings()
