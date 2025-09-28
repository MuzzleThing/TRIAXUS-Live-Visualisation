"""
Test Configuration for TRIAXUS System

This module provides configuration settings for different test environments.
"""

import os
from pathlib import Path
from typing import Dict, Any

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Test configuration
TEST_CONFIG = {
    "database": {
        "test_url": "postgresql://steven@localhost:5432/triaxus_test_db",
        "main_url": "postgresql://steven@localhost:5432/triaxus_db",
        "enabled": True
    },
    "data": {
        "test_data_dir": PROJECT_ROOT / "testdataQC",
        "sample_size": 1000,
        "large_sample_size": 10000
    },
    "output": {
        "test_output_dir": PROJECT_ROOT / "tests" / "output",
        "plot_output_dir": PROJECT_ROOT / "tests" / "output" / "plots",
        "report_output_dir": PROJECT_ROOT / "tests" / "output" / "reports"
    },
    "performance": {
        "timeout": 30,  # seconds
        "memory_limit": "1GB",
        "max_records": 100000
    },
    "coverage": {
        "threshold": 80,  # percentage
        "exclude_patterns": [
            "*/tests/*",
            "*/__pycache__/*",
            "*/migrations/*"
        ]
    }
}

# Environment-specific configurations
ENVIRONMENTS = {
    "test": {
        "database_url": TEST_CONFIG["database"]["test_url"],
        "debug": True,
        "logging_level": "DEBUG"
    },
    "development": {
        "database_url": TEST_CONFIG["database"]["main_url"],
        "debug": True,
        "logging_level": "INFO"
    },
    "production": {
        "database_url": os.getenv("DATABASE_URL", TEST_CONFIG["database"]["main_url"]),
        "debug": False,
        "logging_level": "WARNING"
    }
}

def get_test_config() -> Dict[str, Any]:
    """Get test configuration"""
    return TEST_CONFIG

def get_environment_config(env: str = "test") -> Dict[str, Any]:
    """Get environment-specific configuration"""
    return ENVIRONMENTS.get(env, ENVIRONMENTS["test"])

def setup_test_environment(env: str = "test"):
    """Setup test environment variables"""
    config = get_environment_config(env)
    
    os.environ["TESTING"] = "true"
    os.environ["DATABASE_URL"] = config["database_url"]
    os.environ["DEBUG"] = str(config["debug"])
    os.environ["LOGGING_LEVEL"] = config["logging_level"]
    
    # Create output directories
    output_config = TEST_CONFIG["output"]
    for dir_path in output_config.values():
        Path(dir_path).mkdir(parents=True, exist_ok=True)
