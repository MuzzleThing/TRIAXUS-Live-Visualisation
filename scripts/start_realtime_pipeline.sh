#!/bin/bash

# TRIAXUS Visualization System - Real-time Pipeline Starter
# This script starts the complete real-time data processing pipeline

set -e  # Exit on any error

echo "=========================================="
echo "TRIAXUS Real-time Pipeline Starter"
echo "=========================================="

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "Project root: $PROJECT_ROOT"
cd "$PROJECT_ROOT"

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Check if real-time pipeline script exists
if [ ! -f "scripts/start_realtime_pipeline.py" ]; then
    echo "Error: start_realtime_pipeline.py not found!"
    echo "Please ensure the real-time pipeline script is available."
    exit 1
fi

# Start the real-time pipeline
echo "Starting real-time pipeline..."
echo "This will run in the background. Check logs/ directory for output."
echo "To stop the pipeline, use: ./scripts/stop_realtime_pipeline.sh"
echo ""

python scripts/start_realtime_pipeline.py &

# Store the PID for later reference
echo $! > realtime_pipeline.pid
echo "Real-time pipeline started with PID: $!"
echo "PID stored in realtime_pipeline.pid"
echo ""
echo "To monitor logs:"
echo "  tail -f logs/processor.log"
echo "  tail -f logs/api_server.log"
echo ""
echo "To check status:"
echo "  curl http://localhost:8080/api/status"
echo ""
echo "Dashboard available at: http://localhost:8080"
