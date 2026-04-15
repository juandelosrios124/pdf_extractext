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
    APP_NAME: str = "PDF Extract API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ENVIRONMENT: str = "development"

    # MongoDB Configuration
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "pdf_extract_db"
    MONGODB_MAX_CONNECTIONS: int = 10
    MONGODB_MIN_CONNECTIONS: int = 1
    MONGODB_MAX_IDLE_TIME_MS: int = 60000
    MONGODB_WAIT_QUEUE_TIMEOUT_MS: int = 5000

    # CORS
    ALLOWED_HOSTS: List[str] = ["http://localhost:3000", "http://localhost:8000"]

    # Logging
    LOG_LEVEL: str = "INFO"

    # File Upload
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024  # 50MB
    ALLOWED_EXTENSIONS: List[str] = [".pdf"]

    class Config:
        """Pydantic config."""

        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Global settings instance
settings = Settings()
