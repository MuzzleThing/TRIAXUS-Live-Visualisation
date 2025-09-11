"""
Plot Configuration Manager for TRIAXUS visualization system

This module handles plot-specific configurations including dimensions,
styling, and plot-type specific settings.
"""

from typing import Dict, Any, List, Optional
import logging

from dynaconf import Dynaconf

logger = logging.getLogger(__name__)


class PlotConfigManager:
    """Manages plot-specific configurations"""

    def __init__(self, settings: Dynaconf, yaml_config: Optional[Dict] = None):
        """
        Initialize PlotConfigManager

        Args:
            settings: Dynaconf settings instance
            yaml_config: Fallback YAML configuration
        """
        self.settings = settings
        self._yaml_config = yaml_config
        self._current_plot_type = "time_series"

    def get_available_plot_types(self) -> List[str]:
        """Get list of available plot types"""
        return ["default", "time_series", "depth_profile", "contour", "map"]

    def get_current_plot_type(self) -> str:
        """Get current plot type"""
        return self._current_plot_type

    def set_plot_type(self, plot_type: str):
        """Set current plot type"""
        available_types = self.get_available_plot_types()
        if plot_type in available_types:
            self._current_plot_type = plot_type
            logger.info(f"Plot type changed to: {plot_type}")
        else:
            logger.warning(
                f"Plot type '{plot_type}' not available. Available types: {available_types}"
            )

    def get_plot_config(self, plot_type: str = None) -> Dict[str, Any]:
        """Get plot configuration for plot type"""
        if plot_type is None:
            plot_type = self._current_plot_type

        # Try dynaconf first, then YAML fallback
        config = self.settings.get("plot", {})
        if not config and self._yaml_config:
            config = self._yaml_config.get("plot", {})
        return config

    def get_plot_dimensions(self) -> Dict[str, int]:
        """Get plot dimensions from configuration"""
        plot_config = self.get_plot_config()
        return {
            "width": plot_config.get("default_width", 800),
            "height": plot_config.get("default_height", 600),
        }

    def get_line_config(self) -> Dict[str, Any]:
        """Get line configuration"""
        plot_config = self.get_plot_config()
        return {"width": plot_config.get("line", {}).get("default_width", 2)}

    def get_marker_config(self) -> Dict[str, Any]:
        """Get marker configuration"""
        plot_config = self.get_plot_config()
        return {"size": plot_config.get("marker", {}).get("default_size", 4)}

    # Plot-specific configurations
    def get_time_series_config(self) -> Dict[str, Any]:
        """Get time series plot configuration"""
        return self.settings.get("time_series", {})

    def get_contour_config(self) -> Dict[str, Any]:
        """Get contour plot configuration"""
        return self.settings.get("contour", {})

    def get_depth_profile_config(self) -> Dict[str, Any]:
        """Get depth profile plot configuration"""
        return self.settings.get("depth_profile", {})

    def get_map_config(self) -> Dict[str, Any]:
        """Get map plot configuration"""
        return self.settings.get("map", {})

    def get_mapbox_config(self) -> Dict[str, Any]:
        """Get Mapbox configuration"""
        return self.settings.get("mapbox", {})

    def get_map_plot_config(self) -> Dict[str, Any]:
        """Get map plot specific configuration"""
        return self.settings.get("map_plot", {})
