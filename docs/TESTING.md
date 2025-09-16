# TRIAXUS Testing Documentation

This document provides essential information about running tests for the TRIAXUS visualization system.

## Quick Start

### Run All Tests
```bash
# Database testing (recommended for database validation)
python tests/test_database.py --clean-db

# Quick test (recommended for development)
python tests/test_runner_quick.py --clean-db

# Comprehensive test (full system validation)
python tests/test_comprehensive.py

# Unified test runner
python tests/test_runner.py --category all --clean-db
```

### Run Specific Tests
```bash
# Database tests only
python tests/test_database.py --clean-db

# Specific database test categories
python tests/test_database.py --category connectivity
python tests/test_database.py --category schema
python tests/test_database.py --category mapping
python tests/test_database.py --category operations

# Individual database test modules
python tests/unit/database/test_connectivity.py
python tests/unit/database/test_schema.py
python tests/unit/database/test_mapping.py
python tests/unit/database/test_operations.py

# Unit tests only
python tests/test_runner.py --category unit

# Integration tests only  
python tests/test_runner.py --category integration

# Individual test files
python tests/unit/test_models_and_mappers.py
python tests/unit/test_data_quality.py
python tests/integration/test_integration.py
```

## Test Structure

```
tests/
├── unit/                    # Unit tests
│   ├── test_models_and_mappers.py
│   ├── test_data_quality.py
│   ├── database/            # Database-specific tests
│   │   ├── test_connectivity.py
│   │   ├── test_schema.py
│   │   ├── test_mapping.py
│   │   └── test_operations.py
│   ├── plots/               # Plot component tests
│   └── themes/              # Theme tests
├── integration/             # Integration tests
│   ├── test_integration.py  # Database integration
│   └── maps/               # Map visualization tests
├── output/                  # Generated HTML outputs
├── test_database.py         # Main database test runner
├── test_runner.py          # Main test runner
├── test_runner_quick.py    # Quick test runner
└── test_comprehensive.py   # Full E2E test
```

## Database Testing

### Database Test Scripts

The system includes comprehensive modular database testing:

1. **`test_database.py`** - **Main database test runner** (recommended for database testing)
   - Orchestrates all database test modules
   - Supports category-specific testing
   - Provides unified test reporting

2. **`tests/unit/database/`** - **Modular database test modules**:
   - **`test_connectivity.py`** - Database connection, session management, connection pool
   - **`test_schema.py`** - Table structure, column definitions, indexes
   - **`test_mapping.py`** - DataFrame ↔ Model conversion, field mapping, data types
   - **`test_operations.py`** - CRUD operations, repository pattern, performance testing

3. **`test_runner_quick.py`** - Quick database connectivity and basic operations (~2-3 seconds)
4. **`test_comprehensive.py`** - Full database workflow testing (data generation → storage → retrieval → visualization) (~20 seconds)
5. **`test_runner.py`** - Unified test runner for all test categories (~15 seconds)
6. **`tests/unit/test_models_and_mappers.py`** - Database model and data mapping tests
7. **`tests/integration/test_integration.py`** - Complete database integration tests (database → visualization pipeline)

### Database Test Features

- **Modular design**: Each test category has its own dedicated module
- **Flexible cleanup**: Checks table existence before cleaning
- **Data validation**: Tests realistic oceanographic data
- **Schema validation**: Verifies table structure and column names
- **Performance testing**: Measures database operation speed
- **Comprehensive coverage**: Connectivity, schema, mapping, and operations
- **Reusable modules**: Can be imported and used by other test scripts

### Database Configuration

```bash
# Required environment variables
export DB_ENABLED=true
export DATABASE_URL=postgresql://username@localhost:5432/triaxus_db
```

### Test Script Relationships

- **`test_comprehensive.py`**: Calls `test_runner.py` to run the full test suite, then performs additional E2E validation
- **`test_runner.py`**: Unified runner that executes unit, integration, and E2E tests independently (avoids circular calls)
- **`test_database.py`**: Dedicated database testing with modular test categories
- **`test_runner_quick.py`**: Fast validation for development workflow

### Database Test Architecture

The database testing system is designed with modularity in mind:

- **Main Runner** (`test_database.py`): Orchestrates all database tests and provides unified reporting
- **Test Modules** (`tests/unit/database/`): Individual test categories that can be run independently
- **Reusable Components**: Test modules can be imported and used by other test scripts
- **Category-based Testing**: Run specific test categories (connectivity, schema, mapping, operations)
- **Flexible Integration**: Other test scripts can import and use database test modules

This design allows for:
- Independent testing of specific database functionality
- Easy integration with comprehensive test suites
- Better maintainability and debugging
- Clear separation of concerns

## Test Output

All test outputs are saved to `tests/output/`:
- HTML visualization files
- Test result logs
- Performance metrics

## Troubleshooting

### Common Issues

1. **Database not connected**:
   ```bash
   # macOS (using Homebrew)
   brew services start postgresql@14
   
   # Linux (using systemd)
   sudo systemctl start postgresql
   sudo systemctl start postgresql@14-main  # Ubuntu/Debian
   
   # Check service status
   sudo systemctl status postgresql
   
   # Verify database is running
   ps aux | grep postgres
   
   # Test connection
   psql -h localhost -p 5432 -U username -d triaxus_db
   ```

2. **Environment variables not set**:
   ```bash
   # Check if DB_ENABLED is set
   echo $DB_ENABLED
   
   # Set required environment variables
   export DB_ENABLED=true
   export DATABASE_URL=postgresql://username@localhost:5432/triaxus_db
   
   # For production environments, use proper credentials
   export DATABASE_URL=postgresql://user:password@host:port/database
   ```

3. **Column name errors**: All database columns use lowercase naming (e.g., `tv290c`, `sbeox0mm_l`, `fleco_afl`)

4. **Test data issues**: Check that data points are in ocean areas, not on land

### Debug Mode
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

*Last updated: September 2024 - Updated test structure and performance information*
