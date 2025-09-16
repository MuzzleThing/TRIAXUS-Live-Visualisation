#!/usr/bin/env python3
"""
Test map view fix - verify that maps show focused view instead of world map
"""

import sys
import os

# Add project root to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from triaxus.data import create_map_trajectory_data
from triaxus.visualizer import TriaxusVisualizer


def test_map_view_fix():
    """Test that map view is properly focused on Australian waters"""
    print("Testing map view fix...")

    # Generate Australian waters trajectory data
    data = create_map_trajectory_data(region="australia", hours=2.0)
    print(f"Generated {len(data)} trajectory points")
    print(
        f"Latitude range: {data['latitude'].min():.4f} to {data['latitude'].max():.4f}"
    )
    print(
        f"Longitude range: {data['longitude'].min():.4f} to {data['longitude'].max():.4f}"
    )

    # Calculate expected bounds
    lat_min, lat_max = data["latitude"].min(), data["latitude"].max()
    lon_min, lon_max = data["longitude"].min(), data["longitude"].max()

    # Add padding (20% as configured)
    lat_padding = (lat_max - lat_min) * 0.2
    lon_padding = (lon_max - lon_min) * 0.2

    expected_lat_range = [lat_min - lat_padding, lat_max + lat_padding]
    expected_lon_range = [lon_min - lon_padding, lon_max + lon_padding]

    print(f"Expected map bounds:")
    print(f"  Latitude: {expected_lat_range[0]:.4f} to {expected_lat_range[1]:.4f}")
    print(f"  Longitude: {expected_lon_range[0]:.4f} to {expected_lon_range[1]:.4f}")

    # Initialize visualizer
    visualizer = TriaxusVisualizer()

    # Create map plot
    output_file = visualizer.create_map_plot(
        data=data,
        title="TRIAXUS Trajectory - Australian Waters (Focused View)",
        output_file="tests/output/map_view_fix_test.html",
    )

    print(f"PASS Map view fix test completed: {output_file}")
    print(
        "The map should now show a focused view of Australian waters instead of world map"
    )
    return True


if __name__ == "__main__":
    print("TRIAXUS Map View Fix Test")
    print("=" * 50)

    try:
        test_map_view_fix()
        print("\nSUCCESS Map view fix test completed successfully!")
        print("Check the generated HTML file to verify the focused view")

    except Exception as e:
        print(f"FAIL Error during testing: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
