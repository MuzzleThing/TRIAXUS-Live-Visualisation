"""
Data Configuration Manager for TRIAXUS visualization system

This module handles data-related configurations including variables,
validation, and data generation settings.
"""

from typing import Dict, Any, Optional
import logging

from dynaconf import Dynaconf

logger = logging.getLogger(__name__)


class DataConfigManager:
    """Manages data-related configurations"""

    DEFAULT_VARIABLES = [
        "time",
        "depth",
        "latitude",
        "longitude",
        "tv290c",
        "sal00",
        "sbeox0mm_l",
        "fleco_afl",
        "ph",
    ]

    DEFAULT_REQUIRED = ["time", "depth", "latitude", "longitude"]

    def __init__(self, settings: Dynaconf, yaml_config: Optional[Dict] = None):
        """Initialize DataConfigManager"""
        self.settings = settings
        self._yaml_config = yaml_config

    def _get_section(self, key: str) -> Dict[str, Any]:
        """Safely fetch configuration section from Dynaconf or YAML fallback"""
        config = self.settings.get(key, {}) if self.settings else {}
        if not config and self._yaml_config:
            config = self._yaml_config.get(key, {})
        if isinstance(config, dict):
            return dict(config)
        return {}

    def get_data_config(self) -> Dict[str, Any]:
        """Get data configuration"""
        config = self._get_section("data")

        variables = config.get("variables")
        if isinstance(variables, list):
            config["variables"] = [str(item).strip().lower() for item in variables]
        else:
            config["variables"] = list(self.DEFAULT_VARIABLES)

        required = config.get("required_variables")
        if isinstance(required, list):
            config["required_variables"] = [str(item).strip().lower() for item in required]
        else:
            config["required_variables"] = list(self.DEFAULT_REQUIRED)

        return config

    def get_validation_config(self) -> Dict[str, Any]:
        """Get validation configuration"""
        validation = self.get_data_config().get("validation", {})
        return validation if isinstance(validation, dict) else {}

    def get_data_generation_config(self) -> Dict[str, Any]:
        """Get data generation configuration"""
        return self._get_section("data_generation")

    def get_data_sampling_config(self) -> Dict[str, Any]:
        """Get data sampling configuration"""
        return self._get_section("data_sampling")

    def get_test_data_config(self) -> Dict[str, Any]:
        """Get test data configuration"""
        test_config = self.get_data_config().get("test_data", {})
        if not test_config and self._yaml_config:
            test_config = self._yaml_config.get("data", {}).get("test_data", {})
        return test_config if isinstance(test_config, dict) else {}

    def get_performance_config(self) -> Dict[str, Any]:
        """Get performance configuration"""
        return self._get_section("performance")

    def get_archiving_config(self) -> Dict[str, Any]:
        """Get archiving configuration"""
        return self._get_section("archiving")
