"""
Configuration settings for InvestAI Backend
"""

from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import validator
import os
from pathlib import Path

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent


class Settings(BaseSettings):
    """Application settings"""
    
    # Basic app settings
    APP_NAME: str = "InvestAI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Database settings
    DATABASE_URL: str = "postgresql://postgres:password@localhost/investai_db"
    DATABASE_ECHO: bool = False
    
    # Redis settings
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_CACHE_TTL: int = 3600  # 1 hour
    
    # Security settings
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS settings
    ALLOWED_HOSTS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # AI API settings
    GEMINI_API_KEY: str = ""
    OPENAI_API_KEY: Optional[str] = None
    
    # Market data API settings
    ALPHA_VANTAGE_API_KEY: Optional[str] = None
    YAHOO_FINANCE_ENABLED: bool = True
    
    # External API rate limits
    API_RATE_LIMIT_PER_MINUTE: int = 60
    MARKET_DATA_REFRESH_INTERVAL: int = 300  # 5 minutes
    
    # File upload settings
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_TYPES: List[str] = ["pdf", "csv", "xlsx"]
    
    # Email settings (for notifications)
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    
    # Logging settings
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/investai.log"
    
    # Indian market specific settings
    NSE_ENABLED: bool = True
    BSE_ENABLED: bool = True
    MUTUAL_FUND_DATA_ENABLED: bool = True
    
    # Tax calculation settings
    CURRENT_FINANCIAL_YEAR: str = "2024-25"
    TAX_BRACKETS_UPDATE_DATE: str = "2024-04-01"
    
    @validator("ALLOWED_HOSTS", pre=True)
    def assemble_cors_origins(cls, v):
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v
    
    @validator("DATABASE_URL", pre=True)
    def validate_database_url(cls, v):
        if not v:
            raise ValueError("DATABASE_URL is required")
        return v
    
    @validator("SECRET_KEY", pre=True)
    def validate_secret_key(cls, v):
        if not v or v == "your-secret-key-change-this-in-production":
            if os.getenv("ENVIRONMENT") == "production":
                raise ValueError("SECRET_KEY must be set in production")
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()

# Create logs directory if it doesn't exist
log_dir = PROJECT_ROOT / "logs"
log_dir.mkdir(exist_ok=True)
