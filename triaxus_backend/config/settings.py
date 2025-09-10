"""
Configuration settings for TRIAXUS backend system.
"""
import os
from pathlib import Path
from pydantic import BaseSettings, Field
from typing import Optional

class Settings(BaseSettings):
    """Base settings configuration."""
    
    # Application settings
    APP_NAME: str = "TRIAXUS Live Visualization"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = Field(default=False, env="DEBUG")
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    
    # Database settings
    DATABASE_URL: str = Field(
        default="postgresql://triaxus_user:triaxus_pass@localhost:5432/triaxus_db",
        env="DATABASE_URL"
    )
    DATABASE_ECHO: bool = Field(default=False, env="DATABASE_ECHO")
    
    # TimescaleDB settings
    TIMESCALEDB_ENABLED: bool = Field(default=True, env="TIMESCALEDB_ENABLED")
    
    # PostGIS settings
    POSTGIS_ENABLED: bool = Field(default=True, env="POSTGIS_ENABLED")
    
    # File processing settings
    MAX_FILE_SIZE: int = Field(default=1024*1024*100, env="MAX_FILE_SIZE")  # 100MB
    SUPPORTED_FILE_TYPES: list = ["CNV", "HEX", "HDR", "XMLCON", "NC"]
    CNV_ENCODING: str = "utf-8"
    
    # Real-time processing settings
    REALTIME_BUFFER_SIZE: int = Field(default=1000, env="REALTIME_BUFFER_SIZE")
    PROCESSING_BATCH_SIZE: int = Field(default=100, env="PROCESSING_BATCH_SIZE")
    FILE_WATCH_INTERVAL: float = Field(default=1.0, env="FILE_WATCH_INTERVAL")  # seconds
    
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
    CAST_MIN_DEPTH_CHANGE: float = Field(default=5.0, env="CAST_MIN_DEPTH_CHANGE")  # meters
    CAST_MIN_DURATION: int = Field(default=60, env="CAST_MIN_DURATION")  # seconds
    
    # Data export settings
    EXPORT_FORMAT: str = Field(default="netcdf", env="EXPORT_FORMAT")
    EXPORT_COMPRESSION: bool = Field(default=True, env="EXPORT_COMPRESSION")
    
    # Logging settings
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE: Optional[str] = Field(default=None, env="LOG_FILE")
    
    # Cache settings
    CACHE_TTL: int = Field(default=300, env="CACHE_TTL")  # 5 minutes
    
    # Celery settings (for async tasks)
    CELERY_BROKER_URL: str = Field(default="redis://localhost:6379/0", env="CELERY_BROKER_URL")
    CELERY_RESULT_BACKEND: str = Field(default="redis://localhost:6379/0", env="CELERY_RESULT_BACKEND")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

# Create global settings instance
settings = Settings()