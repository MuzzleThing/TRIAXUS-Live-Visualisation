"""
Base repository class with common database operations.
"""
from typing import Generic, TypeVar, List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func, and_, or_
from uuid import UUID
import logging

from ..config.database import get_db_context
from ..models.base_model import BaseModel

T = TypeVar('T', bound=BaseModel)

logger = logging.getLogger(__name__)

class BaseRepository(Generic[T]):
    """Base repository with common CRUD operations."""
    
    def __init__(self, model_class: T):
        self.model_class = model_class
    
    def create(self, db: Session, **kwargs) -> T:
        """Create a new record."""
        try:
            obj = self.model_class(**kwargs)
            db.add(obj)
            db.commit()
            db.refresh(obj)
            logger.info(f"Created {self.model_class.__name__} with ID: {getattr(obj, 'id', 'N/A')}")
            return obj
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Error creating {self.model_class.__name__}: {str(e)}")
            raise
    
    def get_by_id(self, db: Session, id_value: Any) -> Optional[T]:
        """Get record by ID."""
        try:
            # Get primary key column name
            pk_column = list(self.model_class.__table__.primary_key.columns)[0]
            return db.query(self.model_class).filter(pk_column == id_value).first()
        except SQLAlchemyError as e:
            logger.error(f"Error getting {self.model_class.__name__} by ID {id_value}: {str(e)}")
            raise
    
    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[T]:
        """Get all records with pagination."""
        try:
            return db.query(self.model_class).offset(skip).limit(limit).all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting all {self.model_class.__name__}: {str(e)}")
            raise
    
    def update(self, db: Session, id_value: Any, **kwargs) -> Optional[T]:
        """Update a record by ID."""
        try:
            obj = self.get_by_id(db, id_value)
            if obj:
                for key, value in kwargs.items():
                    if hasattr(obj, key):
                        setattr(obj, key, value)
                db.commit()
                db.refresh(obj)
                logger.info(f"Updated {self.model_class.__name__} with ID: {id_value}")
            return obj
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Error updating {self.model_class.__name__} with ID {id_value}: {str(e)}")
            raise
    
    def delete(self, db: Session, id_value: Any) -> bool:
        """Delete a record by ID."""
        try:
            obj = self.get_by_id(db, id_value)
            if obj:
                db.delete(obj)
                db.commit()
                logger.info(f"Deleted {self.model_class.__name__} with ID: {id_value}")
                return True
            return False
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Error deleting {self.model_class.__name__} with ID {id_value}: {str(e)}")
            raise
    
    def count(self, db: Session, **filters) -> int:
        """Count records with optional filters."""
        try:
            query = db.query(func.count(self.model_class.id))
            if filters:
                query = self._apply_filters(query, **filters)
            return query.scalar()
        except SQLAlchemyError as e:
            logger.error(f"Error counting {self.model_class.__name__}: {str(e)}")
            raise
    
    def exists(self, db: Session, **filters) -> bool:
        """Check if record exists with given filters."""
        try:
            query = db.query(self.model_class)
            query = self._apply_filters(query, **filters)
            return query.first() is not None
        except SQLAlchemyError as e:
            logger.error(f"Error checking existence of {self.model_class.__name__}: {str(e)}")
            raise
    
    def find_by(self, db: Session, **filters) -> List[T]:
        """Find records by filters."""
        try:
            query = db.query(self.model_class)
            query = self._apply_filters(query, **filters)
            return query.all()
        except SQLAlchemyError as e:
            logger.error(f"Error finding {self.model_class.__name__} by filters: {str(e)}")
            raise
    
    def find_one_by(self, db: Session, **filters) -> Optional[T]:
        """Find one record by filters."""
        try:
            query = db.query(self.model_class)
            query = self._apply_filters(query, **filters)
            return query.first()
        except SQLAlchemyError as e:
            logger.error(f"Error finding one {self.model_class.__name__} by filters: {str(e)}")
            raise
    
    def _apply_filters(self, query, **filters):
        """Apply filters to query."""
        for key, value in filters.items():
            if hasattr(self.model_class, key):
                if isinstance(value, list):
                    query = query.filter(getattr(self.model_class, key).in_(value))
                elif isinstance(value, dict) and 'operator' in value:
                    # Handle advanced filter operators
                    column = getattr(self.model_class, key)
                    operator = value['operator']
                    filter_value = value['value']
                    
                    if operator == 'gte':
                        query = query.filter(column >= filter_value)
                    elif operator == 'lte':
                        query = query.filter(column <= filter_value)
                    elif operator == 'gt':
                        query = query.filter(column > filter_value)
                    elif operator == 'lt':
                        query = query.filter(column < filter_value)
                    elif operator == 'like':
                        query = query.filter(column.like(f'%{filter_value}%'))
                    elif operator == 'ilike':
                        query = query.filter(column.ilike(f'%{filter_value}%'))
                else:
                    query = query.filter(getattr(self.model_class, key) == value)
        return query
    
    def bulk_create(self, db: Session, objects_data: List[Dict[str, Any]]) -> List[T]:
        """Bulk create records for better performance."""
        try:
            objects = [self.model_class(**data) for data in objects_data]
            db.add_all(objects)
            db.commit()
            logger.info(f"Bulk created {len(objects)} {self.model_class.__name__} records")
            return objects
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Error bulk creating {self.model_class.__name__}: {str(e)}")
            raise