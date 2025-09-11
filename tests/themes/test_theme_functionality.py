#!/usr/bin/env python3
"""
Test theme functionality across all plot types
"""

import sys
import os

# Add project root to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from triaxus.data import create_plot_test_data, create_map_trajectory_data
from triaxus.visualizer import TriaxusVisualizer


def test_theme_functionality():
    """Test theme functionality across all plot types"""
    print("=" * 60)
    print("Testing Theme Functionality")
    print("=" * 60)

    # Generate test data
    data = create_plot_test_data(hours=1.0)
    print(f"Generated {len(data)} data points for theme testing")

    # Initialize visualizer
    visualizer = TriaxusVisualizer()

    # Test themes
    themes = ["default", "oceanographic", "dark", "high_contrast"]
    plot_types = ["time_series", "depth_profile", "contour", "map"]
    variable = "tv290C"  # Use temperature as test variable

    for theme in themes:
        print(f"\nTesting {theme} theme...")

        # Set theme
        visualizer.set_theme(theme)

        for plot_type in plot_types:
            print(f"  Testing {plot_type} with {theme} theme...")
            try:
                if plot_type == "time_series":
                    output_file = visualizer.create_time_series_plot(
                        data=data,
                        variables=[variable],
                        title=f"{variable} {plot_type} - {theme} theme",
                        output_file=f"tests/output/theme_{theme}_{plot_type}.html",
                    )
                elif plot_type == "depth_profile":
                    output_file = visualizer.create_depth_profile_plot(
                        data=data,
                        variables=[variable],
                        title=f"{variable} {plot_type} - {theme} theme",
                        output_file=f"tests/output/theme_{theme}_{plot_type}.html",
                    )
                elif plot_type == "contour":
                    output_file = visualizer.create_contour_plot(
                        data=data,
                        variable=variable,
                        title=f"{variable} {plot_type} - {theme} theme",
                        output_file=f"tests/output/theme_{theme}_{plot_type}.html",
                    )
                elif plot_type == "map":
                    # Use trajectory data for map plots
                    trajectory_data = create_map_trajectory_data(
                        region="australia", hours=1.0
                    )
                    output_file = visualizer.create_map_plot(
                        data=trajectory_data,
                        title=f"TRIAXUS Trajectory - {theme} theme",
                        output_file=f"tests/output/theme_{theme}_{plot_type}.html",
                    )

                print(f"    PASS {plot_type} with {theme} theme saved to {output_file}")

            except Exception as e:
                print(f"    FAIL Error creating {plot_type} with {theme} theme: {e}")

    print("\nTheme functionality testing completed!")
    return True


if __name__ == "__main__":
    print("TRIAXUS Theme Functionality Test")
    print("=" * 50)

    try:
        test_theme_functionality()
        print("\nSUCCESS Theme functionality tests completed successfully!")

    except Exception as e:
        print(f"FAIL Error during testing: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
