"""
Configuration module for TRIAXUS visualization system

This module provides a unified configuration management system following
industry best practices with clear separation of concerns.
"""

from .manager import ConfigManager
from .loader import ConfigLoader
# Schema classes removed - using simple dict-based configuration

__all__ = [
    'ConfigManager',
    'ConfigLoader'
]
