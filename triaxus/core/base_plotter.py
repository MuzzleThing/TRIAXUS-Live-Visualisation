"""
Base Plotter for TRIAXUS visualization system

This module provides the abstract base class for all plotters.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import pandas as pd
import plotly.graph_objects as go
import logging

from .config import ConfigManager
from .data_validator import DataValidator
from .error_handler import ErrorHandler

logger = logging.getLogger(__name__)


class BasePlotter(ABC):
    """Abstract base class for all plotters"""

    def __init__(self, config_manager: ConfigManager):
        """
        Initialize BasePlotter

        Args:
            config_manager: Configuration manager instance
        """
        self.config_manager = config_manager
        self.validator = DataValidator(config_manager)
        self.error_handler = ErrorHandler()
        self.logger = logging.getLogger(self.__class__.__name__)

        # Get plot-specific configuration
        self.config = self.config_manager.get_plot_config(self.get_plot_type())

    @abstractmethod
    def get_plot_type(self) -> str:
        """Get the plot type identifier"""
        pass

    @abstractmethod
    def get_required_columns(self) -> List[str]:
        """Get required data columns for this plot type"""
        pass

    @abstractmethod
    def create_plot(self, data: pd.DataFrame, **kwargs) -> go.Figure:
        """Create the plot figure"""
        pass

    def validate_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """Validate input data"""
        try:
            return self.validator.validate(data, self.get_required_columns())
        except Exception as e:
            self.logger.error(f"Data validation failed: {e}")
            raise

    def process_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """Process data for plotting"""
        try:
            # Basic data processing
            processed_data = data.copy()

            # Remove rows with all NaN values
            processed_data = processed_data.dropna(how="all")

            # Sort by time if time column exists
            if "time" in processed_data.columns:
                processed_data = processed_data.sort_values("time").reset_index(
                    drop=True
                )

            self.logger.debug(f"Data processed: {len(processed_data)} rows")
            return processed_data

        except Exception as e:
            self.logger.error(f"Data processing failed: {e}")
            raise

    def get_plot_config(self) -> Dict[str, Any]:
        """Get plot-specific configuration"""
        return self.config.copy()

    def update_config(self, **kwargs):
        """Update plot configuration"""
        self.config.update(kwargs)
        self.logger.debug(f"Configuration updated: {kwargs}")

    def get_theme_colors(self) -> Dict[str, str]:
        """Get theme colors for variables"""
        return self.config_manager.get_color_config()

    def get_theme_layout(self) -> Dict[str, Any]:
        """Get theme layout configuration"""
        # Get style configuration for current theme
        style_config = self.config_manager.get_style_config()
        return {
            "background_color": style_config.get("colors", {}).get(
                "background", "#FFFFFF"
            ),
            "text_color": style_config.get("colors", {}).get("text", "#333333"),
            "grid_color": style_config.get("colors", {}).get("grid", "#E0E0E0"),
            "font_family": "Arial, sans-serif",
        }

    def get_layout_config(self) -> Dict[str, Any]:
        """Get layout configuration"""
        return self.config.get("layout", {})

    def create_base_figure(self) -> go.Figure:
        """Create base figure with common settings"""
        fig = go.Figure()

        # Apply common layout settings
        layout_config = self.get_layout_config()
        if layout_config:
            fig.update_layout(**layout_config)

        return fig

    def add_common_layout(self, fig: go.Figure, title: str, x_title: str, y_title: str):
        """Add common layout elements"""
        # Get theme layout configuration
        theme_layout = self.get_theme_layout()

        # Get plot configuration
        plot_config = self.get_plot_config()

        # Determine template based on theme
        template = self._get_plotly_template()

        # Get dimensions from configuration
        height = plot_config.get("default_height", 600)
        width = plot_config.get("default_width", 800)

        # Get grid configuration
        grid_config = plot_config.get("grid", {})
        show_grid = grid_config.get("show", True)

        fig.update_layout(
            title=title,
            xaxis_title=x_title,
            yaxis_title=y_title,
            height=height,
            width=width,
            showlegend=plot_config.get("show_legend", True),
            template=template,
            plot_bgcolor=theme_layout.get("background_color", "white"),
            paper_bgcolor=theme_layout.get("background_color", "white"),
            font=dict(
                family=theme_layout.get("font_family", "Arial, sans-serif"),
                color=theme_layout.get("text_color", "black"),
            ),
        )

        # Add grid if enabled
        if show_grid:
            grid_color = grid_config.get("color", "lightgray")
            grid_width = grid_config.get("width", 1)
            fig.update_xaxes(showgrid=True, gridwidth=grid_width, gridcolor=grid_color)
            fig.update_yaxes(showgrid=True, gridwidth=grid_width, gridcolor=grid_color)

        # Reverse depth axis if enabled
        if plot_config.get("depth_reverse", True) and "depth" in y_title.lower():
            fig.update_yaxes(autorange="reversed")

    def _get_plotly_template(self) -> str:
        """Get Plotly template based on current theme"""
        # Get current theme from config manager
        theme_name = self.config_manager.get_current_theme()

        # Get style configuration for the theme
        style_config = self.config_manager.get_style_config(theme_name)

        # Return template from style configuration
        return style_config.get("template", "plotly_white")

    def handle_error(self, error: Exception, context: str = ""):
        """Handle errors with proper logging and user feedback"""
        return self.error_handler.handle_plot_error(
            error, self.get_plot_type(), context
        )

    def get_available_variables(self, data: pd.DataFrame) -> List[str]:
        """Get list of available variables in the data"""
        # Get variable list from data configuration
        data_config = self.config_manager.get_data_config()
        optional_variables = data_config.get("variables", [])
        return [var for var in optional_variables if var in data.columns]

    def get_data_info(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Get information about the data"""
        info = {
            "shape": data.shape,
            "columns": list(data.columns),
            "available_variables": self.get_available_variables(data),
            "plot_type": self.get_plot_type(),
        }

        # Add depth range if available
        if "depth" in data.columns:
            info["depth_range"] = {
                "min": float(data["depth"].min()),
                "max": float(data["depth"].max()),
            }

        # Add time range if available
        if "time" in data.columns:
            info["time_range"] = {
                "start": str(data["time"].min()),
                "end": str(data["time"].max()),
            }

        return info
