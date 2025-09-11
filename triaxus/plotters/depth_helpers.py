"""
Depth Profile Plotter Helpers for TRIAXUS visualization system

This module provides helper functions for depth profile plotting functionality.
"""

import pandas as pd
import plotly.graph_objects as go
from typing import List, Dict, Any
import logging

from ..core.config import ConfigManager

logger = logging.getLogger(__name__)


class DepthHelpers:
    """Helper class for depth profile plotting functionality"""

    @staticmethod
    def _get_depth_config() -> Dict[str, Any]:
        """Get depth profile configuration from ConfigManager"""
        config_manager = ConfigManager()
        config = config_manager.get_external_config()
        if config is not None:
            return config.get("depth_profile", {})
        else:
            # Fallback configuration when config file is missing
            return {
                "thermocline": {
                    "variable_name": "tv290C",
                    "min_data_points": 10,
                    "line_style": "dash",
                    "line_color": "red",
                    "annotation_position": "top right",
                },
                "annotations": {
                    "depth_range": {
                        "x": 0.98,
                        "y": 0.02,
                        "font_size": 10,
                        "color": "gray",
                    },
                    "data_points": {
                        "x": 0.02,
                        "y": 0.02,
                        "font_size": 10,
                        "color": "gray",
                    },
                    "zone_labels": {"x": 0.02, "font_size": 10, "color": "gray"},
                },
            }

    @staticmethod
    def add_depth_zones(fig: go.Figure, variables: List[str]):
        """Add depth zone annotations"""
        # Get depth zones from config
        config_manager = ConfigManager()
        config = config_manager.get_external_config()
        depth_zones = config.get(
            "depth_zones",
            [
                (0, 200, "Epipelagic", "rgba(0,255,0,0.1)"),
                (200, 1000, "Mesopelagic", "rgba(0,0,255,0.1)"),
                (1000, 4000, "Bathypelagic", "rgba(128,0,128,0.1)"),
                (4000, 6000, "Abyssopelagic", "rgba(0,0,0,0.1)"),
            ],
        )

        for min_depth, max_depth, zone_name, color in depth_zones:
            # Add shape for depth zone
            fig.add_shape(
                type="rect",
                xref="paper",
                yref="y",
                x0=0,
                x1=1,
                y0=min_depth,
                y1=max_depth,
                fillcolor=color,
                line=dict(width=0),
                layer="below",
            )

            # Add zone label
            depth_config = DepthHelpers._get_depth_config()
            annotations_config = depth_config.get("annotations", {})
            zone_labels_config = annotations_config.get("zone_labels", {})

            fig.add_annotation(
                xref="paper",
                yref="y",
                x=zone_labels_config.get("x", 0.02),
                y=(min_depth + max_depth) / 2,
                xanchor="left",
                yanchor="middle",
                text=zone_name,
                showarrow=False,
                font=dict(
                    size=zone_labels_config.get("font_size", 10),
                    color=zone_labels_config.get("color", "gray"),
                ),
                bgcolor="rgba(255,255,255,0.8)",
                bordercolor="gray",
                borderwidth=1,
            )

    @staticmethod
    def add_depth_annotations(fig: go.Figure, data: pd.DataFrame, variables: List[str]):
        """Add depth-specific annotations"""
        depth_config = DepthHelpers._get_depth_config()
        annotations_config = depth_config.get("annotations", {})

        # Add depth range annotation
        depth_range_config = annotations_config.get("depth_range", {})
        depth_range = data["depth"].max() - data["depth"].min()
        fig.add_annotation(
            xref="paper",
            yref="paper",
            x=depth_range_config.get("x", 0.98),
            y=depth_range_config.get("y", 0.02),
            xanchor="right",
            yanchor="bottom",
            text=f"Depth Range: {depth_range:.1f} m",
            showarrow=False,
            font=dict(
                size=depth_range_config.get("font_size", 10),
                color=depth_range_config.get("color", "gray"),
            ),
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="gray",
            borderwidth=1,
        )

        # Add data points annotation
        data_points_config = annotations_config.get("data_points", {})
        total_points = len(data)
        fig.add_annotation(
            xref="paper",
            yref="paper",
            x=data_points_config.get("x", 0.02),
            y=data_points_config.get("y", 0.02),
            xanchor="left",
            yanchor="bottom",
            text=f"Data Points: {total_points}",
            showarrow=False,
            font=dict(
                size=data_points_config.get("font_size", 10),
                color=data_points_config.get("color", "gray"),
            ),
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="gray",
            borderwidth=1,
        )

    @staticmethod
    def get_depth_statistics(data: pd.DataFrame) -> Dict[str, float]:
        """Get depth statistics"""
        depth_data = data["depth"].dropna()

        return {
            "min_depth": float(depth_data.min()),
            "max_depth": float(depth_data.max()),
            "mean_depth": float(depth_data.mean()),
            "std_depth": float(depth_data.std()),
            "depth_range": float(depth_data.max() - depth_data.min()),
            "data_points": len(depth_data),
        }

    @staticmethod
    def add_thermocline_annotation(fig: go.Figure, data: pd.DataFrame):
        """Add thermocline annotation if temperature data is available"""
        depth_config = DepthHelpers._get_depth_config()
        thermocline_config = depth_config.get("thermocline", {})

        variable_name = thermocline_config.get("variable_name", "tv290C")
        if variable_name not in data.columns:
            return

        # Simple thermocline detection (temperature gradient)
        temp_data = data[["depth", variable_name]].dropna().sort_values("depth")
        min_data_points = thermocline_config.get("min_data_points", 10)
        if len(temp_data) < min_data_points:
            return

        # Calculate temperature gradient
        temp_data["temp_gradient"] = (
            temp_data[variable_name].diff() / temp_data["depth"].diff()
        )

        # Find maximum gradient (thermocline)
        max_gradient_idx = temp_data["temp_gradient"].idxmax()
        thermocline_depth = temp_data.loc[max_gradient_idx, "depth"]

        # Add thermocline line
        fig.add_hline(
            y=thermocline_depth,
            line_dash=thermocline_config.get("line_style", "dash"),
            line_color=thermocline_config.get("line_color", "red"),
            annotation_text=f"Thermocline: {thermocline_depth:.1f}m",
            annotation_position=thermocline_config.get(
                "annotation_position", "top right"
            ),
        )

    @staticmethod
    def create_multi_variable_profile(
        plotter, data: pd.DataFrame, variables: List[str], **kwargs
    ) -> go.Figure:
        """Create a multi-variable depth profile plot"""
        return plotter.create_plot(data, variables, **kwargs)

    @staticmethod
    def create_single_variable_profile(
        plotter, data: pd.DataFrame, variable: str, **kwargs
    ) -> go.Figure:
        """Create a single variable depth profile plot"""
        return plotter.create_plot(data, [variable], **kwargs)

    @staticmethod
    def create_vertical_profile(
        plotter, data: pd.DataFrame, variable: str, **kwargs
    ) -> go.Figure:
        """Create a vertical profile plot (variable vs depth)"""
        return DepthHelpers.create_single_variable_profile(
            plotter, data, variable, **kwargs
        )
