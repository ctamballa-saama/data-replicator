"""
Configuration settings for the DataReplicator application.
Uses Pydantic for settings management and validation.
"""
from pathlib import Path
from typing import Optional, Dict, Any, List

from pydantic_settings import BaseSettings
from pydantic import Field, validator


class Settings(BaseSettings):
    """
    Application settings and configuration.
    
    Loads configuration from environment variables and .env file.
    Environment variables take precedence over values loaded from .env file.
    """
    # Application settings
    APP_NAME: str = "DataReplicator"
    APP_VERSION: str = "0.1.0"
    APP_DESCRIPTION: str = "A tool for analyzing clinical trial datasets and generating synthetic data"
    DEBUG: bool = Field(False, description="Debug mode flag")
    
    # API settings
    API_HOST: str = Field("127.0.0.1", description="API host")
    API_PORT: int = Field(8000, description="API port")
    API_PREFIX: str = Field("/api/v1", description="API route prefix")
    
    # Database settings
    DATABASE_URL: str = Field("sqlite:///datareplicator.db", description="Database connection string")
    
    # File storage settings
    UPLOAD_DIR: Path = Field(Path("./uploads"), description="Directory for uploaded files")
    OUTPUT_DIR: Path = Field(Path("./output"), description="Directory for generated outputs")
    
    # Security settings
    SECRET_KEY: str = Field("datareplicator_dev_secret_key", description="Secret key for token signing")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(30, description="Minutes until access token expires")
    
    # Data generation settings
    DEFAULT_TARGET_SUBJECTS: int = Field(100, description="Default number of subjects to generate")
    MAX_TARGET_SUBJECTS: int = Field(1000, description="Maximum number of subjects allowed to generate")
    ALLOW_PII_GENERATION: bool = Field(False, description="Whether to allow PII field generation")
    
    # Validation settings
    APPLY_CDISC_RULES: bool = Field(True, description="Whether to apply CDISC validation rules")
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
    
    @validator("UPLOAD_DIR", "OUTPUT_DIR", pre=True)
    def create_directory(cls, v: Path) -> Path:
        """Create directory if it doesn't exist."""
        v = Path(v)
        v.mkdir(parents=True, exist_ok=True)
        return v


def get_settings() -> Settings:
    """
    Get application settings.
    
    Returns:
        Settings: Application settings object
    """
    return Settings()
