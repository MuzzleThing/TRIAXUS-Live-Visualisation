#!/bin/bash

# TRIAXUS Visualization System - Complete Test Suite Runner
# This script runs the complete test suite with proper environment setup

set -e  # Exit on any error

echo "=========================================="
echo "TRIAXUS Complete Test Suite"
echo "=========================================="

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "Project root: $PROJECT_ROOT"
cd "$PROJECT_ROOT"

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Clean up previous test artifacts
echo "Cleaning up previous test artifacts..."
rm -f logs/*.log 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# Run the complete test suite
echo "Running complete test suite..."
python tests/run_tests.py -v

echo "=========================================="
echo "Test suite completed successfully!"
echo "=========================================="
