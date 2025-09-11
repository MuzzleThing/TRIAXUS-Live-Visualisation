"""
Map Plotter Helpers for TRIAXUS visualization system

This module provides helper functions for map plotting functionality.
"""

import pandas as pd
import plotly.graph_objects as go
from typing import Dict, Any, Tuple
import logging

from ..core.config import ConfigManager

logger = logging.getLogger(__name__)


class MapHelpers:
    """Helper class for map plotting functionality"""
    _cached_map_plot_config: Dict[str, Any] = None

    # --------------------
    # Internal shared utils
    # --------------------
    @staticmethod
    def _get_defaults() -> Dict[str, Any]:
        map_plot_config = MapHelpers._get_map_plot_config()
        return map_plot_config.get("defaults", {})

    @staticmethod
    def _trace_cls(is_geo: bool):
        return go.Scattergeo if is_geo else go.Scattermapbox

    @staticmethod
    def _add_trajectory_line_core(
        fig: go.Figure, data: pd.DataFrame, line_config: Dict[str, Any], *, is_geo: bool
    ) -> None:
        defaults = MapHelpers._get_defaults()
        trace_cls = MapHelpers._trace_cls(is_geo)
        line_trace = trace_cls(
            lat=data["latitude"],
            lon=data["longitude"],
            mode="lines",
            line=dict(
                color=line_config.get("color", defaults.get("line_color", "#D32F2F")),
                width=line_config.get("width", defaults.get("line_width", 3)),
            ),
            name="TRIAXUS Track",
            hovertemplate="<b>TRIAXUS Track</b><br>"
            + "Lat: %{lat:.4f}<br>"
            + "Lon: %{lon:.4f}<br>"
            + "<extra></extra>",
        )
        fig.add_trace(line_trace)

    @staticmethod
    def _add_data_points_core(
        fig: go.Figure, data: pd.DataFrame, marker_config: Dict[str, Any], *, is_geo: bool
    ) -> None:
        defaults = MapHelpers._get_defaults()
        trace_cls = MapHelpers._trace_cls(is_geo)
        marker_trace = trace_cls(
            lat=data["latitude"],
            lon=data["longitude"],
            mode="markers",
            marker=dict(
                size=marker_config.get("size", defaults.get("marker_size", 8)),
                color=marker_config.get(
                    "current_color", defaults.get("current_color", "#1976D2")
                ),
                opacity=marker_config.get(
                    "opacity", defaults.get("marker_opacity", 0.8)
                ),
            ),
            name="Data Points",
            hovertemplate="<b>Data Point</b><br>"
            + "Lat: %{lat:.4f}<br>"
            + "Lon: %{lon:.4f}<br>"
            + "Time: %{customdata}<br>"
            + "<extra></extra>",
            customdata=data["time"],
        )
        fig.add_trace(marker_trace)

    @staticmethod
    def _add_start_end_markers_core(
        fig: go.Figure, data: pd.DataFrame, marker_config: Dict[str, Any], *, is_geo: bool
    ) -> None:
        if len(data) == 0:
            return
        defaults = MapHelpers._get_defaults()
        trace_cls = MapHelpers._trace_cls(is_geo)

        start_trace = trace_cls(
            lat=[data["latitude"].iloc[0]],
            lon=[data["longitude"].iloc[0]],
            mode="markers",
            marker=dict(
                size=marker_config.get("start_size", defaults.get("start_size", 12)),
                color=marker_config.get(
                    "start_color", defaults.get("start_color", "#43A047")
                ),
                symbol="circle",
            ),
            name="Start",
            hovertemplate="<b>Start Point</b><br>"
            + "Lat: %{lat:.4f}<br>"
            + "Lon: %{lon:.4f}<br>"
            + "<extra></extra>",
        )
        fig.add_trace(start_trace)

        if len(data) > 1:
            end_trace = trace_cls(
                lat=[data["latitude"].iloc[-1]],
                lon=[data["longitude"].iloc[-1]],
                mode="markers",
                marker=dict(
                    size=marker_config.get("end_size", defaults.get("end_size", 12)),
                    color=marker_config.get(
                        "end_color", defaults.get("end_color", "#D32F2F")
                    ),
                    symbol="circle",
                ),
                name="End",
                hovertemplate="<b>End Point</b><br>"
                + "Lat: %{lat:.4f}<br>"
                + "Lon: %{lon:.4f}<br>"
                + "<extra></extra>",
            )
            fig.add_trace(end_trace)

    @staticmethod
    def _get_map_plot_config() -> Dict[str, Any]:
        """Get map plot configuration from ConfigManager"""
        if MapHelpers._cached_map_plot_config is not None:
            return MapHelpers._cached_map_plot_config

        config_manager = ConfigManager()
        config = config_manager.get_external_config()
        if config is not None:
            MapHelpers._cached_map_plot_config = config.get("map_plot", {})
        else:
            # Fallback configuration when config file is missing
            MapHelpers._cached_map_plot_config = {
                "defaults": {
                    "line_color": "#D32F2F",
                    "line_width": 3,
                    "marker_size": 8,
                    "marker_opacity": 0.8,
                    "start_color": "#43A047",
                    "end_color": "#D32F2F",
                    "current_color": "#1976D2",
                    "start_size": 12,
                    "end_size": 12,
                },
                "zoom_levels": {
                    "very_wide": 6,
                    "wide": 8,
                    "medium": 10,
                    "small": 12,
                    "very_small": 14,
                },
                "offline": {
                    "style": "open-street-map",
                    "colors": {
                        "land": "lightgray",
                        "ocean": "lightblue",
                        "lakes": "lightblue",
                        "rivers": "lightblue",
                    },
                    "projection": "equirectangular",
                },
            }

        return MapHelpers._cached_map_plot_config

    @staticmethod
    def add_trajectory_line(
        fig: go.Figure, data: pd.DataFrame, line_config: Dict[str, Any]
    ):
        """Add trajectory line to Mapbox plot"""
        MapHelpers._add_trajectory_line_core(fig, data, line_config, is_geo=False)

    @staticmethod
    def add_trajectory_arrows(
        fig: go.Figure, data: pd.DataFrame, line_config: Dict[str, Any], 
        num_arrows: int = None, is_geo: bool = False
    ):
        """Add simple directional arrows along trajectory.
        
        Args:
            fig: Plotly figure object
            data: DataFrame with latitude and longitude columns
            line_config: Line configuration dictionary
            num_arrows: Number of arrows to display (None for config default)
            is_geo: Whether using scattergeo (True) or scattermapbox (False)
        """
        if len(data) < 2:
            return
            
        # Get arrow count from config or use default
        if num_arrows is None:
            map_config = MapHelpers._get_map_plot_config()
            num_arrows = map_config.get("defaults", {}).get("arrow_count", 5)
            
        # Calculate arrow positions (simple evenly spaced)
        n_points = len(data)
        if n_points < num_arrows:
            indices = list(range(1, n_points))
        else:
            step = max(1, (n_points - 2) // num_arrows)
            indices = list(range(1 + step//2, n_points - 1, step))[:num_arrows]

        if not indices:
            return

        defaults = MapHelpers._get_defaults()
        arrow_lats = [data.iloc[i]['latitude'] for i in indices]
        arrow_lons = [data.iloc[i]['longitude'] for i in indices]

        # Add simple triangle arrows
        trace_func = go.Scattergeo if is_geo else go.Scattermapbox

        marker_kwargs = dict(
            symbol="triangle-up",
            size=14,
            color=line_config.get("color", defaults.get("line_color", "#D32F2F")),
            opacity=0.8,
        )
        # scattergeo supports marker.line; scattermapbox does not
        if is_geo:
            marker_kwargs["line"] = dict(width=1, color="white")

        arrow_trace = trace_func(
            lat=arrow_lats,
            lon=arrow_lons,
            mode="markers",
            marker=marker_kwargs,
            name="Direction",
            showlegend=False,
            hoverinfo="skip"
        )

        fig.add_trace(arrow_trace)

    @staticmethod
    def add_trajectory_line_geo(
        fig: go.Figure, data: pd.DataFrame, line_config: Dict[str, Any]
    ):
        """Add trajectory line to scattergeo plot"""
        MapHelpers._add_trajectory_line_core(fig, data, line_config, is_geo=True)

    @staticmethod
    def add_data_points(
        fig: go.Figure, data: pd.DataFrame, marker_config: Dict[str, Any]
    ):
        """Add data points to Mapbox plot"""
        MapHelpers._add_data_points_core(fig, data, marker_config, is_geo=False)

    @staticmethod
    def add_data_points_geo(
        fig: go.Figure, data: pd.DataFrame, marker_config: Dict[str, Any]
    ):
        """Add data points to scattergeo plot"""
        MapHelpers._add_data_points_core(fig, data, marker_config, is_geo=True)

    @staticmethod
    def add_start_end_markers(
        fig: go.Figure, data: pd.DataFrame, marker_config: Dict[str, Any]
    ):
        """Add start and end markers to Mapbox plot"""
        MapHelpers._add_start_end_markers_core(fig, data, marker_config, is_geo=False)

    @staticmethod
    def add_start_end_markers_geo(
        fig: go.Figure, data: pd.DataFrame, marker_config: Dict[str, Any]
    ):
        """Add start and end markers to scattergeo plot"""
        MapHelpers._add_start_end_markers_core(fig, data, marker_config, is_geo=True)

    @staticmethod
    def calculate_zoom_level(
        lat_span: float, lon_span: float, zoom_config: Dict[str, Any]
    ) -> int:
        """Calculate appropriate zoom level based on data span"""
        max_span = max(lat_span, lon_span)
        auto_zoom = zoom_config.get("auto_zoom", {})

        # Get zoom level mappings from config
        map_plot_config = MapHelpers._get_map_plot_config()
        zoom_levels = map_plot_config.get(
            "zoom_levels",
            {"very_wide": 6, "wide": 8, "medium": 10, "small": 12, "very_small": 14},
        )

        if max_span > auto_zoom.get("very_wide", 2.0):
            return zoom_levels.get("very_wide", 6)
        elif max_span > auto_zoom.get("wide", 1.0):
            return zoom_levels.get("wide", 8)
        elif max_span > auto_zoom.get("medium", 0.5):
            return zoom_levels.get("medium", 10)
        elif max_span > auto_zoom.get("small", 0.2):
            return zoom_levels.get("small", 12)
        else:
            return zoom_levels.get("very_small", 14)

    @staticmethod
    def get_style_config(
        map_config: Dict[str, Any], map_style: str
    ) -> Tuple[Dict[str, str], str]:
        """Get style configuration for scattergeo plots"""
        # Get offline map settings from config
        map_plot_config = MapHelpers._get_map_plot_config()
        offline_config = map_plot_config.get("offline", {})

        # Get colors from config file
        colors = map_config.get(
            "colors",
            offline_config.get(
                "colors",
                {
                    "land": "lightgray",
                    "ocean": "lightblue",
                    "lakes": "lightblue",
                    "rivers": "lightblue",
                },
            ),
        )

        # Get projection from config file
        projection = map_config.get(
            "projection", offline_config.get("projection", "equirectangular")
        )

        return colors, projection

    @staticmethod
    def is_offline_map_style(map_style: str) -> bool:
        """Check if the map style is an offline style"""
        map_plot_config = MapHelpers._get_map_plot_config()
        offline_cfg = map_plot_config.get("offline", {})
        # Support single string or list of styles in config
        offline_style = offline_cfg.get("style", "open-street-map")
        if isinstance(offline_style, list):
            return map_style in offline_style
        return map_style == offline_style
