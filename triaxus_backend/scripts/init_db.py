#!/usr/bin/env python3
"""
Database initialization script for TRIAXUS system.
"""
import logging
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import text
from config.database import engine, init_database
from config.settings import settings
from config.logging_config import setup_logging

# Setup logging
logger = setup_logging()

def create_extensions():
    """Create necessary PostgreSQL extensions."""
    logger.info("Creating PostgreSQL extensions...")
    
    with engine.connect() as conn:
        # Create uuid-ossp extension
        conn.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";'))
        logger.info("✓ uuid-ossp extension created")
        
        if settings.POSTGIS_ENABLED:
            conn.execute(text('CREATE EXTENSION IF NOT EXISTS "postgis";'))
            logger.info("✓ PostGIS extension created")
        
        if settings.TIMESCALEDB_ENABLED:
            conn.execute(text('CREATE EXTENSION IF NOT EXISTS "timescaledb";'))
            logger.info("✓ TimescaleDB extension created")
        
        conn.commit()

def create_hypertables():
    """Create TimescaleDB hypertables for time-series data."""
    if not settings.TIMESCALEDB_ENABLED:
        logger.info("TimescaleDB disabled, skipping hypertable creation")
        return
    
    logger.info("Creating TimescaleDB hypertables...")
    
    with engine.connect() as conn:
        # Create hypertable for sensor_data
        try:
            conn.execute(text("""
                SELECT create_hypertable('sensor_data', 'timestamp',
                    chunk_time_interval => INTERVAL '1 day',
                    if_not_exists => TRUE);
            """))
            logger.info("✓ sensor_data hypertable created")
        except Exception as e:
            logger.warning(f"sensor_data hypertable may already exist: {e}")
        
        # Create hypertable for gps_tracks
        try:
            conn.execute(text("""
                SELECT create_hypertable('gps_tracks', 'timestamp',
                    chunk_time_interval => INTERVAL '1 day',
                    if_not_exists => TRUE);
            """))
            logger.info("✓ gps_tracks hypertable created")
        except Exception as e:
            logger.warning(f"gps_tracks hypertable may already exist: {e}")
        
        conn.commit()

def create_indexes():
    """Create additional indexes for performance."""
    logger.info("Creating additional indexes...")
    
    with engine.connect() as conn:
        # Sensor data indexes
        conn.execute(text('CREATE INDEX IF NOT EXISTS idx_sensor_data_cast ON sensor_data(cast_id);'))
        conn.execute(text('CREATE INDEX IF NOT EXISTS idx_sensor_data_file ON sensor_data(file_id);'))
        conn.execute(text('CREATE INDEX IF NOT EXISTS idx_sensor_data_depth ON sensor_data(depth);'))
        
        # GPS tracks indexes
        conn.execute(text('CREATE INDEX IF NOT EXISTS idx_gps_tracks_cruise ON gps_tracks(cruise_id);'))
        if settings.POSTGIS_ENABLED:
            conn.execute(text('CREATE INDEX IF NOT EXISTS idx_gps_location ON gps_tracks USING GIST(location);'))
            conn.execute(text('CREATE INDEX IF NOT EXISTS idx_casts_location ON casts USING GIST(start_location);'))
        
        # Operation logs index
        conn.execute(text('CREATE INDEX IF NOT EXISTS idx_operation_logs_time ON operation_logs(timestamp DESC);'))
        
        conn.commit()
        logger.info("✓ Additional indexes created")

def create_triggers():
    """Create database triggers."""
    logger.info("Creating database triggers...")
    
    with engine.connect() as conn:
        # Create function for updating updated_at timestamp
        conn.execute(text("""
            CREATE OR REPLACE FUNCTION update_updated_at_column()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.updated_at = CURRENT_TIMESTAMP;
                RETURN NEW;
            END;
            $$ language 'plpgsql';
        """))
        
        # Create trigger for cruises table
        conn.execute(text("""
            DROP TRIGGER IF EXISTS update_cruises_updated_at ON cruises;
            CREATE TRIGGER update_cruises_updated_at 
                BEFORE UPDATE ON cruises
                FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
        """))
        
        conn.commit()
        logger.info("✓ Database triggers created")

def create_materialized_views():
    """Create materialized views for performance."""
    logger.info("Creating materialized views...")
    
    with engine.connect() as conn:
        # Drop existing view if it exists
        conn.execute(text('DROP MATERIALIZED VIEW IF EXISTS latest_sensor_readings;'))
        
        # Create materialized view for latest sensor readings
        conn.execute(text("""
            CREATE MATERIALIZED VIEW latest_sensor_readings AS
            SELECT DISTINCT ON (file_id)
                file_id,
                timestamp,
                pressure,
                temperature,
                conductivity,
                salinity,
                depth,
                latitude,
                longitude
            FROM sensor_data
            ORDER BY file_id, timestamp DESC;
        """))
        
        # Create index on materialized view
        conn.execute(text('CREATE INDEX idx_latest_readings_file ON latest_sensor_readings(file_id);'))
        
        conn.commit()
        logger.info("✓ Materialized views created")

def main():
    """Main initialization function."""
    logger.info("Starting TRIAXUS database initialization...")
    logger.info(f"Database URL: {settings.DATABASE_URL.split('@')[1]}")  # Hide credentials
    
    try:
        # Test database connection
        with engine.connect() as conn:
            result = conn.execute(text('SELECT version();'))
            version = result.fetchone()[0]
            logger.info(f"Connected to: {version}")
        
        # Create extensions first
        create_extensions()
        
        # Initialize database tables
        logger.info("Creating database tables...")
        init_database()
        logger.info("✓ Database tables created")
        
        # Create hypertables for time-series data
        create_hypertables()
        
        # Create additional indexes
        create_indexes()
        
        # Create triggers
        create_triggers()
        
        # Create materialized views
        create_materialized_views()
        
        logger.info("🎉 Database initialization completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()