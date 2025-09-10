"""
Cruise model for managing research cruise information.
"""
from sqlalchemy import Column, String, DateTime, Text, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid

from .base_model import BaseModel

class Cruise(BaseModel):
    """Model for research cruise information."""
    __tablename__ = 'cruises'
    
    # Primary key
    cruise_id = Column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4,
        comment="Unique cruise identifier"
    )
    
    # Basic cruise information
    cruise_name = Column(
        String(100), 
        nullable=False,
        comment="Name of the cruise"
    )
    
    vessel_name = Column(
        String(100),
        nullable=True,
        comment="Name of the research vessel"
    )
    
    # Temporal information
    start_date = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Cruise start date and time"
    )
    
    end_date = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Cruise end date and time"
    )
    
    # Personnel information
    chief_scientist = Column(
        String(100),
        nullable=True,
        comment="Name of the chief scientist"
    )
    
    # Additional information
    description = Column(
        Text,
        nullable=True,
        comment="Detailed description of the cruise"
    )
    
    metadata = Column(
        JSONB,
        nullable=True,
        comment="Additional cruise configuration and metadata"
    )
    
    # Timestamp fields (updated_at added separately)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
        nullable=False,
        comment="Record last update timestamp"
    )
    
    # Relationships
    data_files = relationship("DataFile", back_populates="cruise", cascade="all, delete-orphan")
    sensor_configurations = relationship("SensorConfiguration", back_populates="cruise", cascade="all, delete-orphan")
    casts = relationship("Cast", back_populates="cruise", cascade="all, delete-orphan")
    gps_tracks = relationship("GpsTrack", back_populates="cruise", cascade="all, delete-orphan")
    operation_logs = relationship("OperationLog", back_populates="cruise", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Cruise(cruise_id={self.cruise_id}, cruise_name='{self.cruise_name}', vessel_name='{self.vessel_name}')>"