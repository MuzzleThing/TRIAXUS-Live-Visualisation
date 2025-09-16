"""
Data mapping utilities for TRIAXUS visualization system

This module provides mapping between Pandas DataFrames and database models.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import logging

from .models import OceanographicData, DataSource

logger = logging.getLogger(__name__)


class DataMapper:
    """
    Maps data between Pandas DataFrames and database models
    """
    
    # Field mapping from DataFrame columns to model attributes
    FIELD_MAPPING = {
        'time': 'datetime',
        'depth': 'depth',
        'latitude': 'latitude',
        'longitude': 'longitude',
        'tv290c': 'tv290c',
        'sal00': 'sal00',
        'sbeox0mm_l': 'sbeox0mm_l',
        'fleco_afl': 'fleco_afl',
        'ph': 'ph'
    }
    
    def __init__(self):
        """Initialize DataMapper"""
        self.logger = logging.getLogger(__name__)
    
    def dataframe_to_models(self, df: pd.DataFrame, source_file: Optional[str] = None) -> List[OceanographicData]:
        """
        Convert DataFrame to list of OceanographicData models
        
        Args:
            df: Pandas DataFrame with oceanographic data
            source_file: Optional source file name
            
        Returns:
            List of OceanographicData model instances
        """
        models = []
        
        try:
            # Validate DataFrame
            if df.empty:
                self.logger.warning("DataFrame is empty")
                return models
            
            # Check required columns
            required_columns = ['time', 'depth', 'latitude', 'longitude']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                self.logger.error(f"Missing required columns: {missing_columns}")
                return models
            
            # Process each row
            for index, row in df.iterrows():
                try:
                    # Convert row to model data
                    model_data = self._row_to_model_data(row, source_file)
                    
                    # Create model instance
                    model = OceanographicData.from_dict(model_data)
                    
                    # Validate model
                    if model.validate():
                        models.append(model)
                    else:
                        self.logger.warning(f"Invalid data at row {index}: {model_data}")
                        
                except Exception as e:
                    self.logger.error(f"Error processing row {index}: {e}")
                    continue
            
            self.logger.info(f"Successfully converted {len(models)} records from DataFrame")
            
        except Exception as e:
            self.logger.error(f"Error converting DataFrame to models: {e}")
        
        return models
    
    def models_to_dataframe(self, models: List[OceanographicData]) -> pd.DataFrame:
        """
        Convert list of OceanographicData models to DataFrame
        
        Args:
            models: List of OceanographicData model instances
            
        Returns:
            Pandas DataFrame with oceanographic data
        """
        try:
            if not models:
                self.logger.warning("No models provided")
                return pd.DataFrame()
            
            # Convert models to dictionaries - access attributes directly to avoid session issues
            data = []
            for model in models:
                # Access attributes directly to avoid lazy loading issues
                data.append({
                    'id': str(model.id) if hasattr(model, 'id') and model.id else None,
                    'datetime': model.datetime.isoformat() if hasattr(model, 'datetime') and model.datetime else None,
                    'depth': model.depth if hasattr(model, 'depth') else None,
                    'latitude': model.latitude if hasattr(model, 'latitude') else None,
                    'longitude': model.longitude if hasattr(model, 'longitude') else None,
                    'tv290c': model.tv290c if hasattr(model, 'tv290c') else None,
                    'sal00': model.sal00 if hasattr(model, 'sal00') else None,
                    'sbeox0mm_l': model.sbeox0mm_l if hasattr(model, 'sbeox0mm_l') else None,
                    'fleco_afl': model.fleco_afl if hasattr(model, 'fleco_afl') else None,
                    'ph': model.ph if hasattr(model, 'ph') else None,
                    'source_file': model.source_file if hasattr(model, 'source_file') else None,
                    'created_at': model.created_at.isoformat() if hasattr(model, 'created_at') and model.created_at else None
                })
            
            # Create DataFrame
            df = pd.DataFrame(data)
            
            # Rename columns to match expected format
            column_mapping = {v: k for k, v in self.FIELD_MAPPING.items()}
            df = df.rename(columns=column_mapping)
            
            # Convert datetime column
            if 'datetime' in df.columns:
                df['time'] = pd.to_datetime(df['datetime'])
                df = df.drop('datetime', axis=1)
            
            # Remove metadata columns for plotting
            metadata_columns = ['id', 'source_file', 'created_at']
            df = df.drop(columns=[col for col in metadata_columns if col in df.columns])
            
            self.logger.info(f"Successfully converted {len(models)} models to DataFrame")
            
        except Exception as e:
            self.logger.error(f"Error converting models to DataFrame: {e}")
            df = pd.DataFrame()
        
        return df
    
    def _row_to_model_data(self, row: pd.Series, source_file: Optional[str] = None) -> Dict[str, Any]:
        """
        Convert DataFrame row to model data dictionary
        
        Args:
            row: Pandas Series representing a data row
            source_file: Optional source file name
            
        Returns:
            Dictionary with model data
        """
        model_data = {
            'source_file': source_file
        }
        
        # Map DataFrame columns to model fields
        for df_col, model_field in self.FIELD_MAPPING.items():
            if df_col in row.index and pd.notna(row[df_col]):
                value = row[df_col]
                
                # Handle special data types
                if df_col == 'time':
                    # Convert time to datetime
                    if isinstance(value, str):
                        try:
                            value = pd.to_datetime(value)
                        except:
                            value = None
                    elif isinstance(value, pd.Timestamp):
                        value = value.to_pydatetime()
                
                model_data[model_field] = value
        
        return model_data
    
    def validate_dataframe(self, df: pd.DataFrame) -> bool:
        """
        Validate DataFrame structure for oceanographic data
        
        Args:
            df: Pandas DataFrame to validate
            
        Returns:
            True if DataFrame is valid, False otherwise
        """
        try:
            # Check if DataFrame is empty
            if df.empty:
                self.logger.warning("DataFrame is empty")
                return False
            
            # Check required columns
            required_columns = ['time', 'depth', 'latitude', 'longitude']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                self.logger.error(f"Missing required columns: {missing_columns}")
                return False
            
            # Check data types and ranges
            if not self._validate_column_data(df):
                return False
            
            self.logger.info("DataFrame validation passed")
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating DataFrame: {e}")
            return False
    
    def _validate_column_data(self, df: pd.DataFrame) -> bool:
        """
        Validate column data types and ranges
        
        Args:
            df: Pandas DataFrame to validate
            
        Returns:
            True if data is valid, False otherwise
        """
        try:
            # Validate latitude range
            if 'latitude' in df.columns:
                lat_values = df['latitude'].dropna()
                if not lat_values.empty and not lat_values.between(-90, 90).all():
                    self.logger.error("Latitude values out of range [-90, 90]")
                    return False
            
            # Validate longitude range
            if 'longitude' in df.columns:
                lon_values = df['longitude'].dropna()
                if not lon_values.empty and not lon_values.between(-180, 180).all():
                    self.logger.error("Longitude values out of range [-180, 180]")
                    return False
            
            # Validate depth is positive
            if 'depth' in df.columns:
                depth_values = df['depth'].dropna()
                if not depth_values.empty and (depth_values < 0).any():
                    self.logger.error("Depth values should be positive")
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating column data: {e}")
            return False
    
    def get_dataframe_schema(self) -> Dict[str, str]:
        """
        Get expected DataFrame schema
        
        Returns:
            Dictionary mapping column names to data types
        """
        return {
            'time': 'datetime64[ns]',
            'depth': 'float64',
            'latitude': 'float64',
            'longitude': 'float64',
            'tv290c': 'float64',
            'sal00': 'float64',
            'sbeox0mm_l': 'float64',
            'fleco_afl': 'float64',
            'ph': 'float64'
        }
    
    def create_empty_dataframe(self) -> pd.DataFrame:
        """
        Create empty DataFrame with correct schema
        
        Returns:
            Empty DataFrame with oceanographic data columns
        """
        schema = self.get_dataframe_schema()
        return pd.DataFrame(columns=list(schema.keys())).astype(schema)


class DataSourceMapper:
    """
    Maps data source information between files and database models
    """
    
    def __init__(self):
        """Initialize DataSourceMapper"""
        self.logger = logging.getLogger(__name__)
    
    def file_to_model(self, file_path: str, file_stats: Optional[Dict[str, Any]] = None) -> DataSource:
        """
        Convert file information to DataSource model
        
        Args:
            file_path: Path to the data file
            file_stats: Optional file statistics
            
        Returns:
            DataSource model instance
        """
        import os
        
        try:
            filename = os.path.basename(file_path)
            
            model_data = {
                'filename': filename,
                'file_size': file_stats.get('size') if file_stats else None,
                'file_hash': file_stats.get('hash') if file_stats else None,
                'total_records': file_stats.get('total_records') if file_stats else None,
                'processing_status': file_stats.get('status') if file_stats else 'pending'
            }
            
            return DataSource.from_dict(model_data)
            
        except Exception as e:
            self.logger.error(f"Error converting file to model: {e}")
            raise
    
    def model_to_dict(self, model: DataSource) -> Dict[str, Any]:
        """
        Convert DataSource model to dictionary
        
        Args:
            model: DataSource model instance
            
        Returns:
            Dictionary representation of the model
        """
        return model.to_dict()
