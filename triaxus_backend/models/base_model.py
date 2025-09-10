"""
Base model class with common fields and functionality.
"""
from sqlalchemy import Column, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declared_attr
import uuid
from ..database.base import Base

class BaseModel(Base):
    """Abstract base model with common fields."""
    __abstract__ = True
    
    @declared_attr
    def __tablename__(cls):
        """Generate table name from class name."""
        return cls.__name__.lower() + 's'
    
    # Common timestamp fields
    created_at = Column(
        DateTime(timezone=True), 
        server_default=func.current_timestamp(),
        nullable=False,
        comment="Record creation timestamp"
    )
    
    def to_dict(self):
        """Convert model instance to dictionary."""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns.values()
        }
    
    def __repr__(self):
        """String representation of model."""
        attrs = []
        for column in self.__table__.columns.values():
            if hasattr(self, column.name):
                value = getattr(self, column.name)
                attrs.append(f"{column.name}={value!r}")
        return f"<{self.__class__.__name__}({', '.join(attrs)})>"