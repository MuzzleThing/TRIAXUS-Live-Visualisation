#!/usr/bin/env python3
"""
Integration data tests: process first, then archive, then quality checks.
"""

import sys
from pathlib import Path

# Ensure project root on sys.path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from tests.utils import TestDatabaseHelper
from tests.unit.data.test_data_processor import run_data_processor_unit_suite
from tests.unit.data.test_data_archiver import run_data_archiver_unit_suite
from tests.unit.data.test_quality_control_backend import run_quality_backend_unit_suite


def test_data_pipeline_integration(tmp_path):
    # Clean DB before pipeline to avoid unique conflicts if archiver touches DB in future
    try:
        TestDatabaseHelper.clean_database()
    except Exception:
        pass

    # 1) Process
    run_data_processor_unit_suite()

    # 2) Archive (relies on processed data behavior; uses tmp_path for outputs)
    run_data_archiver_unit_suite(tmp_path)

    # 3) Quality backend checks
    run_quality_backend_unit_suite()


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__]))


