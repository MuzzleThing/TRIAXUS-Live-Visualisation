#!/bin/bash

# TRIAXUS Visualization System - Environment Cleanup Script
# This script cleans up all temporary files, logs, and test artifacts

set -e  # Exit on any error

echo "=========================================="
echo "TRIAXUS Environment Cleanup"
echo "=========================================="

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "Project root: $PROJECT_ROOT"
cd "$PROJECT_ROOT"

# Clean up log files
echo "Cleaning up log files..."
rm -f logs/*.log 2>/dev/null || true
echo "✓ Log files cleaned"

# Clean up Python cache
echo "Cleaning up Python cache..."
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
echo "✓ Python cache cleaned"

# Clean up test artifacts
echo "Cleaning up test artifacts..."
rm -rf tests/output/*.html 2>/dev/null || true
rm -rf .pytest_cache 2>/dev/null || true
echo "✓ Test artifacts cleaned"

# Clean up real-time data
echo "Cleaning up real-time data..."
rm -rf realtime_plots/* 2>/dev/null || true
rm -rf live_data_feed_simulation/output/* 2>/dev/null || true
rm -rf data/processed/* 2>/dev/null || true
echo "✓ Real-time data cleaned"

# Clean up archive files
echo "Cleaning up archive files..."
rm -rf archive/*.csv* 2>/dev/null || true
rm -rf archive/*.json 2>/dev/null || true
echo "✓ Archive files cleaned"

echo "=========================================="
echo "Environment cleanup complete!"
echo "=========================================="
