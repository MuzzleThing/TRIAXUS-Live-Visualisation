"""
Sensor configuration and sensor data models.
"""
from sqlalchemy import Column, String, Date, DateTime, ForeignKey, BigInteger, Float, CheckConstraint, Index, PrimaryKeyConstraint, func
from sqlalchemy.dialects.postgresql import UUID, JSONB, DOUBLE_PRECISION
from sqlalchemy.orm import relationship
import uuid

from .base_model import BaseModel

class SensorConfiguration(BaseModel):
    """Model for sensor configuration information."""
    __tablename__ = 'sensor_configurations'
    
    # Primary key
    config_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Unique configuration identifier"
    )
    
    # Foreign key to cruise
    cruise_id = Column(
        UUID(as_uuid=True),
        ForeignKey('cruises.cruise_id'),
        nullable=True,
        comment="Associated cruise ID"
    )
    
    # Sensor information
    sensor_type = Column(
        String(50),
        nullable=False,
        comment="Type of sensor"
    )
    
    sensor_name = Column(
        String(100),
        nullable=True,
        comment="Sensor name or model"
    )
    
    serial_number = Column(
        String(50),
        nullable=True,
        comment="Sensor serial number"
    )
    
    # Calibration information
    calibration_date = Column(
        Date,
        nullable=True,
        comment="Last calibration date"
    )
    
    calibration_coefficients = Column(
        JSONB,
        nullable=True,
        comment="Calibration coefficients"
    )
    
    channel_mapping = Column(
        JSONB,
        nullable=True,
        comment="Channel to variable mapping"
    )
    
    # Validity period
    valid_from = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Configuration valid from timestamp"
    )
    
    valid_to = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Configuration valid to timestamp"
    )
    
    # Relationships
    cruise = relationship("Cruise", back_populates="sensor_configurations")
    
    def __repr__(self):
        return f"<SensorConfiguration(config_id={self.config_id}, sensor_type='{self.sensor_type}', sensor_name='{self.sensor_name}')>"


class SensorData(BaseModel):
    """Model for raw sensor data with TimescaleDB optimization."""
    __tablename__ = 'sensor_data'
    
    # Composite primary key for time-series optimization
    data_id = Column(
        BigInteger,
        autoincrement=True,
        nullable=False,
        comment="Auto-incrementing data ID"
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
    
    # Time-series fields
    scan_number = Column(
        BigInteger,
        nullable=False,
        comment="Scan number from instrument"
    )
    
    timestamp = Column(
        DateTime(timezone=True),
        nullable=False,
        comment="Data timestamp"
    )
    
    # Core CTD data
    pressure = Column(
        Float,
        nullable=True,
        comment="Pressure in decibars"
    )
    
    temperature = Column(
        Float,
        nullable=True,
        comment="Temperature in Celsius"
    )
    
    conductivity = Column(
        Float,
        nullable=True,
        comment="Conductivity in S/m"
    )
    
    salinity = Column(
        Float,
        nullable=True,
        comment="Salinity in PSU"
    )
    
    depth = Column(
        Float,
        nullable=True,
        comment="Depth in meters"
    )
    
    # Additional sensor data
    oxygen = Column(
        Float,
        nullable=True,
        comment="Dissolved oxygen in mg/L"
    )
    
    fluorescence = Column(
        Float,
        nullable=True,
        comment="Fluorescence intensity"
    )
    
    turbidity = Column(
        Float,
        nullable=True,
        comment="Turbidity in NTU"
    )
    
    par = Column(
        Float,
        nullable=True,
        comment="Photosynthetically Available Radiation"
    )
    
    # Position data
    latitude = Column(
        DOUBLE_PRECISION,
        nullable=True,
        comment="Latitude in decimal degrees"
    )
    
    longitude = Column(
        DOUBLE_PRECISION,
        nullable=True,
        comment="Longitude in decimal degrees"
    )
    
    # Quality control and additional data
    qc_flags = Column(
        JSONB,
        nullable=True,
        comment="Quality control flags for each variable"
    )
    
    additional_channels = Column(
        JSONB,
        nullable=True,
        comment="Additional sensor channel data"
    )
    
    # Constraints and table configuration
    __table_args__ = (
        PrimaryKeyConstraint('timestamp', 'scan_number'),
        CheckConstraint(
            "depth >= -10 AND depth <= 400",
            name='ck_sensor_data_depth_range'
        ),
        CheckConstraint(
            "temperature >= -5 AND temperature <= 40",
            name='ck_sensor_data_temperature_range'
        ),
        CheckConstraint(
            "latitude >= -90 AND latitude <= 90 AND longitude >= -180 AND longitude <= 180",
            name='ck_sensor_data_coordinates'
        ),
        Index('idx_sensor_data_cast', 'cast_id'),
        Index('idx_sensor_data_file', 'file_id'),
        Index('idx_sensor_data_depth', 'depth'),
    )
    
    # Relationships
    data_file = relationship("DataFile", back_populates="sensor_data")
    cast = relationship("Cast", back_populates="sensor_data")
    
    def __repr__(self):
        return f"<SensorData(timestamp={self.timestamp}, scan_number={self.scan_number}, depth={self.depth}, temperature={self.temperature})>"
