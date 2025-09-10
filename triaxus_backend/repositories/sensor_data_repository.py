"""
Repository for sensor data operations with time-series optimizations.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc, asc
from uuid import UUID
import logging

from .base_repository import BaseRepository
from ..models.sensor import SensorData

logger = logging.getLogger(__name__)

class SensorDataRepository(BaseRepository[SensorData]):
    """Repository for sensor data with time-series specific operations."""
    
    def __init__(self):
        super().__init__(SensorData)
    
    def get_recent_data(
        self, 
        db: Session, 
        minutes: int = 30,
        file_id: Optional[UUID] = None,
        cast_id: Optional[UUID] = None
    ) -> List[SensorData]:
        """Get recent sensor data within specified time window."""
        try:
            cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)
            query = db.query(SensorData).filter(SensorData.timestamp >= cutoff_time)
            
            if file_id:
                query = query.filter(SensorData.file_id == file_id)
            if cast_id:
                query = query.filter(SensorData.cast_id == cast_id)
            
            return query.order_by(desc(SensorData.timestamp)).all()
        except Exception as e:
            logger.error(f"Error getting recent sensor data: {str(e)}")
            raise
    
    def get_depth_profile(
        self,
        db: Session,
        cast_id: UUID,
        variables: Optional[List[str]] = None
    ) -> List[SensorData]:
        """Get depth profile data for a specific cast."""
        try:
            query = db.query(SensorData).filter(SensorData.cast_id == cast_id)
            
            # Order by depth for profile visualization
            query = query.filter(SensorData.depth.isnot(None))
            query = query.order_by(asc(SensorData.depth))
            
            return query.all()
        except Exception as e:
            logger.error(f"Error getting depth profile for cast {cast_id}: {str(e)}")
            raise
    
    def get_time_series(
        self,
        db: Session,
        start_time: datetime,
        end_time: datetime,
        file_id: Optional[UUID] = None,
        cast_id: Optional[UUID] = None,
        sample_rate: Optional[int] = None
    ) -> List[SensorData]:
        """Get time series data with optional downsampling."""
        try:
            query = db.query(SensorData).filter(
                and_(
                    SensorData.timestamp >= start_time,
                    SensorData.timestamp <= end_time
                )
            )
            
            if file_id:
                query = query.filter(SensorData.file_id == file_id)
            if cast_id:
                query = query.filter(SensorData.cast_id == cast_id)
            
            query = query.order_by(asc(SensorData.timestamp))
            
            # Apply downsampling if requested
            if sample_rate:
                # Use modulo on scan_number for simple downsampling
                query = query.filter(SensorData.scan_number % sample_rate == 0)
            
            return query.all()
        except Exception as e:
            logger.error(f"Error getting time series data: {str(e)}")
            raise
    
    def get_depth_range_data(
        self,
        db: Session,
        min_depth: float,
        max_depth: float,
        cast_id: Optional[UUID] = None,
        file_id: Optional[UUID] = None
    ) -> List[SensorData]:
        """Get data within specific depth range."""
        try:
            query = db.query(SensorData).filter(
                and_(
                    SensorData.depth >= min_depth,
                    SensorData.depth <= max_depth,
                    SensorData.depth.isnot(None)
                )
            )
            
            if cast_id:
                query = query.filter(SensorData.cast_id == cast_id)
            if file_id:
                query = query.filter(SensorData.file_id == file_id)
            
            return query.order_by(asc(SensorData.depth)).all()
        except Exception as e:
            logger.error(f"Error getting depth range data: {str(e)}")
            raise
    
    def get_latest_by_file(self, db: Session, file_id: UUID, limit: int = 100) -> List[SensorData]:
        """Get latest sensor data for a specific file."""
        try:
            return db.query(SensorData).filter(
                SensorData.file_id == file_id
            ).order_by(
                desc(SensorData.timestamp)
            ).limit(limit).all()
        except Exception as e:
            logger.error(f"Error getting latest data for file {file_id}: {str(e)}")
            raise
    
    def get_statistics_by_cast(self, db: Session, cast_id: UUID) -> Dict[str, Any]:
        """Get statistical summary for a cast."""
        try:
            stats = db.query(
                func.count(SensorData.data_id).label('count'),
                func.min(SensorData.depth).label('min_depth'),
                func.max(SensorData.depth).label('max_depth'),
                func.avg(SensorData.temperature).label('avg_temperature'),
                func.min(SensorData.temperature).label('min_temperature'),
                func.max(SensorData.temperature).label('max_temperature'),
                func.avg(SensorData.salinity).label('avg_salinity'),
                func.min(SensorData.salinity).label('min_salinity'),
                func.max(SensorData.salinity).label('max_salinity')
            ).filter(SensorData.cast_id == cast_id).first()
            
            return {
                'data_points': stats.count or 0,
                'depth': {
                    'min': float(stats.min_depth) if stats.min_depth else None,
                    'max': float(stats.max_depth) if stats.max_depth else None
                },
                'temperature': {
                    'avg': float(stats.avg_temperature) if stats.avg_temperature else None,
                    'min': float(stats.min_temperature) if stats.min_temperature else None,
                    'max': float(stats.max_temperature) if stats.max_temperature else None
                },
                'salinity': {
                    'avg': float(stats.avg_salinity) if stats.avg_salinity else None,
                    'min': float(stats.min_salinity) if stats.min_salinity else None,
                    'max': float(stats.max_salinity) if stats.max_salinity else None
                }
            }
        except Exception as e:
            logger.error(f"Error getting statistics for cast {cast_id}: {str(e)}")
            raise
    
    def bulk_insert_sensor_data(self, db: Session, data_records: List[Dict[str, Any]]) -> int:
        """Bulk insert sensor data for high-throughput ingestion."""
        try:
            # Use bulk_insert_mappings for better performance
            db.bulk_insert_mappings(SensorData, data_records)
            db.commit()
            logger.info(f"Bulk inserted {len(data_records)} sensor data records")
            return len(data_records)
        except Exception as e:
            db.rollback()
            logger.error(f"Error bulk inserting sensor data: {str(e)}")
            raise
    
    def get_data_with_qc_flags(
        self,
        db: Session,
        cast_id: UUID,
        qc_flag_filter: Optional[Dict[str, int]] = None
    ) -> List[SensorData]:
        """Get sensor data with optional QC flag filtering."""
        try:
            query = db.query(SensorData).filter(SensorData.cast_id == cast_id)
            
            if qc_flag_filter:
                # Filter by QC flags in JSONB column
                for variable, flag_value in qc_flag_filter.items():
                    query = query.filter(
                        SensorData.qc_flags[variable].astext.cast(Integer) == flag_value
                    )
            
            return query.order_by(asc(SensorData.timestamp)).all()
        except Exception as e:
            logger.error(f"Error getting data with QC flags: {str(e)}")
            raise