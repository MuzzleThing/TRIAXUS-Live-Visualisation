"""
Data Validator for TRIAXUS visualization system

This module provides comprehensive data validation for all plot types.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
import logging

from .config import ConfigManager

logger = logging.getLogger(__name__)


class DataValidator:
    """Data validator for TRIAXUS core functionality"""
    
    def __init__(self, config_manager: Optional[ConfigManager] = None):
        self.logger = logging.getLogger(__name__)
        self.config_manager = config_manager or ConfigManager()
        
        # Get validation configuration
        self.validation_config = self.config_manager.get_validation_config()
        self.data_config = self.config_manager.get_data_config()
    
    def _get_validation_rule(self, column_name: str):
        """Get validation rule for a column from configuration"""
        # First try to get from validation config
        if hasattr(self.validation_config, 'column_rules') and column_name in self.validation_config.column_rules:
            return self.validation_config.column_rules[column_name]
        
        # Fallback to data config variables
        if hasattr(self.data_config, 'variables') and column_name in self.data_config.variables:
            var_config = self.data_config.variables[column_name]
            # Convert VariableConfig to ValidationRule-like object
            from .config.schemas.validation import ValidationRule
            return ValidationRule(
                name=var_config.name,
                description=var_config.description,
                required=var_config.required,
                data_type='numeric' if var_config.unit != 'datetime' else 'datetime',
                min_value=var_config.range.min_value if var_config.range else None,
                max_value=var_config.range.max_value if var_config.range else None
            )
        
        return None
    
    def validate(self, data: pd.DataFrame, required_columns: List[str]) -> pd.DataFrame:
        """
        Validate data for plotting
        
        Args:
            data: Input data
            required_columns: List of required columns
            
        Returns:
            Validated data
            
        Raises:
            ValueError: If validation fails
        """
        self.logger.info(f"Validating data with shape: {data.shape}")
        
        # Basic validation
        self._validate_basic(data)
        
        # Column validation
        self._validate_columns(data, required_columns)
        
        # Data type validation
        self._validate_data_types(data)
        
        # Range validation
        self._validate_ranges(data)
        
        # Quality checks
        self._validate_data_quality(data)
        
        self.logger.info("Data validation passed")
        return data
    
    def _validate_basic(self, data: pd.DataFrame):
        """Basic data validation"""
        if not isinstance(data, pd.DataFrame):
            raise ValueError("Data must be a pandas DataFrame")
        
        if len(data) == 0:
            raise ValueError("Data cannot be empty")
        
        if len(data) < 2:
            self.logger.warning("Data contains very few points")
    
    def _validate_columns(self, data: pd.DataFrame, required_columns: List[str]):
        """Validate required columns"""
        missing_columns = [col for col in required_columns if col not in data.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        
        # Check for empty columns
        empty_columns = [col for col in data.columns if data[col].isna().all()]
        if empty_columns:
            self.logger.warning(f"Columns with all NaN values: {empty_columns}")
    
    def _validate_data_types(self, data: pd.DataFrame):
        """Validate data types"""
        for column in data.columns:
            # Get validation rule from configuration
            rule = self._get_validation_rule(column)
            if rule:
                expected_type = rule.data_type
                
                if expected_type == 'numeric':
                    if not pd.api.types.is_numeric_dtype(data[column]):
                        # Try to convert to numeric
                        try:
                            data[column] = pd.to_numeric(data[column], errors='coerce')
                            self.logger.info(f"Converted column {column} to numeric")
                        except:
                            raise ValueError(f"Column {column} must be numeric")
                
                elif expected_type == 'datetime':
                    if not pd.api.types.is_datetime64_any_dtype(data[column]):
                        # Try to convert to datetime
                        try:
                            data[column] = pd.to_datetime(data[column], errors='coerce')
                            self.logger.info(f"Converted column {column} to datetime")
                        except:
                            raise ValueError(f"Column {column} must be datetime")
    
    def _validate_ranges(self, data: pd.DataFrame):
        """Validate data ranges"""
        for column in data.columns:
            # Get validation rule from configuration
            rule = self._get_validation_rule(column)
            if rule and rule.min_value is not None and rule.max_value is not None:
                min_val = rule.min_value
                max_val = rule.max_value
                
                # Check for values outside range
                if pd.api.types.is_numeric_dtype(data[column]):
                    out_of_range = (data[column] < min_val) | (data[column] > max_val)
                    if out_of_range.any():
                        count = out_of_range.sum()
                        self.logger.warning(
                            f"Column {column} has {count} values outside range [{min_val}, {max_val}]"
                        )
    
    def _validate_data_quality(self, data: pd.DataFrame):
        """Validate data quality"""
        # Check for duplicate rows
        duplicates = data.duplicated().sum()
        if duplicates > 0:
            self.logger.warning(f"Found {duplicates} duplicate rows")
        
        # Check for missing values
        missing_counts = data.isnull().sum()
        high_missing = missing_counts[missing_counts > len(data) * 0.5]
        if len(high_missing) > 0:
            self.logger.warning(f"Columns with >50% missing values: {high_missing.index.tolist()}")
        
        # Check for constant columns
        constant_columns = []
        for column in data.select_dtypes(include=[np.number]).columns:
            if data[column].nunique() <= 1:
                constant_columns.append(column)
        
        if constant_columns:
            self.logger.warning(f"Constant columns found: {constant_columns}")
    
    def validate_for_line_plot(self, data: pd.DataFrame) -> pd.DataFrame:
        """Validate data for line plot"""
        return self.validate(data, ['time', 'depth'])
    
    def validate_for_contour_plot(self, data: pd.DataFrame, variable: str) -> pd.DataFrame:
        """Validate data for contour plot"""
        required_columns = ['time', 'depth', variable]
        return self.validate(data, required_columns)
    
    def validate_for_map_plot(self, data: pd.DataFrame) -> pd.DataFrame:
        """Validate data for map plot"""
        return self.validate(data, ['latitude', 'longitude', 'time'])
    
    def get_validation_summary(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Get validation summary"""
        summary = {
            'shape': data.shape,
            'columns': list(data.columns),
            'missing_values': data.isnull().sum().to_dict(),
            'data_types': data.dtypes.to_dict(),
            'numeric_ranges': {}
        }
        
        # Add numeric ranges
        for column in data.select_dtypes(include=[np.number]).columns:
            summary['numeric_ranges'][column] = {
                'min': float(data[column].min()),
                'max': float(data[column].max()),
                'mean': float(data[column].mean())
            }
        
        return summary
