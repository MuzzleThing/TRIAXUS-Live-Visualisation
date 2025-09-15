"""
SQLAlchemy ORM models for TRIAXUS visualization system

This module defines the database models for oceanographic data storage.
"""

from sqlalchemy import Column, String, Float, DateTime, Text, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import uuid
from datetime import datetime
from typing import Optional, Dict, Any

Base = declarative_base()


class OceanographicData(Base):
    """
    SQLAlchemy model for oceanographic data storage
    
    This model represents a single measurement record with core oceanographic parameters.
    """
    
    __tablename__ = 'oceanographic_data'
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    
    # Core measurement fields
    datetime = Column(DateTime, nullable=False, index=True, comment='Measurement timestamp')
    depth = Column(Float, nullable=False, index=True, comment='Depth in meters')
    latitude = Column(Float, nullable=False, index=True, comment='Latitude in decimal degrees')
    longitude = Column(Float, nullable=False, index=True, comment='Longitude in decimal degrees')
    
    # Oceanographic parameters
    tv290C = Column(Float, nullable=True, comment='Temperature in Celsius')
    sal00 = Column(Float, nullable=True, comment='Salinity in PSU')
    sbeox0Mm_L = Column(Float, nullable=True, comment='Dissolved oxygen in mg/L')
    flECO_AFL = Column(Float, nullable=True, comment='Fluorescence in mg/m³')
    ph = Column(Float, nullable=True, comment='pH value')
    
    # Metadata fields
    source_file = Column(String(255), nullable=True, comment='Source data file name')
    created_at = Column(DateTime, default=func.now(), nullable=False, comment='Record creation timestamp')
    
    # Indexes for common query patterns
    __table_args__ = (
        Index('idx_datetime_depth', 'datetime', 'depth'),
        Index('idx_lat_lon', 'latitude', 'longitude'),
        Index('idx_datetime_lat_lon', 'datetime', 'latitude', 'longitude'),
        Index('idx_source_file', 'source_file'),
    )
    
    def __repr__(self) -> str:
        """String representation of the model"""
        return (
            f"<OceanographicData(id={self.id}, datetime={self.datetime}, "
            f"depth={self.depth}, lat={self.latitude}, lon={self.longitude})>"
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert model instance to dictionary
        
        Returns:
            Dictionary representation of the model
        """
        return {
            'id': str(self.id),
            'datetime': self.datetime.isoformat() if self.datetime else None,
            'depth': self.depth,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'tv290C': self.tv290C,
            'sal00': self.sal00,
            'sbeox0Mm_L': self.sbeox0Mm_L,
            'flECO_AFL': self.flECO_AFL,
            'ph': self.ph,
            'source_file': self.source_file,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'OceanographicData':
        """
        Create model instance from dictionary
        
        Args:
            data: Dictionary containing model data
            
        Returns:
            OceanographicData instance
        """
        # Handle datetime conversion
        if 'datetime' in data and isinstance(data['datetime'], str):
            data['datetime'] = datetime.fromisoformat(data['datetime'].replace('Z', '+00:00'))
        
        if 'created_at' in data and isinstance(data['created_at'], str):
            data['created_at'] = datetime.fromisoformat(data['created_at'].replace('Z', '+00:00'))
        
        # Remove None values to use defaults
        filtered_data = {k: v for k, v in data.items() if v is not None}
        
        return cls(**filtered_data)
    
    def validate(self) -> bool:
        """
        Validate model data
        
        Returns:
            True if data is valid, False otherwise
        """
        # Check required fields
        if not all([self.datetime, self.depth is not None, 
                   self.latitude is not None, self.longitude is not None]):
            return False
        
        # Check latitude range
        if not (-90 <= self.latitude <= 90):
            return False
        
        # Check longitude range
        if not (-180 <= self.longitude <= 180):
            return False
        
        # Check depth is positive
        if self.depth < 0:
            return False
        
        return True


class DataSource(Base):
    """
    SQLAlchemy model for tracking data sources
    
    This model tracks metadata about data files and sources.
    """
    
    __tablename__ = 'data_sources'
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    
    # Source information
    filename = Column(String(255), nullable=False, unique=True, comment='Source filename')
    file_path = Column(String(500), nullable=True, comment='Full file path')
    file_size = Column(Float, nullable=True, comment='File size in bytes')
    file_hash = Column(String(64), nullable=True, comment='File hash for integrity check')
    
    # Processing metadata
    total_records = Column(Float, nullable=True, comment='Total number of records')
    processed_records = Column(Float, nullable=True, comment='Number of successfully processed records')
    processing_status = Column(String(50), nullable=True, comment='Processing status')
    
    # Timestamps
    first_seen = Column(DateTime, default=func.now(), nullable=False, comment='First time file was seen')
    last_processed = Column(DateTime, nullable=True, comment='Last processing time')
    created_at = Column(DateTime, default=func.now(), nullable=False, comment='Record creation timestamp')
    
    def __repr__(self) -> str:
        """String representation of the model"""
        return f"<DataSource(id={self.id}, filename={self.filename}, status={self.processing_status})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert model instance to dictionary
        
        Returns:
            Dictionary representation of the model
        """
        return {
            'id': str(self.id),
            'filename': self.filename,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'file_hash': self.file_hash,
            'total_records': self.total_records,
            'processed_records': self.processed_records,
            'processing_status': self.processing_status,
            'first_seen': self.first_seen.isoformat() if self.first_seen else None,
            'last_processed': self.last_processed.isoformat() if self.last_processed else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DataSource':
        """
        Create model instance from dictionary
        
        Args:
            data: Dictionary containing model data
            
        Returns:
            DataSource instance
        """
        # Handle datetime conversion
        if 'first_seen' in data and isinstance(data['first_seen'], str):
            data['first_seen'] = datetime.fromisoformat(data['first_seen'].replace('Z', '+00:00'))
        
        if 'last_processed' in data and isinstance(data['last_processed'], str):
            data['last_processed'] = datetime.fromisoformat(data['last_processed'].replace('Z', '+00:00'))
        
        if 'created_at' in data and isinstance(data['created_at'], str):
            data['created_at'] = datetime.fromisoformat(data['created_at'].replace('Z', '+00:00'))
        
        # Remove None values to use defaults
        filtered_data = {k: v for k, v in data.items() if v is not None}
        
        return cls(**filtered_data)
