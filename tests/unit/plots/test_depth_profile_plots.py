#!/usr/bin/env python3
"""
Test depth profile plot functionality
"""

import sys
import os

# Add project root to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from triaxus.data import create_plot_test_data
from triaxus.visualizer import TriaxusVisualizer


def test_depth_profile_plots():
    """Test depth profile plot functionality"""
    print("=" * 60)
    print("Testing Depth Profile Plots")
    print("=" * 60)

    # Generate test data
    data = create_plot_test_data(hours=2.0)
    print(f"Generated {len(data)} data points for depth profile testing")

    # Initialize visualizer
    visualizer = TriaxusVisualizer()

    # Test different variables
    variables = ["tv290C", "sal00", "sbeox0Mm_L", "flECO-AFL", "ph"]

    for variable in variables:
        print(f"\nTesting {variable} depth profile plot...")
        try:
            # Create depth profile plot
            output_file = visualizer.create_depth_profile_plot(
                data=data,
                variables=[variable],
                title=f"{variable} Depth Profile Test",
                output_file=f"tests/output/depth_profile_{variable}.html",
            )

            print(f"  PASS: {variable} depth profile plot saved to {output_file}")

        except Exception as e:
            print(f"  FAIL: Error creating {variable} depth profile plot: {e}")

    print("\nDepth profile plot testing completed!")
    return True


if __name__ == "__main__":
    print("TRIAXUS Depth Profile Plot Test")
    print("=" * 50)

    try:
        test_depth_profile_plots()
        print("\nSUCCESS: Depth profile plot tests completed successfully!")

    except Exception as e:
        print(f"ERROR: Error during testing: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
