"""
Configuration settings for the CodeMentor AI Backend
"""
import os
from functools import lru_cache
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    app_name: str = "CodeMentor AI Backend"
    port: int = 8000
    debug: bool = False
    
    # CORS - stored as string, converted to list via property
    cors_origins_str: str = "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173"
    
    @property
    def cors_origins(self) -> List[str]:
        """Parse CORS origins from comma-separated string"""
        return [origin.strip() for origin in self.cors_origins_str.split(",")]
    
    # Supabase
    supabase_url: str = ""
    supabase_key: str = ""
    
    # Google Gemini API
    gemini_api_key: str = ""
    
    # Tavily API (for web search)
    tavily_api_key: str = ""
    
    # JWT Secret
    jwt_secret: str = "your-secret-key-change-this-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 60 * 24  # 24 hours
    
    # File upload settings
    max_upload_size: int = 10 * 1024 * 1024  # 10MB
    upload_dir: str = "uploads"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        # Don't try to parse strings as JSON
        env_parse_none_str="null"
    )


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
