"""
Configuration module for TRIAXUS visualization system

This module provides a unified configuration management system following
industry best practices with clear separation of concerns.
"""

from .manager import ConfigManager

# Schema classes removed - using simple dict-based configuration
# ConfigLoader removed - using dynaconf for configuration management

__all__ = ["ConfigManager"]
