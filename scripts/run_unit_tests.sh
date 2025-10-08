#!/bin/bash

# TRIAXUS Visualization System - Unit Tests Runner
# This script runs only unit tests

set -e  # Exit on any error

echo "=========================================="
echo "TRIAXUS Unit Tests"
echo "=========================================="

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "Project root: $PROJECT_ROOT"
cd "$PROJECT_ROOT"

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Run unit tests
echo "Running unit tests..."
python tests/run_tests.py --type unit -v

echo "=========================================="
echo "Unit tests completed successfully!"
echo "=========================================="
