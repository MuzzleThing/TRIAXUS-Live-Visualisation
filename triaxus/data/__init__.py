"""
TRIAXUS Data Module

This module contains data processing, validation, archiving, and plot
test data generation utilities.
"""

from .processor import DataProcessor
from .sampler import DataSampler
from .simple_data_generator import (
    PlotTestDataGenerator,
    create_plot_test_data,
    create_daily_plot_data,
    create_quick_plot_data,
    create_map_trajectory_data,
)
from .quality_control import ColumnQualityResult, QualityReport, generate_quality_report
from .archiver import DataArchiver
from .cnv_reader import CNVFileReader
from .cnv_batch_processor import (
    CNVBatchProcessor,
    main as process_cnv_files, 
    test_cnv_reader, 
    get_cnv_source_directory
)
from .cnv_realtime_processor import CNVRealtimeProcessor

__all__ = [
    "DataProcessor",
    "DataSampler",
    "PlotTestDataGenerator",
    "create_plot_test_data",
    "create_daily_plot_data",
    "create_quick_plot_data",
    "create_map_trajectory_data",
    "ColumnQualityResult",
    "QualityReport",
    "generate_quality_report",
    "DataArchiver",
    "CNVFileReader",
    "CNVBatchProcessor",
    "CNVRealtimeProcessor",
    "process_cnv_files",
    "test_cnv_reader",
    "get_cnv_source_directory",
]
