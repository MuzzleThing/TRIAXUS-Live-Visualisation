#!/bin/bash

# TRIAXUS Visualization System - Environment Setup Script
# This script sets up the complete environment for TRIAXUS system

set -e  # Exit on any error

echo "=========================================="
echo "TRIAXUS Environment Setup"
echo "=========================================="

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "Project root: $PROJECT_ROOT"
cd "$PROJECT_ROOT"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
else
    echo "Virtual environment already exists"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Install additional test dependencies
echo "Installing test dependencies..."
pip install requests pytest pytest-timeout

# Create necessary directories
echo "Creating necessary directories..."
mkdir -p logs
mkdir -p archive
mkdir -p realtime_plots
mkdir -p data/processed
mkdir -p live_data_feed_simulation/output

# Set permissions
echo "Setting permissions..."
chmod +x scripts/*.sh

echo "=========================================="
echo "Environment setup complete!"
echo "=========================================="
echo ""
echo "To activate the environment in the future, run:"
echo "  source .venv/bin/activate"
echo ""
echo "To run tests:"
echo "  python tests/run_tests.py"
echo ""
echo "To start real-time processing:"
echo "  ./scripts/start_realtime_pipeline.sh"
echo ""
