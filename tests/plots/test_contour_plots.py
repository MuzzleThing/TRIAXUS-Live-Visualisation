#!/usr/bin/env python3
"""
Test contour plot functionality
"""

import sys
import os

# Add project root to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from triaxus.data import create_plot_test_data
from triaxus.visualizer import TriaxusVisualizer


def test_contour_plots():
    """Test contour plot functionality"""
    print("=" * 60)
    print("Testing Contour Plots")
    print("=" * 60)

    # Generate test data
    data = create_plot_test_data(hours=2.0)
    print(f"Generated {len(data)} data points for contour testing")

    # Initialize visualizer
    visualizer = TriaxusVisualizer()

    # Test different variables
    variables = ["tv290C", "sal00", "sbeox0Mm_L", "flECO-AFL", "ph"]

    for variable in variables:
        print(f"\nTesting {variable} contour plot...")
        try:
            # Create contour plot
            output_file = visualizer.create_contour_plot(
                data=data,
                variable=variable,
                title=f"{variable} Contour Test",
                output_file=f"tests/output/contour_{variable}.html",
            )

            print(f"  PASS: {variable} contour plot saved to {output_file}")

        except Exception as e:
            print(f"  FAIL: Error creating {variable} contour plot: {e}")

    print("\nContour plot testing completed!")
    return True


if __name__ == "__main__":
    print("TRIAXUS Contour Plot Test")
    print("=" * 50)

    try:
        test_contour_plots()
        print("\nSUCCESS: Contour plot tests completed successfully!")

    except Exception as e:
        print(f"ERROR: Error during testing: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
