#!/bin/bash

# TRIAXUS Visualization System - Integration Tests Runner
# This script runs only integration tests

set -e  # Exit on any error

echo "=========================================="
echo "TRIAXUS Integration Tests"
echo "=========================================="

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "Project root: $PROJECT_ROOT"
cd "$PROJECT_ROOT"

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Run integration tests
echo "Running integration tests..."
python tests/run_tests.py --type integration -v

echo "=========================================="
echo "Integration tests completed successfully!"
echo "=========================================="
