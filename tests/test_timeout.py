#!/usr/bin/env python3
"""
Test with timeout to prevent infinite loops
"""

import sys
import os
import signal
import time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from triaxus.data import create_plot_test_data
from triaxus.visualizer import TriaxusVisualizer

class TimeoutError(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutError("Operation timed out")

def test_with_timeout():
    """Test with 30 second timeout"""
    print("Testing with 30 second timeout...")
    
    # Set up timeout
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(30)  # 30 second timeout
    
    try:
        # Generate data
        data = create_plot_test_data(hours=0.1)
        print(f"Generated {len(data)} data points")
        
        # Initialize visualizer
        visualizer = TriaxusVisualizer()
        print("Visualizer initialized")
        
        # Test the problematic method
        print("Testing create_time_series_plot...")
        start_time = time.time()
        
        output_file = visualizer.create_time_series_plot(
            data=data,
            variables=['tv290C'],
            title="Timeout Test Plot",
            output_file="tests/output/timeout_test.html"
        )
        
        end_time = time.time()
        print(f"PASS Plot created successfully in {end_time - start_time:.2f} seconds")
        print(f"Output file: {output_file}")
        
        # Cancel timeout
        signal.alarm(0)
        return True
        
    except TimeoutError:
        print("FAIL Test timed out after 30 seconds - infinite loop detected!")
        signal.alarm(0)
        return False
    except Exception as e:
        print(f"FAIL Error: {e}")
        signal.alarm(0)
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_with_timeout()
    if success:
        print("\nPASS Timeout test passed!")
    else:
        print("\nFAIL Timeout test failed!")
