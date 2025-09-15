-- =============================================================================
-- TRIAXUS Database Initialization Script
-- PostgreSQL Database Schema for Oceanographic Data
-- =============================================================================
-- 
-- This script creates the complete database schema for the TRIAXUS visualization system.
-- It includes tables, indexes, constraints, and initial data structures.
--
-- Usage:
--   psql -U username -d database_name -f init_database.sql
--   or execute sections individually as needed
--
-- =============================================================================

-- =============================================================================
-- DATABASE SETUP
-- =============================================================================

-- Create database (run as superuser)
-- CREATE DATABASE triaxus_db;
-- CREATE USER triaxus_user WITH PASSWORD 'your_secure_password';
-- GRANT ALL PRIVILEGES ON DATABASE triaxus_db TO triaxus_user;

-- Connect to the database
-- \c triaxus_db;

-- =============================================================================
-- EXTENSIONS
-- =============================================================================

-- Enable UUID extension for generating UUIDs
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable PostGIS for geographic operations (optional)
-- CREATE EXTENSION IF NOT EXISTS postgis;

-- =============================================================================
-- MAIN DATA TABLE
-- =============================================================================

-- Drop table if exists (for clean reinstall)
DROP TABLE IF EXISTS oceanographic_data CASCADE;

-- Create main oceanographic data table
CREATE TABLE oceanographic_data (
    -- Primary key
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Time and spatial information
    datetime TIMESTAMP WITH TIME ZONE NOT NULL,
    depth DOUBLE PRECISION NOT NULL CHECK (depth >= 0),
    latitude DOUBLE PRECISION CHECK (latitude >= -90 AND latitude <= 90),
    longitude DOUBLE PRECISION CHECK (longitude >= -180 AND longitude <= 180),
    
    -- Oceanographic variables (matching current code structure)
    tv290C DOUBLE PRECISION,           -- Temperature [ITS-90, deg C]
    sal00 DOUBLE PRECISION,           -- Salinity [PSU]
    sbeox0Mm_L DOUBLE PRECISION,      -- Dissolved Oxygen [umol/kg]
    flECO_AFL DOUBLE PRECISION,       -- Fluorescence [mg/m^3]
    ph DOUBLE PRECISION,              -- pH
    
    -- Metadata
    source_file VARCHAR(255),          -- Source CNV file or data source
    quality_flag INTEGER DEFAULT 1,    -- Data quality flag (1=good, 2=questionable, 3=bad)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- INDEXES FOR PERFORMANCE
-- =============================================================================

-- Primary query indexes
CREATE INDEX idx_oceanographic_data_datetime ON oceanographic_data (datetime);
CREATE INDEX idx_oceanographic_data_depth ON oceanographic_data (depth);
CREATE INDEX idx_oceanographic_data_latitude ON oceanographic_data (latitude);
CREATE INDEX idx_oceanographic_data_longitude ON oceanographic_data (longitude);

-- Composite indexes for common query patterns
CREATE INDEX idx_oceanographic_data_datetime_depth ON oceanographic_data (datetime, depth);
CREATE INDEX idx_oceanographic_data_lat_lon ON oceanographic_data (latitude, longitude);
CREATE INDEX idx_oceanographic_data_datetime_lat_lon ON oceanographic_data (datetime, latitude, longitude);

-- Variable-specific indexes
CREATE INDEX idx_oceanographic_data_temperature ON oceanographic_data (tv290C) WHERE tv290C IS NOT NULL;
CREATE INDEX idx_oceanographic_data_salinity ON oceanographic_data (sal00) WHERE sal00 IS NOT NULL;
CREATE INDEX idx_oceanographic_data_oxygen ON oceanographic_data (sbeox0Mm_L) WHERE sbeox0Mm_L IS NOT NULL;

-- Quality and source indexes
CREATE INDEX idx_oceanographic_data_quality ON oceanographic_data (quality_flag);
CREATE INDEX idx_oceanographic_data_source ON oceanographic_data (source_file) WHERE source_file IS NOT NULL;

-- =============================================================================
-- DATA SOURCE METADATA TABLE (Optional)
-- =============================================================================

-- Create data source metadata table
CREATE TABLE IF NOT EXISTS data_sources (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_file VARCHAR(255) UNIQUE NOT NULL,
    file_type VARCHAR(50) DEFAULT 'CNV',
    file_size BIGINT,
    file_hash VARCHAR(64),  -- SHA-256 hash for integrity checking
    
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
);

-- Indexes for data sources
CREATE INDEX idx_data_sources_file ON data_sources (source_file);
CREATE INDEX idx_data_sources_status ON data_sources (status);
CREATE INDEX idx_data_sources_processed ON data_sources (processed_at);

-- =============================================================================
-- VIEWS FOR COMMON QUERIES
-- =============================================================================

-- View for latest data by depth
CREATE OR REPLACE VIEW latest_data_by_depth AS
SELECT DISTINCT ON (depth)
    datetime,
    depth,
    latitude,
    longitude,
    tv290C,
    sal00,
    sbeox0Mm_L,
    flECO_AFL,
    ph,
    source_file,
    quality_flag
FROM oceanographic_data
WHERE datetime >= CURRENT_TIMESTAMP - INTERVAL '24 hours'
ORDER BY depth, datetime DESC;

-- View for data statistics
CREATE OR REPLACE VIEW data_statistics AS
SELECT 
    COUNT(*) as total_records,
    COUNT(DISTINCT source_file) as unique_sources,
    MIN(datetime) as earliest_datetime,
    MAX(datetime) as latest_datetime,
    MIN(depth) as min_depth,
    MAX(depth) as max_depth,
    AVG(tv290C) as avg_temperature,
    AVG(sal00) as avg_salinity,
    AVG(sbeox0Mm_L) as avg_oxygen,
    AVG(flECO_AFL) as avg_fluorescence,
    AVG(ph) as avg_ph
FROM oceanographic_data
WHERE quality_flag = 1;

-- =============================================================================
-- FUNCTIONS AND TRIGGERS
-- =============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger to automatically update updated_at
CREATE TRIGGER update_oceanographic_data_updated_at 
    BEFORE UPDATE ON oceanographic_data 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Function to validate data ranges
CREATE OR REPLACE FUNCTION validate_oceanographic_data()
RETURNS TRIGGER AS $$
BEGIN
    -- Validate temperature range
    IF NEW.tv290C IS NOT NULL AND (NEW.tv290C < -2 OR NEW.tv290C > 40) THEN
        RAISE EXCEPTION 'Temperature out of valid range: %', NEW.tv290C;
    END IF;
    
    -- Validate salinity range
    IF NEW.sal00 IS NOT NULL AND (NEW.sal00 < 0 OR NEW.sal00 > 50) THEN
        RAISE EXCEPTION 'Salinity out of valid range: %', NEW.sal00;
    END IF;
    
    -- Validate pH range
    IF NEW.ph IS NOT NULL AND (NEW.ph < 6 OR NEW.ph > 9) THEN
        RAISE EXCEPTION 'pH out of valid range: %', NEW.ph;
    END IF;
    
    -- Validate oxygen range
    IF NEW.sbeox0Mm_L IS NOT NULL AND (NEW.sbeox0Mm_L < 0 OR NEW.sbeox0Mm_L > 20) THEN
        RAISE EXCEPTION 'Oxygen out of valid range: %', NEW.sbeox0Mm_L;
    END IF;
    
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger for data validation
CREATE TRIGGER validate_oceanographic_data_trigger
    BEFORE INSERT OR UPDATE ON oceanographic_data
    FOR EACH ROW
    EXECUTE FUNCTION validate_oceanographic_data();

-- =============================================================================
-- PERMISSIONS
-- =============================================================================

-- Grant permissions to application user
-- GRANT SELECT, INSERT, UPDATE, DELETE ON oceanographic_data TO triaxus_user;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON data_sources TO triaxus_user;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO triaxus_user;
-- GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO triaxus_user;

-- =============================================================================
-- SAMPLE DATA (Optional - for testing)
-- =============================================================================

-- Insert sample data for testing (uncomment if needed)
/*
INSERT INTO oceanographic_data (
    datetime, depth, latitude, longitude, 
    tv290C, sal00, sbeox0Mm_L, flECO_AFL, ph,
    source_file, quality_flag
) VALUES 
    (CURRENT_TIMESTAMP, 10.5, 35.0, -120.0, 15.2, 35.1, 8.5, 0.3, 8.1, 'sample_data.cnv', 1),
    (CURRENT_TIMESTAMP, 20.0, 35.1, -120.1, 14.8, 35.2, 8.2, 0.4, 8.0, 'sample_data.cnv', 1),
    (CURRENT_TIMESTAMP, 30.0, 35.2, -120.2, 14.5, 35.3, 7.9, 0.5, 7.9, 'sample_data.cnv', 1);
*/

-- =============================================================================
-- MAINTENANCE QUERIES
-- =============================================================================

-- Query to check table sizes
-- SELECT 
--     schemaname,
--     tablename,
--     attname,
--     n_distinct,
--     correlation
-- FROM pg_stats 
-- WHERE tablename = 'oceanographic_data';

-- Query to analyze table performance
-- ANALYZE oceanographic_data;

-- Query to check index usage
-- SELECT 
--     schemaname,
--     tablename,
--     indexname,
--     idx_tup_read,
--     idx_tup_fetch
-- FROM pg_stat_user_indexes 
-- WHERE tablename = 'oceanographic_data';

-- =============================================================================
-- CLEANUP COMMANDS (Use with caution!)
-- =============================================================================

-- Drop all tables and functions (for complete cleanup)
-- DROP TABLE IF EXISTS oceanographic_data CASCADE;
-- DROP TABLE IF EXISTS data_sources CASCADE;
-- DROP FUNCTION IF EXISTS update_updated_at_column();
-- DROP FUNCTION IF EXISTS validate_oceanographic_data();

-- =============================================================================
-- END OF INITIALIZATION SCRIPT
-- =============================================================================
