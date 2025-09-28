"""
TRIAXUS Test Utilities

This module provides common utilities and helpers for testing.
"""

import os
import sys
import time
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import pandas as pd
import numpy as np

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import the new test data generator
from .utils.test_data_generator import TestDataGenerator

class TestDatabaseHelper:
    """Helper functions for database testing"""
    
    @staticmethod
    def create_test_database_url() -> str:
        """Create test database URL"""
        return "postgresql://steven@localhost:5432/triaxus_test_db"
    
    @staticmethod
    def setup_test_database():
        """Setup test database environment"""
        os.environ['TESTING'] = 'true'
        os.environ['DB_ENABLED'] = 'true'
        os.environ['DATABASE_URL'] = TestDatabaseHelper.create_test_database_url()
    
    @staticmethod
    def cleanup_test_database():
        """Cleanup test database environment"""
        if 'TESTING' in os.environ:
            del os.environ['TESTING']

    @staticmethod
    def clean_database(host: str = 'localhost', user: str = 'steven', dbname: str = 'triaxus_db') -> bool:
        """Truncate core tables to ensure a clean state before tests.

        Uses psql CLI non-interactively. Returns True on success.
        """
        import subprocess
        try:
            result1 = subprocess.run(
                ['psql', '-h', host, '-U', user, '-d', dbname, '-c', 'TRUNCATE TABLE oceanographic_data CASCADE;'],
                capture_output=True, text=True
            )
            result2 = subprocess.run(
                ['psql', '-h', host, '-U', user, '-d', dbname, '-c', 'TRUNCATE TABLE data_sources CASCADE;'],
                capture_output=True, text=True
            )
            return result1.returncode == 0 and result2.returncode == 0
        except Exception:
            return False

class TestFileHelper:
    """Helper functions for file operations in tests"""
    
    @staticmethod
    def create_temp_file(content: str, suffix: str = '.txt') -> Path:
        """Create a temporary file with given content"""
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix=suffix, delete=False)
        temp_file.write(content)
        temp_file.close()
        return Path(temp_file.name)
    
    @staticmethod
    def create_temp_directory() -> Path:
        """Create a temporary directory"""
        return Path(tempfile.mkdtemp())
    
    @staticmethod
    def cleanup_temp_file(file_path: Path):
        """Cleanup temporary file"""
        if file_path.exists():
            file_path.unlink()
    
    @staticmethod
    def cleanup_temp_directory(dir_path: Path):
        """Cleanup temporary directory"""
        if dir_path.exists():
            shutil.rmtree(dir_path, ignore_errors=True)

class TestTimer:
    """Timer utility for performance testing"""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
    
    def start(self):
        """Start timing"""
        self.start_time = time.time()
    
    def stop(self):
        """Stop timing"""
        self.end_time = time.time()
    
    def elapsed(self) -> float:
        """Get elapsed time in seconds"""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return 0.0
    
    def __enter__(self):
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

class TestAssertions:
    """Custom assertions for testing"""
    
    @staticmethod
    def assert_dataframe_shape(df: pd.DataFrame, expected_rows: int, expected_cols: int):
        """Assert DataFrame has expected shape"""
        assert df.shape == (expected_rows, expected_cols), \
            f"Expected shape ({expected_rows}, {expected_cols}), got {df.shape}"
    
    @staticmethod
    def assert_dataframe_columns(df: pd.DataFrame, expected_columns: List[str]):
        """Assert DataFrame has expected columns"""
        missing_cols = set(expected_columns) - set(df.columns)
        extra_cols = set(df.columns) - set(expected_columns)
        
        assert not missing_cols, f"Missing columns: {missing_cols}"
        assert not extra_cols, f"Extra columns: {extra_cols}"
    
    @staticmethod
    def assert_dataframe_dtypes(df: pd.DataFrame, expected_dtypes: Dict[str, str]):
        """Assert DataFrame has expected dtypes"""
        for col, expected_dtype in expected_dtypes.items():
            assert col in df.columns, f"Column {col} not found"
            actual_dtype = str(df[col].dtype)
            assert expected_dtype in actual_dtype, \
                f"Column {col}: expected {expected_dtype}, got {actual_dtype}"

def run_test_with_timer(test_func):
    """Decorator to run test with timing"""
    def wrapper(*args, **kwargs):
        with TestTimer() as timer:
            result = test_func(*args, **kwargs)
        print(f"Test {test_func.__name__} completed in {timer.elapsed():.3f}s")
        return result
    return wrapper
