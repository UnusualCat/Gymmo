from typing import Any, Dict, Optional
from pydantic import PostgresDsn, validator
from pydantic import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Gymmo"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = "your-secret-key-here"  # Change in production
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # Database
    SQLALCHEMY_DATABASE_URI: str = "sqlite:///./gymmo.db"
    
    # Google Drive
    GOOGLE_DRIVE_CREDENTIALS_FILE: str = "credentials.json"
    GOOGLE_DRIVE_TOKEN_FILE: str = "token.json"
    
    # CORS
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:3000"]  # Frontend URL
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings() 