"""
Cast model for managing CTD cast operations.
"""
from sqlalchemy import Column, Integer, DateTime, ForeignKey, Float, String, Text, CheckConstraint, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from geoalchemy2 import Geography
import uuid

from .base_model import BaseModel

class Cast(BaseModel):
    """Model for CTD cast operations."""
    __tablename__ = 'casts'
    
    # Primary key
    cast_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Unique cast identifier"
    )
    
    # Foreign keys
    cruise_id = Column(
        UUID(as_uuid=True),
        ForeignKey('cruises.cruise_id'),
        nullable=True,
        comment="Associated cruise ID"
    )
    
    file_id = Column(
        UUID(as_uuid=True),
        ForeignKey('data_files.file_id'),
        nullable=True,
        comment="Associated file ID"
    )
    
    # Cast identification
    cast_number = Column(
        Integer,
        nullable=False,
        comment="Cast number within cruise"
    )
    
    # Temporal information
    start_time = Column(
        DateTime(timezone=True),
        nullable=False,
        comment="Cast start time"
    )
    
    end_time = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Cast end time"
    )
    
    # Spatial information (using PostGIS geography type)
    start_location = Column(
        Geography('POINT', srid=4326),
        nullable=True,
        comment="Cast start location (lat, lon)"
    )
    
    end_location = Column(
        Geography('POINT', srid=4326),
        nullable=True,
        comment="Cast end location (lat, lon)"
    )
    
    # Depth information
    max_depth = Column(
        Float,
        nullable=True,
        comment="Maximum depth reached in meters"
    )
    
    min_depth = Column(
        Float,
        nullable=True,
        comment="Minimum depth reached in meters"
    )
    
    # Cast characteristics
    direction = Column(
        String(10),
        nullable=True,
        comment="Cast direction (down, up, both)"
    )
    
    quality_flag = Column(
        Integer,
        nullable=False,
        default=0,
        comment="Quality flag (0=good, 1=questionable, 2=bad)"
    )
    
    # Additional information
    operator_notes = Column(
        Text,
        nullable=True,
        comment="Operator notes and comments"
    )
    
    # 'metadata' is reserved in SQLAlchemy; use a safe attribute name while keeping the DB column as 'metadata'
    extra_metadata = Column(
        'metadata',
        JSONB,
        nullable=True,
        comment="Additional cast metadata"
    )
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "direction IN ('down', 'up', 'both')",
            name='ck_casts_direction'
        ),
        CheckConstraint(
            "quality_flag >= 0 AND quality_flag <= 2",
            name='ck_casts_quality_flag'
        ),
        Index('idx_cast_time', 'cruise_id', 'start_time'),
        Index('idx_casts_location', 'start_location', postgresql_using='gist'),
    )
    
    # Relationships
    cruise = relationship("Cruise", back_populates="casts")
    data_file = relationship("DataFile", back_populates="casts")
    sensor_data = relationship("SensorData", back_populates="cast", cascade="all, delete-orphan")
    processed_data = relationship("ProcessedData", back_populates="cast", cascade="all, delete-orphan")
    qc_logs = relationship("QcLog", back_populates="cast", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Cast(cast_id={self.cast_id}, cast_number={self.cast_number}, start_time={self.start_time}, max_depth={self.max_depth})>"
    
    @property
    def duration_seconds(self):
        """Calculate cast duration in seconds."""
        if self.end_time and self.start_time:
            return (self.end_time - self.start_time).total_seconds()
        return None
    
    @property
    def depth_range(self):
        """Calculate depth range in meters."""
        if self.max_depth is not None and self.min_depth is not None:
            return self.max_depth - self.min_depth
        return None
