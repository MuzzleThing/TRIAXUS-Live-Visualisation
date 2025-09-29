#!/usr/bin/env python3
"""
Integration test: orchestrate all plotter tests by delegating to unit entries.
"""

import sys
from pathlib import Path

# Ensure project root on sys.path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from tests.unit.plotters.test_comprehensive_plots import (
    test_all_time_series_plots,
    test_all_depth_profile_plots,
    test_all_contour_plots,
    test_all_map_plots,
    test_generic_plot_method,
)


def test_all_plotters_integration():
    assert test_all_time_series_plots() is True
    assert test_all_depth_profile_plots() is True
    assert test_all_contour_plots() is True
    assert test_all_map_plots() is True
    assert test_generic_plot_method() is True


if __name__ == "__main__":
    ok = (
        test_all_time_series_plots()
        and test_all_depth_profile_plots()
        and test_all_contour_plots()
        and test_all_map_plots()
        and test_generic_plot_method()
    )
    sys.exit(0 if ok else 1)


