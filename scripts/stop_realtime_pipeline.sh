#!/bin/bash

# TRIAXUS Visualization System - Real-time Pipeline Stopper
# This script stops the real-time data processing pipeline

set -e  # Exit on any error

echo "=========================================="
echo "TRIAXUS Real-time Pipeline Stopper"
echo "=========================================="

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "Project root: $PROJECT_ROOT"
cd "$PROJECT_ROOT"

# Check if PID file exists
if [ -f "realtime_pipeline.pid" ]; then
    PID=$(cat realtime_pipeline.pid)
    echo "Found PID file with PID: $PID"
    
    # Check if process is still running
    if ps -p $PID > /dev/null 2>&1; then
        echo "Stopping real-time pipeline (PID: $PID)..."
        kill $PID
        
        # Wait for graceful shutdown with multiple checks
        echo "Waiting for graceful shutdown..."
        for i in {1..10}; do
            if ! ps -p $PID > /dev/null 2>&1; then
                echo "[OK] Process stopped gracefully"
                break
            fi
            echo "  Attempt $i/10: Process still running, waiting..."
            sleep 1
        done
        
        # Final check - force kill if still running
        if ps -p $PID > /dev/null 2>&1; then
            echo "[WARN] Process did not stop gracefully, force killing..."
            kill -9 $PID
            sleep 1
            
            # Verify force kill worked
            if ps -p $PID > /dev/null 2>&1; then
                echo "[ERROR] Failed to force kill process $PID"
            else
                echo "[OK] Process force killed successfully"
            fi
        fi
    else
        echo "Process with PID $PID is not running"
    fi
    
    # Remove PID file
    rm -f realtime_pipeline.pid
    echo "PID file removed"
else
    echo "No PID file found. Attempting to stop any running Python processes..."
    
    # Try to find and stop Python processes related to real-time pipeline
    PIDS=$(pgrep -f "start_realtime_pipeline.py\|realtime_api_server.py\|cnv_realtime_processor.py" 2>/dev/null || true)
    
    if [ -n "$PIDS" ]; then
        echo "Found running real-time processes: $PIDS"
        for pid in $PIDS; do
            echo "Stopping process $pid..."
            kill $pid 2>/dev/null || true
            
            # Wait for graceful shutdown
            for i in {1..5}; do
                if ! ps -p $pid > /dev/null 2>&1; then
                    echo "  [OK] Process $pid stopped gracefully"
                    break
                fi
                echo "  Attempt $i/5: Process $pid still running, waiting..."
                sleep 1
            done
            
            # Force kill if still running
            if ps -p $pid > /dev/null 2>&1; then
                echo "  [WARN] Force killing process $pid..."
                kill -9 $pid 2>/dev/null || true
                sleep 1
                
                if ps -p $pid > /dev/null 2>&1; then
                    echo "  [ERROR] Failed to kill process $pid"
                else
                    echo "  [OK] Process $pid force killed"
                fi
            fi
        done
        echo "Real-time processes cleanup complete"
    else
        echo "No running real-time processes found"
    fi
fi

# Also try to stop any processes using port 8080
echo "Checking for processes using port 8080..."
PORT_PIDS=$(lsof -ti:8080 2>/dev/null || true)
if [ -n "$PORT_PIDS" ]; then
    echo "Found processes using port 8080: $PORT_PIDS"
    for pid in $PORT_PIDS; do
        echo "Stopping process $pid using port 8080..."
        kill $pid 2>/dev/null || true
        
        # Wait for graceful shutdown
        for i in {1..3}; do
            if ! ps -p $pid > /dev/null 2>&1; then
                echo "  [OK] Process $pid using port 8080 stopped"
                break
            fi
            echo "  Attempt $i/3: Process $pid still using port 8080..."
            sleep 1
        done
        
        # Force kill if still running
        if ps -p $pid > /dev/null 2>&1; then
            echo "  [WARN] Force killing process $pid using port 8080..."
            kill -9 $pid 2>/dev/null || true
            sleep 1
            
            if ps -p $pid > /dev/null 2>&1; then
                echo "  [ERROR] Failed to kill process $pid using port 8080"
            else
                echo "  [OK] Process $pid using port 8080 force killed"
            fi
        fi
    done
else
    echo "No processes using port 8080"
fi

# Final verification - check if any TRIAXUS processes are still running
echo ""
echo "=== Final verification ==="
REMAINING_PROCESSES=$(ps aux | grep -E "(start_realtime_pipeline|realtime_api_server|cnv_realtime_processor)" | grep -v grep | grep -v "stop_realtime_pipeline" || true)
REMAINING_PORTS=$(lsof -ti:8080 2>/dev/null || true)

if [ -n "$REMAINING_PROCESSES" ]; then
    echo "[WARN] Some TRIAXUS processes may still be running:"
    echo "$REMAINING_PROCESSES"
    echo ""
    echo "Attempting to force kill remaining processes..."
    
    # Extract PIDs and force kill them
    echo "$REMAINING_PROCESSES" | awk '{print $2}' | while read pid; do
        if [ -n "$pid" ] && ps -p $pid > /dev/null 2>&1; then
            echo "  Force killing PID $pid..."
            kill -9 $pid 2>/dev/null || true
            sleep 1
            if ps -p $pid > /dev/null 2>&1; then
                echo "  [ERROR] Failed to kill PID $pid"
            else
                echo "  [OK] PID $pid killed"
            fi
        fi
    done
    
    # Final check
    sleep 2
    FINAL_CHECK=$(ps aux | grep -E "(start_realtime_pipeline|realtime_api_server|cnv_realtime_processor)" | grep -v grep | grep -v "stop_realtime_pipeline" || true)
    if [ -n "$FINAL_CHECK" ]; then
        echo "[WARN] Some processes may still be running after force kill"
        echo "$FINAL_CHECK"
    else
        echo "[OK] All TRIAXUS processes successfully terminated"
    fi
else
    echo "[OK] No TRIAXUS processes found running"
fi

if [ -n "$REMAINING_PORTS" ]; then
    echo "[WARN] Port 8080 is still in use by processes: $REMAINING_PORTS"
else
    echo "[OK] Port 8080 is free"
fi

echo "=========================================="
echo "Real-time pipeline cleanup complete!"
echo "=========================================="
