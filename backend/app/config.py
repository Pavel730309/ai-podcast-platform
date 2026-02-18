"""
Configuration settings for the AI Podcast Platform
"""
from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "AI Podcast Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    SECRET_KEY: str = "your-secret-key-change-in-production"
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/podcast_db"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # OpenAI
    OPENAI_API_KEY: Optional[str] = None
    
    # ElevenLabs
    ELEVENLABS_API_KEY: Optional[str] = None
    
    # Google Cloud
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = None
    
    # KIE.ai
    KIE_API_KEY: Optional[str] = None
    
    # File storage
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50 MB
    ALLOWED_EXTENSIONS: list = [".pdf", ".docx", ".txt"]
    
    # Audio settings
    AUDIO_SAMPLE_RATE: int = 22050
    AUDIO_FORMAT: str = "mp3"
    
    # TTS settings
    DEFAULT_TTS_PROVIDER: str = "openai"
    
    # Base URL (used for RSS feeds, export links, etc.)
    BASE_URL: str = "http://localhost:8000"

    # CORS
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:5173"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


settings = get_settings()
