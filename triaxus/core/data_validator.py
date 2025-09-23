"""
Data Validator for TRIAXUS visualization system

This module provides comprehensive data validation for all plot types.
"""

import logging
from functools import lru_cache
from typing import Any, Dict, List, Optional, TYPE_CHECKING

import numpy as np
import pandas as pd

from .config import ConfigManager

if TYPE_CHECKING:
    from ..data.quality_control import QualityReport  # pragma: no cover

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def _get_quality_control_utils():
    """Lazy import to avoid circular dependencies"""
    from ..data.quality_control import QualityReport, generate_quality_report  # pragma: no cover
    return QualityReport, generate_quality_report

class DataValidator:
    """Data validator for TRIAXUS core functionality"""

    def __init__(self, config_manager: Optional[ConfigManager] = None):
        self.logger = logging.getLogger(__name__)
        self.config_manager = config_manager or ConfigManager()

        # Cached configuration
        self.validation_config = self.config_manager.get_validation_config()
        self.data_config = self.config_manager.get_data_config()

        # Store last generated quality report for downstream consumers
        self._last_report: Optional["QualityReport"] = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def validate(self, data: pd.DataFrame, required_columns: List[str]) -> pd.DataFrame:
        """Validate data for plotting"""
        self.logger.info(f"Validating data with shape: {data.shape}")

        validated_data = self._coerce_dataframe(data)

        # Basic validation steps
        self._validate_basic(validated_data)
        self._validate_columns(validated_data, required_columns)
        self._validate_data_types(validated_data)
        self._validate_ranges(validated_data)
        self._validate_data_quality(validated_data)

        # Quality control report
        report = self.generate_quality_report(validated_data)
        self._handle_quality_report(report)

        self.logger.info("Data validation passed")
        return validated_data

    def generate_quality_report(self, data: pd.DataFrame) -> "QualityReport":
        """Generate and store the latest quality report"""
        config = self.validation_config if isinstance(self.validation_config, dict) else {}
        _, generate_fn = _get_quality_control_utils()
        self._last_report = generate_fn(data, config)
        return self._last_report

    def get_last_report(self) -> Optional["QualityReport"]:
        """Return the last computed quality report"""
        return self._last_report

    # ------------------------------------------------------------------
    # Internal validation helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _coerce_dataframe(data: pd.DataFrame) -> pd.DataFrame:
        if isinstance(data, pd.DataFrame):
            return data.copy()
        raise ValueError("Data must be a pandas DataFrame")

    @staticmethod
    def _normalize_column_key(column: str) -> str:
        return str(column).strip().lower()

    def _get_validation_rule(self, column_name: str) -> Optional[Dict[str, Any]]:
        """Get validation rule for a column from configuration"""
        if not isinstance(self.validation_config, dict):
            return None

        rules = self.validation_config.get("column_rules", {})
        if isinstance(rules, dict):
            key_variants = [
                column_name,
                column_name.lower(),
                column_name.upper(),
                column_name.replace("_", ""),
                column_name.lower().replace("_", ""),
            ]
            for key in key_variants:
                if key in rules:
                    return rules[key]

        data_variables = self.data_config.get("variables", []) if isinstance(self.data_config, dict) else []
        normalized = [self._normalize_column_key(item) for item in data_variables]
        normalized_name = self._normalize_column_key(column_name)

        if normalized_name in normalized:
            data_type = "datetime" if normalized_name == "time" else "numeric"
            required_variables = self.data_config.get("required_variables", [])
            required = normalized_name in [self._normalize_column_key(item) for item in required_variables]
            return {
                "name": column_name,
                "description": f"Variable: {column_name}",
                "required": required,
                "data_type": data_type,
                "min_value": None,
                "max_value": None,
            }
        return None

    def _validate_basic(self, data: pd.DataFrame):
        if len(data) == 0:
            raise ValueError("Data cannot be empty")
        if len(data) < 2:
            self.logger.warning("Data contains very few points")

    def _validate_columns(self, data: pd.DataFrame, required_columns: List[str]):
        """Validate required columns"""
        available = {self._normalize_column_key(col) for col in data.columns}
        missing_columns = [col for col in required_columns if self._normalize_column_key(col) not in available]
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")

        empty_columns = [col for col in data.columns if data[col].isna().all()]
        if empty_columns:
            self.logger.warning(f"Columns with all NaN values: {empty_columns}")

    def _validate_data_types(self, data: pd.DataFrame):
        """Validate and convert data types"""
        for column in data.columns:
            rule = self._get_validation_rule(column)
            if not rule:
                continue

            expected_type = str(rule.get("data_type", "")).lower()
            if expected_type == "numeric":
                if not pd.api.types.is_numeric_dtype(data[column]):
                    try:
                        data[column] = pd.to_numeric(data[column], errors="coerce")
                        self.logger.info(f"Converted column {column} to numeric")
                    except Exception as exc:
                        raise ValueError(f"Column {column} must be numeric") from exc
            elif expected_type == "datetime":
                if not pd.api.types.is_datetime64_any_dtype(data[column]):
                    try:
                        data[column] = pd.to_datetime(data[column], errors="coerce")
                        self.logger.info(f"Converted column {column} to datetime")
                    except Exception as exc:
                        raise ValueError(f"Column {column} must be datetime") from exc

    def _validate_ranges(self, data: pd.DataFrame):
        """Validate data ranges based on configuration"""
        for column in data.columns:
            rule = self._get_validation_rule(column)
            if not rule:
                continue

            min_val = rule.get("min_value")
            max_val = rule.get("max_value")
            if min_val is None and max_val is None:
                continue

            series = pd.to_numeric(data[column], errors="coerce")
            if min_val is not None:
                below_min = series < min_val
            else:
                below_min = pd.Series([False] * len(series), index=series.index)
            if max_val is not None:
                above_max = series > max_val
            else:
                above_max = pd.Series([False] * len(series), index=series.index)

            out_of_range = (below_min | above_max) & series.notna()
            if out_of_range.any():
                count = int(out_of_range.sum())
                self.logger.warning(
                    f"Column {column} has {count} values outside range [{min_val}, {max_val}]"
                )

    def _validate_data_quality(self, data: pd.DataFrame):
        """Lightweight data quality checks for logging"""
        duplicates = data.duplicated().sum()
        if duplicates > 0:
            self.logger.warning(f"Found {duplicates} duplicate rows")

        missing_counts = data.isnull().sum()
        high_missing = missing_counts[missing_counts > len(data) * 0.5]
        if len(high_missing) > 0:
            self.logger.warning(
                f"Columns with >50% missing values: {high_missing.index.tolist()}"
            )

        constant_columns = [
            column for column in data.select_dtypes(include=[np.number]).columns
            if data[column].nunique() <= 1
        ]
        if constant_columns:
            self.logger.warning(f"Constant columns found: {constant_columns}")

    def _handle_quality_report(self, report: "QualityReport"):
        if not report:
            return

        action = str(self.validation_config.get("error_action", "warn")).lower() if isinstance(self.validation_config, dict) else "warn"
        max_errors = int(self.validation_config.get("max_errors", 100)) if isinstance(self.validation_config, dict) else 100
        log_errors = bool(self.validation_config.get("log_errors", True)) if isinstance(self.validation_config, dict) else True

        if report.errors:
            message = "; ".join(report.errors[:max_errors])
            if len(report.errors) > max_errors:
                message += f"; ... {len(report.errors) - max_errors} more"

            if action == "raise":
                raise ValueError(f"Quality control errors detected: {message}")

            if log_errors:
                self.logger.error(f"Quality control errors detected: {message}")

        if report.warnings and log_errors:
            warn_message = "; ".join(report.warnings[:max_errors])
            if len(report.warnings) > max_errors:
                warn_message += f"; ... {len(report.warnings) - max_errors} more"
            self.logger.warning(f"Quality control warnings: {warn_message}")

    # ------------------------------------------------------------------
    # Convenience validators
    # ------------------------------------------------------------------
    def validate_for_line_plot(self, data: pd.DataFrame) -> pd.DataFrame:
        """Validate data for line plot"""
        return self.validate(data, ["time", "depth"])

    def validate_for_contour_plot(
        self, data: pd.DataFrame, variable: str
    ) -> pd.DataFrame:
        """Validate data for contour plot"""
        required_columns = ["time", "depth", variable]
        return self.validate(data, required_columns)

    def validate_for_map_plot(self, data: pd.DataFrame) -> pd.DataFrame:
        """Validate data for map plot"""
        return self.validate(data, ["latitude", "longitude", "time"])

    def get_validation_summary(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Get validation summary"""
        summary = {
            "shape": data.shape,
            "columns": list(data.columns),
            "missing_values": data.isnull().sum().to_dict(),
            "data_types": data.dtypes.to_dict(),
            "numeric_ranges": {},
        }

        for column in data.select_dtypes(include=[np.number]).columns:
            summary["numeric_ranges"][column] = {
                "min": float(data[column].min()),
                "max": float(data[column].max()),
                "mean": float(data[column].mean()),
            }

        return summary






