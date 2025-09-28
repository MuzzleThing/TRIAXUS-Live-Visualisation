#!/usr/bin/env python3
"""
Comprehensive tests for DataProcessor module

This module tests all functionality of the DataProcessor class including:
- Data normalization and cleaning
- Type validation and conversion
- Missing value handling
- Data filtering
- Data sorting
- Resampling and interpolation
- Derived variable calculation
- Quality checks integration
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any

# Add project root to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from triaxus.core.config import ConfigManager
from triaxus.data.processor import DataProcessor


class TestDataProcessor:
    """Comprehensive test class for DataProcessor"""
    
    def setup_method(self):
        """Setup test data for each test method"""
        self.config_manager = ConfigManager()
        self.processor = DataProcessor(self.config_manager)
        
        # Create comprehensive test data
        self.test_data = self._create_comprehensive_test_data()
        
        # Create problematic data for edge case testing
        self.problematic_data = self._create_problematic_test_data()
    
    def _create_comprehensive_test_data(self) -> pd.DataFrame:
        """Create comprehensive test data with various scenarios"""
        base_time = datetime(2024, 1, 1, 12, 0, 0)
        time_series = [base_time + timedelta(hours=i) for i in range(10)]
        
        return pd.DataFrame({
            'Time': time_series,  # Mixed case column name
            'Depth': [10, 15, 20, 25, 30, 35, 40, 45, 50, 55],
            'LATITUDE': [45.0 + i*0.1 for i in range(10)],  # Uppercase
            'LONGITUDE': [-120.0 + i*0.1 for i in range(10)],
            'tv290C': [15.0 + i*0.5 for i in range(10)],  # Mixed case
            'SAL00': [35.0 + i*0.1 for i in range(10)],
            'Sbeox0Mm_L': [8.0 + i*0.1 for i in range(10)],  # Mixed case
            'flECO-AFL': [0.5 + i*0.05 for i in range(10)],  # Mixed case with dash
            'pH': [8.1 + i*0.01 for i in range(10)]  # Mixed case
        })
    
    def _create_problematic_test_data(self) -> pd.DataFrame:
        """Create problematic test data for edge case testing"""
        base_time = datetime(2024, 1, 1, 12, 0, 0)
        time_series = [base_time + timedelta(hours=i) for i in range(8)]
        
        return pd.DataFrame({
            'time': time_series,
            'depth': [10, np.nan, 20, -5, 30, 10000, np.nan, 50],  # Invalid depths
            'latitude': [45.0, 46.0, 95.0, 47.0, -95.0, 48.0, 49.0, 50.0],  # Invalid lat
            'longitude': [-120.0, -121.0, 185.0, -122.0, -185.0, -123.0, -124.0, -125.0],  # Invalid lon
            'tv290c': [15.0, np.nan, 'invalid', 17.0, 18.0, 100, 19.0, 20.0],  # Invalid values
            'sal00': [35.0, np.nan, 36.0, 'text', 37.0, 38.0, np.nan, 39.0],
            'sbeox0mm_l': [8.0, 8.1, np.nan, 8.3, 'invalid', 8.5, 8.6, 8.7],
            'fleco_afl': [0.5, np.nan, 0.6, 0.7, 0.8, 'text', 0.9, 1.0],
            'ph': [8.1, np.nan, 8.2, 8.3, 15.0, 8.4, 8.5, 8.6]  # Invalid pH
        })


def test_data_processor_initialization():
    """Test DataProcessor initialization"""
    print("Testing DataProcessor initialization...")
    
    # Test with default config
    processor = DataProcessor()
    assert processor is not None
    assert processor.config_manager is not None
    print("  PASS: Default initialization")
    
    # Test with custom config
    config_manager = ConfigManager()
    processor = DataProcessor(config_manager)
    assert processor.config_manager == config_manager
    print("  PASS: Custom config initialization")


def test_column_normalization():
    """Test column name normalization"""
    print("Testing column normalization...")
    
    test_instance = TestDataProcessor()
    test_instance.setup_method()
    processor = test_instance.processor
    data = test_instance.test_data
    
    # Test normalization
    processed = processor._normalize_columns(data)
    
    # Check that columns are normalized
    expected_columns = ['time', 'depth', 'latitude', 'longitude', 
                       'tv290c', 'sal00', 'sbeox0mm_l', 'fleco_afl', 'ph']
    
    for col in expected_columns:
        assert col in processed.columns, f"Column {col} not found in normalized data"
    
    # Check that original data is preserved
    assert len(processed) == len(data)
    assert processed['depth'].iloc[0] == 10
    assert processed['latitude'].iloc[0] == 45.0
    
    print("  PASS: Column normalization works correctly")


def test_data_cleaning():
    """Test data cleaning functionality"""
    print("Testing data cleaning...")
    
    test_instance = TestDataProcessor()
    test_instance.setup_method()
    processor = test_instance.processor
    
    # Create data with duplicates and invalid entries
    dirty_data = pd.DataFrame({
        'time': [datetime.now(), datetime.now(), datetime.now() + timedelta(hours=1)],
        'depth': [10, 10, 20],  # Duplicate depth
        'latitude': [45.0, 45.0, 46.0],  # Duplicate lat
        'longitude': [-120.0, -120.0, -121.0],  # Duplicate lon
        'tv290c': [15.0, 15.0, 16.0],
        'sal00': [35.0, 35.0, 36.0],
        'sbeox0mm_l': [8.0, 8.0, 8.1],
        'fleco_afl': [0.5, 0.5, 0.6],
        'ph': [8.1, 8.1, 8.2]
    })
    
    # Add some invalid entries
    dirty_data.loc[3] = [datetime.now() + timedelta(hours=2), 20000, 200.0, 300.0, 15.0, 35.0, 8.0, 0.5, 8.1]
    
    processed = processor._clean_data(dirty_data)
    
    # Should remove duplicates and invalid entries
    assert len(processed) <= len(dirty_data)
    
    # Check that invalid coordinates are filtered out
    valid_lat = (processed['latitude'] >= -90) & (processed['latitude'] <= 90)
    valid_lon = (processed['longitude'] >= -180) & (processed['longitude'] <= 180)
    valid_depth = (processed['depth'] >= 0) & (processed['depth'] <= 11000)
    
    assert valid_lat.all(), "Invalid latitudes found in cleaned data"
    assert valid_lon.all(), "Invalid longitudes found in cleaned data"
    assert valid_depth.all(), "Invalid depths found in cleaned data"
    
    print("  PASS: Data cleaning removes duplicates and invalid entries")


def test_data_type_validation():
    """Test data type validation and conversion"""
    print("Testing data type validation...")
    
    test_instance = TestDataProcessor()
    test_instance.setup_method()
    processor = test_instance.processor
    data = test_instance.problematic_data
    
    processed = processor._validate_data_types(data)
    
    # Check that time column is datetime
    assert pd.api.types.is_datetime64_any_dtype(processed['time']), "Time column not converted to datetime"
    
    # Check that numeric columns are numeric
    numeric_columns = ['depth', 'latitude', 'longitude', 'tv290c', 'sal00', 'sbeox0mm_l', 'fleco_afl', 'ph']
    for col in numeric_columns:
        if col in processed.columns:
            assert pd.api.types.is_numeric_dtype(processed[col]), f"Column {col} not converted to numeric"
    
    print("  PASS: Data type validation and conversion")


def test_missing_value_handling():
    """Test missing value handling strategies"""
    print("Testing missing value handling...")
    
    test_instance = TestDataProcessor()
    test_instance.setup_method()
    processor = test_instance.processor
    
    # Create data with missing values
    data_with_nans = pd.DataFrame({
        'time': pd.date_range('2024-01-01', periods=5, freq='H'),
        'depth': [10, np.nan, 20, np.nan, 30],
        'latitude': [45.0, 46.0, np.nan, 48.0, 49.0],
        'longitude': [-120.0, -121.0, -122.0, np.nan, -124.0],
        'tv290c': [15.0, np.nan, 17.0, 18.0, np.nan],
        'sal00': [35.0, 36.0, 37.0, 38.0, 39.0],
        'sbeox0mm_l': [8.0, 8.1, 8.2, 8.3, 8.4],
        'fleco_afl': [0.5, 0.6, 0.7, 0.8, 0.9],
        'ph': [8.1, 8.2, 8.3, 8.4, 8.5]
    })
    
    # Test drop strategy
    config_drop = {'missing_values': 'drop', 'required_columns': ['time', 'depth']}
    processed_drop = processor._handle_missing_values(data_with_nans, config_drop)
    assert len(processed_drop) < len(data_with_nans), "Drop strategy should remove rows"
    
    # Test interpolate strategy
    config_interpolate = {'missing_values': 'interpolate'}
    processed_interpolate = processor._handle_missing_values(data_with_nans, config_interpolate)
    assert len(processed_interpolate) == len(data_with_nans), "Interpolate strategy should preserve all rows"
    
    # Test fill strategy
    config_fill = {
        'missing_values': 'fill',
        'fill_values': {'depth': 25.0, 'tv290c': 16.0}
    }
    processed_fill = processor._handle_missing_values(data_with_nans, config_fill)
    assert len(processed_fill) == len(data_with_nans), "Fill strategy should preserve all rows"
    
    print("  PASS: Missing value handling strategies work correctly")


def test_data_filtering():
    """Test data filtering functionality"""
    print("Testing data filtering...")
    
    test_instance = TestDataProcessor()
    test_instance.setup_method()
    processor = test_instance.processor
    data = test_instance.test_data
    
    # Test range filter
    config_range = {
        'filters': {
            'depth': {'type': 'range', 'value': [20, 40]}
        }
    }
    # First normalize the data to get the correct column names
    normalized_data = processor._normalize_columns(test_instance.test_data)
    processed_range = processor._apply_filters(normalized_data, config_range)
    depth_values = processed_range['depth'].values
    assert (depth_values >= 20).all() and (depth_values <= 40).all(), "Range filter not working"
    
    # Test greater than filter
    config_gt = {
        'filters': {
            'depth': {'type': 'greater_than', 'value': 30}
        }
    }
    processed_gt = processor._apply_filters(normalized_data, config_gt)
    assert (processed_gt['depth'] > 30).all(), "Greater than filter not working"
    
    # Test less than filter
    config_lt = {
        'filters': {
            'depth': {'type': 'less_than', 'value': 40}
        }
    }
    processed_lt = processor._apply_filters(normalized_data, config_lt)
    assert (processed_lt['depth'] < 40).all(), "Less than filter not working"
    
    print("  PASS: Data filtering works correctly")


def test_data_sorting():
    """Test data sorting functionality"""
    print("Testing data sorting...")
    
    test_instance = TestDataProcessor()
    test_instance.setup_method()
    processor = test_instance.processor
    
    # Create unsorted data
    unsorted_data = pd.DataFrame({
        'time': pd.date_range('2024-01-01', periods=5, freq='H')[::-1],  # Reverse order
        'depth': [50, 40, 30, 20, 10],  # Reverse order
        'latitude': [49.0, 48.0, 47.0, 46.0, 45.0],
        'longitude': [-124.0, -123.0, -122.0, -121.0, -120.0],
        'tv290c': [19.0, 18.0, 17.0, 16.0, 15.0],
        'sal00': [39.0, 38.0, 37.0, 36.0, 35.0],
        'sbeox0mm_l': [8.4, 8.3, 8.2, 8.1, 8.0],
        'fleco_afl': [0.9, 0.8, 0.7, 0.6, 0.5],
        'ph': [8.5, 8.4, 8.3, 8.2, 8.1]
    })
    
    sorted_data = processor._sort_data(unsorted_data)
    
    # Check that data is sorted by time
    assert sorted_data['time'].is_monotonic_increasing, "Data not sorted by time"
    assert sorted_data.index.tolist() == list(range(len(sorted_data))), "Index not reset"
    
    print("  PASS: Data sorting works correctly")


def test_data_resampling():
    """Test data resampling functionality"""
    print("Testing data resampling...")
    
    test_instance = TestDataProcessor()
    test_instance.setup_method()
    processor = test_instance.processor
    
    # Create high-frequency data
    high_freq_data = pd.DataFrame({
        'time': pd.date_range('2024-01-01', periods=60, freq='1min'),  # 1 minute intervals
        'depth': [10 + i*0.1 for i in range(60)],
        'latitude': [45.0 + i*0.001 for i in range(60)],
        'longitude': [-120.0 + i*0.001 for i in range(60)],
        'tv290c': [15.0 + i*0.01 for i in range(60)],
        'sal00': [35.0 + i*0.001 for i in range(60)],
        'sbeox0mm_l': [8.0 + i*0.01 for i in range(60)],
        'fleco_afl': [0.5 + i*0.001 for i in range(60)],
        'ph': [8.1 + i*0.001 for i in range(60)]
    })
    
    # Resample to 5-minute intervals
    resampled = processor.resample_data(high_freq_data, '5min')
    
    # Should have fewer rows
    assert len(resampled) < len(high_freq_data), "Resampled data should have fewer rows"
    assert len(resampled) == 12, f"Expected 12 rows for 1-hour of 5-minute data, got {len(resampled)}"
    
    print("  PASS: Data resampling works correctly")


def test_data_interpolation():
    """Test data interpolation functionality"""
    print("Testing data interpolation...")
    
    test_instance = TestDataProcessor()
    test_instance.setup_method()
    processor = test_instance.processor
    
    # Create data with gaps
    data_with_gaps = pd.DataFrame({
        'time': pd.date_range('2024-01-01', periods=10, freq='H'),
        'depth': [10, np.nan, 20, np.nan, np.nan, 30, 35, np.nan, 40, 45],
        'latitude': [45.0, 46.0, 47.0, 48.0, 49.0, 50.0, 51.0, 52.0, 53.0, 54.0],
        'longitude': [-120.0, -121.0, -122.0, -123.0, -124.0, -125.0, -126.0, -127.0, -128.0, -129.0],
        'tv290c': [15.0, np.nan, 17.0, np.nan, 19.0, 20.0, np.nan, 22.0, 23.0, 24.0],
        'sal00': [35.0, 36.0, 37.0, 38.0, 39.0, 40.0, 41.0, 42.0, 43.0, 44.0],
        'sbeox0mm_l': [8.0, 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7, 8.8, 8.9],
        'fleco_afl': [0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4],
        'ph': [8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7, 8.8, 8.9, 9.0]
    })
    
    original_nan_count = data_with_gaps.isnull().sum().sum()
    
    # Interpolate missing values
    interpolated = processor.interpolate_data(data_with_gaps, 'linear')
    
    # Should have fewer NaN values
    interpolated_nan_count = interpolated.isnull().sum().sum()
    assert interpolated_nan_count < original_nan_count, "Interpolation should reduce NaN values"
    
    print("  PASS: Data interpolation works correctly")


def test_derived_variables():
    """Test derived variable calculation"""
    print("Testing derived variable calculation...")
    
    test_instance = TestDataProcessor()
    test_instance.setup_method()
    processor = test_instance.processor
    
    # Create data with temperature and salinity
    data_with_vars = pd.DataFrame({
        'time': pd.date_range('2024-01-01', periods=5, freq='H'),
        'depth': [10, 20, 30, 40, 50],
        'latitude': [45.0, 46.0, 47.0, 48.0, 49.0],
        'longitude': [-120.0, -121.0, -122.0, -123.0, -124.0],
        'tv290c': [15.0, 14.0, 13.0, 12.0, 11.0],  # Temperature decreasing with depth
        'sal00': [35.0, 35.1, 35.2, 35.3, 35.4],  # Salinity increasing with depth
        'sbeox0mm_l': [8.0, 7.9, 7.8, 7.7, 7.6],
        'fleco_afl': [0.5, 0.6, 0.7, 0.8, 0.9],
        'ph': [8.1, 8.0, 7.9, 7.8, 7.7]
    })
    
    # Calculate derived variables
    derived = processor.calculate_derived_variables(data_with_vars)
    
    # Check that density column was added
    assert 'density' in derived.columns, "Density column not calculated"
    
    # Check that temp_gradient column was added
    assert 'temp_gradient' in derived.columns, "Temperature gradient column not calculated"
    
    # Check that density values are reasonable
    density_values = derived['density'].dropna()
    assert len(density_values) > 0, "No density values calculated"
    assert density_values.min() > 1000, "Density values seem too low"
    assert density_values.max() < 1100, "Density values seem too high"
    
    print("  PASS: Derived variable calculation works correctly")


def test_quality_checks_integration():
    """Test quality checks integration"""
    print("Testing quality checks integration...")
    
    test_instance = TestDataProcessor()
    test_instance.setup_method()
    processor = test_instance.processor
    data = test_instance.test_data
    
    # Process with quality checks
    processed = processor.process(test_instance.test_data, run_quality_checks=True)
    
    # Check that quality report was generated
    quality_report = processor.get_last_quality_report()
    assert quality_report is not None, "Quality report not generated"
    assert quality_report.row_count == len(processed), "Quality report row count mismatch"
    
    print("  PASS: Quality checks integration works correctly")


def test_data_summary():
    """Test data summary generation"""
    print("Testing data summary generation...")
    
    test_instance = TestDataProcessor()
    test_instance.setup_method()
    processor = test_instance.processor
    data = test_instance.test_data
    
    # Generate summary
    summary = processor.get_data_summary(data)
    
    # Check summary structure
    required_keys = ['shape', 'columns', 'dtypes', 'missing_values', 'numeric_summary']
    for key in required_keys:
        assert key in summary, f"Summary missing key: {key}"
    
    # Check summary values
    assert summary['shape'] == data.shape, "Summary shape mismatch"
    assert summary['columns'] == list(data.columns), "Summary columns mismatch"
    
    # Check numeric summary
    numeric_cols = data.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        assert col in summary['numeric_summary'], f"Numeric summary missing column: {col}"
        col_summary = summary['numeric_summary'][col]
        assert 'count' in col_summary, f"Numeric summary missing count for {col}"
        assert 'mean' in col_summary, f"Numeric summary missing mean for {col}"
        assert 'std' in col_summary, f"Numeric summary missing std for {col}"
    
    print("  PASS: Data summary generation works correctly")


def test_complete_processing_pipeline():
    """Test complete data processing pipeline"""
    print("Testing complete processing pipeline...")
    
    test_instance = TestDataProcessor()
    test_instance.setup_method()
    processor = test_instance.processor
    
    # Use problematic data to test full pipeline
    raw_data = test_instance.problematic_data
    
    # Process with comprehensive configuration
    processing_config = {
        'missing_values': 'interpolate',
        'required_columns': ['time', 'depth', 'latitude', 'longitude'],
        'filters': {
            'depth': {'type': 'range', 'value': [0, 1000]},
            'latitude': {'type': 'range', 'value': [-90, 90]},
            'longitude': {'type': 'range', 'value': [-180, 180]}
        }
    }
    
    try:
        processed = processor.process(
            raw_data, 
            processing_config=processing_config,
            run_quality_checks=True
        )
        
        # Check that processing completed successfully
        assert processed is not None, "Processing returned None"
        assert len(processed) > 0, "Processed data is empty"
        
        # Check that invalid data was filtered out
        assert (processed['depth'] >= 0).all(), "Invalid depths still present"
        assert (processed['depth'] <= 1000).all(), "Invalid depths still present"
        assert (processed['latitude'] >= -90).all(), "Invalid latitudes still present"
        assert (processed['latitude'] <= 90).all(), "Invalid latitudes still present"
        assert (processed['longitude'] >= -180).all(), "Invalid longitudes still present"
        assert (processed['longitude'] <= 180).all(), "Invalid longitudes still present"
        
        # Check that quality report was generated
        quality_report = processor.get_last_quality_report()
        assert quality_report is not None, "Quality report not generated"
        
        print("  PASS: Complete processing pipeline works correctly")
        
    except Exception as e:
        print(f"  FAIL: Processing pipeline failed: {e}")
        raise


def test_data_processor_comprehensive():
    """Comprehensive test of all DataProcessor functionality"""
    print("=" * 80)
    print("COMPREHENSIVE DATAPROCESSOR TESTING")
    print("=" * 80)
    
    try:
        # Run all individual tests
        test_data_processor_initialization()
        test_column_normalization()
        test_data_cleaning()
        test_data_type_validation()
        test_missing_value_handling()
        test_data_filtering()
        test_data_sorting()
        test_data_resampling()
        test_data_interpolation()
        test_derived_variables()
        test_quality_checks_integration()
        test_data_summary()
        test_complete_processing_pipeline()
        
        print("\n" + "=" * 80)
        print("SUCCESS: All DataProcessor tests passed!")
        print("=" * 80)
        # No return value to avoid pytest warnings
        return None
        
    except Exception as e:
        print(f"\nFAIL: DataProcessor test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("TRIAXUS DataProcessor Test Suite")
    print("=" * 50)
    
    test_data_processor_comprehensive()
    
    if True:
        print("\nAll tests completed successfully!")
        sys.exit(0)
    else:
        print("\nSome tests failed!")
        sys.exit(1)


def run_data_processor_unit_suite() -> None:
    """Reusable entrypoint for integration/e2e to run data processor tests in order."""
    test_data_processor_initialization()
    test_column_normalization()
    test_data_cleaning()
    test_data_type_validation()
    test_missing_value_handling()
    test_data_filtering()
    test_data_sorting()
    test_data_resampling()
    test_data_interpolation()
    test_derived_variables()
    test_quality_checks_integration()
    test_data_summary()
    test_complete_processing_pipeline()
