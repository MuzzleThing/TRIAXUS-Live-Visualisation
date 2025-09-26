"""
Quality control utilities for TRIAXUS data processing.

This module centralises the logic for building column-level and
frame-level quality reports used by validation and archiving layers.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
import math

import numpy as np
import pandas as pd


def _safe_ratio(count: int, total: int) -> float:
    return float(count) / total if total else 0.0


@dataclass
class ColumnQualityResult:
    """Per-column quality metrics"""

    name: str
    total: int
    missing_count: int
    missing_ratio: float
    out_of_range_count: int = 0
    anomaly_count: int = 0
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "total": self.total,
            "missing_count": self.missing_count,
            "missing_ratio": self.missing_ratio,
            "out_of_range_count": self.out_of_range_count,
            "anomaly_count": self.anomaly_count,
            "min_value": self.min_value,
            "max_value": self.max_value,
            "warnings": list(self.warnings),
            "errors": list(self.errors),
        }

    def has_errors(self) -> bool:
        return bool(self.errors)

    def has_warnings(self) -> bool:
        return bool(self.warnings)


@dataclass
class QualityReport:
    """Aggregate data quality metrics"""

    row_count: int
    duplicate_count: int
    duplicate_ratio: float
    column_results: Dict[str, ColumnQualityResult] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "row_count": self.row_count,
            "duplicate_count": self.duplicate_count,
            "duplicate_ratio": self.duplicate_ratio,
            "warnings": list(self.warnings),
            "errors": list(self.errors),
            "columns": {
                name: result.to_dict() for name, result in self.column_results.items()
            },
        }

    def has_errors(self) -> bool:
        return bool(self.errors)

    def has_warnings(self) -> bool:
        return bool(self.warnings)


def generate_quality_report(
    data: pd.DataFrame, validation_config: Dict[str, Any]
) -> QualityReport:
    """Create a QualityReport from the provided data frame and config."""

    row_count = len(data)
    duplicate_subset = validation_config.get("duplicate_subset", []) if validation_config else []
    subset = [col for col in duplicate_subset if col in data.columns]
    duplicate_mask = data.duplicated(subset=subset or None, keep=False)
    duplicate_count = int(duplicate_mask.sum())
    duplicate_ratio = _safe_ratio(duplicate_count, row_count)

    duplicate_threshold = (
        validation_config.get("duplicate_threshold", {}) if validation_config else {}
    )
    dup_warn = float(duplicate_threshold.get("warn", 0.0) or 0.0)
    dup_error = float(duplicate_threshold.get("error", 0.0) or 0.0)

    report = QualityReport(
        row_count=row_count,
        duplicate_count=duplicate_count,
        duplicate_ratio=duplicate_ratio,
    )

    if dup_error and duplicate_ratio >= dup_error:
        report.errors.append(
            f"Duplicate ratio {duplicate_ratio:.2%} exceeds error threshold {dup_error:.2%}"
        )
    elif dup_warn and duplicate_ratio >= dup_warn:
        report.warnings.append(
            f"Duplicate ratio {duplicate_ratio:.2%} exceeds warning threshold {dup_warn:.2%}"
        )

    defaults = validation_config.get("defaults", {}) if validation_config else {}
    default_warn_missing = defaults.get("warn_missing_ratio")
    default_error_missing = defaults.get("error_missing_ratio")

    anomaly_config = validation_config.get("anomaly_detection", {}) if validation_config else {}
    anomaly_enabled = bool(anomaly_config.get("enabled", False))
    anomaly_zscore = float(anomaly_config.get("zscore_threshold", 0) or 0)
    anomaly_min_samples = int(anomaly_config.get("min_samples", 0) or 0)
    anomaly_warn_ratio = float(anomaly_config.get("warn_ratio", 0) or 0)
    anomaly_error_ratio = float(anomaly_config.get("error_ratio", 0) or 0)

    column_rules = validation_config.get("column_rules", {}) if validation_config else {}
    normalised_rules = {}
    if isinstance(column_rules, dict):
        for key, value in column_rules.items():
            normalised_rules[str(key).strip().lower()] = value

    for column in data.columns:
        series = data[column]
        total = len(series)
        missing_count = int(series.isna().sum())
        missing_ratio = _safe_ratio(missing_count, total)
        normalised_name = str(column).strip().lower()
        rule = normalised_rules.get(normalised_name, {})

        column_result = ColumnQualityResult(
            name=column,
            total=total,
            missing_count=missing_count,
            missing_ratio=missing_ratio,
        )

        warn_missing = rule.get("warn_missing_ratio", default_warn_missing)
        error_missing = rule.get("error_missing_ratio", default_error_missing)
        if error_missing is not None and missing_ratio >= float(error_missing):
            column_result.errors.append(
                f"Missing ratio {missing_ratio:.2%} exceeds error threshold {float(error_missing):.2%}"
            )
        elif warn_missing is not None and missing_ratio >= float(warn_missing):
            column_result.warnings.append(
                f"Missing ratio {missing_ratio:.2%} exceeds warning threshold {float(warn_missing):.2%}"
            )

        min_value = rule.get("min_value")
        max_value = rule.get("max_value")
        numeric_series = None
        if min_value is not None or max_value is not None or anomaly_enabled:
            numeric_series = pd.to_numeric(series, errors="coerce")
        if min_value is not None or max_value is not None:
            out_of_range_mask = pd.Series([False] * len(series), index=series.index)
            if min_value is not None:
                out_of_range_mask |= numeric_series < float(min_value)
            if max_value is not None:
                out_of_range_mask |= numeric_series > float(max_value)
            out_of_range_mask &= numeric_series.notna()
            column_result.out_of_range_count = int(out_of_range_mask.sum())
            if column_result.out_of_range_count:
                message = (
                    f"{column_result.out_of_range_count} values outside range"
                    f" [{min_value}, {max_value}]"
                )
                column_result.errors.append(message)

        if numeric_series is None and anomaly_enabled:
            numeric_series = pd.to_numeric(series, errors="coerce")

        clean_numeric = numeric_series.dropna() if numeric_series is not None else pd.Series([], dtype=float)
        if anomaly_enabled and len(clean_numeric) >= anomaly_min_samples:
            std = clean_numeric.std(ddof=0)
            if std and not math.isclose(std, 0):
                zscores = ((clean_numeric - clean_numeric.mean()).abs()) / std
                anomaly_mask = zscores > anomaly_zscore if anomaly_zscore else pd.Series([False] * len(clean_numeric), index=clean_numeric.index)
                anomaly_count = int(anomaly_mask.sum())
                column_result.anomaly_count = anomaly_count
                if anomaly_count:
                    ratio = _safe_ratio(anomaly_count, len(clean_numeric))
                    message = (
                        f"{anomaly_count} potential anomalies (>{anomaly_zscore} z-score)"
                    )
                    if anomaly_error_ratio and ratio >= anomaly_error_ratio:
                        column_result.errors.append(message)
                    elif anomaly_warn_ratio and ratio >= anomaly_warn_ratio:
                        column_result.warnings.append(message)

        if clean_numeric.size:
            column_result.min_value = float(clean_numeric.min())
            column_result.max_value = float(clean_numeric.max())

        report.column_results[column] = column_result

    # Aggregate column messages into report level lists
    for name, result in report.column_results.items():
        for msg in result.errors:
            report.errors.append(f"{name}: {msg}")
        for msg in result.warnings:
            report.warnings.append(f"{name}: {msg}")

    return report
