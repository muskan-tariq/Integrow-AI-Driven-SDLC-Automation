from pydantic_settings import BaseSettings
from typing import List
import os
from pathlib import Path

class Settings(BaseSettings):
    # Environment
    ENVIRONMENT: str = "production"
    DEBUG: bool = False
    HOST: str = "localhost"
    PORT: int = 8000
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8080",
        "http://localhost:8888",  # Electron dev server
        "http://127.0.0.1:8888",
        "integrow://",  # Electron app protocol
    ]
    
    # Supabase Configuration
    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_SERVICE_KEY: str
    
    # GitHub OAuth
    GITHUB_CLIENT_ID: str
    GITHUB_CLIENT_SECRET: str
    GITHUB_REDIRECT_URI: str = "integrow://auth/callback"
    
    # JWT Configuration
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    
    # Encryption
    ENCRYPTION_KEY: str
    
    # Local Storage
    PROJECTS_BASE_DIR: str = str(Path.home() / "InteGrow" / "Projects")
    
    # Redis (for session management)
    REDIS_URL: str = "redis://localhost:6379"
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60  # seconds
    
    # Phase 1: LLM API Keys
    GROQ_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    HUGGINGFACE_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    
    # Phase 1: Feature Flags
    USE_LOCAL_SPACY: bool = True
    ENABLE_CACHE: bool = True
    CACHE_TTL_HOURS: int = 24
    DEVELOPMENT_MODE: bool = False
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

# Create settings instance
settings = Settings()

# Ensure projects directory exists
os.makedirs(settings.PROJECTS_BASE_DIR, exist_ok=True)

# Getter function for dependency injection
def get_settings() -> Settings:
    return settings
