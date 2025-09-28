from pathlib import Path

import pandas as pd

from triaxus.core.config import ConfigManager
from triaxus.data.archiver import DataArchiver


class StubDatabaseDataSource:
    """Simple stub that mimics the database interface without persistence"""

    def __init__(self):
        self.stored = False

    def is_available(self) -> bool:
        return False

    def store_data(self, data: pd.DataFrame, source_file: str = None):
        self.stored = True
        return False


def test_archiver_creates_files(tmp_path):
    archive_dir = tmp_path / "archive_outputs"

    data = pd.DataFrame(
        {
            "time": pd.date_range("2024-01-01", periods=3, freq="H"),
            "depth": [10, 20, 30],
            "latitude": [10.0, 10.1, 10.2],
            "longitude": [100.0, 100.1, 100.2],
            "tv290c": [15.0, 15.4, 15.6],
            "sal00": [35.0, 35.2, 35.3],
            "sbeox0mm_l": [8.0, 8.1, 8.2],
            "fleco_afl": [0.5, 0.6, 0.7],
            "ph": [8.1, 8.2, 8.0],
        }
    )

    archiver = DataArchiver(
        config_manager=ConfigManager(),
        database_source=StubDatabaseDataSource(),
        archive_dir=archive_dir,
    )

    result = archiver.archive(data, source_name="unit_test")

    assert result["row_count"] == len(data)
    assert result["database_stored"] is False

    archive_info = result["archive"]
    data_path = Path(archive_info["data_path"])
    assert data_path.exists()

    quality_report = result["quality_report"]
    assert quality_report is not None
    assert quality_report["row_count"] == len(data)

    if archive_info.get("quality_report_path"):
        assert Path(archive_info["quality_report_path"]).exists()


def run_data_archiver_unit_suite(tmp_path) -> None:
    """Reusable entrypoint for integration/e2e to run data archiver tests after processing."""
    test_archiver_creates_files(tmp_path)
