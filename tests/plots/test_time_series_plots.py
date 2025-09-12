#!/usr/bin/env python3
"""
Test time series plot functionality
"""

import sys
import os

# Add project root to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from triaxus.data import create_plot_test_data
from triaxus.visualizer import TriaxusVisualizer


def test_time_series_plots():
    """Test time series plot functionality"""
    print("=" * 60)
    print("Testing Time Series Plots")
    print("=" * 60)

    # Generate test data
    data = create_plot_test_data(hours=2.0)
    print(f"Generated {len(data)} data points for time series testing")

    # Initialize visualizer
    visualizer = TriaxusVisualizer()

    # Test different variables
    variables = ["tv290C", "sal00", "sbeox0Mm_L", "flECO-AFL", "ph"]

    for variable in variables:
        print(f"\nTesting {variable} time series plot...")
        try:
            # Create time series plot
            output_file = visualizer.create_time_series_plot(
                data=data,
                variables=[variable],
                title=f"{variable} Time Series Test",
                output_file=f"tests/output/time_series_{variable}.html",
            )

            print(f"  PASS: {variable} time series plot saved to {output_file}")

        except Exception as e:
            print(f"  FAIL: Error creating {variable} time series plot: {e}")

    print("\nTime series plot testing completed!")
    return True


if __name__ == "__main__":
    print("TRIAXUS Time Series Plot Test")
    print("=" * 50)

    try:
        test_time_series_plots()
        print("\nSUCCESS: Time series plot tests completed successfully!")

    except Exception as e:
        print(f"ERROR: Error during testing: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
