# TRIAXUS Real-time Data Processing - Quick Start Guide

This guide provides quick steps to get the TRIAXUS real-time oceanographic data processing and visualization system running.

## Prerequisites

- Python 3.8+
- PostgreSQL database
- Required Python packages (see requirements.txt)

## Quick Start (5 minutes)

### 1. Start the Complete Pipeline

```bash
# Start all components with one command
python scripts/start_realtime_pipeline.py
```

This will:
- Start data simulation
- Start real-time CNV processor
- Start API server
- Open the web dashboard

### 2. Access the Dashboard

Open your browser and go to: **http://localhost:8080**

### 3. Stop the Pipeline

```bash
# Stop all components
python scripts/stop_realtime_pipeline.py
```

## Manual Component Control

### Start Individual Components

```bash
# 1. Start data simulation (generates CNV files)
python live_data_feed_simulation/simulation.py

# 2. Start real-time processor (processes CNV files)
python -m triaxus.data.cnv_realtime_processor --watch

# 3. Start API server (serves web dashboard)
python realtime/realtime_api_server.py
```

### Stop Individual Components

```bash
# Stop all processes
pkill -f "simulation.py"
pkill -f "cnv_realtime_processor"
pkill -f "realtime_api_server.py"
```

## Dashboard Features

### Controls

- **Refresh Rate**: 0.5s, 1s, 2s, 5s, 10s, 30s, 1min, 5min, 10min, 15min, 30min, 1hour, or Manual (default: 1min)
- **Time Range**: 5m, 15m, 30m, 1h, 6h, 12h, 24h, 3d, 7d, 30d, or All Data (default: 1h)
- **Plot Type**: All, Time Series, Profile, or Map
- **Map Zoom**: 6 (wide) to 20 (detail)
- **Manual Refresh**: Click to update immediately

### Visualizations

1. **Temperature vs Time**: Real-time temperature trends
2. **Salinity vs Time**: Real-time salinity changes
3. **Oxygen vs Time**: Real-time oxygen levels
4. **Depth Profile**: Temperature vs depth relationship
5. **Oceanographic Map**: Trajectory and position tracking

## Configuration

### Basic Configuration

Edit `configs/realtime_test.yaml`:

```yaml
cnv_processing:
  source_directory: "testdataQC"
  
  realtime:
    enabled: true
    interval_seconds: 60  # Check for new files every 60 seconds
    plot_after_ingest: true
    plot_output_dir: "tests/output/realtime_plots"
    file_patterns:
      - "live_*.cnv"      # Only process live generated files
    min_age_seconds: 0.1  # Wait 0.1 seconds before processing files
    state_file: ".runtime/cnv_seen_realtime.json"
```

### Custom Refresh Rates

The dashboard supports these refresh intervals:
- **0.5s**: High-frequency monitoring
- **1s**: Fast updates
- **2s**: Quick updates
- **5s**: Standard monitoring
- **10s**: Slow updates
- **30s**: Low-frequency monitoring
- **1min**: Long-term monitoring (default)
- **5min**: Very slow updates
- **10min**: Extended monitoring
- **15min**: Long-term monitoring
- **30min**: Very long-term monitoring
- **1hour**: Maximum interval
- **Manual**: On-demand only

## Troubleshooting

### Common Issues

#### 1. Port Already in Use
```bash
# Kill existing processes
python scripts/stop_realtime_pipeline.py
# Or use a different port
python realtime/realtime_api_server.py 8081
```

#### 2. Database Connection Failed
```bash
# Check if PostgreSQL is running
pg_ctl status
# Or start it
pg_ctl start
```

#### 3. No Data Showing
- Check if data simulation is running
- Verify database has data
- Check API server logs
- Try manual refresh
- Delete state file `.runtime/cnv_seen_realtime.json` to force reprocessing

#### 4. Dashboard Not Loading
- Check if API server is running
- Verify port 8080 is accessible
- Check browser console for errors
- Try different browser

### Log Files

- **API Server**: Console output
- **Batch Processor**: `cnv_batch_processing.log`
- **Real-time Processor**: `processor.log` or `processor_debug.log`
- **Watcher**: `logs/cnv_watcher.log`

## Advanced Usage

### Daemon Mode

Run components as background services:

```bash
# Start as daemon
python -m triaxus.services.cnv_watcher start

# Check status
python -m triaxus.services.cnv_watcher status

# Stop daemon
python -m triaxus.services.cnv_watcher stop
```

### API Access

Access data programmatically:

```bash
# Get latest data
curl "http://localhost:8080/api/latest_data?limit=10"

# Check system status
curl "http://localhost:8080/api/status"
```

### Custom Data Sources

To use your own CNV files:

1. Place CNV files in the configured source directory
2. Update `file_patterns` in configuration
3. Start the real-time processor
4. Data will be automatically processed and stored

## Performance Tips

### For High-Frequency Monitoring
- Use 0.5s-5s refresh rates
- Limit data points to 100-500
- Monitor system resources

### For Long-term Monitoring
- Use 30s-5min refresh rates
- Enable data archiving
- Use manual refresh for analysis

### For Development/Testing
- Use manual refresh mode
- Check logs frequently
- Test with small datasets

## Next Steps

1. **Explore the Dashboard**: Try different refresh rates and plot types
2. **Check the Logs**: Monitor system behavior
3. **Customize Configuration**: Adjust settings for your needs
4. **Read Full Documentation**: See `REALTIME_DATA_PROCESSING.md`
5. **Join the Community**: Get help and share experiences

## Support

- **Documentation**: `docs/REALTIME_DATA_PROCESSING.md`
- **Configuration**: `configs/realtime_test.yaml`
- **Logs**: `logs/` directory
- **Source Code**: Individual module files

---
