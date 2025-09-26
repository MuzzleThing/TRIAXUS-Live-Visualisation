import pandas as pd

from triaxus.core.config import ConfigManager
from triaxus.core.data_validator import DataValidator
from triaxus.data.processor import DataProcessor


def test_quality_report_flags_anomalies_and_duplicates():
    config_manager = ConfigManager()
    validator = DataValidator(config_manager)

    df = pd.DataFrame(
        {
            "time": pd.date_range("2024-01-01", periods=6, freq="H"),
            "depth": [10, 10, 30, None, None, 50],
            "latitude": [10, 10, 10, 10, 10, 10],
            "longitude": [100, 100, 100, 100, 100, 100],
            "tv290c": [15, 16, 17, 18, 19, 120],
            "sal00": [35, 36, 37, 38, 39, 40],
            "sbeox0mm_l": [8, 8, None, 8, 8, 8],
            "fleco_afl": [0.5, 0.6, 0.4, 0.3, 0.4, 0.5],
            "ph": [8.1, 8.2, 8.3, 8.4, 8.2, 9.5],
        }
    )

    # Introduce deliberate duplicate on required subset (time, depth, lat, lon)
    df.loc[1, ["time", "depth"]] = df.loc[0, ["time", "depth"]]

    validator.validate(df, ["time", "depth", "latitude", "longitude"])
    report = validator.get_last_report()

    assert report is not None
    assert report.row_count == len(df)
    assert report.duplicate_count >= 2
    assert any("tv290c" in entry for entry in report.errors)
    assert any("ph" in entry for entry in report.errors)
    assert any("depth" in entry for entry in report.warnings)


def test_data_processor_normalises_columns_and_runs_quality_checks():
    df = pd.DataFrame(
        {
            "Time": pd.date_range("2024-01-01", periods=4, freq="H"),
            "Depth": [10, 15, 20, 25],
            "LATITUDE": [10.0, 10.2, 10.4, 10.6],
            "LONGITUDE": [100.0, 100.2, 100.4, 100.6],
            "tv290C": [15.1, 15.3, 15.4, 15.5],
            "SAL00": [35.0, 35.1, 35.3, 35.4],
            "Sbeox0Mm_L": [8.0, 8.1, 8.2, 8.3],
            "flECO-AFL": [0.5, 0.6, 0.55, 0.58],
            "pH": [8.1, 8.1, 8.2, 8.2],
        }
    )

    processor = DataProcessor()
    processed = processor.process(df, run_quality_checks=True)

    assert "tv290c" in processed.columns
    assert "sal00" in processed.columns
    report = processor.get_last_quality_report()
    assert report is not None
    assert report.row_count == len(df)


