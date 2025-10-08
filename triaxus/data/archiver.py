"""
Data archiving utilities for TRIAXUS.

Provides helpers to persist processed datasets to disk (and optionally the
database) alongside quality-control metadata.
"""

from __future__ import annotations

import json
import logging
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any

import pandas as pd

from ..core.config import ConfigManager
from .processor import DataProcessor
from .quality_control import QualityReport
from .database_source import DatabaseDataSource
from ..database.repositories import DataSourceRepository
from ..database.models import DataSource


class DataArchiver:
    """Coordinate quality control and archival storage of datasets"""

    def __init__(
        self,
        config_manager: Optional[ConfigManager] = None,
        data_processor: Optional[DataProcessor] = None,
        database_source: Optional[DatabaseDataSource] = None,
        archive_dir: Optional[Path] = None,
    ):
        self.logger = logging.getLogger(__name__)
        self.config_manager = config_manager or ConfigManager()
        self.archiving_config = self.config_manager.get_archiving_config() or {}
        self.data_processor = data_processor or DataProcessor(self.config_manager)
        self._database_source = database_source

        directory_setting = archive_dir or self.archiving_config.get("directory", "archive")
        directory_path = Path(directory_setting)
        if not directory_path.is_absolute():
            directory_path = Path.cwd() / directory_path
        self.archive_dir = directory_path

        if self.archiving_config.get("ensure_directory", True):
            self.archive_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def archive(
        self,
        data: pd.DataFrame,
        source_name: str,
        processing_config: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Run quality control, persist artefacts, and return a summary."""
        if data is None or data.empty:
            raise ValueError("Cannot archive empty dataset")

        metadata = dict(metadata) if metadata else {}

        processed = self.data_processor.process(
            data, processing_config=processing_config, run_quality_checks=True
        )
        report = self.data_processor.get_last_quality_report()
        if report is None:
            report = self.data_processor.run_quality_checks(processed)

        archive_info = self._write_to_filesystem(processed, source_name, report, metadata, processing_config)
        database_result = self._store_in_database(processed, source_name, metadata)

        return {
            "row_count": len(processed),
            "database_stored": database_result,
            "archive": archive_info,
            "quality_report": report.to_dict() if report else None,
        }

    # ------------------------------------------------------------------
    # Convenience methods for testing
    # ------------------------------------------------------------------
    def archive_to_csv(self, data: pd.DataFrame, output_file: str, compress: bool = False) -> Dict[str, Any]:
        """Archive data to CSV file"""
        # Temporarily override archive directory for this operation
        original_dir = self.archive_dir
        try:
            output_path = Path(output_file)
            self.archive_dir = output_path.parent
            try:
                self.archive_dir.mkdir(parents=True, exist_ok=True)
            except (OSError, PermissionError) as e:
                # If we can't create directory, raise appropriate error
                raise ValueError(f"Cannot create output directory {self.archive_dir}: {e}")
            
            config = {"write_files": True, "file_format": "csv.gz" if compress else "csv", "include_timestamp": False}
            result = self.archive(data, output_path.stem, processing_config=config)
            return result
        finally:
            self.archive_dir = original_dir

    def archive_quality_report(self, quality_report: Any, output_file: str) -> Dict[str, Any]:
        """Archive quality report"""
        # Temporarily override archive directory for this operation
        original_dir = self.archive_dir
        try:
            output_path = Path(output_file)
            self.archive_dir = output_path.parent
            self.archive_dir.mkdir(parents=True, exist_ok=True)
            
            # Create dummy data for quality report archiving
            dummy_data = pd.DataFrame({"dummy": [1, 2, 3]})
            config = {"write_files": True, "include_timestamp": False}
            return self.archive(dummy_data, output_path.stem, processing_config=config, metadata={"quality_report": quality_report})
        finally:
            self.archive_dir = original_dir

    def archive_metadata(self, metadata: Dict[str, Any], output_file: str) -> Dict[str, Any]:
        """Archive metadata"""
        # Temporarily override archive directory for this operation
        original_dir = self.archive_dir
        try:
            output_path = Path(output_file)
            self.archive_dir = output_path.parent
            self.archive_dir.mkdir(parents=True, exist_ok=True)
            
            dummy_data = pd.DataFrame({"dummy": [1, 2, 3]})
            config = {"write_files": True, "include_timestamp": False}
            return self.archive(dummy_data, output_path.stem, processing_config=config, metadata=metadata)
        finally:
            self.archive_dir = original_dir

    def archive_to_database(self, data: pd.DataFrame, source_name: str) -> Dict[str, Any]:
        """Archive data to database only"""
        config = {"write_files": False}
        return self.archive(data, source_name, processing_config=config)

    def archive_comprehensive(self, data: pd.DataFrame, source_name: str,
                            quality_report: Any = None, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Comprehensive archiving with all options"""
        config = {"write_files": True, "include_timestamp": False}
        return self.archive(data, source_name, processing_config=config, metadata=metadata)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _write_to_filesystem(
        self,
        data: pd.DataFrame,
        source_name: str,
        report: Optional[QualityReport],
        metadata: Dict[str, Any],
        processing_config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Optional[str]]:
        if not self.archiving_config.get("write_files", True):
            return {}

        base_name = self._build_base_name(source_name, processing_config)
        file_format = str(self.archiving_config.get("file_format", "csv")).lower()

        if file_format != "csv":
            raise ValueError("Only CSV archiving is currently supported")

        compress = bool(self.archiving_config.get("compress", True))
        compression = "gzip" if compress else None
        suffix = ".csv.gz" if compress else ".csv"
        data_path = self.archive_dir / f"{base_name}{suffix}"
        data.to_csv(data_path, index=False, compression=compression)

        report_path = None
        if self.archiving_config.get("write_quality_report", True) and report:
            report_path = self.archive_dir / f"{base_name}_quality.json"
            report_path.write_text(
                json.dumps(report.to_dict(), indent=2),
                encoding="utf-8",
            )

        metadata_path = None
        if metadata:
            metadata_payload = dict(metadata)
            metadata_payload.setdefault("row_count", len(data))
            if report:
                metadata_payload.setdefault(
                    "quality_summary",
                    {
                        "warnings": report.warnings,
                        "errors": report.errors,
                        "duplicate_ratio": report.duplicate_ratio,
                    },
                )
            metadata_path = self.archive_dir / f"{base_name}_metadata.json"
            metadata_path.write_text(
                json.dumps(metadata_payload, indent=2, default=str),
                encoding="utf-8",
            )

        return {
            "data_path": str(data_path),
            "quality_report_path": str(report_path) if report_path else None,
            "metadata_path": str(metadata_path) if metadata_path else None,
        }

    def _store_in_database(
        self,
        data: pd.DataFrame,
        source_name: str,
        metadata: Dict[str, Any],
    ) -> bool:
        if not self.archiving_config.get("store_in_database", True):
            return False

        db_source = self._get_database_source()
        if not db_source or not db_source.is_available():
            self.logger.info("Database unavailable for archiving; skipping persistence")
            return False

        try:
            stored = db_source.store_data(data, source_file=source_name)
        except Exception as exc:
            self.logger.warning(f"Failed to persist data to database: {exc}")
            return False

        if not stored:
            return False

        try:
            repository = DataSourceRepository(db_source.connection_manager)
            filename = metadata.get("filename", source_name)
            
            # Check if data source already exists
            existing = repository.get_by_filename(filename)
            if existing:
                self.logger.info(f"Data source {filename} already exists, updating status")
                repository.update_status(filename, metadata.get("status", "archived"), 
                                       metadata.get("total_records", len(data)))
            else:
                # Create new data source record
                record = DataSource(
                    filename=filename,
                    file_type=metadata.get("file_type", "DATAFRAME"),
                    file_size=metadata.get("file_size"),
                    file_hash=metadata.get("file_hash"),
                    total_records=metadata.get("total_records", len(data)),
                    processing_status=metadata.get("status", "archived"),
                )
                repository.create(record)
        except Exception as exc:
            self.logger.warning(
                f"Data archived but metadata could not be recorded: {exc}"
            )

        return True

    def _get_database_source(self) -> Optional[DatabaseDataSource]:
        if self._database_source is None and self.archiving_config.get(
            "store_in_database", True
        ):
            try:
                self._database_source = DatabaseDataSource()
            except Exception as exc:
                self.logger.warning(
                    f"Failed to initialise database data source for archiving: {exc}"
                )
                self._database_source = None
        return self._database_source

    def _build_base_name(self, source_name: str, processing_config: Optional[Dict[str, Any]] = None) -> str:
        sanitized = re.sub(r"[^A-Za-z0-9_-]+", "_", source_name.strip().lower()) or "dataset"
        
        # Check both processing_config and archiving_config for include_timestamp
        include_timestamp = True
        if processing_config and "include_timestamp" in processing_config:
            include_timestamp = processing_config["include_timestamp"]
        elif "include_timestamp" in self.archiving_config:
            include_timestamp = self.archiving_config["include_timestamp"]
            
        if include_timestamp:
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            return f"{sanitized}_{timestamp}"
        return sanitized
