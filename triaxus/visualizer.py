"""
Main TRIAXUS Visualizer Interface

This module provides the main interface for the TRIAXUS visualization system.
"""

import pandas as pd
import plotly.graph_objects as go
from typing import Dict, Any, Optional, List, Union
import logging

from .core import ConfigManager, ErrorHandler
from .plotters import PlotterFactory
from .data import DataProcessor
from .utils import HTMLGenerator


class TriaxusVisualizer:
    """Main interface for TRIAXUS visualization system"""

    def __init__(self, config_path: Optional[str] = None, theme: str = "oceanographic"):
        """
        Initialize TriaxusVisualizer

        Args:
            config_path: Path to configuration file
            theme: Theme name to use
        """
        self.logger = logging.getLogger(__name__)

        # Initialize core components
        self.config_manager = ConfigManager(config_path)
        self.error_handler = ErrorHandler()
        # Theme management is now handled by ConfigManager
        self.data_processor = DataProcessor(self.config_manager)
        self.html_generator = HTMLGenerator(self.config_manager)
        self.factory = PlotterFactory()

        # Initialize plotters
        self._plotters = {}
        self._initialize_plotters()

        # Set theme
        self.set_theme(theme)

        self.logger.info(f"TriaxusVisualizer initialized with theme: {theme}")

    def _initialize_plotters(self):
        """Initialize all plotters"""
        plot_types = self.factory.get_available_plot_types()
        for plot_type in plot_types:
            self._plotters[plot_type] = self.factory.create_plotter(
                plot_type, self.config_manager
            )

    def set_theme(self, theme_name: str):
        """Set the visualization theme"""
        if theme_name not in self.config_manager.get_available_themes():
            available_themes = self.config_manager.get_available_themes()
            raise ValueError(
                f"Invalid theme: {theme_name}. Available themes: {available_themes}"
            )

        # Set theme in config manager
        self.config_manager.set_theme(theme_name)

        # Update plotter configurations
        for plotter in self._plotters.values():
            plotter.config = self.config_manager.get_plot_config(
                plotter.get_plot_type()
            )

        self.logger.info(f"Theme set to: {theme_name}")

    def get_available_plot_types(self) -> List[str]:
        """Get list of available plot types"""
        return self.factory.get_available_plot_types()

    def get_available_themes(self) -> List[str]:
        """Get list of available themes"""
        return self.theme_manager.get_available_themes()

    def create_plot(self, plot_type: str, data: pd.DataFrame, **kwargs) -> str:
        """
        Create a plot and return HTML string or file path

        Args:
            plot_type: Type of plot to create
            data: Input data
            **kwargs: Additional plot parameters (including output_file)

        Returns:
            HTML string of the plot or file path if output_file is specified
        """
        try:
            # Validate plot type
            if plot_type not in self._plotters:
                available_types = self.get_available_plot_types()
                raise ValueError(
                    f"Unknown plot type: {plot_type}. Available types: {available_types}"
                )

            # Get plotter
            plotter = self._plotters[plot_type]

            # Process data
            processed_data = self.data_processor.process(data)

            # Create plot
            figure = plotter.create_plot(processed_data, **kwargs)

            # Check if output_file is specified
            output_file = kwargs.get("output_file")
            if output_file:
                # Save to file and return file path
                title = kwargs.get(
                    "title", f"TRIAXUS {plot_type.replace('_', ' ').title()} Plot"
                )
                self.html_generator.save_html_file(figure, output_file, title)
                self.logger.info(f"Plot saved to: {output_file}")
                return output_file
            else:
                # Generate HTML string
                html = self._generate_plot_html(figure, plot_type)
                self.logger.info(f"Plot created successfully: {plot_type}")
                return html

        except Exception as e:
            error_message = self.error_handler.handle_plot_error(e, plot_type)
            self.logger.error(f"Failed to create plot {plot_type}: {error_message}")
            raise

    def create_plot_figure(
        self, plot_type: str, data: pd.DataFrame, **kwargs
    ) -> go.Figure:
        """
        Create a plot and return Plotly Figure object

        Args:
            plot_type: Type of plot to create
            data: Input data
            **kwargs: Additional plot parameters

        Returns:
            Plotly Figure object
        """
        try:
            # Validate plot type
            if plot_type not in self._plotters:
                available_types = self.get_available_plot_types()
                raise ValueError(
                    f"Unknown plot type: {plot_type}. Available types: {available_types}"
                )

            # Get plotter
            plotter = self._plotters[plot_type]

            # Process data
            processed_data = self.data_processor.process(data)

            # Create plot
            figure = plotter.create_plot(processed_data, **kwargs)

            self.logger.info(f"Plot figure created successfully: {plot_type}")
            return figure

        except Exception as e:
            error_message = self.error_handler.handle_plot_error(e, plot_type)
            self.logger.error(
                f"Failed to create plot figure {plot_type}: {error_message}"
            )
            raise

    def _generate_plot_html(self, figure: go.Figure, plot_type: str) -> str:
        """Generate HTML for a specific plot type"""
        if plot_type == "time_series":
            return self.html_generator.generate_time_series_html(figure)
        elif plot_type == "depth_profile":
            return self.html_generator.generate_depth_profile_html(figure)
        elif plot_type == "contour":
            return self.html_generator.generate_contour_plot_html(figure)
        elif plot_type == "map":
            return self.html_generator.generate_map_plot_html(figure)
        else:
            # Generic HTML generation
            div_id = f"triaxus-{plot_type}-plot"
            return self.html_generator._generate_html(figure, div_id)

    # Convenience methods for specific plot types
    def create_time_series_plot(
        self, data: pd.DataFrame, variables: Optional[List[str]] = None, **kwargs
    ) -> str:
        """Create a time series plot"""
        return self.create_plot("time_series", data, variables=variables, **kwargs)

    def create_depth_profile_plot(
        self, data: pd.DataFrame, variables: Optional[List[str]] = None, **kwargs
    ) -> str:
        """Create a depth profile plot"""
        return self.create_plot("depth_profile", data, variables=variables, **kwargs)

    def create_contour_plot(self, data: pd.DataFrame, variable: str, **kwargs) -> str:
        """Create a contour plot"""
        return self.create_plot("contour", data, variable=variable, **kwargs)

    def create_map_plot(self, data: pd.DataFrame, **kwargs) -> str:
        """Create a map plot"""
        return self.create_plot("map", data, **kwargs)

    def create_dashboard(
        self, data: pd.DataFrame, plot_configs: Dict[str, Dict[str, Any]]
    ) -> str:
        """
        Create a dashboard with multiple plots

        Args:
            data: Input data
            plot_configs: Dictionary of plot configurations

        Returns:
            Dashboard HTML string
        """
        try:
            figures = {}

            # Process data once
            processed_data = self.data_processor.process(data)

            # Create each plot
            for plot_type, config in plot_configs.items():
                if plot_type in self._plotters:
                    plotter = self._plotters[plot_type]
                    figure = plotter.create_plot(processed_data, **config)
                    figures[plot_type] = figure

            # Generate dashboard HTML
            dashboard_html = self.html_generator.generate_dashboard_html(figures)

            self.logger.info(f"Dashboard created with {len(figures)} plots")
            return dashboard_html

        except Exception as e:
            self.logger.error(f"Failed to create dashboard: {e}")
            raise

    def get_plot_recommendations(self, data: pd.DataFrame) -> Dict[str, str]:
        """Get recommendations for which plots to create based on data"""
        return self.factory.get_plotter_recommendations(list(data.columns), data.shape)

    def validate_data(self, data: pd.DataFrame, plot_type: str) -> bool:
        """Validate data for a specific plot type"""
        try:
            plotter = self._plotters[plot_type]
            plotter.validate_data(data)
            return True
        except Exception as e:
            self.logger.warning(f"Data validation failed for {plot_type}: {e}")
            return False

    def get_plot_capabilities(self, plot_type: str) -> Dict[str, bool]:
        """Get capabilities of a specific plot type"""
        return self.factory.get_plotter_capabilities(plot_type)

    def update_config(self, config_updates: Dict[str, Any]):
        """Update configuration"""
        for key, value in config_updates.items():
            self.config_manager.set_config(key, value)

        # Reinitialize plotters with new configuration
        self._initialize_plotters()

        self.logger.info("Configuration updated and plotters reinitialized")

    def save_plot(self, plot_type: str, data: pd.DataFrame, filepath: str, **kwargs):
        """Save a plot as HTML file"""
        try:
            # Create plot
            figure = self._plotters[plot_type].create_plot(data, **kwargs)

            # Save as HTML file
            title = f"TRIAXUS {plot_type.replace('_', ' ').title()} Plot"
            self.html_generator.save_html_file(figure, filepath, title)

            self.logger.info(f"Plot saved to: {filepath}")

        except Exception as e:
            self.logger.error(f"Failed to save plot: {e}")
            raise

    def get_plot_statistics(
        self, data: pd.DataFrame, plot_type: str, **kwargs
    ) -> Dict[str, Any]:
        """Get statistics for a specific plot type"""
        try:
            plotter = self._plotters[plot_type]
            processed_data = self.data_processor.process(data)

            if hasattr(plotter, "get_plot_statistics"):
                return plotter.get_plot_statistics(processed_data, **kwargs)
            else:
                return self.data_processor.get_data_summary(processed_data)

        except Exception as e:
            self.logger.error(f"Failed to get plot statistics: {e}")
            return {}

    def create_custom_theme(
        self,
        name: str,
        base_theme: str = "default",
        custom_config: Optional[Dict[str, Any]] = None,
    ):
        """Create a custom theme"""
        custom_theme = self.theme_manager.create_custom_theme(
            name, base_theme, custom_config
        )
        self.theme_manager.register_theme(name, custom_theme)
        self.logger.info(f"Custom theme '{name}' created and registered")

    def get_system_info(self) -> Dict[str, Any]:
        """Get system information"""
        return {
            "version": "1.0.0",
            "available_plot_types": self.get_available_plot_types(),
            "available_themes": self.get_available_themes(),
            "current_theme": self.config_manager.get_config("theme"),
            "plotter_count": len(self._plotters),
            "configuration_keys": list(self.config_manager.get_config().keys()),
        }
