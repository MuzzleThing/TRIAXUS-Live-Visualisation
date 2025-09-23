"""
Data Processor for TRIAXUS visualization system

This module provides data processing functionality for TRIAXUS data.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List, Tuple
import logging

from ..core.config import ConfigManager
from ..core.data_validator import DataValidator
from .quality_control import QualityReport


class DataProcessor:
    """Data processor for TRIAXUS data processing"""

    NUMERIC_COLUMNS = [
        "depth",
        "latitude",
        "longitude",
        "tv290c",
        "fleco_afl",
        "ph",
        "sbeox0mm_l",
        "sal00",
    ]

    def __init__(self, config_manager: Optional[ConfigManager] = None):
        """
        Initialize DataProcessor

        Args:
            config_manager: Configuration manager instance
        """
        self.config_manager = config_manager or ConfigManager()
        self.logger = logging.getLogger(__name__)
        self.last_quality_report: Optional[QualityReport] = None

    def process(
        self,
        data: pd.DataFrame,
        processing_config: Optional[Dict[str, Any]] = None,
        run_quality_checks: bool = False,
    ) -> pd.DataFrame:
        """
        Process data for plotting

        Args:
            data: Input data
            processing_config: Processing configuration
            run_quality_checks: Whether to compute a quality report after processing

        Returns:
            Processed data
        """
        try:
            processed_data = data.copy()
            processed_data = self._normalize_columns(processed_data)

            # Apply processing steps
            processed_data = self._clean_data(processed_data)
            processed_data = self._validate_data_types(processed_data)
            processed_data = self._handle_missing_values(
                processed_data, processing_config
            )
            processed_data = self._apply_filters(processed_data, processing_config)
            processed_data = self._sort_data(processed_data)

            self.logger.info(f"Data processed: {len(processed_data)} rows")

            quality_requested = run_quality_checks or bool(
                (processing_config or {}).get("quality_checks", False)
            )
            self.last_quality_report = None
            if quality_requested:
                self.last_quality_report = self.run_quality_checks(processed_data)

            return processed_data

        except Exception as e:
            self.logger.error(f"Data processing failed: {e}")
            raise

    def run_quality_checks(self, data: pd.DataFrame) -> QualityReport:
        """Run validation-backed quality checks and return the report"""
        validator = DataValidator(self.config_manager)
        report = validator.generate_quality_report(data)
        self.logger.info("Quality control report generated for processed data")
        return report

    def get_last_quality_report(self) -> Optional[QualityReport]:
        """Return the last quality report computed during processing"""
        return self.last_quality_report

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _normalize_columns(self, data: pd.DataFrame) -> pd.DataFrame:
        """Normalize column names to lowercase with underscores"""
        rename_map: Dict[str, str] = {}
        seen: Dict[str, int] = {}

        for column in data.columns:
            normalized = str(column).strip().lower().replace(" ", "_").replace("-", "_")
            if normalized in seen:
                seen[normalized] += 1
                candidate = f"{normalized}_{seen[normalized]}"
            else:
                seen[normalized] = 0
                candidate = normalized
            rename_map[column] = candidate

        return data.rename(columns=rename_map)

    def _clean_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """Clean data by removing invalid entries"""
        data = data.dropna(how="all")
        data = data.drop_duplicates()

        if "latitude" in data.columns:
            data = data[(data["latitude"] >= -90) & (data["latitude"] <= 90)]
        if "longitude" in data.columns:
            data = data[(data["longitude"] >= -180) & (data["longitude"] <= 180)]
        if "depth" in data.columns:
            data = data[(data["depth"] >= 0) & (data["depth"] <= 11000)]

        return data

    def _validate_data_types(self, data: pd.DataFrame) -> pd.DataFrame:
        """Validate and convert data types"""
        if "time" in data.columns:
            data["time"] = pd.to_datetime(data["time"], errors="coerce")

        for col in self.NUMERIC_COLUMNS:
            if col in data.columns:
                data[col] = pd.to_numeric(data[col], errors="coerce")

        return data

    def _handle_missing_values(
        self, data: pd.DataFrame, config: Optional[Dict[str, Any]]
    ) -> pd.DataFrame:
        """Handle missing values based on configuration"""
        if not config:
            return data

        missing_strategy = config.get("missing_values", "drop")

        if missing_strategy == "drop":
            required_columns = config.get("required_columns", [])
            if required_columns:
                data = data.dropna(subset=required_columns)

        elif missing_strategy == "interpolate":
            numeric_columns = data.select_dtypes(include=[np.number]).columns
            for col in numeric_columns:
                if data[col].isna().any():
                    data[col] = data[col].interpolate(method="linear")

        elif missing_strategy == "fill":
            fill_values = config.get("fill_values", {})
            for col, value in fill_values.items():
                if col in data.columns:
                    data[col] = data[col].fillna(value)

        return data

    def _apply_filters(
        self, data: pd.DataFrame, config: Optional[Dict[str, Any]]
    ) -> pd.DataFrame:
        """Apply data filters based on configuration"""
        if not config:
            return data

        filters = config.get("filters", {})

        for column, filter_config in filters.items():
            if column not in data.columns:
                continue

            filter_type = filter_config.get("type")
            filter_value = filter_config.get("value")

            if filter_type == "range":
                min_val, max_val = filter_value
                data = data[(data[column] >= min_val) & (data[column] <= max_val)]
            elif filter_type == "greater_than":
                data = data[data[column] > filter_value]
            elif filter_type == "less_than":
                data = data[data[column] < filter_value]
            elif filter_type == "equals":
                data = data[data[column] == filter_value]
            elif filter_type == "not_equals":
                data = data[data[column] != filter_value]

        return data

    def _sort_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """Sort data by time or depth when available"""
        if "time" in data.columns:
            data = data.sort_values("time").reset_index(drop=True)
        elif "depth" in data.columns:
            data = data.sort_values("depth").reset_index(drop=True)

        return data

    def resample_data(
        self, data: pd.DataFrame, frequency: str = "1min"
    ) -> pd.DataFrame:
        """Resample data to a specific frequency"""
        if "time" not in data.columns:
            self.logger.warning("No time column found for resampling")
            return data

        data_indexed = data.set_index("time")
        resampled = data_indexed.resample(frequency).mean()
        resampled = resampled.reset_index()

        self.logger.info(
            f"Data resampled to {frequency} frequency: {len(resampled)} rows"
        )
        return resampled

    def interpolate_data(
        self, data: pd.DataFrame, method: str = "linear"
    ) -> pd.DataFrame:
        """Interpolate missing values in data"""
        numeric_columns = data.select_dtypes(include=[np.number]).columns

        for col in numeric_columns:
            if data[col].isna().any():
                data[col] = data[col].interpolate(method=method)

        self.logger.info(f"Data interpolated using {method} method")
        return data

    def calculate_derived_variables(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate derived variables from existing data"""
        processed_data = data.copy()

        if "tv290c" in data.columns and "sal00" in data.columns:
            processed_data["density"] = self._calculate_density(
                processed_data["tv290c"], processed_data["sal00"]
            )

        if "depth" in data.columns and "tv290c" in data.columns:
            processed_data["temp_gradient"] = self._calculate_temperature_gradient(
                processed_data["depth"], processed_data["tv290c"]
            )

        return processed_data

    def _calculate_density(
        self, temperature: pd.Series, salinity: pd.Series
    ) -> pd.Series:
        """Calculate seawater density using simplified equation"""
        density = 1000 + 0.8 * salinity - 0.2 * temperature
        return density

    def _calculate_temperature_gradient(
        self, depth: pd.Series, temperature: pd.Series
    ) -> pd.Series:
        """Calculate temperature gradient with depth"""
        sorted_data = pd.DataFrame(
            {"depth": depth, "temperature": temperature}
        ).sort_values("depth")

        gradient = sorted_data["temperature"].diff() / sorted_data["depth"].diff()
        gradient = gradient.reindex(temperature.index)

        return gradient

    def get_data_summary(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Get summary statistics for the data"""
        summary = {
            "shape": data.shape,
            "columns": list(data.columns),
            "dtypes": data.dtypes.to_dict(),
            "missing_values": data.isnull().sum().to_dict(),
            "numeric_summary": {},
        }

        numeric_columns = data.select_dtypes(include=[np.number]).columns
        for col in numeric_columns:
            summary["numeric_summary"][col] = {
                "count": int(data[col].count()),
                "mean": float(data[col].mean()),
                "std": float(data[col].std()),
                "min": float(data[col].min()),
                "max": float(data[col].max()),
                "median": float(data[col].median()),
            }

        if "time" in data.columns:
            summary["time_range"] = {
                "start": str(data["time"].min()),
                "end": str(data["time"].max()),
                "duration": str(data["time"].max() - data["time"].min()),
            }

        if "depth" in data.columns:
            summary["depth_range"] = {
                "min": float(data["depth"].min()),
                "max": float(data["depth"].max()),
                "range": float(data["depth"].max() - data["depth"].min()),
            }

        return summary
