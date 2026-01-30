"""Application configuration settings."""
from pydantic_settings import BaseSettings
from functools import lru_cache
from pathlib import Path


class Settings(BaseSettings):
    """Application settings."""

    # Application
    APP_NAME: str = "Meeting Assistant"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # API
    API_V1_STR: str = "/api/v1"

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./meeting_assistant.db"

    # File Upload
    UPLOAD_DIR: Path = Path("uploads")
    MAX_UPLOAD_SIZE: int = 100 * 1024 * 1024  # 100MB
    ALLOWED_AUDIO_EXTENSIONS: set = {".mp3", ".wav", ".m4a", ".flac", ".ogg"}

    # External APIs
    ZHIPU_API_KEY: str = "232cb49079384ffab6053c98abb8f301.5OSqsh8KF3687sEU"
    SEPARATION_API_KEY: str = ""
    SEPARATION_API_URL: str = "http://192.168.0.100:40901/recognize"  # Example local URL
    ASR_API_KEY: str = ""  # API key for ASR service (e.g., OpenAI Whisper, iFLYTEK)
    ASR_API_URL: str = ""  # ASR service endpoint

    # Task Processing
    TASK_RETRY_COUNT: int = 3
    TASK_POLLING_INTERVAL: int = 3  # seconds

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
