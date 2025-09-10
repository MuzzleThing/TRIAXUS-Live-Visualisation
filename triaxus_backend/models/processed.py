"""
Processed data model for storing computed and aggregated data products.
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY, REAL
from sqlalchemy.orm import relationship
import uuid

from .base_model import BaseModel

class ProcessedData(BaseModel):
    """Model for processed/computed data products."""
    __tablename__ = 'processed_data'
    
    # Primary key
    processed_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Unique processed data identifier"
    )
    
    # Foreign key to cast
    cast_id = Column(
        UUID(as_uuid=True),
        ForeignKey('casts.cast_id'),
        nullable=True,
        comment="Associated cast ID"
    )
    
    # Processing information
    processing_type = Column(
        String(50),
        nullable=True,
        comment="Type of processing applied (gridded, binned, smoothed)"
    )
    
    # Binning/gridding information
    depth_bins = Column(
        ARRAY(REAL),
        nullable=True,
        comment="Depth bin boundaries"
    )
    
    time_bins = Column(
        ARRAY(DateTime(timezone=True)),
        nullable=True,
        comment="Time bin boundaries"
    )
    
    # Data content
    variable_name = Column(
        String(50),
        nullable=True,
        comment="Name of the processed variable"
    )
    
    data_array = Column(
        JSONB,
        nullable=True,
        comment="Processed multi-dimensional array data"
    )
    
    # Processing metadata
    processing_params = Column(
        JSONB,
        nullable=True,
        comment="Parameters used in processing"
    )
    
    # Constraints
    __table_args__ = (
        Index('idx_processed_cast', 'cast_id', 'variable_name'),
        Index('idx_processed_type', 'processing_type'),
    )
    
    # Relationships
    cast = relationship("Cast", back_populates="processed_data")
    
    def __repr__(self):
        return f"<ProcessedData(processed_id={self.processed_id}, processing_type='{self.processing_type}', variable_name='{self.variable_name}')>"