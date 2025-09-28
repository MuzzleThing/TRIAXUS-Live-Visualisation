"""
TRIAXUS Test Configuration

This module provides pytest configuration and shared fixtures for all tests.
"""

import os
import sys
import pytest
import tempfile
import shutil
from pathlib import Path
from typing import Generator, Dict, Any

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

@pytest.fixture(scope="session")
def test_config() -> Dict[str, Any]:
    """Provide test configuration settings"""
    return {
        "database": {
            "enabled": True,
            "url": "postgresql://steven@localhost:5432/triaxus_test_db",
            "test_mode": True
        },
        "data": {
            "test_data_dir": project_root / "testdataQC",
            "sample_size": 1000
        },
        "plots": {
            "output_dir": project_root / "tests" / "output",
            "test_mode": True
        }
    }

@pytest.fixture(scope="session")
def test_database_url() -> str:
    """Provide test database URL"""
    return "postgresql://steven@localhost:5432/triaxus_test_db"

@pytest.fixture(scope="session")
def test_data_directory() -> Path:
    """Provide test data directory path"""
    return project_root / "testdataQC"

@pytest.fixture(scope="session")
def test_output_directory() -> Path:
    """Provide test output directory path"""
    output_dir = project_root / "tests" / "output"
    output_dir.mkdir(exist_ok=True)
    return output_dir

@pytest.fixture
def temp_directory() -> Generator[Path, None, None]:
    """Provide a temporary directory for tests"""
    temp_dir = Path(tempfile.mkdtemp())
    try:
        yield temp_dir
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

@pytest.fixture(autouse=True)
def setup_test_environment():
    """Setup test environment variables"""
    # Set test environment variables
    os.environ['TESTING'] = 'true'
    os.environ['DB_ENABLED'] = 'true'
    os.environ['DATABASE_URL'] = 'postgresql://steven@localhost:5432/triaxus_test_db'
    
    yield
    
    # Cleanup after test
    if 'TESTING' in os.environ:
        del os.environ['TESTING']
