#!/usr/bin/env python3
"""
Start the complete TRIAXUS real-time data processing pipeline
"""

import subprocess
import time
import sys
import os
import signal
import webbrowser
from pathlib import Path

# Project root
project_root = Path(__file__).parent.parent

# Add project root to Python path
import sys
sys.path.insert(0, str(project_root))

def start_process(command, cwd=None, background=True):
    """Start a process and return the process object"""
    print(f"Starting: {' '.join(command)}")
    if background:
        return subprocess.Popen(command, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        return subprocess.Popen(command, cwd=cwd)

def check_database():
    """Check if database is accessible"""
    try:
        # Change to project root directory
        os.chdir(project_root)
        
        from triaxus.data.database_source import DatabaseDataSource
        db = DatabaseDataSource()
        data = db.load_data(limit=1)
        print("✓ Database connection OK")
        return True
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False

def main():
    """Start the complete real-time pipeline"""
    print("=" * 60)
    print("TRIAXUS Real-time Data Processing Pipeline")
    print("=" * 60)
    
    # Check database
    if not check_database():
        print("Please ensure PostgreSQL is running and configured")
        return 1
    
    processes = []
    
    try:
        # Step 1: Start data simulation
        print("\n1. Starting data simulation...")
        sim_cmd = [
            sys.executable, "live_data_feed_simulation/simulation.py",
            "--file", "testdataQC/live_realtime_demo.cnv",
            "--hz", "1.0",
            "--live-every", "5",
            "--start-city", "sydney",
            "--end-city", "melbourne",
            "--speed-knots", "15",
            "--noninteractive"
        ]
        sim_process = start_process(sim_cmd, cwd=project_root)
        processes.append(("Data Simulation", sim_process))
        time.sleep(2)
        
        # Step 2: Start real-time processor
        print("\n2. Starting real-time processor...")
        proc_cmd = [
            sys.executable, "-m", "triaxus.data.cnv_realtime_processor",
            "--watch",
            "--config", "configs/realtime_test.yaml",
            "--verbose"
        ]
        proc_process = start_process(proc_cmd, cwd=project_root)
        processes.append(("Real-time Processor", proc_process))
        time.sleep(3)
        
        # Step 3: Start API server
        print("\n3. Starting API server...")
        api_cmd = [sys.executable, "realtime/realtime_api_server.py", "8080"]
        api_process = start_process(api_cmd, cwd=project_root)
        processes.append(("API Server", api_process))
        time.sleep(2)
        
        # Step 4: Open dashboard
        print("\n4. Opening dashboard...")
        dashboard_url = "http://localhost:8080"
        webbrowser.open(dashboard_url)
        
        print("\n" + "=" * 60)
        print("Pipeline started successfully!")
        print("=" * 60)
        print(f"Dashboard: {dashboard_url}")
        print("Data simulation: Generating CNV files")
        print("Real-time processor: Monitoring and processing files")
        print("API server: Serving data to dashboard")
        print("\nPress Ctrl+C to stop all processes")
        print("=" * 60)
        
        # Keep running until interrupted
        while True:
            time.sleep(1)
            
            # Check if any process has died
            for name, process in processes:
                if process.poll() is not None:
                    print(f"\n⚠️  {name} has stopped unexpectedly")
                    return_code = process.returncode
                    stdout, stderr = process.communicate()
                    if stderr:
                        print(f"Error: {stderr.decode()}")
    
    except KeyboardInterrupt:
        print("\n\nStopping pipeline...")
        
        # Stop all processes
        for name, process in processes:
            print(f"Stopping {name}...")
            try:
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                print(f"Force killing {name}...")
                process.kill()
        
        print("Pipeline stopped.")
        return 0
    
    except Exception as e:
        print(f"\nError starting pipeline: {e}")
        
        # Clean up processes
        for name, process in processes:
            try:
                process.terminate()
            except:
                pass
        
        return 1

if __name__ == "__main__":
    sys.exit(main())
