"""
Simple database data source for TRIAXUS visualization system

This module provides basic database functionality without complex fallback mechanisms.
"""

import pandas as pd
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
import logging

from ..database import (
    DatabaseConnectionManager,
    SecureDatabaseConfigManager,
    DataMapper,
    OceanographicDataRepository
)


class DatabaseDataSource:
    """
    Simple database data source for TRIAXUS visualization system
    """
    
    def __init__(self):
        """Initialize database data source"""
        self.logger = logging.getLogger(__name__)
        
        try:
            # Initialize database components
            self.config_manager = SecureDatabaseConfigManager()
            self.connection_manager = DatabaseConnectionManager(self.config_manager)
            self.mapper = DataMapper()
            self.repository = OceanographicDataRepository(self.connection_manager)
            
            # Connect to database
            connection_success = self.connection_manager.connect()
            self.available = connection_success and self.connection_manager.is_connected()
            
        except Exception as e:
            self.logger.error(f"Database initialization failed: {e}")
            self.available = False
    
    def is_available(self) -> bool:
        """Check if database is available"""
        return self.available
    
    def load_data(self, limit: int = 100) -> pd.DataFrame:
        """
        Load data from database
        
        Args:
            limit: Maximum number of records to load
            
        Returns:
            Pandas DataFrame with oceanographic data
        """
        if not self.available:
            return pd.DataFrame()
        
        try:
            # Get latest records from database
            models = self.repository.get_latest_records(limit)
            
            # Convert models to DataFrame
            df = self.mapper.models_to_dataframe(models)
            
            self.logger.info(f"Loaded {len(df)} records from database")
            return df
            
        except Exception as e:
            self.logger.error(f"Error loading data from database: {e}")
            return pd.DataFrame()
    
    def store_data(self, data: pd.DataFrame, source_file: Optional[str] = None) -> bool:
        """
        Store data to database
        
        Args:
            data: Pandas DataFrame to store
            source_file: Source file name
            
        Returns:
            True if successful, False otherwise
        """
        if not self.available:
            return False
        
        try:
            # Convert DataFrame to models
            models = self.mapper.dataframe_to_models(data, source_file)
            
            if not models:
                self.logger.warning("No valid models to store")
                return False
            
            # Store in database
            success = self.repository.create(models)
            
            if success:
                self.logger.info(f"Stored {len(models)} records in database")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error storing data to database: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get database statistics
        
        Returns:
            Dictionary with database statistics
        """
        if not self.available:
            return {"available": False}
        
        try:
            stats = self.repository.get_statistics()
            stats["available"] = True
            return stats
        except Exception as e:
            self.logger.error(f"Error getting database statistics: {e}")
            return {"available": False}
