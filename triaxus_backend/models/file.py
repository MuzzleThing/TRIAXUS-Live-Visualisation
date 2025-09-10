"""
Data file model for managing uploaded and processed files.
"""
from sqlalchemy import Column, String, BigInteger, DateTime, ForeignKey, CheckConstraint, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid

from .base_model import BaseModel

class DataFile(BaseModel):
    """Model for data file management."""
    __tablename__ = 'data_files'
    
    # Primary key
    file_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Unique file identifier"
    )
    
    # Foreign key to cruise
    cruise_id = Column(
        UUID(as_uuid=True),
        ForeignKey('cruises.cruise_id'),
        nullable=True,
        comment="Associated cruise ID"
    )
    
    # File basic information
    file_name = Column(
        String(255),
        nullable=False,
        comment="Original file name"
    )
    
    file_path = Column(
        String(500),
        nullable=True,
        comment="File storage path"
    )
    
    file_type = Column(
        String(20),
        nullable=True,
        comment="File type (CNV, HEX, HDR, XMLCON, NC)"
    )
    
    file_size = Column(
        BigInteger,
        nullable=True,
        comment="File size in bytes"
    )
    
    file_hash = Column(
        String(64),
        nullable=True,
        comment="SHA256 hash for integrity verification"
    )
    
    # Processing information
    upload_time = Column(
        DateTime(timezone=True),
        server_default=func.current_timestamp(),
        nullable=False,
        comment="File upload timestamp"
    )
    
    processing_status = Column(
        String(20),
        nullable=False,
        default='pending',
        comment="File processing status"
    )
    
    # SeaBird specific information
    header_info = Column(
        JSONB,
        nullable=True,
        comment="SeaBird header information"
    )
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "file_type IN ('CNV', 'HEX', 'HDR', 'XMLCON', 'NC')",
            name='ck_data_files_file_type'
        ),
        CheckConstraint(
            "processing_status IN ('pending', 'processing', 'completed', 'failed')",
            name='ck_data_files_processing_status'
        ),
        UniqueConstraint('file_name', 'file_hash', name='uq_data_files_name_hash'),
    )
    
    # Relationships
    cruise = relationship("Cruise", back_populates="data_files")
    casts = relationship("Cast", back_populates="data_file", cascade="all, delete-orphan")
    sensor_data = relationship("SensorData", back_populates="data_file", cascade="all, delete-orphan")
    qc_logs = relationship("QcLog", back_populates="data_file", cascade="all, delete-orphan")
    realtime_buffer = relationship("RealtimeBuffer", back_populates="data_file", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<DataFile(file_id={self.file_id}, file_name='{self.file_name}', file_type='{self.file_type}', status='{self.processing_status}')>"


class RealtimeBuffer(BaseModel):
    """Model for real-time data buffering."""
    __tablename__ = 'realtime_buffer'
    
    # Primary key
    buffer_id = Column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
        comment="Auto-incrementing buffer ID"
    )
    
    # Foreign key to data file
    file_id = Column(
        UUID(as_uuid=True),
        ForeignKey('data_files.file_id'),
        nullable=True,
        comment="Associated file ID"
    )
    
    # Raw data
    raw_line = Column(
        String,
        nullable=False,
        comment="Raw CNV data line"
    )
    
    line_number = Column(
        BigInteger,
        nullable=True,
        comment="Line number in source file"
    )
    
    parsed_data = Column(
        JSONB,
        nullable=True,
        comment="Parsed data structure"
    )
    
    processing_status = Column(
        String(20),
        nullable=False,
        default='pending',
        comment="Processing status"
    )
    
    received_at = Column(
        DateTime(timezone=True),
        server_default=func.current_timestamp(),
        nullable=False,
        comment="Data received timestamp"
    )
    
    processed_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Data processed timestamp"
    )
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "processing_status IN ('pending', 'processing', 'completed', 'failed')",
            name='ck_realtime_buffer_processing_status'
        ),
    )
    
    # Relationships
    data_file = relationship("DataFile", back_populates="realtime_buffer")
    
    def __repr__(self):
        return f"<RealtimeBuffer(buffer_id={self.buffer_id}, file_id={self.file_id}, status='{self.processing_status}')>"