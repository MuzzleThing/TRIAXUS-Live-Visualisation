# TRIAXUS Visualization System - Standalone Usage Guide

This guide provides complete instructions for running the TRIAXUS system without Cursor IDE, using only the terminal.

## Prerequisites

- Python 3.8 or higher
- Git (for cloning the repository)
- PostgreSQL (optional, for database features)

## Quick Start

### 1. Initial Setup (One-time)

```bash
# Navigate to the project directory
cd "/Users/steven/TRIAXUS visualisation project/triaxus-plotter"

# Make all scripts executable
chmod +x scripts/*.sh

# Run the environment setup script
./scripts/setup_environment.sh
```

### 2. Run Tests

```bash
# Run all tests
./scripts/run_all_tests.sh

# Or run specific test types:
./scripts/run_unit_tests.sh
./scripts/run_integration_tests.sh
./scripts/run_e2e_tests.sh
```

### 3. Quick Demo

```bash
# Run a quick demonstration
./scripts/quick_demo.sh
```

### 4. Real-time Processing

```bash
# Start real-time pipeline
./scripts/start_realtime_pipeline.sh

# Check status
curl http://localhost:8080/api/status

# View dashboard
open http://localhost:8080

# Stop pipeline when done
./scripts/stop_realtime_pipeline.sh
```

### 5. Cleanup

```bash
# Clean up all temporary files and logs
./scripts/cleanup_environment.sh
```

## Available Scripts

| Script | Purpose |
|--------|---------|
| `setup_environment.sh` | Initial environment setup (one-time) |
| `run_all_tests.sh` | Run complete test suite |
| `run_unit_tests.sh` | Run only unit tests |
| `run_integration_tests.sh` | Run only integration tests |
| `run_e2e_tests.sh` | Run only end-to-end tests |
| `quick_demo.sh` | Run quick demonstration |
| `start_realtime_pipeline.sh` | Start real-time processing |
| `stop_realtime_pipeline.sh` | Stop real-time processing |
| `cleanup_environment.sh` | Clean up temporary files |

## Manual Commands

If you prefer to run commands manually:

### Environment Activation

```bash
# Activate virtual environment
source .venv/bin/activate

# Deactivate when done
deactivate
```

### Test Execution

```bash
# Run all tests
python tests/run_tests.py -v

# Run specific test types
python tests/run_tests.py --type unit -v
python tests/run_tests.py --type integration -v
python tests/run_tests.py --type e2e -v

# Run specific test patterns
python tests/run_tests.py --pattern "test_cnv_reader" -v
python tests/run_tests.py --pattern "test_data_archiver" -v
```

### Real-time Processing

```bash
# Start pipeline (background)
python scripts/start_realtime_pipeline.py &

# Check logs
tail -f logs/processor.log
tail -f logs/api_server.log

# Test API endpoints
curl http://localhost:8080/api/status
curl http://localhost:8080/api/latest_data

# Stop pipeline (find and kill the process)
ps aux | grep start_realtime_pipeline
kill <PID>
```

## Configuration

The system uses configuration files in the `configs/` directory:

- `configs/default.yaml` - Main configuration
- `configs/realtime_test.yaml` - Real-time processing settings
- `configs/custom.yaml` - Custom overrides (optional)

## Logs and Output

- **Logs**: `logs/` directory
- **Archive files**: `archive/` directory
- **Real-time plots**: `realtime_plots/` directory
- **Test outputs**: `tests/output/` directory

## Troubleshooting

### Common Issues

1. **Permission denied**: Make scripts executable with `chmod +x scripts/*.sh`
2. **Module not found**: Ensure virtual environment is activated
3. **Port 8080 in use**: Stop existing processes or change port in config
4. **Database connection issues**: Check PostgreSQL is running and configured

### Debug Commands

```bash
# Check virtual environment
which python
pip list

# Check processes
ps aux | grep python
lsof -i :8080

# Check logs
ls -la logs/
tail -f logs/processor.log
```

## Complete Workflow Example

```bash
# 1. Setup (first time only)
cd "/Users/steven/TRIAXUS visualisation project/triaxus-plotter"
chmod +x scripts/*.sh
./scripts/setup_environment.sh

# 2. Run tests
./scripts/run_all_tests.sh

# 3. Start real-time processing
./scripts/start_realtime_pipeline.sh

# 4. Monitor (in another terminal)
tail -f logs/processor.log

# 5. Test API
curl http://localhost:8080/api/status

# 6. View dashboard
open http://localhost:8080

# 7. Stop when done
./scripts/stop_realtime_pipeline.sh

# 8. Cleanup
./scripts/cleanup_environment.sh
```

## Support

For issues or questions:
1. Check the logs in `logs/` directory
2. Verify configuration in `configs/` directory
3. Ensure all dependencies are installed
4. Check PostgreSQL is running (if using database features)
