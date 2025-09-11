"""
Contour Plotter Helpers for TRIAXUS visualization system

This module provides helper functions for contour plotting functionality.
"""

import pandas as pd
import plotly.graph_objects as go
import numpy as np
from scipy.interpolate import griddata
from typing import Dict, Any, Tuple
import logging

from ..core.config import ConfigManager

logger = logging.getLogger(__name__)


class ContourHelpers:
    """Helper class for contour plotting functionality"""

    @staticmethod
    def _get_contour_config() -> Dict[str, Any]:
        """Get contour configuration from ConfigManager"""
        config_manager = ConfigManager()
        config = config_manager.get_external_config()
        if config is not None:
            return config.get("contour", {})
        else:
            # Fallback configuration when config file is missing
            return {
                "grid_resolution": {
                    "max_time_points": 100,
                    "max_depth_points": 100,
                    "fallback_time_points": 50,
                    "fallback_depth_points": 50,
                },
                "interpolation": {"method": "linear", "fill_value": None},
                "colorscale": "Viridis",
                "show_colorbar": True,
                "annotations": {
                    "variable_info": {
                        "x": 0.02,
                        "y": 0.98,
                        "font_size": 12,
                        "color": "black",
                    },
                    "interpolation_note": {
                        "x": 0.98,
                        "y": 0.02,
                        "font_size": 10,
                        "color": "gray",
                        "text": "Interpolated data",
                    },
                },
                "scatter_overlay": {
                    "size": 4,
                    "line_width": 1,
                    "line_color": "black",
                    "colorscale": "Viridis",
                },
                "min_data_points": 3,
            }

    @staticmethod
    def prepare_contour_data(
        data: pd.DataFrame, variable: str
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Prepare data for contour plotting with interpolation"""
        # Remove rows with missing values
        clean_data = data[["time", "depth", variable]].dropna()

        contour_config = ContourHelpers._get_contour_config()
        min_points = contour_config.get("min_data_points", 3)

        if len(clean_data) < min_points:
            raise ValueError(
                f"Insufficient data for contour plotting (need at least {min_points} points)"
            )

        # Convert time to datetime if it's not already
        if not pd.api.types.is_datetime64_any_dtype(clean_data["time"]):
            clean_data["time"] = pd.to_datetime(clean_data["time"])

        # Convert time to numeric for interpolation (but keep original for display)
        time_numeric = pd.to_numeric(clean_data["time"])
        time_original = clean_data["time"]
        depth_values = clean_data["depth"].values
        variable_values = clean_data[variable].values

        # Create regular grid
        time_min, time_max = time_numeric.min(), time_numeric.max()
        depth_min, depth_max = depth_values.min(), depth_values.max()

        # Determine grid resolution from config
        grid_config = contour_config.get("grid_resolution", {})
        max_time_points = grid_config.get("max_time_points", 100)
        max_depth_points = grid_config.get("max_depth_points", 100)

        n_time_points = min(max_time_points, len(clean_data) // 2)
        n_depth_points = min(max_depth_points, len(clean_data) // 2)

        time_grid = np.linspace(time_min, time_max, n_time_points)
        depth_grid = np.linspace(depth_min, depth_max, n_depth_points)

        # Create meshgrid
        time_mesh, depth_mesh = np.meshgrid(time_grid, depth_grid)

        # Interpolate data onto regular grid
        try:
            # Use scipy's griddata for interpolation
            points = np.column_stack((time_numeric, depth_values))
            # Get interpolation settings from config
            interp_config = contour_config.get("interpolation", {})
            method = interp_config.get("method", "linear")
            fill_value = interp_config.get("fill_value", np.nan)

            z_interpolated = griddata(
                points,
                variable_values,
                (time_mesh, depth_mesh),
                method=method,
                fill_value=fill_value,
            )
        except Exception as e:
            logger.warning(f"Interpolation failed: {e}, using scatter plot fallback")
            # Fallback to scatter plot if interpolation fails
            return ContourHelpers.create_scatter_fallback(clean_data, variable)

        # Convert numeric time grid back to datetime for display
        time_grid_datetime = pd.to_datetime(time_grid)

        return time_grid_datetime, depth_grid, z_interpolated

    @staticmethod
    def create_scatter_fallback(
        data: pd.DataFrame, variable: str
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Create scatter plot fallback when interpolation fails"""
        # Convert time to datetime if it's not already
        if not pd.api.types.is_datetime64_any_dtype(data["time"]):
            data["time"] = pd.to_datetime(data["time"])

        time_numeric = pd.to_numeric(data["time"])
        depth_values = data["depth"].values
        variable_values = data[variable].values

        # Create a simple grid for scatter plot using config
        contour_config = ContourHelpers._get_contour_config()
        grid_config = contour_config.get("grid_resolution", {})
        fallback_time_points = grid_config.get("fallback_time_points", 50)
        fallback_depth_points = grid_config.get("fallback_depth_points", 50)

        time_grid = np.linspace(
            time_numeric.min(), time_numeric.max(), fallback_time_points
        )
        depth_grid = np.linspace(
            depth_values.min(), depth_values.max(), fallback_depth_points
        )

        # Create meshgrid
        time_mesh, depth_mesh = np.meshgrid(time_grid, depth_grid)

        # Create a simple interpolation using nearest neighbor
        z_interpolated = np.full_like(time_mesh, np.nan)

        for i in range(len(time_grid)):
            for j in range(len(depth_grid)):
                # Find nearest data point
                distances = np.sqrt(
                    (time_numeric - time_grid[i]) ** 2
                    + (depth_values - depth_grid[j]) ** 2
                )
                nearest_idx = np.argmin(distances)
                z_interpolated[j, i] = variable_values[nearest_idx]

        # Convert numeric time grid back to datetime for display
        time_grid_datetime = pd.to_datetime(time_grid)

        return time_grid_datetime, depth_grid, z_interpolated

    @staticmethod
    def add_contour_annotations(fig: go.Figure, variable: str):
        """Add annotations to contour plot"""
        contour_config = ContourHelpers._get_contour_config()
        annotations_config = contour_config.get("annotations", {})

        # Add variable information
        var_info_config = annotations_config.get("variable_info", {})
        fig.add_annotation(
            xref="paper",
            yref="paper",
            x=var_info_config.get("x", 0.02),
            y=var_info_config.get("y", 0.98),
            xanchor="left",
            yanchor="top",
            text=f"Variable: {variable}",
            showarrow=False,
            font=dict(
                size=var_info_config.get("font_size", 12),
                color=var_info_config.get("color", "black"),
            ),
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="gray",
            borderwidth=1,
        )

        # Add interpolation note
        interp_note_config = annotations_config.get("interpolation_note", {})
        fig.add_annotation(
            xref="paper",
            yref="paper",
            x=interp_note_config.get("x", 0.98),
            y=interp_note_config.get("y", 0.02),
            xanchor="right",
            yanchor="bottom",
            text=annotations_config.get("text", "Interpolated data"),
            showarrow=False,
            font=dict(
                size=interp_note_config.get("font_size", 10),
                color=interp_note_config.get("color", "gray"),
            ),
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="gray",
            borderwidth=1,
        )

    @staticmethod
    def create_heatmap(
        plotter, data: pd.DataFrame, variable: str, **kwargs
    ) -> go.Figure:
        """Create a heatmap version of the contour plot"""
        # Get configuration
        config = plotter.get_plot_config()
        contour_config = config.get("contour", {})

        # Prepare data
        x_data, y_data, z_data = ContourHelpers.prepare_contour_data(data, variable)

        # Create heatmap
        fig = go.Figure()

        # Get visual settings from config
        colorscale = contour_config.get("colorscale", "Viridis")
        show_colorbar = contour_config.get("show_colorbar", True)

        heatmap_trace = go.Heatmap(
            x=x_data,
            y=y_data,
            z=z_data,
            colorscale=colorscale,
            showscale=show_colorbar,
            colorbar=dict(title=variable),
            hovertemplate=f"<b>{variable}</b><br>"
            + "Time: %{x}<br>"
            + "Depth: %{y} m<br>"
            + "Value: %{z}<br>"
            + "<extra></extra>",
        )

        fig.add_trace(heatmap_trace)

        # Update layout
        plotter._update_contour_layout(fig, variable, **kwargs)

        return fig

    @staticmethod
    def add_contour_lines(
        plotter, fig: go.Figure, data: pd.DataFrame, variable: str, **kwargs
    ):
        """Add contour lines to existing plot"""
        # Get configuration
        config = plotter.get_plot_config()

        # Prepare data
        x_data, y_data, z_data = ContourHelpers.prepare_contour_data(data, variable)

        # Add contour lines
        contour_lines = go.Contour(
            x=x_data,
            y=y_data,
            z=z_data,
            contours=dict(showlines=True, linewidth=1, linecolor="black"),
            showscale=False,
            hoverinfo="skip",
        )

        fig.add_trace(contour_lines)

    @staticmethod
    def get_contour_statistics(data: pd.DataFrame, variable: str) -> Dict[str, float]:
        """Get statistics for contour plot data"""
        var_data = data[variable].dropna()

        return {
            "min_value": float(var_data.min()),
            "max_value": float(var_data.max()),
            "mean_value": float(var_data.mean()),
            "std_value": float(var_data.std()),
            "data_points": len(var_data),
            "time_range": float(
                pd.to_numeric(data["time"]).max() - pd.to_numeric(data["time"]).min()
            ),
            "depth_range": float(data["depth"].max() - data["depth"].min()),
        }

    @staticmethod
    def create_contour_with_scatter(
        plotter, data: pd.DataFrame, variable: str, **kwargs
    ) -> go.Figure:
        """Create contour plot with original data points overlaid"""
        # Create base contour plot
        fig = plotter.create_plot(data, variable, **kwargs)

        # Get scatter overlay settings from config
        contour_config = ContourHelpers._get_contour_config()
        scatter_config = contour_config.get("scatter_overlay", {})

        # Add scatter points for original data
        scatter_trace = go.Scatter(
            x=pd.to_numeric(data["time"]),
            y=data["depth"],
            mode="markers",
            marker=dict(
                size=scatter_config.get("size", 4),
                color=data[variable],
                colorscale=scatter_config.get("colorscale", "Viridis"),
                showscale=False,
                line=dict(
                    width=scatter_config.get("line_width", 1),
                    color=scatter_config.get("line_color", "black"),
                ),
            ),
            name="Data Points",
            hovertemplate=f"<b>{variable}</b><br>"
            + "Time: %{x}<br>"
            + "Depth: %{y} m<br>"
            + "Value: %{marker.color}<br>"
            + "<extra></extra>",
        )

        fig.add_trace(scatter_trace)

        return fig
