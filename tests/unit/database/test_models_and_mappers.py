"""
Tests for database models and mappers

This module provides basic tests for the database functionality.
"""

import pytest
import pandas as pd
from datetime import datetime
from typing import List

from triaxus.database.models import OceanographicData, DataSource
from triaxus.database.mappers import DataMapper, DataSourceMapper


class TestOceanographicDataModel:
    """Test OceanographicData model"""
    
    def test_model_creation(self):
        """Test basic model creation"""
        data = OceanographicData(
            datetime=datetime.now(),
            depth=10.5,
            latitude=45.0,
            longitude=-120.0,
            tv290c=15.2,
            sal00=35.1
        )
        
        assert data.depth == 10.5
        assert data.latitude == 45.0
        assert data.longitude == -120.0
        assert data.validate() is True
    
    def test_model_validation(self):
        """Test model validation"""
        # Valid data
        valid_data = OceanographicData(
            datetime=datetime.now(),
            depth=10.0,
            latitude=45.0,
            longitude=-120.0
        )
        assert valid_data.validate() is True
        
        # Invalid latitude
        invalid_lat = OceanographicData(
            datetime=datetime.now(),
            depth=10.0,
            latitude=95.0,  # Invalid
            longitude=-120.0
        )
        assert invalid_lat.validate() is False
        
        # Invalid longitude
        invalid_lon = OceanographicData(
            datetime=datetime.now(),
            depth=10.0,
            latitude=45.0,
            longitude=185.0  # Invalid
        )
        assert invalid_lon.validate() is False
        
        # Negative depth
        invalid_depth = OceanographicData(
            datetime=datetime.now(),
            depth=-5.0,  # Invalid
            latitude=45.0,
            longitude=-120.0
        )
        assert invalid_depth.validate() is False
    
    def test_model_to_dict(self):
        """Test model to dictionary conversion"""
        data = OceanographicData(
            datetime=datetime(2023, 1, 1, 12, 0, 0),
            depth=10.0,
            latitude=45.0,
            longitude=-120.0,
            tv290c=15.0
        )
        
        result = data.to_dict()
        
        assert result['depth'] == 10.0
        assert result['latitude'] == 45.0
        assert result['longitude'] == -120.0
        assert result['tv290c'] == 15.0
        assert 'id' in result
        assert 'created_at' in result
    
    def test_model_from_dict(self):
        """Test model creation from dictionary"""
        data_dict = {
            'datetime': '2023-01-01T12:00:00',
            'depth': 10.0,
            'latitude': 45.0,
            'longitude': -120.0,
            'tv290c': 15.0,
            'source_file': 'test.csv'
        }
        
        model = OceanographicData.from_dict(data_dict)
        
        assert model.depth == 10.0
        assert model.latitude == 45.0
        assert model.longitude == -120.0
        assert model.tv290c == 15.0
        assert model.source_file == 'test.csv'


class TestDataMapper:
    """Test DataMapper functionality"""
    
    def setup_method(self):
        """Setup test data"""
        self.mapper = DataMapper()
        
        # Create test DataFrame
        self.test_df = pd.DataFrame({
            'time': [datetime(2023, 1, 1, 12, 0, 0), datetime(2023, 1, 1, 13, 0, 0)],
            'depth': [10.0, 20.0],
            'latitude': [45.0, 46.0],
            'longitude': [-120.0, -121.0],
            'tv290c': [15.0, 16.0],
            'sal00': [35.0, 35.1]
        })
    
    def test_dataframe_to_models(self):
        """Test DataFrame to models conversion"""
        models = self.mapper.dataframe_to_models(self.test_df, 'test.csv')
        
        assert len(models) == 2
        assert models[0].depth == 10.0
        assert models[0].latitude == 45.0
        assert models[0].source_file == 'test.csv'
        assert models[1].depth == 20.0
        assert models[1].latitude == 46.0
    
    def test_models_to_dataframe(self):
        """Test models to DataFrame conversion"""
        # Create test models
        models = [
            OceanographicData(
                datetime=datetime(2023, 1, 1, 12, 0, 0),
                depth=10.0,
                latitude=45.0,
                longitude=-120.0,
                tv290c=15.0
            ),
            OceanographicData(
                datetime=datetime(2023, 1, 1, 13, 0, 0),
                depth=20.0,
                latitude=46.0,
                longitude=-121.0,
                tv290c=16.0
            )
        ]
        
        df = self.mapper.models_to_dataframe(models)
        
        assert len(df) == 2
        assert 'time' in df.columns
        assert 'depth' in df.columns
        assert 'latitude' in df.columns
        assert 'longitude' in df.columns
        assert 'tv290c' in df.columns
        assert df['depth'].iloc[0] == 10.0
        assert df['depth'].iloc[1] == 20.0
    
    def test_dataframe_validation(self):
        """Test DataFrame validation"""
        # Valid DataFrame
        assert self.mapper.validate_dataframe(self.test_df) is True
        
        # Empty DataFrame
        empty_df = pd.DataFrame()
        assert self.mapper.validate_dataframe(empty_df) is False
        
        # Missing required columns
        invalid_df = pd.DataFrame({
            'time': [datetime.now()],
            'depth': [10.0]
            # Missing latitude and longitude
        })
        assert self.mapper.validate_dataframe(invalid_df) is False
    
    def test_create_empty_dataframe(self):
        """Test empty DataFrame creation"""
        df = self.mapper.create_empty_dataframe()
        
        expected_columns = ['time', 'depth', 'latitude', 'longitude', 
                          'tv290c', 'sal00', 'sbeox0mm_l', 'fleco_afl', 'ph']
        
        for col in expected_columns:
            assert col in df.columns
        
        assert len(df) == 0


class TestDataSourceMapper:
    """Test DataSourceMapper functionality"""
    
    def setup_method(self):
        """Setup test data"""
        self.mapper = DataSourceMapper()
    
    def test_file_to_model(self):
        """Test file to model conversion"""
        file_path = '/path/to/test.csv'
        file_stats = {
            'size': 1024,
            'hash': 'abc123',
            'total_records': 100,
            'processed_records': 95,
            'status': 'completed'
        }
        
        model = self.mapper.file_to_model(file_path, file_stats)
        
        assert model.filename == 'test.csv'
        assert model.file_size == 1024
        assert model.file_hash == 'abc123'
        assert model.total_records == 100
        assert model.processing_status == 'completed'
    
    def test_model_to_dict(self):
        """Test model to dictionary conversion"""
        model = DataSource(
            filename='test.csv',
            file_size=1024,
            processing_status='pending'
        )
        
        result = self.mapper.model_to_dict(model)
        
        assert result['filename'] == 'test.csv'
        assert result['file_size'] == 1024
        assert result['processing_status'] == 'pending'
        assert 'id' in result
        assert 'processed_at' in result


if __name__ == '__main__':
    # Run basic tests
    print("Running database model and mapper tests...")
    
    # Test OceanographicData model
    test_model = TestOceanographicDataModel()
    test_model.test_model_creation()
    test_model.test_model_validation()
    test_model.test_model_to_dict()
    test_model.test_model_from_dict()
    print("OceanographicData model tests passed")
    
    # Test DataMapper
    test_mapper = TestDataMapper()
    test_mapper.setup_method()
    test_mapper.test_dataframe_to_models()
    test_mapper.test_models_to_dataframe()
    test_mapper.test_dataframe_validation()
    test_mapper.test_create_empty_dataframe()
    print("DataMapper tests passed")
    
    # Test DataSourceMapper
    test_source_mapper = TestDataSourceMapper()
    test_source_mapper.setup_method()
    test_source_mapper.test_file_to_model()
    test_source_mapper.test_model_to_dict()
    print("DataSourceMapper tests passed")
    
    print("All tests passed!")


def run_models_and_mappers_unit_tests() -> bool:
    """Reusable entrypoint for integration tests to invoke models/mappers checks.

    Returns True if core mapping/model tests pass; False otherwise.
    """
    try:
        test_model = TestOceanographicDataModel()
        test_model.test_model_creation()
        test_model.test_model_validation()
        test_model.test_model_to_dict()
        test_model.test_model_from_dict()

        test_mapper = TestDataMapper()
        test_mapper.setup_method()
        test_mapper.test_dataframe_to_models()
        test_mapper.test_models_to_dataframe()
        test_mapper.test_dataframe_validation()
        test_mapper.test_create_empty_dataframe()

        test_source_mapper = TestDataSourceMapper()
        test_source_mapper.setup_method()
        test_source_mapper.test_file_to_model()
        test_source_mapper.test_model_to_dict()
        return True
    except Exception:
        return False
