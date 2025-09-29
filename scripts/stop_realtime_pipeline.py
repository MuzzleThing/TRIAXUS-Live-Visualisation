#!/usr/bin/env python3
"""
Stop all TRIAXUS real-time data processing processes
"""

import subprocess
import sys
import signal
import os

def find_processes():
    """Find running TRIAXUS processes"""
    try:
        # Find processes by name
        result = subprocess.run(
            ["pgrep", "-f", "triaxus|simulation|realtime_api_server"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            pids = result.stdout.strip().split('\n')
            return [pid for pid in pids if pid]
        else:
            return []
    except FileNotFoundError:
        # Fallback for systems without pgrep
        try:
            result = subprocess.run(
                ["ps", "aux"],
                capture_output=True,
                text=True
            )
            lines = result.stdout.split('\n')
            pids = []
            for line in lines:
                if any(keyword in line for keyword in ['simulation.py', 'cnv_realtime_processor', 'realtime_api_server']):
                    parts = line.split()
                    if parts:
                        pids.append(parts[1])
            return pids
        except:
            return []

def stop_process(pid):
    """Stop a process by PID"""
    try:
        os.kill(int(pid), signal.SIGTERM)
        return True
    except (ProcessLookupError, ValueError):
        return False

def main():
    """Stop all TRIAXUS processes"""
    print("Stopping TRIAXUS real-time pipeline...")
    
    pids = find_processes()
    
    if not pids:
        print("No TRIAXUS processes found running.")
        return 0
    
    print(f"Found {len(pids)} processes to stop:")
    
    stopped = 0
    for pid in pids:
        try:
            # Get process info
            result = subprocess.run(
                ["ps", "-p", pid, "-o", "pid,cmd"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:
                    print(f"  Stopping PID {pid}: {lines[1]}")
                else:
                    print(f"  Stopping PID {pid}")
            else:
                print(f"  Stopping PID {pid}")
            
            if stop_process(pid):
                stopped += 1
            else:
                print(f"    Failed to stop PID {pid}")
        except Exception as e:
            print(f"    Error stopping PID {pid}: {e}")
    
    print(f"\nStopped {stopped} processes.")
    
    # Wait a moment and check for any remaining processes
    import time
    time.sleep(1)
    
    remaining = find_processes()
    if remaining:
        print(f"Warning: {len(remaining)} processes still running. You may need to stop them manually.")
        return 1
    else:
        print("All processes stopped successfully.")
        return 0

if __name__ == "__main__":
    sys.exit(main())
