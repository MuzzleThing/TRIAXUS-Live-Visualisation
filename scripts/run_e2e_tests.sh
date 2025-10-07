#!/bin/bash

# TRIAXUS Visualization System - End-to-End Tests Runner
# This script runs only end-to-end tests

set -e  # Exit on any error

echo "=========================================="
echo "TRIAXUS End-to-End Tests"
echo "=========================================="

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "Project root: $PROJECT_ROOT"
cd "$PROJECT_ROOT"

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Run end-to-end tests
echo "Running end-to-end tests..."
python tests/run_tests.py --type e2e -v

echo "=========================================="
echo "End-to-end tests completed successfully!"
echo "=========================================="
