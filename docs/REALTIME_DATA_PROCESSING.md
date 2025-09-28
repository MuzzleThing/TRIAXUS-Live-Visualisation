# TRIAXUS Real-time Data Processing System

This document provides comprehensive documentation for the TRIAXUS real-time oceanographic data processing and visualization system.

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Core Components](#core-components)
4. [Configuration](#configuration)
5. [Usage Guide](#usage-guide)
6. [API Reference](#api-reference)
7. [Troubleshooting](#troubleshooting)
8. [Performance Optimization](#performance-optimization)

## System Overview

The TRIAXUS real-time data processing system provides a complete pipeline for ingesting, processing, storing, and visualizing oceanographic data in real-time. The system supports CNV file ingestion, database storage, and web-based visualization dashboards.

### Key Features

- **Real-time CNV File Ingestion**: Automated monitoring and processing of new CNV files
- **Database Storage**: PostgreSQL-based data persistence with validation
- **Web Dashboard**: Interactive real-time visualization with customizable refresh rates
- **Cross-platform Support**: Works on macOS, Linux, and Windows
- **Daemon Management**: Background process management with PID tracking
- **API Server**: RESTful API for data access and system status

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   CNV Files     │───▶│  Data Processor  │───▶│   PostgreSQL    │
│   (Source)      │    │   & Validator    │    │   Database      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │   Data Archiver  │    │   API Server    │
                       │   & Cleanup      │    │   (REST API)    │
                       └──────────────────┘    └─────────────────┘
                                                        │
                                                        ▼
                                               ┌─────────────────┐
                                               │  Web Dashboard  │
                                               │  (Real-time)    │
                                               └─────────────────┘
```

## Core Components

### 1. Real-time Data Processor (`triaxus.data.cnv_realtime_processor`)

Specialized processor for real-time data streams with enhanced monitoring capabilities.

**Features:**
- Real-time file monitoring
- Configurable processing intervals
- State persistence across restarts
- Automatic plot generation
- Performance metrics

**Usage:**
```bash
# Start real-time monitoring
python -m triaxus.data.cnv_realtime_processor --watch

# Show configuration
python -m triaxus.data.cnv_realtime_processor --config

# Default: start real-time monitoring
python -m triaxus.data.cnv_realtime_processor
```

### 2. Database Data Source (`triaxus.data.database_source`)

Provides database connectivity and data access layer.

**Features:**
- PostgreSQL integration
- Connection pooling
- Data validation
- Query optimization
- Error handling
- Shared connection instances for API server

### 3. API Server (`realtime/realtime_api_server.py`)

RESTful API server for real-time data access and system monitoring.

**Endpoints:**
- `GET /api/latest_data?limit=N` - Retrieve latest N records
- `GET /api/status` - System status and health check
- `GET /` - Serve the web dashboard

**Features:**
- Real-time data filtering (last 24 hours)
- JSON serialization
- CORS support
- Error handling
- Shared database connections

### 4. Web Dashboard (`realtime/dashboard.html`)

Interactive web-based visualization dashboard.

**Features:**
- Real-time data visualization
- Multiple plot types (time series, depth profile, map)
- Customizable refresh rates (0.5s to 5min)
- Manual refresh option
- Responsive design
- Map integration with trajectory tracking

## Configuration

### Main Configuration (`configs/default.yaml`)

```yaml
cnv_processing:
  source_directory: "testdataQC"
  auto_process: false
  batch_size: 1000
  
  realtime:
    enabled: false
    interval_seconds: 60
    plot_after_ingest: true
    plot_output_dir: "tests/output"
    file_patterns:
      - "*.cnv"
      - "*.CNV"
    min_age_seconds: 5
    state_file: ".runtime/cnv_seen.json"
  
  output_options:
    log_file: "cnv_processing.log"
    verbose: true
  
  file_patterns:
    - "*.cnv"
    - "*.CNV"
  
  quality_control:
    enabled: true
    strict_mode: false
    skip_invalid_files: true

database:
  enabled: true
  url: "postgresql://user:password@localhost:5432/triaxus_db"
  echo: false
  pool_size: 5
  max_overflow: 10
  pool_timeout: 30
  pool_recycle: 3600
  
  table:
    name: "oceanographic_data"
    indexes: ["datetime", "depth", "latitude", "longitude"]
```

### Real-time Test Configuration (`configs/realtime_test.yaml`)

```yaml
cnv_processing:
  source_directory: "testdataQC"
  
  realtime:
    enabled: true
    interval_seconds: 60
    plot_after_ingest: true
    plot_output_dir: "tests/output/realtime_plots"
    file_patterns:
      - "live_*.cnv"
    min_age_seconds: 0.1
    state_file: ".runtime/cnv_seen_realtime.json"
```

## Usage Guide

### 1. Quick Start

```bash
# Start the complete real-time pipeline
python scripts/start_realtime_pipeline.py

# Stop the pipeline
python scripts/stop_realtime_pipeline.py
```

### 2. Manual Processing

```bash
# Start real-time monitoring
python -m triaxus.data.cnv_realtime_processor --watch

# Start with custom config
python -m triaxus.data.cnv_realtime_processor --watch --config configs/realtime_test.yaml
```

### 3. Daemon Management

```bash
# Start as background daemon
python -m triaxus.services.cnv_watcher start

# Check status
python -m triaxus.services.cnv_watcher status

# Stop daemon
python -m triaxus.services.cnv_watcher stop
```

**Note:** The daemon runs `python -m triaxus.data.cnv_realtime_processor --watch` in the background.

### 4. API Server

```bash
# Start API server (default port 8080)
python realtime/realtime_api_server.py

# Start API server on custom port
python realtime/realtime_api_server.py 8080

# Access dashboard
open http://localhost:8080
```

### 5. Web Dashboard Usage

1. **Access the Dashboard**: Open `http://localhost:8080` in your browser
2. **Set Refresh Rate**: Choose from 0.5s, 1s, 2s, 5s, 10s, 30s, 1min, 5min, 10min, 15min, 30min, 1hour, or Manual mode (default: 1min)
3. **Select Time Range**: Choose from 5m, 15m, 30m, 1h, 6h, 12h, 24h, 3d, 7d, 30d, or All Data (default: 1h)
4. **Select Plot Type**: All, Time Series, Profile, or Map only
5. **Adjust Map Zoom**: 6 (wide) to 20 (detail)
6. **Manual Refresh**: Click "Manual Refresh" button when needed
7. **Real-time Data**: Shows data based on selected time range with timezone-aware display

## API Reference

### GET /api/latest_data

Retrieve the latest oceanographic data records.

**Parameters:**
- `limit` (optional): Number of records to return (default: 1000)

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "time": "2025-09-28T02:27:10+08:00",
      "depth": 150.5,
      "latitude": -35.57462,
      "longitude": 154.30952,
      "tv290c": 16.2,
      "sal00": 35.4,
      "sbeox0mm_l": 7.1
    }
  ],
  "count": 10,
  "timestamp": "2025-09-28T11:25:26.908420"
}
```

**Note:** The API returns the latest 1000 records by default. The frontend dashboard handles time-based filtering based on user selection.

### GET /api/status

Get system status and health information.

**Response:**
```json
{
  "success": true,
  "database_connected": true,
  "latest_records": 10,
  "timestamp": "2025-09-28T11:25:26.908420"
}
```

## Troubleshooting

### Common Issues

#### 1. Database Connection Errors

**Problem**: "Database connection failed"
**Solutions:**
- Verify PostgreSQL is running
- Check database URL in configuration
- Ensure database exists and user has permissions
- Check network connectivity

#### 2. No Files Being Processed

**Problem**: CNV files not being ingested
**Solutions:**
- Verify `source_directory` exists
- Check `file_patterns` match your files (default: "live_*.cnv")
- Reduce `min_age_seconds` if files are short-lived (default: 0.1s)
- Check file permissions
- Review logs for errors
- Delete state file `.runtime/cnv_seen_realtime.json` to force reprocessing

#### 3. API Server Issues

**Problem**: Dashboard not loading or API errors
**Solutions:**
- Check if API server is running on correct port
- Verify database connectivity
- Check for port conflicts
- Review server logs

#### 4. Time Format Errors

**Problem**: "time data doesn't match format"
**Solutions:**
- Ensure ISO8601 format in database
- Check timezone settings
- Verify data processing pipeline

#### 5. Performance Issues

**Problem**: Slow response or high resource usage
**Solutions:**
- Reduce refresh rate
- Limit data records returned
- Optimize database queries
- Check system resources

### Log Files

- **Real-time Processing**: `processor.log` or `processor_debug.log`
- **Watcher Log**: `logs/cnv_watcher.log`
- **API Server**: Console output
- **Dashboard**: Browser console (F12)

### Debug Mode

Enable debug logging in the configuration files or set environment variables for verbose output.

## Performance Optimization

### 1. Database Optimization

- Use connection pooling
- Index frequently queried columns
- Regular database maintenance
- Monitor query performance

### 2. API Optimization

- Implement data caching
- Use pagination for large datasets
- Optimize JSON serialization
- Monitor response times

### 3. Dashboard Optimization

- Adjust refresh rates based on needs
- Limit data points displayed
- Use efficient plotting libraries
- Implement client-side caching

### 4. System Resources

- Monitor CPU and memory usage
- Optimize file I/O operations
- Use efficient data structures
- Implement resource limits

## Security Considerations

### 1. Database Security

- Use strong passwords
- Limit database user permissions
- Enable SSL connections
- Regular security updates

### 2. API Security

- Implement authentication if needed
- Use HTTPS in production
- Validate input parameters
- Rate limiting

### 3. File System Security

- Secure file permissions
- Validate file types
- Scan for malware
- Backup important data

## Monitoring and Maintenance

### 1. System Monitoring

- Monitor process status
- Check log files regularly
- Monitor database performance
- Track system resources

### 2. Data Quality

- Validate incoming data
- Monitor data completeness
- Check for anomalies
- Regular data cleanup

### 3. Backup and Recovery

- Regular database backups
- Configuration file backups
- Test recovery procedures
- Document procedures

## Future Enhancements

### Planned Features

1. **Advanced Analytics**: Statistical analysis and trend detection
2. **Alert System**: Automated alerts for data anomalies
3. **Multi-user Support**: User authentication and role management
4. **Data Export**: Multiple export formats (CSV, NetCDF, etc.)
5. **Mobile Support**: Responsive design for mobile devices
6. **Real-time Collaboration**: Multi-user dashboard sharing

### Integration Opportunities

1. **External APIs**: Integration with weather and oceanographic services
2. **Machine Learning**: Predictive modeling and anomaly detection
3. **Cloud Deployment**: AWS, Azure, or Google Cloud integration
4. **IoT Integration**: Direct sensor data ingestion
5. **GIS Integration**: Advanced mapping and spatial analysis

---

For more detailed information about specific components, refer to the individual module documentation and the source code comments.
