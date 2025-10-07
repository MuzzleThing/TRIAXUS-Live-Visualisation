#!/bin/bash

# TRIAXUS Visualization System - Quick Demo Script
# This script runs a quick demonstration of the system capabilities

set -e  # Exit on any error

echo "=========================================="
echo "TRIAXUS Quick Demo"
echo "=========================================="

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "Project root: $PROJECT_ROOT"
cd "$PROJECT_ROOT"

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Clean environment first
echo "Cleaning environment..."
./scripts/cleanup_environment.sh

# Run a subset of tests to demonstrate functionality
echo "Running demonstration tests..."

echo ""
echo "1. Running unit tests for core functionality..."
python tests/run_tests.py --type unit --pattern "test_cnv_reader|test_data_archiver" -v

echo ""
echo "2. Running integration tests for file processing..."
python tests/run_tests.py --type integration --pattern "test_file_processing_pipeline" -v

echo ""
echo "3. Running visualization tests..."
python tests/run_tests.py --type unit --pattern "test_.*plots" -v

echo ""
echo "4. Checking system status..."
python -c "
import sys
sys.path.append('.')
from settings import settings
print(f'Configuration loaded: {settings is not None}')
print(f'Database enabled: {getattr(settings, \"database\", {}).get(\"enabled\", False)}')
print(f'Archive directory: {getattr(settings, \"archiving\", {}).get(\"directory\", \"archive\")}')
"

echo ""
echo "=========================================="
echo "Quick demo completed successfully!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Run full test suite: ./scripts/run_all_tests.sh"
echo "2. Start real-time pipeline: ./scripts/start_realtime_pipeline.sh"
echo "3. View dashboard at: http://localhost:8080"
echo "4. Stop pipeline: ./scripts/stop_realtime_pipeline.sh"
