#!/usr/bin/env python3
"""
Test plot functionality with different data qualities
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from triaxus.data import (
    create_plot_test_data,
    create_daily_plot_data,
    create_quick_plot_data,
)
from triaxus.visualizer import TriaxusVisualizer


def test_data_quality():
    """Test plot functionality with different data qualities"""
    print("=" * 60)
    print("Testing Data Quality Scenarios")
    print("=" * 60)

    # Initialize visualizer
    visualizer = TriaxusVisualizer()

    # Test scenarios
    scenarios = [
        ("Quick Data", create_quick_plot_data()),
        ("Standard Data", create_plot_test_data(hours=2.0)),
        ("Daily Data", create_daily_plot_data("2024-01-01")),
    ]

    for scenario_name, data in scenarios:
        print(f"\nTesting {scenario_name} ({len(data)} points)...")

        try:
            # Test time series plot
            output_file = visualizer.create_time_series_plot(
                data=data,
                variables=["tv290C"],
                title=f"Temperature Time Series - {scenario_name}",
                output_file=f"tests/output/data_quality_{scenario_name.lower().replace(' ', '_')}.html",
            )

            print(f"  PASS {scenario_name} time series plot saved to {output_file}")

        except Exception as e:
            print(f"  FAIL Error creating {scenario_name} time series plot: {e}")

    print("\nData quality testing completed!")
    return True


if __name__ == "__main__":
    print("TRIAXUS Data Quality Test")
    print("=" * 50)

    try:
        test_data_quality()
        print("\nSUCCESS Data quality tests completed successfully!")

    except Exception as e:
        print(f"FAIL Error during testing: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
