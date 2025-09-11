"""
Data Configuration Manager for TRIAXUS visualization system

This module handles data-related configurations including variables,
validation, and data generation settings.
"""

from typing import Dict, Any, List, Optional
import logging

from dynaconf import Dynaconf

logger = logging.getLogger(__name__)


class DataConfigManager:
    """Manages data-related configurations"""

    def __init__(self, settings: Dynaconf, yaml_config: Optional[Dict] = None):
        """
        Initialize DataConfigManager

        Args:
            settings: Dynaconf settings instance
            yaml_config: Fallback YAML configuration
        """
        self.settings = settings
        self._yaml_config = yaml_config

    def get_data_config(self) -> Dict[str, Any]:
        """Get data configuration"""
        return {
            "variables": [
                "time",
                "depth",
                "latitude",
                "longitude",
                "tv290C",
                "sal00",
                "sbeox0Mm_L",
                "flECO-AFL",
                "ph",
            ],
            "required_variables": ["time", "depth", "latitude", "longitude"],
        }

    def get_validation_config(self) -> Dict[str, Any]:
        """Get validation configuration"""
        config = self.settings.get("data.validation", {})
        if not config and self._yaml_config:
            config = self._yaml_config.get("data", {}).get("validation", {})
        return config

    def get_data_generation_config(self) -> Dict[str, Any]:
        """Get data generation configuration"""
        config = self.settings.get("data_generation", {})
        if not config and self._yaml_config:
            config = self._yaml_config.get("data_generation", {})
        return config

    def get_data_sampling_config(self) -> Dict[str, Any]:
        """Get data sampling configuration"""
        config = self.settings.get("data_sampling", {})
        if not config and self._yaml_config:
            config = self._yaml_config.get("data_sampling", {})
        return config

    def get_test_data_config(self) -> Dict[str, Any]:
        """Get test data configuration"""
        config = self.settings.get("data.test_data", {})
        if not config and self._yaml_config:
            config = self._yaml_config.get("data", {}).get("test_data", {})
        return config

    def get_performance_config(self) -> Dict[str, Any]:
        """Get performance configuration"""
        config = self.settings.get("performance", {})
        if not config and self._yaml_config:
            config = self._yaml_config.get("performance", {})
        return config
