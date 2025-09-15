"""
Repository pattern implementation for TRIAXUS database operations

This module provides high-level data access methods for oceanographic data.
"""

from typing import List, Optional, Dict, Any, Union
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func
from sqlalchemy.exc import SQLAlchemyError
import logging

from .models import OceanographicData, DataSource
from .connection_manager import DatabaseConnectionManager
from .config_manager import SecureDatabaseConfigManager

logger = logging.getLogger(__name__)


class OceanographicDataRepository:
    """
    Repository for oceanographic data operations
    """
    
    def __init__(self, connection_manager: Optional[DatabaseConnectionManager] = None):
        """
        Initialize repository
        
        Args:
            connection_manager: DatabaseConnectionManager instance
        """
        self.connection_manager = connection_manager or DatabaseConnectionManager()
        self.logger = logging.getLogger(__name__)
    
    def create(self, data: Union[OceanographicData, List[OceanographicData]]) -> bool:
        """
        Create new oceanographic data records
        
        Args:
            data: Single record or list of records to create
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with self.connection_manager.get_session() as session:
                if isinstance(data, list):
                    session.add_all(data)
                else:
                    session.add(data)
                
                session.commit()
                
                count = len(data) if isinstance(data, list) else 1
                self.logger.info(f"Successfully created {count} oceanographic data records")
                return True
                
        except SQLAlchemyError as e:
            self.logger.error(f"Error creating oceanographic data: {e}")
            return False
    
    def get_by_id(self, record_id: str) -> Optional[OceanographicData]:
        """
        Get oceanographic data record by ID
        
        Args:
            record_id: Record ID
            
        Returns:
            OceanographicData instance or None
        """
        try:
            with self.connection_manager.get_session() as session:
                record = session.query(OceanographicData).filter(
                    OceanographicData.id == record_id
                ).first()
                
                return record
                
        except SQLAlchemyError as e:
            self.logger.error(f"Error getting record by ID {record_id}: {e}")
            return None
    
    def get_by_time_range(self, start_time: datetime, end_time: datetime) -> List[OceanographicData]:
        """
        Get records within time range
        
        Args:
            start_time: Start datetime
            end_time: End datetime
            
        Returns:
            List of OceanographicData records
        """
        try:
            with self.connection_manager.get_session() as session:
                records = session.query(OceanographicData).filter(
                    and_(
                        OceanographicData.datetime >= start_time,
                        OceanographicData.datetime <= end_time
                    )
                ).order_by(OceanographicData.datetime).all()
                
                self.logger.info(f"Found {len(records)} records in time range")
                return records
                
        except SQLAlchemyError as e:
            self.logger.error(f"Error getting records by time range: {e}")
            return []
    
    def get_by_depth_range(self, min_depth: float, max_depth: float) -> List[OceanographicData]:
        """
        Get records within depth range
        
        Args:
            min_depth: Minimum depth
            max_depth: Maximum depth
            
        Returns:
            List of OceanographicData records
        """
        try:
            with self.connection_manager.get_session() as session:
                records = session.query(OceanographicData).filter(
                    and_(
                        OceanographicData.depth >= min_depth,
                        OceanographicData.depth <= max_depth
                    )
                ).order_by(OceanographicData.depth).all()
                
                self.logger.info(f"Found {len(records)} records in depth range")
                return records
                
        except SQLAlchemyError as e:
            self.logger.error(f"Error getting records by depth range: {e}")
            return []
    
    def get_by_location(self, lat_min: float, lat_max: float, 
                       lon_min: float, lon_max: float) -> List[OceanographicData]:
        """
        Get records within geographic bounds
        
        Args:
            lat_min: Minimum latitude
            lat_max: Maximum latitude
            lon_min: Minimum longitude
            lon_max: Maximum longitude
            
        Returns:
            List of OceanographicData records
        """
        try:
            with self.connection_manager.get_session() as session:
                records = session.query(OceanographicData).filter(
                    and_(
                        OceanographicData.latitude >= lat_min,
                        OceanographicData.latitude <= lat_max,
                        OceanographicData.longitude >= lon_min,
                        OceanographicData.longitude <= lon_max
                    )
                ).all()
                
                self.logger.info(f"Found {len(records)} records in geographic bounds")
                return records
                
        except SQLAlchemyError as e:
            self.logger.error(f"Error getting records by location: {e}")
            return []
    
    def get_by_source_file(self, source_file: str) -> List[OceanographicData]:
        """
        Get records by source file
        
        Args:
            source_file: Source file name
            
        Returns:
            List of OceanographicData records
        """
        try:
            with self.connection_manager.get_session() as session:
                records = session.query(OceanographicData).filter(
                    OceanographicData.source_file == source_file
                ).order_by(OceanographicData.datetime).all()
                
                self.logger.info(f"Found {len(records)} records from source file: {source_file}")
                return records
                
        except SQLAlchemyError as e:
            self.logger.error(f"Error getting records by source file: {e}")
            return []
    
    def get_latest_records(self, limit: int = 100) -> List[OceanographicData]:
        """
        Get latest records
        
        Args:
            limit: Maximum number of records to return
            
        Returns:
            List of latest OceanographicData records
        """
        try:
            with self.connection_manager.get_session() as session:
                records = session.query(OceanographicData).order_by(
                    desc(OceanographicData.datetime)
                ).limit(limit).all()
                
                # Convert to detached objects to avoid session issues
                detached_records = []
                for record in records:
                    # Create a new instance with the same data
                    detached_record = OceanographicData(
                        datetime=record.datetime,
                        depth=record.depth,
                        latitude=record.latitude,
                        longitude=record.longitude,
                        tv290C=record.tv290C,
                        sal00=record.sal00,
                        sbeox0Mm_L=record.sbeox0Mm_L,
                        flECO_AFL=record.flECO_AFL,
                        ph=record.ph,
                        source_file=record.source_file
                    )
                    detached_record.id = record.id
                    detached_record.created_at = record.created_at
                    detached_records.append(detached_record)
                
                self.logger.info(f"Retrieved {len(detached_records)} latest records")
                return detached_records
                
        except SQLAlchemyError as e:
            self.logger.error(f"Error getting latest records: {e}")
            return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get database statistics
        
        Returns:
            Dictionary with database statistics
        """
        try:
            with self.connection_manager.get_session() as session:
                stats = {}
                
                # Total records
                stats['total_records'] = session.query(OceanographicData).count()
                
                # Date range
                date_range = session.query(
                    func.min(OceanographicData.datetime),
                    func.max(OceanographicData.datetime)
                ).first()
                
                if date_range and date_range[0] and date_range[1]:
                    stats['date_range'] = {
                        'start': date_range[0].isoformat(),
                        'end': date_range[1].isoformat()
                    }
                
                # Depth range
                depth_range = session.query(
                    func.min(OceanographicData.depth),
                    func.max(OceanographicData.depth)
                ).first()
                
                if depth_range and depth_range[0] is not None and depth_range[1] is not None:
                    stats['depth_range'] = {
                        'min': float(depth_range[0]),
                        'max': float(depth_range[1])
                    }
                
                # Geographic bounds
                geo_bounds = session.query(
                    func.min(OceanographicData.latitude),
                    func.max(OceanographicData.latitude),
                    func.min(OceanographicData.longitude),
                    func.max(OceanographicData.longitude)
                ).first()
                
                if geo_bounds and all(x is not None for x in geo_bounds):
                    stats['geographic_bounds'] = {
                        'lat_min': float(geo_bounds[0]),
                        'lat_max': float(geo_bounds[1]),
                        'lon_min': float(geo_bounds[2]),
                        'lon_max': float(geo_bounds[3])
                    }
                
                # Source files
                source_files = session.query(
                    OceanographicData.source_file,
                    func.count(OceanographicData.id)
                ).group_by(OceanographicData.source_file).all()
                
                stats['source_files'] = {
                    file_name: count for file_name, count in source_files
                    if file_name is not None
                }
                
                self.logger.info("Retrieved database statistics")
                return stats
                
        except SQLAlchemyError as e:
            self.logger.error(f"Error getting database statistics: {e}")
            return {}
    
    def delete_by_id(self, record_id: str) -> bool:
        """
        Delete record by ID
        
        Args:
            record_id: Record ID to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with self.connection_manager.get_session() as session:
                deleted = session.query(OceanographicData).filter(
                    OceanographicData.id == record_id
                ).delete()
                
                session.commit()
                
                if deleted > 0:
                    self.logger.info(f"Successfully deleted record {record_id}")
                    return True
                else:
                    self.logger.warning(f"Record {record_id} not found")
                    return False
                    
        except SQLAlchemyError as e:
            self.logger.error(f"Error deleting record {record_id}: {e}")
            return False
    
    def delete_by_source_file(self, source_file: str) -> int:
        """
        Delete all records from a source file
        
        Args:
            source_file: Source file name
            
        Returns:
            Number of deleted records
        """
        try:
            with self.connection_manager.get_session() as session:
                deleted = session.query(OceanographicData).filter(
                    OceanographicData.source_file == source_file
                ).delete()
                
                session.commit()
                
                self.logger.info(f"Successfully deleted {deleted} records from {source_file}")
                return deleted
                
        except SQLAlchemyError as e:
            self.logger.error(f"Error deleting records from {source_file}: {e}")
            return 0


class DataSourceRepository:
    """
    Repository for data source operations
    """
    
    def __init__(self, connection_manager: Optional[DatabaseConnectionManager] = None):
        """
        Initialize repository
        
        Args:
            connection_manager: DatabaseConnectionManager instance
        """
        self.connection_manager = connection_manager or DatabaseConnectionManager()
        self.logger = logging.getLogger(__name__)
    
    def create(self, data_source: DataSource) -> bool:
        """
        Create new data source record
        
        Args:
            data_source: DataSource instance to create
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with self.connection_manager.get_session() as session:
                session.add(data_source)
                session.commit()
                
                self.logger.info(f"Successfully created data source: {data_source.filename}")
                return True
                
        except SQLAlchemyError as e:
            self.logger.error(f"Error creating data source: {e}")
            return False
    
    def get_by_filename(self, filename: str) -> Optional[DataSource]:
        """
        Get data source by filename
        
        Args:
            filename: Filename to search for
            
        Returns:
            DataSource instance or None
        """
        try:
            with self.connection_manager.get_session() as session:
                data_source = session.query(DataSource).filter(
                    DataSource.filename == filename
                ).first()
                
                return data_source
                
        except SQLAlchemyError as e:
            self.logger.error(f"Error getting data source by filename: {e}")
            return None
    
    def get_all(self) -> List[DataSource]:
        """
        Get all data sources
        
        Returns:
            List of DataSource records
        """
        try:
            with self.connection_manager.get_session() as session:
                data_sources = session.query(DataSource).order_by(
                    desc(DataSource.created_at)
                ).all()
                
                self.logger.info(f"Retrieved {len(data_sources)} data sources")
                return data_sources
                
        except SQLAlchemyError as e:
            self.logger.error(f"Error getting all data sources: {e}")
            return []
    
    def update_status(self, filename: str, status: str, 
                     processed_records: Optional[int] = None) -> bool:
        """
        Update data source processing status
        
        Args:
            filename: Filename to update
            status: New processing status
            processed_records: Number of processed records
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with self.connection_manager.get_session() as session:
                data_source = session.query(DataSource).filter(
                    DataSource.filename == filename
                ).first()
                
                if data_source:
                    data_source.processing_status = status
                    data_source.last_processed = datetime.now()
                    
                    if processed_records is not None:
                        data_source.processed_records = processed_records
                    
                    session.commit()
                    
                    self.logger.info(f"Updated status for {filename}: {status}")
                    return True
                else:
                    self.logger.warning(f"Data source {filename} not found")
                    return False
                    
        except SQLAlchemyError as e:
            self.logger.error(f"Error updating data source status: {e}")
            return False
