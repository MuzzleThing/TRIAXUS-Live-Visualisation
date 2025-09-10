"""
GPS tracking model for vessel and instrument positions.
"""
from sqlalchemy import Column, BigInteger, DateTime, ForeignKey, Float, String, CheckConstraint, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from geoalchemy2 import Geography

from .base_model import BaseModel

class GpsTrack(BaseModel):
    """Model for GPS tracking data."""
    __tablename__ = 'gps_tracks'
    
    # Primary key
    track_id = Column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
        comment="Auto-incrementing track ID"
    )
    
    # Foreign key to cruise
    cruise_id = Column(
        UUID(as_uuid=True),
        ForeignKey('cruises.cruise_id'),
        nullable=True,
        comment="Associated cruise ID"
    )
    
    # Temporal information
    timestamp = Column(
        DateTime(timezone=True),
        nullable=False,
        comment="GPS timestamp"
    )
    
    # Device information
    device_type = Column(
        String(20),
        nullable=True,
        comment="Device type (TRIAXUS or VESSEL)"
    )
    
    # Spatial information (using PostGIS geography type)
    location = Column(
        Geography('POINT', srid=4326),
        nullable=False,
        comment="GPS location (lat, lon)"
    )
    
    # Navigation information
    heading = Column(
        Float,
        nullable=True,
        comment="Heading in degrees"
    )
    
    speed = Column(
        Float,
        nullable=True,
        comment="Speed in knots"
    )
    
    # Status information
    status = Column(
        String(20),
        nullable=False,
        default='active',
        comment="GPS status"
    )
    
    # Additional metadata (SQLAlchemy reserves 'metadata'; keep column name, change attribute)
    extra_metadata = Column(
        'metadata',
        JSONB,
        nullable=True,
        comment="Additional GPS metadata"
    )
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "device_type IN ('TRIAXUS', 'VESSEL')",
            name='ck_gps_tracks_device_type'
        ),
        CheckConstraint(
            "status IN ('active', 'inactive', 'error')",
            name='ck_gps_tracks_status'
        ),
        CheckConstraint(
            "heading >= 0 AND heading < 360",
            name='ck_gps_tracks_heading'
        ),
        CheckConstraint(
            "speed >= 0",
            name='ck_gps_tracks_speed'
        ),
        Index('idx_gps_tracks_cruise', 'cruise_id'),
        Index('idx_gps_location', 'location', postgresql_using='gist'),
        Index('idx_gps_timestamp', 'timestamp'),
        Index('idx_gps_device_time', 'device_type', 'timestamp'),
    )
    
    # Relationships
    cruise = relationship("Cruise", back_populates="gps_tracks")
    
    def __repr__(self):
        return f"<GpsTrack(track_id={self.track_id}, device_type='{self.device_type}', timestamp={self.timestamp}, status='{self.status}')>"
    
    @property
    def latitude(self):
        """Extract latitude from geography column."""
        if self.location:
            return self.location.latitude
        return None
    
    @property  
    def longitude(self):
        """Extract longitude from geography column."""
        if self.location:
            return self.location.longitude
        return None
