"""
Quality control models for data validation and logging.
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, BigInteger, Text, func, CheckConstraint, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship
import uuid

from .base_model import BaseModel

class QcLog(BaseModel):
    """Model for quality control logging."""
    __tablename__ = 'qc_logs'
    
    # Primary key
    qc_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Unique QC record identifier"
    )
    
    # Foreign keys
    file_id = Column(
        UUID(as_uuid=True),
        ForeignKey('data_files.file_id'),
        nullable=True,
        comment="Associated file ID"
    )
    
    cast_id = Column(
        UUID(as_uuid=True),
        ForeignKey('casts.cast_id'),
        nullable=True,
        comment="Associated cast ID"
    )
    
    # QC test information
    qc_type = Column(
        String(50),
        nullable=True,
        comment="Type of QC test performed"
    )
    
    variable_name = Column(
        String(50),
        nullable=True,
        comment="Variable name tested"
    )
    
    # Test parameters and results
    test_params = Column(
        JSONB,
        nullable=True,
        comment="QC test parameters"
    )
    
    flagged_count = Column(
        Integer,
        nullable=True,
        comment="Number of data points flagged"
    )
    
    flagged_indices = Column(
        ARRAY(Integer),
        nullable=True,
        comment="Array of flagged data indices"
    )
    
    # Audit information
    qc_timestamp = Column(
        DateTime(timezone=True),
        server_default=func.current_timestamp(),
        nullable=False,
        comment="QC execution timestamp"
    )
    
    operator = Column(
        String(100),
        nullable=True,
        comment="Operator who performed QC"
    )
    
    notes = Column(
        Text,
        nullable=True,
        comment="Additional QC notes"
    )
    
    # Relationships
    data_file = relationship("DataFile", back_populates="qc_logs")
    cast = relationship("Cast", back_populates="qc_logs")
    
    def __repr__(self):
        return f"<QcLog(qc_id={self.qc_id}, qc_type='{self.qc_type}', variable_name='{self.variable_name}', flagged_count={self.flagged_count})>"


class OperationLog(BaseModel):
    """Model for system operation logging."""
    __tablename__ = 'operation_logs'
    
    # Primary key
    log_id = Column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
        comment="Auto-incrementing log ID"
    )
    
    # Foreign key to cruise
    cruise_id = Column(
        UUID(as_uuid=True),
        ForeignKey('cruises.cruise_id'),
        nullable=True,
        comment="Associated cruise ID"
    )
    
    # Log information
    timestamp = Column(
        DateTime(timezone=True),
        server_default=func.current_timestamp(),
        nullable=False,
        comment="Log timestamp"
    )
    
    log_type = Column(
        String(20),
        nullable=True,
        comment="Log level/type"
    )
    
    component = Column(
        String(50),
        nullable=True,
        comment="System component that generated log"
    )
    
    message = Column(
        Text,
        nullable=False,
        comment="Log message"
    )
    
    details = Column(
        JSONB,
        nullable=True,
        comment="Additional log details"
    )
    
    user_id = Column(
        String(100),
        nullable=True,
        comment="User ID if user action"
    )
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "log_type IN ('info', 'warning', 'error', 'user_action')",
            name='ck_operation_logs_log_type'
        ),
        Index('idx_operation_logs_time', 'timestamp', postgresql_ops={'timestamp': 'DESC'}),
        Index('idx_operation_logs_type', 'log_type'),
        Index('idx_operation_logs_component', 'component'),
    )
    
    # Relationships
    cruise = relationship("Cruise", back_populates="operation_logs")
    
    def __repr__(self):
        return f"<OperationLog(log_id={self.log_id}, log_type='{self.log_type}', component='{self.component}', message='{self.message[:50]}...')>"
