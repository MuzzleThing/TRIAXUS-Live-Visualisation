#!/usr/bin/env python3
"""
Run the new split test modules for TRIAXUS visualization system
"""

import sys
import os
from datetime import datetime

# Add the parent directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def run_test_module(module_name, test_function):
    """Run a test module and return success status"""
    print(f"\n{'='*60}")
    print(f"Running {module_name}")
    print(f"{'='*60}")

    try:
        start_time = datetime.now()
        success = test_function()
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        if success:
            print(
                f"\nPASS: {module_name} completed successfully in {duration:.2f} seconds"
            )
            return True
        else:
            print(f"\nFAIL: {module_name} failed")
            return False

    except Exception as e:
        print(f"\nERROR: {module_name} failed with error: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Run all split test modules"""
    print("TRIAXUS Visualization System - Split Test Suite")
    print("=" * 60)
    print(f"Test started at: {datetime.now()}")
    print("=" * 60)

    # Import test modules (reorganized structure)
    from plots.test_time_series_plots import test_time_series_plots
    from plots.test_depth_profile_plots import test_depth_profile_plots
    from plots.test_contour_plots import test_contour_plots
    from maps.test_map_trajectory import (
        test_map_trajectory,
        test_map_trajectory_extended,
        test_map_trajectory_different_styles,
    )
    from themes.test_theme_functionality import test_theme_functionality
    from test_data_quality import test_data_quality

    # Define test modules
    test_modules = [
        ("Time Series Plots", test_time_series_plots),
        ("Depth Profile Plots", test_depth_profile_plots),
        ("Contour Plots", test_contour_plots),
        ("Map Trajectory (Australia)", lambda: test_map_trajectory()),
        ("Map Trajectory (Extended Australia)", lambda: test_map_trajectory_extended()),
        ("Map Trajectory (Styles)", lambda: test_map_trajectory_different_styles()),
        ("Theme Functionality", test_theme_functionality),
        ("Data Quality", test_data_quality),
    ]

    # Run all tests
    results = []
    total_start_time = datetime.now()

    for module_name, test_function in test_modules:
        success = run_test_module(module_name, test_function)
        results.append((module_name, success))

    total_end_time = datetime.now()
    total_duration = (total_end_time - total_start_time).total_seconds()

    # Print summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Test completed at: {total_end_time}")
    print(f"Total duration: {total_duration:.2f} seconds")
    print()

    passed = 0
    failed = 0

    for module_name, success in results:
        status = "PASSED" if success else "FAILED"
        print(f"{status} - {module_name}")
        if success:
            passed += 1
        else:
            failed += 1

    print()
    print(f"Total tests: {len(results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success rate: {(passed/len(results)*100):.1f}%")

    if failed == 0:
        print("\nSUCCESS: All split tests passed successfully!")
        print("Generated test plots are saved in tests/output/ directory")
        print("You can open the HTML files in a web browser to view the plots")
        return 0
    else:
        print(
            f"\nWARNING: {failed} test(s) failed. Please check the output above for details."
        )
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
