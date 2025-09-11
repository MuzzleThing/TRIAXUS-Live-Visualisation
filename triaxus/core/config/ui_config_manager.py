"""
UI Configuration Manager for TRIAXUS visualization system

This module handles UI-related configurations including fonts,
annotations, status displays, and HTML settings.
"""

from typing import Dict, Any, Optional
import logging

from dynaconf import Dynaconf

logger = logging.getLogger(__name__)


class UIConfigManager:
    """Manages UI-related configurations"""

    def __init__(self, settings: Dynaconf, yaml_config: Optional[Dict] = None):
        """
        Initialize UIConfigManager

        Args:
            settings: Dynaconf settings instance
            yaml_config: Fallback YAML configuration
        """
        self.settings = settings
        self._yaml_config = yaml_config

    def get_font_config(self) -> Dict[str, Any]:
        """Get font configuration"""
        config = self.settings.get("font", {})
        if not config and self._yaml_config:
            config = self._yaml_config.get("font", {})
        return config

    def get_annotation_config(self) -> Dict[str, Any]:
        """Get annotation configuration"""
        config = self.settings.get("annotations", {})
        if not config and self._yaml_config:
            config = self._yaml_config.get("annotations", {})
        return config

    def get_status_config(self) -> Dict[str, Any]:
        """Get status configuration"""
        config = self.settings.get("status", {})
        if not config and self._yaml_config:
            config = self._yaml_config.get("status", {})
        return config

    def get_html_config(self) -> Dict[str, Any]:
        """Get HTML configuration"""
        config = self.settings.get("html", {})
        if not config and self._yaml_config:
            config = self._yaml_config.get("html", {})
        return config

    def get_files_config(self) -> Dict[str, Any]:
        """Get file I/O configuration"""
        config = self.settings.get("files", {})
        if not config and self._yaml_config:
            config = self._yaml_config.get("files", {})
        return config

    def get_statistics_config(self) -> Dict[str, Any]:
        """Get statistics configuration"""
        config = self.settings.get("statistics", {})
        if not config and self._yaml_config:
            config = self._yaml_config.get("statistics", {})
        return config

    def get_depth_zones_config(self) -> list:
        """Get depth zones configuration"""
        config = self.settings.get("depth_zones", [])
        if not config and self._yaml_config:
            config = self._yaml_config.get("depth_zones", [])
        return config
