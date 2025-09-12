"""
Map Plotter for TRIAXUS visualization system

This module provides map plotting functionality for TRIAXUS data.
"""

import pandas as pd
import plotly.graph_objects as go
from typing import Optional, Dict, Any, List
import logging

from ..core.base_plotter import BasePlotter
from ..core.config import ConfigManager
from .map_helpers import MapHelpers


class MapPlotter(BasePlotter):
    """Map plotter for TRIAXUS visualization system"""

    def __init__(self, config_manager: ConfigManager):
        """
        Initialize MapPlotter

        Args:
            config_manager: Configuration manager instance
        """
        super().__init__(config_manager)
        self.logger = logging.getLogger(__name__)

    def _get_map_config(self) -> Dict[str, Any]:
        """Get map configuration from config manager"""
        return self.config_manager.get_external_config().get("map", {})

    def _get_mapbox_config(self) -> Dict[str, Any]:
        """Get Mapbox configuration from config manager"""
        return self.config_manager.get_mapbox_config() or {}

    def _get_line_config(self) -> Dict[str, Any]:
        """Get line configuration for map plots"""
        map_config = self._get_map_config()
        return map_config.get("line", {"width": 3, "color": "#D32F2F"})

    def _get_marker_config(self) -> Dict[str, Any]:
        """Get marker configuration for map plots"""
        map_config = self._get_map_config()
        return map_config.get(
            "marker",
            {
                "size": 8,
                "opacity": 0.8,
                "start_color": "#43A047",
                "end_color": "#D32F2F",
                "current_color": "#1976D2",
                "start_size": 12,
                "end_size": 12,
            },
        )

    def _get_zoom_config(self) -> Dict[str, Any]:
        """Get zoom configuration for map plots"""
        map_config = self._get_map_config()
        return map_config.get("zoom", {})

    def _get_margin_config(self) -> Dict[str, Any]:
        """Get margin configuration for map plots"""
        map_config = self._get_map_config()
        return map_config.get("margin", {"left": 0, "right": 0, "top": 60, "bottom": 0})

    def _get_dimensions(self) -> tuple:
        """Get map dimensions"""
        map_config = self._get_map_config()
        width = map_config.get("width", 800)
        height = map_config.get("height", 600)
        return width, height

    # --------------------
    # Shared geo view helpers
    # --------------------
    def _compute_center(self, data: pd.DataFrame) -> tuple:
        """Compute center latitude and longitude from data."""
        center_lat = data["latitude"].mean()
        center_lon = data["longitude"].mean()
        return center_lat, center_lon

    def _compute_bounds_with_padding(self, data: pd.DataFrame, padding: float) -> tuple:
        """Compute lat/lon axis ranges with padding."""
        lat_min, lat_max = data["latitude"].min(), data["latitude"].max()
        lon_min, lon_max = data["longitude"].min(), data["longitude"].max()
        lat_padding = (lat_max - lat_min) * padding
        lon_padding = (lon_max - lon_min) * padding
        lataxis_range = [lat_min - lat_padding, lat_max + lat_padding]
        lonaxis_range = [lon_min - lon_padding, lon_max + lon_padding]
        return lataxis_range, lonaxis_range

    def _get_dimensions_and_margins(self) -> tuple:
        """Get figure width/height and margin config."""
        width, height = self._get_dimensions()
        margin_config = self._get_margin_config()
        return width, height, margin_config

    def _calculate_zoom_level(self, lat_span: float, lon_span: float) -> int:
        """Calculate appropriate zoom level based on data span"""
        zoom_config = self._get_zoom_config()
        return MapHelpers.calculate_zoom_level(lat_span, lon_span, zoom_config)

    def _get_style_config(self, map_style: str) -> tuple:
        """Get style configuration for scattergeo plots"""
        map_config = self._get_map_config()
        return MapHelpers.get_style_config(map_config, map_style)

    def get_plot_type(self) -> str:
        """Get the plot type identifier"""
        return "map"

    def get_required_columns(self) -> List[str]:
        """Get required data columns for map plot"""
        return ["latitude", "longitude", "time"]

    def create_plot(self, data: pd.DataFrame, **kwargs) -> go.Figure:
        """
        Create map plot

        Args:
            data: Input data
            **kwargs: Additional plot parameters

        Returns:
            Plotly figure object
        """
        try:
            # Validate and process data
            self.validate_data(data)
            processed_data = self.process_data(data)

            # Check if Mapbox token is available or offline mode is enabled
            mapbox_config = self._get_mapbox_config()
            map_style = kwargs.get(
                "map_style", mapbox_config.get("style", "satellite-streets")
            )

            # Check if we should use Mapbox (has token and not offline mode)
            if mapbox_config.get("token") and not mapbox_config.get(
                "offline_mode", False
            ):
                return self._create_mapbox_plot(processed_data, **kwargs)
            else:
                # Use offline map styles or scattergeo fallback
                if MapHelpers.is_offline_map_style(map_style):
                    self.logger.info(f"Using offline map style: {map_style}")
                    return self._create_offline_map_plot(processed_data, **kwargs)
                else:
                    self.logger.warning(
                        "Mapbox token not provided, using scattergeo fallback"
                    )
                    return self._create_scattergeo_plot(processed_data, **kwargs)

        except Exception as e:
            self.logger.error(f"Failed to create map plot: {e}")
            raise

    def _create_mapbox_plot(self, data: pd.DataFrame, **kwargs) -> go.Figure:
        """Create Mapbox plot"""
        fig = go.Figure()

        # Add trajectory line
        if len(data) > 1:
            line_config = self._get_line_config()
            MapHelpers.add_trajectory_line(fig, data, line_config)
            # Add directional arrows
            MapHelpers.add_trajectory_arrows(fig, data, line_config, is_geo=False)

        # Add data points
        marker_config = self._get_marker_config()
        MapHelpers.add_data_points(fig, data, marker_config)

        # Add start and end markers
        MapHelpers.add_start_end_markers(fig, data, marker_config)

        # Update layout
        self._update_mapbox_layout(fig, data, **kwargs)

        return fig

    def _create_offline_map_plot(self, data: pd.DataFrame, **kwargs) -> go.Figure:
        """Create offline map plot using Plotly's built-in map styles"""
        fig = go.Figure()

        # Add common geo traces (trajectory, arrows, points, start/end)
        self._add_common_geo_traces(fig, data)

        # Update layout with offline map style
        self._update_offline_map_layout(fig, data, **kwargs)

        return fig

    def _create_scattergeo_plot(self, data: pd.DataFrame, **kwargs) -> go.Figure:
        """Create scattergeo plot (fallback)"""
        fig = go.Figure()

        # Add common geo traces (trajectory, arrows, points, start/end)
        self._add_common_geo_traces(fig, data)

        # Update layout
        self._update_scattergeo_layout(fig, data, **kwargs)

        return fig

    def _add_common_geo_traces(self, fig: go.Figure, data: pd.DataFrame) -> None:
        """Add common traces for geo-based plots (offline and scattergeo)."""
        # Trajectory + arrows
        if len(data) > 1:
            line_config = self._get_line_config()
            MapHelpers.add_trajectory_line_geo(fig, data, line_config)
            MapHelpers.add_trajectory_arrows(fig, data, line_config, is_geo=True)

        # Points
        marker_config = self._get_marker_config()
        MapHelpers.add_data_points_geo(fig, data, marker_config)

        # Start/End markers
        MapHelpers.add_start_end_markers_geo(fig, data, marker_config)

    def _update_mapbox_layout(self, fig: go.Figure, data: pd.DataFrame, **kwargs):
        """Update layout for Mapbox plot"""
        mapbox_config = self._get_mapbox_config()
        map_config = self._get_map_config()

        # Get title
        title = kwargs.get("title", "TRIAXUS Map Plot")

        # Get map style
        map_style = kwargs.get(
            "map_style",
            mapbox_config.get(
                "style", map_config.get("default_style", "satellite-streets")
            ),
        )

        # Calculate center and zoom
        center_lat = data["latitude"].mean()
        center_lon = data["longitude"].mean()

        # Calculate zoom level
        lat_span = data["latitude"].max() - data["latitude"].min()
        lon_span = data["longitude"].max() - data["longitude"].min()
        zoom_level = self._calculate_zoom_level(lat_span, lon_span)

        # Get dimensions
        width, height = self._get_dimensions()

        # Get margin configuration
        margin_config = self._get_margin_config()

        # Update layout
        fig.update_layout(
            title=title,
            height=height,
            width=width,
            template=self._get_plotly_template(),
            plot_bgcolor=self.get_theme_layout().get("background_color", "white"),
            paper_bgcolor=self.get_theme_layout().get("background_color", "white"),
            font=dict(
                family=self.get_theme_layout().get("font_family", "Arial, sans-serif"),
                color=self.get_theme_layout().get("text_color", "black"),
            ),
            mapbox=dict(
                accesstoken=mapbox_config.get("token"),
                style=map_style,
                center=dict(lat=center_lat, lon=center_lon),
                zoom=zoom_level,
            ),
            margin=dict(
                l=margin_config.get("left", 0),
                r=margin_config.get("right", 0),
                t=margin_config.get("top", 60),
                b=margin_config.get("bottom", 0),
            ),
        )

    def _update_offline_map_layout(self, fig: go.Figure, data: pd.DataFrame, **kwargs):
        """Update layout for offline map plot"""
        map_config = self._get_map_config()

        title = kwargs.get("title", "TRIAXUS Map Plot")

        # Compute center and bounds
        center_lat, center_lon = self._compute_center(data)
        padding = map_config.get("padding", 0.2)
        lataxis_range, lonaxis_range = self._compute_bounds_with_padding(data, padding)

        # Dimensions and margins
        width, height, margin_config = self._get_dimensions_and_margins()

        # Update layout with offline map style
        fig.update_layout(
            title=title,
            height=height,
            width=width,
            template=self._get_plotly_template(),
            plot_bgcolor=self.get_theme_layout().get("background_color", "white"),
            paper_bgcolor=self.get_theme_layout().get("background_color", "white"),
            font=dict(
                family=self.get_theme_layout().get("font_family", "Arial, sans-serif"),
                color=self.get_theme_layout().get("text_color", "black"),
            ),
            geo=dict(
                projection_type="equirectangular",
                center=dict(lat=center_lat, lon=center_lon),
                lataxis=dict(range=lataxis_range),
                lonaxis=dict(range=lonaxis_range),
                showland=True,
                landcolor="lightgray",
                showocean=True,
                oceancolor="lightblue",
                showlakes=True,
                lakecolor="lightblue",
                showrivers=True,
                rivercolor="lightblue",
            ),
            margin=dict(
                l=margin_config.get("left", 0),
                r=margin_config.get("right", 0),
                t=margin_config.get("top", 60),
                b=margin_config.get("bottom", 0),
            ),
        )

    def _update_scattergeo_layout(self, fig: go.Figure, data: pd.DataFrame, **kwargs):
        """Update layout for scattergeo plot"""
        map_config = self._get_map_config()

        title = kwargs.get("title", "TRIAXUS Map Plot")

        # Compute center and bounds
        center_lat, center_lon = self._compute_center(data)
        padding = map_config.get("padding", 0.2)
        lataxis_range, lonaxis_range = self._compute_bounds_with_padding(data, padding)

        # Get map style (used for colors/projection resolution)
        map_style = kwargs.get(
            "map_style", map_config.get("default_style", "satellite-streets")
        )

        # Get style configuration
        style_colors, projection_type = self._get_style_config(map_style)

        # Dimensions and margins
        width, height, margin_config = self._get_dimensions_and_margins()

        # Update layout
        fig.update_layout(
            title=title,
            height=height,
            width=width,
            template=self._get_plotly_template(),
            plot_bgcolor=self.get_theme_layout().get("background_color", "white"),
            paper_bgcolor=self.get_theme_layout().get("background_color", "white"),
            font=dict(
                family=self.get_theme_layout().get("font_family", "Arial, sans-serif"),
                color=self.get_theme_layout().get("text_color", "black"),
            ),
            geo=dict(
                projection_type=projection_type,
                center=dict(lat=center_lat, lon=center_lon),
                lataxis=dict(range=lataxis_range),
                lonaxis=dict(range=lonaxis_range),
                showland=True,
                landcolor=style_colors.get("land", "lightgray"),
                showocean=True,
                oceancolor=style_colors.get("ocean", "lightblue"),
                showlakes=True,
                lakecolor=style_colors.get("lakes", "lightblue"),
                showrivers=True,
                rivercolor=style_colors.get("rivers", "lightblue"),
            ),
            margin=dict(
                l=margin_config.get("left", 0),
                r=margin_config.get("right", 0),
                t=margin_config.get("top", 60),
                b=margin_config.get("bottom", 0),
            ),
        )
