# TRIAXUS Testing Guide

This comprehensive guide covers testing the TRIAXUS oceanographic data visualization system using the modern pytest-based test suite.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Test Structure](#test-structure)
3. [Running Tests](#running-tests)
4. [Test Categories](#test-categories)
5. [Real-time System Testing](#real-time-system-testing)
6. [Database Testing](#database-testing)
7. [Configuration](#configuration)
8. [Troubleshooting](#troubleshooting)

## Quick Start

### Prerequisites

```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Run All Tests

```bash
# Run complete test suite
python tests/run_tests.py

# Run with verbose output
python tests/run_tests.py -v

# Run with coverage report
python tests/run_tests.py --coverage
```

### Run Specific Test Types

```bash
# Unit tests only
python tests/run_tests.py --type unit

# Integration tests only
python tests/run_tests.py --type integration

# End-to-end tests only
python tests/run_tests.py --type e2e

# Database tests only
python tests/run_tests.py --type database

# Visualization tests only
python tests/run_tests.py --type visualization
```

## Test Structure

```
tests/
├── conftest.py              # Pytest configuration and shared fixtures
├── utils.py                 # Test utilities and helpers
├── run_tests.py            # Modern test runner
├── unit/                   # Unit tests for individual components
│   ├── core/              # Core functionality tests
│   ├── data/              # Data processing tests
│   ├── database/          # Database operation tests
│   ├── file_processing/   # File processing tests
│   ├── plotters/          # Visualization component tests
│   ├── realtime/          # Real-time system tests
│   └── utils/             # Utility function tests
├── integration/           # Integration tests for cross-component functionality
│   ├── workflows/         # End-to-end workflow tests
│   ├── visualization/     # Visualization integration tests
│   ├── database/         # Database integration tests
│   ├── file_processing/  # File processing integration tests
│   └── realtime/         # Real-time system integration tests
├── e2e/                   # End-to-end system tests
│   ├── full_system/      # Complete system tests
│   └── performance/      # Performance and load tests
├── fixtures/             # Test fixtures and sample data
├── config/               # Test configuration files
└── output/               # Test output and reports
```

## Running Tests

### Using the Modern Test Runner

The `tests/run_tests.py` script provides a comprehensive test runner with multiple options:

```bash
# Basic usage
python tests/run_tests.py

# Show test structure
python tests/run_tests.py --structure

# Run specific test types
python tests/run_tests.py --type unit
python tests/run_tests.py --type integration
python tests/run_tests.py --type e2e
python tests/run_tests.py --type database
python tests/run_tests.py --type visualization
python tests/run_tests.py --type performance

# Run with options
python tests/run_tests.py -v --coverage
python tests/run_tests.py -k "database"
python tests/run_tests.py --parallel
```

### Using pytest directly

```bash
# Run all tests
python -m pytest tests/

# Run specific categories
python -m pytest tests/unit/
python -m pytest tests/integration/
python -m pytest tests/e2e/

# Run with options
python -m pytest tests/ -v
python -m pytest tests/ --cov=triaxus
python -m pytest tests/ -k "database"
```

## Test Categories

### Unit Tests (`tests/unit/`)

Unit tests focus on testing individual components in isolation:

- **Core** (`tests/unit/core/`): Configuration, error handling, validation
- **Data** (`tests/unit/data/`): Data processing, quality control, archiving
- **Database** (`tests/unit/database/`): Database operations, mapping, connectivity
- **File Processing** (`tests/unit/file_processing/`): CNV file reading, data archiving
- **Plotters** (`tests/unit/plotters/`): Visualization components
- **Realtime** (`tests/unit/realtime/`): Real-time processing components
- **Utils** (`tests/unit/utils/`): Utility functions

### Integration Tests (`tests/integration/`)

Integration tests verify that components work together correctly:

- **Workflows** (`tests/integration/workflows/`): End-to-end workflow tests
- **Visualization** (`tests/integration/visualization/`): Visualization integration
- **Database** (`tests/integration/database/`): Database integration
- **File Processing** (`tests/integration/file_processing/`): File processing pipeline
- **Realtime** (`tests/integration/realtime/`): Real-time system integration

### End-to-End Tests (`tests/e2e/`)

E2E tests verify complete system functionality:

- **Full System** (`tests/e2e/full_system/`): Complete system tests
- **Performance** (`tests/e2e/performance/`): Performance and load tests

## Real-time System Testing

### Real-time Pipeline Tests

```bash
# Test real-time components
python tests/run_tests.py --type realtime

# Test specific real-time modules
python -m pytest tests/unit/realtime/
python -m pytest tests/integration/realtime/
```

### Real-time System Validation

```bash
# Start real-time pipeline
python scripts/start_realtime_pipeline.py --config configs/realtime_test.yaml

# Verify components are running
ps aux | grep -E "(simulation|cnv_realtime_processor|realtime_api_server)"

# Test API endpoints
curl http://localhost:8080/api/status
curl http://localhost:8080/api/latest_data

# Stop real-time pipeline
python scripts/stop_realtime_pipeline.py
```

### Real-time Test Coverage

The real-time tests cover:
- CNV file processing and validation
- Real-time data ingestion
- Database storage and retrieval
- API server functionality
- Web dashboard integration
- Plot generation and updates

## Database Testing

### Database Test Configuration

```bash
# Set environment variables
export DB_ENABLED=true
export DATABASE_URL=postgresql://triaxus_user:password@localhost:5432/triaxus_db
```

### Database Test Types

```bash
# Run all database tests
python tests/run_tests.py --type database

# Test database connectivity
python -m pytest tests/unit/database/test_connectivity.py

# Test database schema
python -m pytest tests/unit/database/test_schema.py

# Test data mapping
python -m pytest tests/unit/database/test_mapping.py

# Test database operations
python -m pytest tests/unit/database/test_operations.py
```

### Database Test Features

- **Connection testing**: Database connectivity and session management
- **Schema validation**: Table structure and column definitions
- **Data mapping**: DataFrame ↔ Model conversion
- **CRUD operations**: Create, read, update, delete operations
- **Performance testing**: Database operation speed and efficiency

## Configuration

### Test Configuration

Test configuration is managed in `tests/config/` and `conftest.py`:

- Database URLs for different environments
- Test data directories
- Performance thresholds
- Coverage settings

### Environment Variables

```bash
# Database configuration
export DB_ENABLED=true
export DATABASE_URL=postgresql://user:password@host:port/database

# Test configuration
export TEST_DATA_DIR=./testdataQC
export TEST_OUTPUT_DIR=./tests/output
```

## Test Utilities

### TestDataGenerator

Provides methods to generate test data:

```python
from tests.utils.test_data_generator import TestDataGenerator

# Generate sample oceanographic data
data = TestDataGenerator.create_sample_oceanographic_data(n_records=100)

# Generate CNV-style test data
cnv_data = TestDataGenerator.create_cnv_test_data(n_records=100)

# Generate problematic data for testing
problematic_data = TestDataGenerator.create_problematic_data()
```

### TestDatabaseHelper

Provides database testing utilities:

```python
from tests.utils import TestDatabaseHelper

# Setup test database
TestDatabaseHelper.create_test_database(db_url)

# Cleanup after tests
TestDatabaseHelper.drop_test_database(db_url)
```

### TestFileHelper

Provides file-based testing utilities:

```python
from tests.utils import TestFileHelper

# Create dummy CNV file
TestFileHelper.create_dummy_cnv_file(file_path, n_lines=10)

# Create invalid CNV file for error testing
TestFileHelper.create_invalid_cnv_file(file_path)
```

## Troubleshooting

### Common Issues

1. **Database Connection Issues**:
   ```bash
   # Check PostgreSQL service
   brew services list | grep postgresql  # macOS
   sudo systemctl status postgresql     # Linux
   
   # Start PostgreSQL service
   brew services start postgresql@14    # macOS
   sudo systemctl start postgresql      # Linux
   
   # Test connection
   psql -h localhost -p 5432 -U username -d triaxus_db
   ```

2. **Environment Variables**:
   ```bash
   # Check if DB_ENABLED is set
   echo $DB_ENABLED
   
   # Set required environment variables
   export DB_ENABLED=true
   export DATABASE_URL=postgresql://username@localhost:5432/triaxus_db
   ```

3. **Missing Dependencies**:
   ```bash
   # Install test dependencies
   pip install -r requirements.txt
   
   # Install additional test packages
   pip install pytest-cov pytest-xdist
   ```

4. **Permission Issues**:
   ```bash
   # Ensure write permissions for test output
   chmod 755 tests/output/
   
   # Check file permissions
   ls -la tests/output/
   ```

### Debug Mode

Run tests with verbose output for debugging:

```bash
# Verbose output
python tests/run_tests.py -v

# Debug specific test
python -m pytest tests/unit/data/test_data_processor.py -v -s

# Run with debugging
python -m pytest tests/ --pdb
```

### Test Coverage

Generate coverage reports:

```bash
# Generate coverage report
python tests/run_tests.py --coverage

# View coverage report
open tests/output/coverage/index.html
```

### Performance Testing

Run performance tests:

```bash
# Run performance tests
python tests/run_tests.py --type performance

# Run with timing
python -m pytest tests/e2e/performance/ -v --durations=10
```

## Best Practices

1. **Test Isolation**: Each test should be independent and not rely on other tests
2. **Clear Naming**: Use descriptive test names that explain what is being tested
3. **Arrange-Act-Assert**: Structure tests with clear setup, execution, and verification phases
4. **Mock External Dependencies**: Use mocks for external services and databases
5. **Test Data**: Use the TestDataGenerator for consistent test data
6. **Cleanup**: Always clean up resources after tests
7. **Real-time Testing**: Test real-time components in isolation before integration

## Continuous Integration

The test suite is designed to work with CI/CD pipelines:

- Tests run in parallel for faster execution
- Coverage reports are generated
- Performance benchmarks are tracked
- Database tests use isolated test databases
- Real-time tests can be run in headless mode

## Test Output

All test outputs are saved to `tests/output/`:
- HTML visualization files
- Test result logs
- Performance metrics
- Coverage reports
- Real-time test artifacts

This comprehensive testing guide provides all the information needed to effectively test the TRIAXUS system using the modern pytest-based test suite.