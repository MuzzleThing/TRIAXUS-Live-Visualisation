"""
HTML Generator for TRIAXUS visualization system

This module provides HTML generation functionality for Plotly figures.
"""

import plotly.graph_objects as go
from typing import Dict, Any, Optional
import logging

from ..core.config import ConfigManager


class HTMLGenerator:
    """
    Generates HTML strings from Plotly figures.
    This class centralizes the HTML export logic, separating it from plot generation.
    """

    def __init__(self, config_manager: Optional[ConfigManager] = None):
        """
        Initialize HTMLGenerator

        Args:
            config_manager: Configuration manager instance
        """
        self.config_manager = config_manager or ConfigManager()
        self.logger = logging.getLogger(__name__)

        # Get HTML configuration
        self.html_config = self.config_manager.get_html_config()

    def _generate_html(
        self, figure: go.Figure, div_id: str, include_plotlyjs: bool = True
    ) -> str:
        """
        Internal method to generate HTML from a Plotly figure.

        Args:
            figure: Plotly figure object
            div_id: HTML div ID for the plot
            include_plotlyjs: Whether to include Plotly.js library

        Returns:
            HTML string
        """
        if not isinstance(figure, go.Figure):
            raise TypeError("Input must be a Plotly Figure object.")

        try:
            # Get plotly configuration
            plotly_config = self.html_config.get("plotly_config", {})

            html_string = figure.to_html(
                include_plotlyjs=include_plotlyjs,
                div_id=div_id,
                full_html=False,  # Only generate the div, not a full HTML page
                config=plotly_config,
            )

            self.logger.debug(f"Generated HTML for div_id: {div_id}")
            return html_string

        except Exception as e:
            self.logger.error(f"Failed to generate HTML for {div_id}: {e}")
            raise

    def generate_line_plot_html(self, figure: go.Figure) -> str:
        """Generates HTML for a line plot."""
        div_id = f"{self.html_config.get('div_id_prefix', 'triaxus')}-line-plot"
        return self._generate_html(figure, div_id)

    def generate_contour_plot_html(self, figure: go.Figure) -> str:
        """Generates HTML for a contour plot."""
        div_id = f"{self.html_config.get('div_id_prefix', 'triaxus')}-contour-plot"
        return self._generate_html(figure, div_id)

    def generate_map_plot_html(self, figure: go.Figure) -> str:
        """Generates HTML for a map plot."""
        div_id = f"{self.html_config.get('div_id_prefix', 'triaxus')}-map-plot"
        return self._generate_html(figure, div_id)

    def generate_time_series_html(self, figure: go.Figure) -> str:
        """Generates HTML for a time series plot."""
        div_id = f"{self.html_config.get('div_id_prefix', 'triaxus')}-time-series-plot"
        return self._generate_html(figure, div_id)

    def generate_depth_profile_html(self, figure: go.Figure) -> str:
        """Generates HTML for a depth profile plot."""
        div_id = (
            f"{self.html_config.get('div_id_prefix', 'triaxus')}-depth-profile-plot"
        )
        return self._generate_html(figure, div_id)

    def generate_dashboard_html(
        self, figures: Dict[str, go.Figure], include_plotlyjs: bool = True
    ) -> str:
        """
        Generates a dashboard HTML string from multiple Plotly figures.

        Args:
            figures: Dictionary of plot types and their figures
            include_plotlyjs: Whether to include Plotly.js library

        Returns:
            Dashboard HTML string
        """
        html_parts = []

        # Add Plotly.js if requested
        if include_plotlyjs:
            plotly_js_cdn = (
                '<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>'
            )
            html_parts.append(plotly_js_cdn)

        # Generate HTML for each figure
        for plot_type, figure in figures.items():
            div_id = (
                f"{self.html_config.get('div_id_prefix', 'triaxus')}-{plot_type}-plot"
            )
            html_parts.append(
                self._generate_html(figure, div_id, include_plotlyjs=False)
            )

        return "\n".join(html_parts)

    def generate_full_html_page(
        self,
        figure: go.Figure,
        title: str = "TRIAXUS Plot",
        div_id: str = "triaxus-plot",
    ) -> str:
        """
        Generate a complete HTML page with the plot.

        Args:
            figure: Plotly figure object
            title: Page title
            div_id: HTML div ID for the plot

        Returns:
            Complete HTML page string
        """
        try:
            html_string = figure.to_html(
                include_plotlyjs=True,
                div_id=div_id,
                full_html=True,
                config=self.html_config.get("plotly_config", {}),
            )

            # Customize the HTML
            html_string = html_string.replace(
                "<title>Plotly</title>", f"<title>{title}</title>"
            )

            self.logger.debug(f"Generated full HTML page for {div_id}")
            return html_string

        except Exception as e:
            self.logger.error(f"Failed to generate full HTML page: {e}")
            raise

    def generate_embedded_html(
        self, figure: go.Figure, div_id: str, width: str = "100%", height: str = "600px"
    ) -> str:
        """
        Generate HTML for embedding in existing pages.

        Args:
            figure: Plotly figure object
            div_id: HTML div ID for the plot
            width: Width of the plot container
            height: Height of the plot container

        Returns:
            Embedded HTML string
        """
        try:
            # Generate the plot HTML
            plot_html = self._generate_html(figure, div_id, include_plotlyjs=False)

            # Wrap in a container div
            container_html = f"""
            <div id="{div_id}-container" style="width: {width}; height: {height};">
                {plot_html}
            </div>
            """

            self.logger.debug(f"Generated embedded HTML for {div_id}")
            return container_html

        except Exception as e:
            self.logger.error(f"Failed to generate embedded HTML: {e}")
            raise

    def save_html_file(
        self, figure: go.Figure, filepath: str, title: str = "TRIAXUS Plot"
    ):
        """
        Save plot as HTML file.

        Args:
            figure: Plotly figure object
            filepath: Path to save the HTML file
            title: Page title
        """
        try:
            html_content = self.generate_full_html_page(figure, title)

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(html_content)

            self.logger.info(f"HTML file saved to: {filepath}")

        except Exception as e:
            self.logger.error(f"Failed to save HTML file: {e}")
            raise

    def get_plotly_config(self) -> Dict[str, Any]:
        """Get Plotly configuration"""
        return self.html_config.get("plotly_config", {})

    def update_plotly_config(self, config: Dict[str, Any]):
        """Update Plotly configuration"""
        current_config = self.html_config.get("plotly_config", {})
        current_config.update(config)
        self.html_config["plotly_config"] = current_config
        self.logger.debug("Plotly configuration updated")

    def set_div_id_prefix(self, prefix: str):
        """Set the prefix for div IDs"""
        self.html_config["div_id_prefix"] = prefix
        self.logger.debug(f"Div ID prefix set to: {prefix}")

    def get_div_id_prefix(self) -> str:
        """Get the current div ID prefix"""
        return self.html_config.get("div_id_prefix", "triaxus")
