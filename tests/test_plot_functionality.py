#!/usr/bin/env python3
"""
TRIAXUS Plot Functionality Test

Comprehensive testing of all plot types using the plot test data generator.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from triaxus.data import create_plot_test_data, create_daily_plot_data, create_quick_plot_data, create_map_trajectory_data
from triaxus.visualizer import TriaxusVisualizer
import pandas as pd
from datetime import datetime


def test_time_series_plot():
    """Test time series plot functionality"""
    print("=" * 60)
    print("Testing Time Series Plot")
    print("=" * 60)
    
    # Generate test data
    data = create_plot_test_data(hours=2.0)
    print(f"Generated {len(data)} data points for time series testing")
    
    # Initialize visualizer
    visualizer = TriaxusVisualizer()
    
    # Test different variables
    variables = ['tv290C', 'sal00', 'sbeox0Mm_L', 'flECO-AFL', 'ph']
    
    for variable in variables:
        print(f"\nTesting {variable} time series plot...")
        try:
            # Create time series plot
            output_file = visualizer.create_time_series_plot(
                data=data,
                variables=[variable],
                title=f"{variable} Time Series Test",
                output_file=f"tests/output/time_series_{variable}.html"
            )
            
            print(f"  PASS: {variable} time series plot saved to {output_file}")
            
        except Exception as e:
            print(f"  FAIL: Error creating {variable} time series plot: {e}")
    
    print("\nTime series plot testing completed!")


def test_depth_profile_plot():
    """Test depth profile plot functionality"""
    print("\n" + "=" * 60)
    print("Testing Depth Profile Plot")
    print("=" * 60)
    
    # Generate test data
    data = create_plot_test_data(hours=2.0)
    print(f"Generated {len(data)} data points for depth profile testing")
    
    # Initialize visualizer
    visualizer = TriaxusVisualizer()
    
    # Test different variables
    variables = ['tv290C', 'sal00', 'sbeox0Mm_L', 'flECO-AFL', 'ph']
    
    for variable in variables:
        print(f"\nTesting {variable} depth profile plot...")
        try:
            # Create depth profile plot
            output_file = visualizer.create_depth_profile_plot(
                data=data,
                variables=[variable],
                title=f"{variable} Depth Profile Test",
                output_file=f"tests/output/depth_profile_{variable}.html"
            )
            
            print(f"  PASS: {variable} depth profile plot saved to {output_file}")
            
        except Exception as e:
            print(f"  FAIL: Error creating {variable} depth profile plot: {e}")
    
    print("\nDepth profile plot testing completed!")


def test_contour_plot():
    """Test contour plot functionality"""
    print("\n" + "=" * 60)
    print("Testing Contour Plot")
    print("=" * 60)
    
    # Generate test data
    data = create_plot_test_data(hours=2.0)
    print(f"Generated {len(data)} data points for contour testing")
    
    # Initialize visualizer
    visualizer = TriaxusVisualizer()
    
    # Test different variables
    variables = ['tv290C', 'sal00', 'sbeox0Mm_L', 'flECO-AFL', 'ph']
    
    for variable in variables:
        print(f"\nTesting {variable} contour plot...")
        try:
            # Create contour plot
            output_file = visualizer.create_contour_plot(
                data=data,
                variable=variable,
                title=f"{variable} Contour Test",
                output_file=f"tests/output/contour_{variable}.html"
            )
            
            print(f"  PASS: {variable} contour plot saved to {output_file}")
            
        except Exception as e:
            print(f"  FAIL: Error creating {variable} contour plot: {e}")
    
    print("\nContour plot testing completed!")


def test_map_plot():
    """Test map plot functionality - focused on trajectory"""
    print("\n" + "=" * 60)
    print("Testing Map Plot (Trajectory)")
    print("=" * 60)
    
    # Generate trajectory data for Australian waters
    regions = [
        ("australia", "Australian Waters (Great Barrier Reef)"),
        ("australia", "Extended Australian Waters")
    ]
    
    # Initialize visualizer
    visualizer = TriaxusVisualizer()
    
    for region, description in regions:
        print(f"\nTesting {description} trajectory...")
        try:
            # Generate trajectory data with different durations
            hours = 2.0 if "Great Barrier Reef" in description else 3.0
            data = create_map_trajectory_data(region=region, hours=hours)
            print(f"  Generated {len(data)} trajectory points")
            print(f"  Latitude range: {data['latitude'].min():.4f} to {data['latitude'].max():.4f}")
            print(f"  Longitude range: {data['longitude'].min():.4f} to {data['longitude'].max():.4f}")
            
            # Create map plot
            output_file = visualizer.create_map_plot(
                data=data,
                title=f"TRIAXUS Trajectory - {description}",
                output_file=f"tests/output/map_trajectory_{region}_{'extended' if hours > 2.0 else 'standard'}.html"
            )
            
            print(f"  PASS: {description} trajectory plot saved to {output_file}")
            
        except Exception as e:
            print(f"  FAIL: Error creating {description} trajectory plot: {e}")
    
    print("\nMap trajectory testing completed!")


def test_theme_functionality():
    """Test theme functionality across all plot types"""
    print("\n" + "=" * 60)
    print("Testing Theme Functionality")
    print("=" * 60)
    
    # Generate test data
    data = create_plot_test_data(hours=1.0)
    print(f"Generated {len(data)} data points for theme testing")
    
    # Initialize visualizer
    visualizer = TriaxusVisualizer()
    
    # Test different themes
    themes = ['default', 'oceanographic', 'dark', 'high_contrast']
    plot_types = ['time_series', 'depth_profile', 'contour', 'map']
    variable = 'tv290C'  # Use temperature for theme testing
    
    for theme in themes:
        print(f"\nTesting {theme} theme...")
        
        # Set theme
        visualizer.set_theme(theme)
        
        for plot_type in plot_types:
            print(f"  Testing {plot_type} with {theme} theme...")
            try:
                if plot_type == 'time_series':
                    output_file = visualizer.create_time_series_plot(
                        data=data,
                        variables=[variable],
                        title=f"{variable} {plot_type} - {theme} theme",
                        output_file=f"tests/output/theme_{theme}_{plot_type}.html"
                    )
                elif plot_type == 'depth_profile':
                    output_file = visualizer.create_depth_profile_plot(
                        data=data,
                        variables=[variable],
                        title=f"{variable} {plot_type} - {theme} theme",
                        output_file=f"tests/output/theme_{theme}_{plot_type}.html"
                    )
                elif plot_type == 'contour':
                    output_file = visualizer.create_contour_plot(
                        data=data,
                        variable=variable,
                        title=f"{variable} {plot_type} - {theme} theme",
                        output_file=f"tests/output/theme_{theme}_{plot_type}.html"
                    )
                elif plot_type == 'map':
                    # Use trajectory data for map plots
                    trajectory_data = create_map_trajectory_data(region="australia", hours=1.0)
                    output_file = visualizer.create_map_plot(
                        data=trajectory_data,
                        title=f"TRIAXUS Trajectory - {theme} theme",
                        output_file=f"tests/output/theme_{theme}_{plot_type}.html"
                    )
                
                print(f"    PASS: {plot_type} with {theme} theme saved to {output_file}")
                
            except Exception as e:
                print(f"    FAIL: Error creating {plot_type} with {theme} theme: {e}")
    
    print("\nTheme functionality testing completed!")


def test_data_quality():
    """Test plot functionality with different data qualities"""
    print("\n" + "=" * 60)
    print("Testing Data Quality Scenarios")
    print("=" * 60)
    
    # Initialize visualizer
    visualizer = TriaxusVisualizer()
    
    # Test scenarios
    scenarios = [
        ("Quick Data", create_quick_plot_data()),
        ("Standard Data", create_plot_test_data(hours=2.0)),
        ("Daily Data", create_daily_plot_data("2024-01-01"))
    ]
    
    for scenario_name, data in scenarios:
        print(f"\nTesting {scenario_name} ({len(data)} points)...")
        
        try:
            # Test time series plot
            output_file = visualizer.create_time_series_plot(
                data=data,
                variables=['tv290C'],
                title=f"Temperature Time Series - {scenario_name}",
                output_file=f"tests/output/data_quality_{scenario_name.lower().replace(' ', '_')}.html"
            )
            
            print(f"  PASS: {scenario_name} time series plot saved to {output_file}")
            
        except Exception as e:
            print(f"  FAIL: Error with {scenario_name}: {e}")
    
    print("\nData quality testing completed!")


def main():
    """Run all plot functionality tests"""
    print("TRIAXUS Plot Functionality Test Suite")
    print("=" * 80)
    print(f"Test started at: {datetime.now()}")
    print("=" * 80)
    
    # Create output directory
    os.makedirs("tests/output", exist_ok=True)
    
    # Run all tests
    test_time_series_plot()
    test_depth_profile_plot()
    test_contour_plot()
    test_map_plot()
    test_theme_functionality()
    test_data_quality()
    
    print("\n" + "=" * 80)
    print("All plot functionality tests completed!")
    print(f"Test completed at: {datetime.now()}")
    print("=" * 80)
    print("\nGenerated test plots are saved in tests/output/ directory")
    print("You can open the HTML files in a web browser to view the plots")


if __name__ == "__main__":
    main()
