"""
Configuration settings for the DataReplicator application.
"""
from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings."""
    
    # API configuration
    API_V1_PREFIX: str = "/api/v1"
    APP_NAME: str = "DataReplicator"
    APP_DESCRIPTION: str = "Clinical data analysis and synthetic data generation"
    
    # CORS configuration
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    CORS_METHODS: List[str] = ["*"]
    CORS_HEADERS: List[str] = ["*"]
    
    # File upload configuration
    UPLOAD_DIR: str = "/tmp/datareplicator_uploads"
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024  # 50 MB
    
    # Generation job configuration
    JOB_TIMEOUT: int = 300  # seconds
    
    # Create upload directory if it doesn't exist
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        os.makedirs(self.UPLOAD_DIR, exist_ok=True)

    class Config:
        env_prefix = "DR_"  # environment variables prefix
        case_sensitive = True


# Create singleton instance
settings = Settings()
