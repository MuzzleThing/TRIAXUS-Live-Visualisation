"""
Configuration settings for TRIAXUS backend system.
"""
import os
from pathlib import Path
from typing import Optional

# Pydantic v2: BaseSettings moved to pydantic-settings
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Base settings configuration."""
    
    # Application settings
    APP_NAME: str = "TRIAXUS Live Visualization"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    
    # Database settings
    DATABASE_URL: str = "postgresql://triaxus_user:triaxus_pass@localhost:5432/triaxus_db"
    DATABASE_ECHO: bool = False
    
    # TimescaleDB settings
    TIMESCALEDB_ENABLED: bool = True
    
    # PostGIS settings
    POSTGIS_ENABLED: bool = True
    
    # File processing settings
    MAX_FILE_SIZE: int = 1024*1024*100  # 100MB
    SUPPORTED_FILE_TYPES: list = ["CNV", "HEX", "HDR", "XMLCON", "NC"]
    CNV_ENCODING: str = "utf-8"
    
    # Real-time processing settings
    REALTIME_BUFFER_SIZE: int = 1000
    PROCESSING_BATCH_SIZE: int = 100
    FILE_WATCH_INTERVAL: float = 1.0  # seconds
    
    # Quality control settings
    QC_TEMPERATURE_MIN: float = -5.0
    QC_TEMPERATURE_MAX: float = 40.0
    QC_DEPTH_MIN: float = -10.0
    QC_DEPTH_MAX: float = 400.0
    QC_LATITUDE_MIN: float = -90.0
    QC_LATITUDE_MAX: float = 90.0
    QC_LONGITUDE_MIN: float = -180.0
    QC_LONGITUDE_MAX: float = 180.0
    
    # Cast detection settings
    CAST_MIN_DEPTH_CHANGE: float = 5.0  # meters
    CAST_MIN_DURATION: int = 60  # seconds
    
    # Data export settings
    EXPORT_FORMAT: str = "netcdf"
    EXPORT_COMPRESSION: bool = True
    
    # Logging settings
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE: Optional[str] = None
    
    # Cache settings
    CACHE_TTL: int = 300  # 5 minutes
    
    # Celery settings (for async tasks)
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # Pydantic v2 settings config
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

# Create global settings instance
settings = Settings()
