"""
Application configuration.

Uses Pydantic Settings for environment-based configuration.
Follows the Dependency Inversion Principle by abstracting configuration.
"""

from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings.

    Loads configuration from environment variables.
    Follows the Single Responsibility Principle.
    """

    # Application
    APP_NAME: str = "FastAPI MVC Application"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    SECRET_KEY: str = "dev-secret-key-change-in-production"

    # Database
    DATABASE_URL: str = "sqlite:///./app.db"

    # CORS
    ALLOWED_HOSTS: List[str] = ["http://localhost:3000", "http://localhost:8000"]

    # Logging
    LOG_LEVEL: str = "INFO"

    class Config:
        """Pydantic config."""

        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Global settings instance
settings = Settings()
