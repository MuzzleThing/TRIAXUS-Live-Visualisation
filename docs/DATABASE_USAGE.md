# TRIAXUS Database Integration Guide

This comprehensive guide covers PostgreSQL database setup, configuration, and usage with TRIAXUS for oceanographic data management.

## Table of Contents

1. [Database Setup](#database-setup)
2. [Configuration](#configuration)
3. [Database Schema](#database-schema)
4. [API Reference](#api-reference)
5. [Data Operations](#data-operations)
6. [Advanced Usage](#advanced-usage)
7. [Troubleshooting](#troubleshooting)

## Database Setup

### 1. PostgreSQL Installation

#### macOS (using Homebrew)
```bash
# Install PostgreSQL
brew install postgresql

# Start PostgreSQL service
brew services start postgresql

# Create a database user (optional)
createuser -s triaxus_user
```

#### Ubuntu/Debian
```bash
# Install PostgreSQL
sudo apt update
sudo apt install postgresql postgresql-contrib

# Start PostgreSQL service
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create a database user
sudo -u postgres createuser --interactive
```

#### Windows
1. Download PostgreSQL installer from [postgresql.org](https://www.postgresql.org/download/windows/)
2. Run installer and follow setup wizard
3. Remember the password for the `postgres` user

### 2. Database Creation

```bash
# Create database
createdb triaxus_db

# Or using psql
psql -U postgres
CREATE DATABASE triaxus_db;
CREATE USER triaxus_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE triaxus_db TO triaxus_user;
\q
```

### 3. Environment Configuration

Create a `.env` file in your project root:

```bash
# Database Configuration
DATABASE_URL=postgresql://triaxus_user:your_password@localhost:5432/triaxus_db
DB_ENABLED=true

# Optional: Connection pool settings
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10
DB_POOL_TIMEOUT=30
```

Or set environment variables directly:

```bash
export DATABASE_URL="postgresql://triaxus_user:your_password@localhost:5432/triaxus_db"
export DB_ENABLED=true
```

## Configuration

### Database Configuration Manager

TRIAXUS uses `SecureDatabaseConfigManager` to handle database settings:

```python
from triaxus.database import SecureDatabaseConfigManager

# Get database configuration
config_manager = SecureDatabaseConfigManager()
db_config = config_manager.get_database_config()

print(f"Database enabled: {config_manager.is_database_enabled()}")
print(f"Connection URL: {config_manager.get_connection_url()}")
```

### Configuration Options

| Environment Variable | Description | Default |
|---------------------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `DB_ENABLED` | Enable/disable database functionality | `true` |
| `DB_POOL_SIZE` | Connection pool size | `5` |
| `DB_MAX_OVERFLOW` | Maximum pool overflow | `10` |
| `DB_POOL_TIMEOUT` | Pool timeout in seconds | `30` |

## Database Schema

### Tables Overview

TRIAXUS creates two main tables using SQLAlchemy ORM models:

1. **`oceanographic_data`** - Main data table for measurements
2. **`data_sources`** - Metadata table for tracking data files

<<<<<<< HEAD
### Important Note: Column Naming Convention

All database column names use lowercase naming convention to ensure compatibility with PostgreSQL's identifier handling. This means:

- `tv290C` → `tv290c` (Temperature)
- `sbeox0Mm_L` → `sbeox0mm_l` (Dissolved Oxygen)  
- `flECO_AFL` → `fleco_afl` (Fluorescence)
- `filename` → `source_file` (in data_sources table)

This naming convention is consistent throughout the codebase, SQL files, and documentation.

=======
>>>>>>> origin
### Oceanographic Data Table

The `OceanographicData` model creates the following table structure:

```sql
CREATE TABLE oceanographic_data (
    -- Primary key (UUID)
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Core measurement fields
    datetime TIMESTAMP WITH TIME ZONE NOT NULL,
    depth DOUBLE PRECISION NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    
    -- Oceanographic parameters
<<<<<<< HEAD
    tv290c DOUBLE PRECISION,           -- Temperature in Celsius
    sal00 DOUBLE PRECISION,           -- Salinity in PSU
    sbeox0mm_l DOUBLE PRECISION,      -- Dissolved oxygen in mg/L
    fleco_afl DOUBLE PRECISION,      -- Fluorescence in mg/m³
=======
    tv290C DOUBLE PRECISION,           -- Temperature in Celsius
    sal00 DOUBLE PRECISION,           -- Salinity in PSU
    sbeox0Mm_L DOUBLE PRECISION,      -- Dissolved oxygen in mg/L
    flECO_AFL DOUBLE PRECISION,      -- Fluorescence in mg/m³
>>>>>>> origin
    ph DOUBLE PRECISION,              -- pH value
    
    -- Metadata fields
    source_file VARCHAR(255),         -- Source data file name
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

### Data Sources Table

The `DataSource` model creates the following table structure:

```sql
CREATE TABLE data_sources (
    -- Primary key (UUID)
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Source information
<<<<<<< HEAD
    source_file VARCHAR(255) UNIQUE NOT NULL,
    file_type VARCHAR(50) DEFAULT 'CNV',
    file_size BIGINT,
    file_hash VARCHAR(64),            -- File hash for integrity check
    
    -- CNV file metadata
    software_version VARCHAR(100),
    temperature_sn VARCHAR(50),
    conductivity_sn VARCHAR(50),
    number_of_scans INTEGER,
    number_of_cycles INTEGER,
    sample_interval DOUBLE PRECISION,
    start_time TIMESTAMP WITH TIME ZONE,
    end_time TIMESTAMP WITH TIME ZONE,
    
    -- Geographic metadata
    nmea_latitude VARCHAR(50),
    nmea_longitude VARCHAR(50),
    initial_depth DOUBLE PRECISION,
    
    -- Processing metadata
    processed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'processed',  -- pending, processed, error
    error_message TEXT,
    
    -- Data statistics
    total_records INTEGER,
    min_datetime TIMESTAMP WITH TIME ZONE,
    max_datetime TIMESTAMP WITH TIME ZONE,
    min_depth DOUBLE PRECISION,
    max_depth DOUBLE PRECISION,
    min_latitude DOUBLE PRECISION,
    max_latitude DOUBLE PRECISION,
    min_longitude DOUBLE PRECISION,
    max_longitude DOUBLE PRECISION
=======
    filename VARCHAR(255) UNIQUE NOT NULL,
    file_path VARCHAR(500),
    file_size DOUBLE PRECISION,
    file_hash VARCHAR(64),            -- File hash for integrity check
    
    -- Processing metadata
    total_records DOUBLE PRECISION,
    processed_records DOUBLE PRECISION,
    processing_status VARCHAR(50),
    
    -- Timestamps
    first_seen TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_processed TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
>>>>>>> origin
);
```

### Indexes

The ORM models automatically create the following indexes:

```sql
-- Oceanographic data indexes
CREATE INDEX idx_oceanographic_data_datetime ON oceanographic_data (datetime);
CREATE INDEX idx_oceanographic_data_depth ON oceanographic_data (depth);
CREATE INDEX idx_oceanographic_data_latitude ON oceanographic_data (latitude);
CREATE INDEX idx_oceanographic_data_longitude ON oceanographic_data (longitude);

-- Composite indexes
CREATE INDEX idx_datetime_depth ON oceanographic_data (datetime, depth);
CREATE INDEX idx_lat_lon ON oceanographic_data (latitude, longitude);
CREATE INDEX idx_datetime_lat_lon ON oceanographic_data (datetime, latitude, longitude);
CREATE INDEX idx_source_file ON oceanographic_data (source_file);
```

## API Reference

### DatabaseDataSource

The main class for database operations in TRIAXUS.

#### Constructor

```python
from triaxus.data.database_source import DatabaseDataSource

# Initialize with default configuration
db = DatabaseDataSource()

# Check if database is available
if db.is_available():
    print("Database connection successful")
```

#### Core Methods

##### `is_available() -> bool`
Check if database connection is available.

```python
if db.is_available():
    print("Database is ready")
else:
    print("Database not available")
```

##### `load_data(limit: int = 100) -> pd.DataFrame`
Load oceanographic data from database.

```python
# Load latest 100 records
data = db.load_data(limit=100)

# Load all data (use with caution)
all_data = db.load_data(limit=10000)
```

##### `store_data(data: pd.DataFrame, source_file: str = None) -> bool`
Store oceanographic data to database.

```python
import pandas as pd

# Prepare data
new_data = pd.DataFrame({
    'time': ['2024-01-01 00:00:00', '2024-01-01 01:00:00'],
    'depth': [10.0, 15.0],
    'latitude': [-33.5, -33.6],
    'longitude': [115.0, 115.1],
<<<<<<< HEAD
    'tv290c': [22.5, 22.3],
    'sal00': [35.2, 35.1],
    'sbeox0mm_l': [5.8, 5.7],
    'fleco_afl': [1.2, 1.1],
=======
    'tv290C': [22.5, 22.3],
    'sal00': [35.2, 35.1],
    'sbeox0Mm_L': [5.8, 5.7],
    'flECO-AFL': [1.2, 1.1],
>>>>>>> origin
    'ph': [8.1, 8.0]
})

# Store data
success = db.store_data(new_data, "survey_2024.csv")
if success:
    print("Data stored successfully")
```

##### `get_stats() -> dict`
Get database statistics.

```python
stats = db.get_stats()
print(f"Total records: {stats.get('total_records', 0)}")
print(f"Source files: {list(stats.get('source_files', {}).keys())}")
print(f"Available: {stats.get('available', False)}")
```

### DatabaseConnectionManager

Low-level database connection management.

#### Constructor

```python
from triaxus.database import DatabaseConnectionManager, SecureDatabaseConfigManager

# Initialize with configuration
config_manager = SecureDatabaseConfigManager()
conn_manager = DatabaseConnectionManager(config_manager)

# Connect to database
if conn_manager.connect():
    print("Connected successfully")
```

#### Core Methods

##### `connect() -> bool`
Establish database connection.

```python
success = conn_manager.connect()
if success:
    print("Database connected")
```

##### `disconnect() -> None`
Close database connection.

```python
conn_manager.disconnect()
print("Database disconnected")
```

##### `is_connected() -> bool`
Check if database is connected.

```python
if conn_manager.is_connected():
    print("Database is connected")
```

##### `health_check() -> bool`
Check database connection health.

```python
if conn_manager.health_check():
    print("Database is healthy")
```

##### `get_session()`
Get database session context manager.

```python
with conn_manager.get_session() as session:
    # Use session for database operations
    result = session.query(OceanographicData).all()
```

### OceanographicDataRepository

High-level data access operations.

#### Constructor

```python
from triaxus.database import OceanographicDataRepository, DatabaseConnectionManager

# Initialize repository
conn_manager = DatabaseConnectionManager()
repository = OceanographicDataRepository(conn_manager)
```

#### Core Methods

##### `create(data: Union[OceanographicData, List[OceanographicData]]) -> bool`
Create new oceanographic data records.

```python
from triaxus.database import OceanographicData

# Create single record
record = OceanographicData(
    datetime=datetime.now(),
    depth=10.0,
    latitude=-33.5,
    longitude=115.0,
<<<<<<< HEAD
    tv290c=22.5,
=======
    tv290C=22.5,
>>>>>>> origin
    sal00=35.2
)

success = repository.create(record)
```

##### `get_latest_records(limit: int = 100) -> List[OceanographicData]`
Get latest records from database.

```python
records = repository.get_latest_records(limit=50)
print(f"Retrieved {len(records)} records")
```

##### `get_by_time_range(start_time: datetime, end_time: datetime) -> List[OceanographicData]`
Get records within time range.

```python
from datetime import datetime, timedelta

end_time = datetime.now()
start_time = end_time - timedelta(hours=24)

records = repository.get_by_time_range(start_time, end_time)
```

##### `get_by_location(lat_min: float, lat_max: float, lon_min: float, lon_max: float) -> List[OceanographicData]`
Get records within geographic bounds.

```python
records = repository.get_by_location(
    lat_min=-35.0, lat_max=-27.0,
    lon_min=113.0, lon_max=116.0
)
```

##### `get_statistics() -> Dict[str, Any]`
Get database statistics.

```python
stats = repository.get_statistics()
print(f"Total records: {stats.get('total_records', 0)}")
print(f"Date range: {stats.get('date_range', {})}")
```

### DataMapper

Convert between DataFrames and database models.

#### Constructor

```python
from triaxus.database import DataMapper

mapper = DataMapper()
```

#### Core Methods

##### `dataframe_to_models(df: pd.DataFrame, source_file: str = None) -> List[OceanographicData]`
Convert DataFrame to list of OceanographicData models.

```python
models = mapper.dataframe_to_models(df, "my_data.csv")
print(f"Created {len(models)} models")
```

##### `models_to_dataframe(models: List[OceanographicData]) -> pd.DataFrame`
Convert list of OceanographicData models to DataFrame.

```python
df = mapper.models_to_dataframe(models)
print(f"DataFrame shape: {df.shape}")
```

## Data Operations

### Data Validation

The `OceanographicData` model includes built-in validation:

```python
from triaxus.database import OceanographicData

# Create model instance
record = OceanographicData(
    datetime=datetime.now(),
    depth=10.0,
    latitude=-33.5,  # Valid latitude
    longitude=115.0,  # Valid longitude
<<<<<<< HEAD
    tv290c=22.5
=======
    tv290C=22.5
>>>>>>> origin
)

# Validate data
if record.validate():
    print("Data is valid")
else:
    print("Data validation failed")
```

### Data Conversion

Convert between different data formats:

```python
# Convert model to dictionary
record_dict = record.to_dict()

# Create model from dictionary
new_record = OceanographicData.from_dict(record_dict)
```

### Batch Operations

For large datasets, use batch operations:

```python
def store_large_dataset(data_file, batch_size=1000):
    """Store large dataset in batches"""
    import pandas as pd
    
    # Read data in chunks
    chunk_iter = pd.read_csv(data_file, chunksize=batch_size)
    
    total_stored = 0
    for i, chunk in enumerate(chunk_iter):
        # Store chunk
        success = db.store_data(chunk, f"{data_file}_batch_{i}")
        
        if success:
            total_stored += len(chunk)
            print(f"Stored batch {i+1}: {len(chunk)} records")
        else:
            print(f"Failed to store batch {i+1}")
    
    print(f"Total records stored: {total_stored}")
```

## Advanced Usage

### Database Initialization

Use `DatabaseInitializer` to set up the database:

```python
from triaxus.database import DatabaseInitializer, SecureDatabaseConfigManager

# Initialize database
config_manager = SecureDatabaseConfigManager()
initializer = DatabaseInitializer(config_manager)

# Create tables and indexes
if initializer.initialize_database():
    print("Database initialized successfully")
else:
    print("Database initialization failed")
```

### Custom Queries

For complex queries, access the database directly:

```python
from triaxus.database import DatabaseConnectionManager
from sqlalchemy import text

# Get database connection
conn_manager = DatabaseConnectionManager()
conn_manager.connect()

# Execute custom query
query = text("""
    SELECT 
        DATE_TRUNC('hour', datetime) as hour,
<<<<<<< HEAD
        AVG(tv290c) as avg_temp,
=======
        AVG(tv290C) as avg_temp,
>>>>>>> origin
        COUNT(*) as record_count
    FROM oceanographic_data 
    WHERE datetime >= :start_date 
    AND datetime <= :end_date
    GROUP BY DATE_TRUNC('hour', datetime)
    ORDER BY hour
""")

result = conn_manager.execute_raw_sql(
    query, 
    start_date='2024-01-01',
    end_date='2024-01-02'
)

# Process results
for row in result:
    print(f"Hour: {row.hour}, Avg Temp: {row.avg_temp:.2f}")
```

### Data Export

Export data to various formats:

```python
def export_data_to_csv(start_date, end_date, output_file):
    """Export data to CSV"""
    # Get data using repository
    repository = OceanographicDataRepository()
    records = repository.get_by_time_range(start_date, end_date)
    
    # Convert to DataFrame
    mapper = DataMapper()
    df = mapper.models_to_dataframe(records)
    
    # Export to CSV
    df.to_csv(output_file, index=False)
    print(f"Exported {len(df)} records to {output_file}")
```

## Troubleshooting

### Common Issues

#### 1. Connection Errors

**Error**: `psycopg2.OperationalError: could not connect to server`

**Solutions**:
```bash
# Check if PostgreSQL is running
brew services list | grep postgresql  # macOS
sudo systemctl status postgresql     # Linux

# Start PostgreSQL service
brew services start postgresql       # macOS
sudo systemctl start postgresql      # Linux
```

#### 2. Authentication Errors

**Error**: `psycopg2.OperationalError: FATAL: password authentication failed`

**Solutions**:
```bash
# Reset password
sudo -u postgres psql
ALTER USER triaxus_user PASSWORD 'new_password';
\q

# Update environment variable
export DATABASE_URL="postgresql://triaxus_user:new_password@localhost:5432/triaxus_db"
```

#### 3. Database Not Found

**Error**: `psycopg2.OperationalError: FATAL: database "triaxus_db" does not exist`

**Solutions**:
```bash
# Create database
createdb triaxus_db

# Or using psql
psql -U postgres
CREATE DATABASE triaxus_db;
\q
```

### Debugging Connection

```python
from triaxus.database import DatabaseConnectionManager

# Test connection
conn_manager = DatabaseConnectionManager()

try:
    conn_manager.connect()
    print("✓ Database connection successful")
    
    # Test query
    result = conn_manager.execute_raw_sql("SELECT version()")
    print(f"✓ PostgreSQL version: {result[0][0]}")
    
    # Check connection info
    info = conn_manager.get_connection_info()
    print(f"✓ Connection info: {info}")
    
except Exception as e:
    print(f"✗ Database connection failed: {e}")
```

### Logging

Enable detailed logging for debugging:

```python
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('triaxus.database')

# Database operations will now log detailed information
db = DatabaseDataSource()
data = db.load_data(limit=10)
```

## Performance Tips

### 1. Connection Pooling

Configure appropriate pool settings:

```bash
# In .env file
DB_POOL_SIZE=10        # Number of persistent connections
DB_MAX_OVERFLOW=20     # Additional connections when needed
DB_POOL_TIMEOUT=30     # Timeout for getting connection
```

### 2. Query Optimization

Use appropriate LIMIT clauses and WHERE conditions:

```python
# Good: Use LIMIT for large datasets
data = db.load_data(limit=1000)

# Good: Use specific filters
repository = OceanographicDataRepository()
recent_data = repository.get_by_time_range(
    start_time=datetime.now() - timedelta(hours=24),
    end_time=datetime.now()
)

# Avoid: Loading all data at once
# all_data = db.load_data(limit=1000000)  # Don't do this
```

### 3. Batch Operations

For large data imports, use batch processing:

```python
def efficient_data_import(csv_file, batch_size=1000):
    """Efficiently import large CSV file"""
    import pandas as pd
    
    total_imported = 0
    for chunk in pd.read_csv(csv_file, chunksize=batch_size):
        success = db.store_data(chunk, csv_file)
        if success:
            total_imported += len(chunk)
            print(f"Imported {total_imported} records")
        else:
            print("Import failed")
            break
    
    return total_imported
```

This guide covers all aspects of database integration with TRIAXUS, from initial setup to advanced usage patterns and troubleshooting, based on the actual implementation in the codebase.