"""
TRIAXUS Visualization System

A comprehensive visualization system for TRIAXUS oceanographic data.
"""

from .core import ConfigManager, DataValidator, ErrorHandler
from .plotters import (
    TimeSeriesPlotter,
    DepthProfilePlotter,
    ContourPlotter,
    MapPlotter,
    PlotterFactory,
)
from .data import DataProcessor
from .utils import HTMLGenerator
from .visualizer import TriaxusVisualizer

# Main API
__all__ = [
    "TriaxusVisualizer",
    "ConfigManager",
    "DataValidator",
    "ErrorHandler",
    "TimeSeriesPlotter",
    "DepthProfilePlotter",
    "ContourPlotter",
    "MapPlotter",
    "PlotterFactory",
    "DataProcessor",
    "HTMLGenerator",
]

# Version information
__version__ = "1.0.0"
__author__ = "TRIAXUS Visualization Team"
__description__ = "TRIAXUS Oceanographic Data Visualization System"
