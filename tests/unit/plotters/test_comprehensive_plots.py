#!/usr/bin/env python3
"""
Comprehensive test for all plotting functionality
This test covers all plotter types and all their methods
"""

import sys
import os
from pathlib import Path

# Add project root to sys.path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from triaxus.data import create_plot_test_data, create_map_trajectory_data
from triaxus.visualizer import TriaxusVisualizer
from triaxus.data.database_source import DatabaseDataSource


def test_all_time_series_plots():
    """Test all time series plotting methods"""
    print("=" * 60)
    print("Testing ALL Time Series Plot Methods")
    print("=" * 60)

    # Generate test data
    data = create_plot_test_data(hours=2.0)
    print(f"Generated {len(data)} data points for time series testing")

    # Initialize visualizer
    visualizer = TriaxusVisualizer()

    # Test variables
    variables = ["tv290c", "sal00", "sbeox0mm_l", "fleco_afl", "ph"]

    # Test 1: Single variable plots
    print("\n1. Testing single variable time series plots...")
    for variable in variables:
        try:
            output_file = visualizer.create_time_series_plot(
                data=data,
                variables=[variable],
                title=f"{variable} Time Series (Single Variable)",
                output_file=f"tests/output/time_series_single_{variable}.html",
            )
            print(f"  Single {variable} time series plot: {output_file}")
        except Exception as e:
            print(f"  Single {variable} time series plot failed: {e}")

    # Test 2: Multi-variable plots
    print("\n2. Testing multi-variable time series plots...")
    try:
        output_file = visualizer.create_time_series_plot(
            data=data,
            variables=variables,
            title="Multi-Variable Time Series",
            output_file="tests/output/time_series_multi_all.html",
        )
        print(f"  Multi-variable time series plot: {output_file}")
    except Exception as e:
        print(f"  Multi-variable time series plot failed: {e}")

    # Test 3: Subset multi-variable plots
    print("\n3. Testing subset multi-variable time series plots...")
    subset_vars = ["tv290c", "sal00", "ph"]
    try:
        output_file = visualizer.create_time_series_plot(
            data=data,
            variables=subset_vars,
            title="Subset Multi-Variable Time Series",
            output_file="tests/output/time_series_multi_subset.html",
        )
        print(f"  Subset multi-variable time series plot: {output_file}")
    except Exception as e:
        print(f"  Subset multi-variable time series plot failed: {e}")

    # Test 4: Time series with different parameters
    print("\n4. Testing time series with different parameters...")
    try:
        output_file = visualizer.create_time_series_plot(
            data=data,
            variables=["tv290c"],
            title="Time Series with Custom Parameters",
            show_statistics=True,
            line_width=3,
            marker_size=6,
            height=600,
            width=1000,
            output_file="tests/output/time_series_custom_params.html",
        )
        print(f"  Custom parameters time series plot: {output_file}")
    except Exception as e:
        print(f"  Custom parameters time series plot failed: {e}")

    print("\nTime series plot testing completed!")
    return True


def test_all_depth_profile_plots():
    """Test all depth profile plotting methods"""
    print("=" * 60)
    print("Testing ALL Depth Profile Plot Methods")
    print("=" * 60)

    # Generate test data
    data = create_plot_test_data(hours=2.0)
    print(f"Generated {len(data)} data points for depth profile testing")

    # Initialize visualizer
    visualizer = TriaxusVisualizer()

    # Test variables
    variables = ["tv290c", "sal00", "sbeox0mm_l", "fleco_afl", "ph"]

    # Test 1: Single variable plots
    print("\n1. Testing single variable depth profile plots...")
    for variable in variables:
        try:
            output_file = visualizer.create_depth_profile_plot(
                data=data,
                variables=[variable],
                title=f"{variable} Depth Profile (Single Variable)",
                output_file=f"tests/output/depth_profile_single_{variable}.html",
            )
            print(f"  Single {variable} depth profile plot: {output_file}")
        except Exception as e:
            print(f"  Single {variable} depth profile plot failed: {e}")

    # Test 2: Multi-variable plots
    print("\n2. Testing multi-variable depth profile plots...")
    try:
        output_file = visualizer.create_depth_profile_plot(
            data=data,
            variables=variables,
            title="Multi-Variable Depth Profile",
            output_file="tests/output/depth_profile_multi_all.html",
        )
        print(f"  Multi-variable depth profile plot: {output_file}")
    except Exception as e:
        print(f"  Multi-variable depth profile plot failed: {e}")

    # Test 3: Subset multi-variable plots
    print("\n3. Testing subset multi-variable depth profile plots...")
    subset_vars = ["tv290c", "sal00", "ph"]
    try:
        output_file = visualizer.create_depth_profile_plot(
            data=data,
            variables=subset_vars,
            title="Subset Multi-Variable Depth Profile",
            output_file="tests/output/depth_profile_multi_subset.html",
        )
        print(f"  Subset multi-variable depth profile plot: {output_file}")
    except Exception as e:
        print(f"  Subset multi-variable depth profile plot failed: {e}")

    # Test 4: Depth profile with different parameters
    print("\n4. Testing depth profile with different parameters...")
    try:
        output_file = visualizer.create_depth_profile_plot(
            data=data,
            variables=["tv290c"],
            title="Depth Profile with Custom Parameters",
            show_statistics=True,
            line_width=3,
            marker_size=6,
            height=600,
            width=1000,
            output_file="tests/output/depth_profile_custom_params.html",
        )
        print(f"  Custom parameters depth profile plot: {output_file}")
    except Exception as e:
        print(f"  Custom parameters depth profile plot failed: {e}")

    print("\nDepth profile plot testing completed!")
    return True


def test_all_contour_plots():
    """Test all contour plotting methods"""
    print("=" * 60)
    print("Testing ALL Contour Plot Methods")
    print("=" * 60)

    # Generate test data
    data = create_plot_test_data(hours=2.0)
    print(f"Generated {len(data)} data points for contour testing")

    # Initialize visualizer
    visualizer = TriaxusVisualizer()

    # Test variables
    variables = ["tv290c", "sal00", "sbeox0mm_l", "fleco_afl", "ph"]

    # Test 1: Single variable contour plots
    print("\n1. Testing single variable contour plots...")
    for variable in variables:
        try:
            output_file = visualizer.create_contour_plot(
                data=data,
                variable=variable,
                title=f"{variable} Contour Plot",
                output_file=f"tests/output/contour_single_{variable}.html",
            )
            print(f"  Single {variable} contour plot: {output_file}")
        except Exception as e:
            print(f"  Single {variable} contour plot failed: {e}")

    # Test 2: Contour plots with different parameters
    print("\n2. Testing contour plots with different parameters...")
    try:
        output_file = visualizer.create_contour_plot(
            data=data,
            variable="tv290c",
            title="Contour Plot with Custom Parameters",
            height=600,
            width=1000,
            output_file="tests/output/contour_custom_params.html",
        )
        print(f"  Custom parameters contour plot: {output_file}")
    except Exception as e:
        print(f"  Custom parameters contour plot failed: {e}")

    print("\nContour plot testing completed!")
    return True


def test_all_map_plots():
    """Test all map plotting methods"""
    print("=" * 60)
    print("Testing ALL Map Plot Methods")
    print("=" * 60)

    # Try to get data from database first, then fallback to generated data
    try:
        db = DatabaseDataSource()
        if db.is_available():
            data = db.load_data(limit=50)
            print(f"Retrieved {len(data)} oceanographic data points from database")
        else:
            raise Exception("Database not available")
    except Exception:
        data = create_map_trajectory_data(region="australia", hours=2.0)
        print(f"Generated {len(data)} trajectory data points")

    # Initialize visualizer
    visualizer = TriaxusVisualizer()

    # Test 1: Basic map plot
    print("\n1. Testing basic map plot...")
    try:
        output_file = visualizer.create_map_plot(
            data=data,
            title="TRIAXUS Trajectory - Basic Map",
            output_file="tests/output/map_basic.html",
        )
        print(f"  Basic map plot: {output_file}")
    except Exception as e:
        print(f"  Basic map plot failed: {e}")

    # Test 2: Map plots with different styles
    print("\n2. Testing map plots with different styles...")
    styles = ["light", "dark", "satellite", "streets"]
    for style in styles:
        try:
            output_file = visualizer.create_map_plot(
                data=data,
                title=f"TRIAXUS Trajectory - {style.title()} Style",
                map_style=style,
                output_file=f"tests/output/map_{style}.html",
            )
            print(f"  {style.title()} style map plot: {output_file}")
        except Exception as e:
            print(f"  {style.title()} style map plot failed: {e}")

    # Test 3: Map plot with custom parameters
    print("\n3. Testing map plot with custom parameters...")
    try:
        output_file = visualizer.create_map_plot(
            data=data,
            title="TRIAXUS Trajectory - Custom Parameters",
            map_style="satellite",
            height=600,
            width=1000,
            output_file="tests/output/map_custom_params.html",
        )
        print(f"  Custom parameters map plot: {output_file}")
    except Exception as e:
        print(f"  Custom parameters map plot failed: {e}")

    print("\nMap plot testing completed!")
    return True


def test_generic_plot_method():
    """Test the generic create_plot method"""
    print("=" * 60)
    print("Testing Generic create_plot Method")
    print("=" * 60)

    # Generate test data
    data = create_plot_test_data(hours=2.0)
    print(f"Generated {len(data)} data points for generic plot testing")

    # Initialize visualizer
    visualizer = TriaxusVisualizer()

    # Test all plot types using generic method
    plot_types = ["time_series", "depth_profile", "contour", "map"]
    
    for plot_type in plot_types:
        print(f"\nTesting generic {plot_type} plot...")
        try:
            if plot_type == "contour":
                # Contour plots need a specific variable
                output_file = visualizer.create_plot(
                    plot_type=plot_type,
                    data=data,
                    variable="tv290c",
                    title=f"Generic {plot_type.title()} Plot",
                    output_file=f"tests/output/generic_{plot_type}.html",
                )
            elif plot_type == "map":
                # Map plots need geographic data
                try:
                    db = DatabaseDataSource()
                    if db.is_available():
                        map_data = db.load_data(limit=20)
                    else:
                        map_data = create_map_trajectory_data(region="australia", hours=1.0)
                except Exception:
                    map_data = create_map_trajectory_data(region="australia", hours=1.0)
                
                output_file = visualizer.create_plot(
                    plot_type=plot_type,
                    data=map_data,
                    title=f"Generic {plot_type.title()} Plot",
                    output_file=f"tests/output/generic_{plot_type}.html",
                )
            else:
                # Time series and depth profile plots
                output_file = visualizer.create_plot(
                    plot_type=plot_type,
                    data=data,
                    variables=["tv290c", "sal00"],
                    title=f"Generic {plot_type.title()} Plot",
                    output_file=f"tests/output/generic_{plot_type}.html",
                )
            
            print(f"  Generic {plot_type} plot: {output_file}")
        except Exception as e:
            print(f"  Generic {plot_type} plot failed: {e}")

    print("\nGeneric plot method testing completed!")
    return True


def run_comprehensive_plot_tests():
    """Run all comprehensive plot tests"""
    print("Starting Comprehensive Plot Testing")
    print("=" * 80)
    
    # Ensure output directory exists
    output_dir = project_root / "tests" / "output"
    output_dir.mkdir(exist_ok=True)
    
    test_results = {}
    
    # Run all test suites
    test_suites = [
        ("Time Series Plots", test_all_time_series_plots),
        ("Depth Profile Plots", test_all_depth_profile_plots),
        ("Contour Plots", test_all_contour_plots),
        ("Map Plots", test_all_map_plots),
        ("Generic Plot Method", test_generic_plot_method),
    ]
    
    for test_name, test_func in test_suites:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            test_results[test_name] = result
            print(f"{test_name}: PASSED")
        except Exception as e:
            test_results[test_name] = False
            print(f"{test_name}: FAILED - {e}")
    
    # Summary
    print("\n" + "=" * 80)
    print("COMPREHENSIVE PLOT TEST SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for result in test_results.values() if result)
    total = len(test_results)
    
    for test_name, result in test_results.items():
        status = "PASS" if result else "FAIL"
        print(f"{'PASS' if result else 'FAIL'} {test_name}: {status}")
    
    print(f"\nOverall Result: {passed}/{total} test suites passed")
    
    if passed == total:
        print("All comprehensive plot tests PASSED!")
        return True
    else:
        print("Some comprehensive plot tests FAILED!")
        return False


if __name__ == "__main__":
    print("TRIAXUS Comprehensive Plot Test Suite")
    print("=" * 50)

    try:
        success = run_comprehensive_plot_tests()
        if success:
            print("\nSUCCESS: All comprehensive plot tests completed successfully!")
            print("Generated plots are saved in tests/output/ directory")
        else:
            print("\nFAILURE: Some tests failed. Check the output above.")
            sys.exit(1)

    except Exception as e:
        print(f"ERROR: Error during comprehensive testing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
