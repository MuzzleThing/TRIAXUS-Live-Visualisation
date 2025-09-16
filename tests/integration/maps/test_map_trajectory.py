#!/usr/bin/env python3
"""
Test map trajectory plotting functionality
"""

import sys
import os

# Add project root to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from triaxus.data import create_map_trajectory_data
from triaxus.visualizer import TriaxusVisualizer


def test_map_trajectory():
    """Test map trajectory plotting with oceanographic data"""
    print("Testing map trajectory plotting...")

    # Use oceanographic data from database (preferred) or generate new data
    from triaxus.data.database_source import DatabaseDataSource
    
    db = DatabaseDataSource()
    if db.is_available():
        data = db.load_data(limit=20)
        print(f"Retrieved {len(data)} oceanographic data points from database")
    else:
        print("Database not available, generating new trajectory data")
        data = create_map_trajectory_data(region="australia", hours=2.0)
    
    print(f"Using {len(data)} trajectory points")
    print(
        f"Latitude range: {data['latitude'].min():.4f} to {data['latitude'].max():.4f}"
    )
    print(
        f"Longitude range: {data['longitude'].min():.4f} to {data['longitude'].max():.4f}"
    )

    # Initialize visualizer
    visualizer = TriaxusVisualizer()
    print("Visualizer initialized")

    # Create map plot
    output_file = visualizer.create_map_plot(
        data=data,
        title="TRIAXUS Trajectory - Oceanographic Survey",
        output_file="tests/output/map_trajectory_australia.html",
    )

    print(f"PASS Map trajectory plot created: {output_file}")
    return True


def test_map_trajectory_extended():
    """Test map trajectory plotting with extended oceanographic data"""
    print("\nTesting extended oceanographic trajectory...")

    # Use oceanographic data from database
    from triaxus.data.database_source import DatabaseDataSource
    
    db = DatabaseDataSource()
    if not db.is_available():
        print("Database not available, using generated data")
        data = create_map_trajectory_data(region="australia", hours=3.0)
    else:
        data = db.load_data(limit=20)
        print(f"Retrieved {len(data)} oceanographic data points from database")
    
    print(f"Generated {len(data)} trajectory points")
    print(
        f"Latitude range: {data['latitude'].min():.4f} to {data['latitude'].max():.4f}"
    )
    print(
        f"Longitude range: {data['longitude'].min():.4f} to {data['longitude'].max():.4f}"
    )

    # Initialize visualizer
    visualizer = TriaxusVisualizer()

    # Create map plot
    output_file = visualizer.create_map_plot(
        data=data,
        title="TRIAXUS Trajectory - Extended Oceanographic Survey",
        output_file="tests/output/map_trajectory_extended_australia.html",
    )

    print(f"PASS Extended oceanographic trajectory plot created: {output_file}")
    return True


def test_map_trajectory_different_styles():
    """Test map trajectory with different map styles using oceanographic data"""
    print("\nTesting map trajectory with different styles...")

    # Use oceanographic data from database
    from triaxus.data.database_source import DatabaseDataSource
    
    db = DatabaseDataSource()
    if not db.is_available():
        print("Database not available, using generated data")
        data = create_map_trajectory_data(region="australia", hours=1.0)
    else:
        data = db.load_data(limit=20)
        print(f"Retrieved {len(data)} oceanographic data points from database")

    # Initialize visualizer
    visualizer = TriaxusVisualizer()

    # Test different map styles
    styles = ["light", "dark", "satellite", "streets"]

    for style in styles:
        output_file = visualizer.create_map_plot(
            data=data,
            title=f"TRIAXUS Trajectory - Oceanographic Survey ({style.title()} Style)",
            map_style=style,
            output_file=f"tests/output/map_trajectory_{style}.html",
        )
        print(f"PASS {style.title()} style trajectory plot created: {output_file}")

    return True


if __name__ == "__main__":
    print("TRIAXUS Map Trajectory Test Suite")
    print("=" * 50)

    try:
        # Test Australian waters trajectory
        test_map_trajectory()

        # Test extended Australian waters trajectory
        test_map_trajectory_extended()

        # Test different map styles
        test_map_trajectory_different_styles()

        print("\nSUCCESS All map trajectory tests completed successfully!")
        print("Generated trajectory plots are saved in tests/output/ directory")

    except Exception as e:
        print(f"FAIL Error during testing: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
