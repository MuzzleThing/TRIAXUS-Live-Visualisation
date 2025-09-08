#!/usr/bin/env python3
"""
Test map trajectory plotting functionality
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from triaxus.data import create_map_trajectory_data
from triaxus.visualizer import TriaxusVisualizer

def test_map_trajectory():
    """Test map trajectory plotting with Australian waters data"""
    print("Testing map trajectory plotting...")
    
    # Generate Australian waters trajectory data
    data = create_map_trajectory_data(region="australia", hours=2.0)
    print(f"Generated {len(data)} trajectory points")
    print(f"Latitude range: {data['latitude'].min():.4f} to {data['latitude'].max():.4f}")
    print(f"Longitude range: {data['longitude'].min():.4f} to {data['longitude'].max():.4f}")
    
    # Initialize visualizer
    visualizer = TriaxusVisualizer()
    print("Visualizer initialized")
    
    # Create map plot
    output_file = visualizer.create_map_plot(
        data=data,
        title="TRIAXUS Trajectory - Australian Waters (Great Barrier Reef)",
        output_file="tests/output/map_trajectory_australia.html"
    )
    
    print(f"PASS Map trajectory plot created: {output_file}")
    return True

def test_map_trajectory_extended():
    """Test map trajectory plotting with extended Australian waters data"""
    print("\nTesting extended Australian waters trajectory...")
    
    # Generate extended Australian waters trajectory data
    data = create_map_trajectory_data(region="australia", hours=3.0)
    print(f"Generated {len(data)} trajectory points")
    print(f"Latitude range: {data['latitude'].min():.4f} to {data['latitude'].max():.4f}")
    print(f"Longitude range: {data['longitude'].min():.4f} to {data['longitude'].max():.4f}")
    
    # Initialize visualizer
    visualizer = TriaxusVisualizer()
    
    # Create map plot
    output_file = visualizer.create_map_plot(
        data=data,
        title="TRIAXUS Trajectory - Extended Australian Waters",
        output_file="tests/output/map_trajectory_extended_australia.html"
    )
    
    print(f"PASS Extended Australian waters trajectory plot created: {output_file}")
    return True

def test_map_trajectory_different_styles():
    """Test map trajectory with different map styles"""
    print("\nTesting map trajectory with different styles...")
    
    # Generate trajectory data
    data = create_map_trajectory_data(region="australia", hours=1.0)
    
    # Initialize visualizer
    visualizer = TriaxusVisualizer()
    
    # Test different map styles
    styles = ["light", "dark", "satellite", "streets"]
    
    for style in styles:
        output_file = visualizer.create_map_plot(
            data=data,
            title=f"TRIAXUS Trajectory - {style.title()} Style",
            map_style=style,
            output_file=f"tests/output/map_trajectory_{style}.html"
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
