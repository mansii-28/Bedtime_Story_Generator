from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # Model config
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    
    # Story constraints
    STORY_MIN_WORDS: int = 80
    STORY_MAX_WORDS: int = 300
    MAX_REVISION_ATTEMPTS: int = 2
    
    # App config
    FRONTEND_ORIGIN: str = "http://localhost:5173"
    LOG_LEVEL: str = "INFO"
    RATE_LIMIT_PER_MINUTE: int = 10
    
    # Optional: allow reading from .env file
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
