"""
Depth Profile Plotter for TRIAXUS visualization system

This module provides depth profile plotting functionality for TRIAXUS data.
"""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import List, Optional, Dict, Any
import logging

from ..core.base_plotter import BasePlotter
from ..core.config import ConfigManager
from .depth_helpers import DepthHelpers


class DepthProfilePlotter(BasePlotter):
    """Depth profile plotter for TRIAXUS visualization system"""
    
    def __init__(self, config_manager: ConfigManager):
        """
        Initialize DepthProfilePlotter
        
        Args:
            config_manager: Configuration manager instance
        """
        super().__init__(config_manager)
        self.logger = logging.getLogger(__name__)
    
    def get_plot_type(self) -> str:
        """Get the plot type identifier"""
        return 'depth_profile'
    
    def get_required_columns(self) -> List[str]:
        """Get required data columns for depth profile plot"""
        return ['depth']
    
    def create_plot(self, data: pd.DataFrame, variables: Optional[List[str]] = None, **kwargs) -> go.Figure:
        """
        Create depth profile plot
        
        Args:
            data: Input data
            variables: List of variables to plot
            **kwargs: Additional plot parameters
            
        Returns:
            Plotly figure object
        """
        try:
            # Validate and process data
            validated_data = self.validate_data(data)
            processed_data = self.process_data(validated_data)
            
            # Get variables to plot
            if variables is None:
                variables = self.get_available_variables(processed_data)
            
            if not variables:
                raise ValueError("No variables available for plotting")
            
            # Create the plot
            fig = self._create_depth_profile_plot(processed_data, variables, **kwargs)
            
            self.logger.info(f"Depth profile plot created with variables: {variables}")
            return fig
            
        except Exception as e:
            self.logger.error(f"Failed to create depth profile plot: {e}")
            raise
    
    def _create_depth_profile_plot(self, data: pd.DataFrame, variables: List[str], **kwargs) -> go.Figure:
        """Create the actual depth profile plot"""
        # Get configuration
        config = self.get_plot_config()
        theme_colors = self.get_theme_colors()
        
        # Create subplots if multiple variables
        if len(variables) > 1:
            fig = make_subplots(
                rows=1,
                cols=len(variables),
                subplot_titles=[f"{var} vs Depth" for var in variables],
                horizontal_spacing=0.05,
                shared_yaxes=True
            )
        else:
            fig = go.Figure()
        
        # Add traces for each variable
        for i, variable in enumerate(variables):
            if variable not in data.columns:
                self.logger.warning(f"Variable {variable} not found in data")
                continue
            
            # Get color for variable
            color = theme_colors.get(variable, f'hsl({i * 360 / len(variables)}, 70%, 50%)')
            
            # Create trace
            trace = go.Scatter(
                x=data[variable],
                y=data['depth'],
                mode='lines+markers',
                name=variable,
                line=dict(
                    color=color,
                    width=config.get('line_width', 2)
                ),
                marker=dict(
                    size=config.get('marker_size', 4),
                    color=color
                ),
                hovertemplate=f'<b>{variable}</b><br>' +
                             'Depth: %{y} m<br>' +
                             'Value: %{x}<br>' +
                             '<extra></extra>'
            )
            
            if len(variables) > 1:
                fig.add_trace(trace, row=1, col=i+1)
            else:
                fig.add_trace(trace)
        
        # Update layout
        self._update_depth_profile_layout(fig, variables, **kwargs)
        
        return fig
    
    def _update_depth_profile_layout(self, fig: go.Figure, variables: List[str], **kwargs):
        """Update layout for depth profile plot"""
        config = self.get_plot_config()
        
        # Get title
        title = kwargs.get('title', f'TRIAXUS Depth Profile - {", ".join(variables)}')
        
        # Get theme layout configuration
        theme_layout = self.get_theme_layout()
        
        # Determine template based on theme
        template = self._get_plotly_template()
        
        # Update layout
        fig.update_layout(
            title=title,
            height=config.get('plot_height', 600),
            width=config.get('plot_width', 800),
            showlegend=config.get('show_legend', True),
            template=template,
            hovermode='y unified',
            plot_bgcolor=theme_layout.get('background_color', 'white'),
            paper_bgcolor=theme_layout.get('background_color', 'white'),
            font=dict(
                family=theme_layout.get('font_family', 'Arial, sans-serif'),
                color=theme_layout.get('text_color', 'black')
            )
        )
        
        # Update y-axis (depth) - always reversed for depth profiles
        fig.update_yaxes(
            title='Depth (m)',
            showgrid=True,
            gridwidth=1,
            gridcolor=theme_layout.get('grid_color', 'lightgray'),
            autorange="reversed"  # Depth axis reversed
        )
        
        # Update x-axes
        if len(variables) > 1:
            for i, variable in enumerate(variables):
                fig.update_xaxes(
                    title=variable,
                    showgrid=True,
                    gridwidth=1,
                    gridcolor=theme_layout.get('grid_color', 'lightgray'),
                    row=1,
                    col=i+1
                )
        else:
            fig.update_xaxes(
                title=variables[0] if variables else 'Value',
                showgrid=True,
                gridwidth=1,
                gridcolor=theme_layout.get('grid_color', 'lightgray')
            )
        
        # Add depth zones if requested
        if kwargs.get('add_depth_zones', False):
            DepthHelpers.add_depth_zones(fig, variables)
    
    def create_multi_variable_profile(self, data: pd.DataFrame, variables: List[str], **kwargs) -> go.Figure:
        """Create a multi-variable depth profile plot"""
        return DepthHelpers.create_multi_variable_profile(self, data, variables, **kwargs)
    
    def create_single_variable_profile(self, data: pd.DataFrame, variable: str, **kwargs) -> go.Figure:
        """Create a single variable depth profile plot"""
        return DepthHelpers.create_single_variable_profile(self, data, variable, **kwargs)
    
    def add_depth_annotations(self, fig: go.Figure, data: pd.DataFrame, variables: List[str]):
        """Add depth-specific annotations"""
        return DepthHelpers.add_depth_annotations(fig, data, variables)
    
    def get_depth_statistics(self, data: pd.DataFrame) -> Dict[str, float]:
        """Get depth statistics"""
        return DepthHelpers.get_depth_statistics(data)
    
    def create_vertical_profile(self, data: pd.DataFrame, variable: str, **kwargs) -> go.Figure:
        """Create a vertical profile plot (variable vs depth)"""
        return DepthHelpers.create_vertical_profile(self, data, variable, **kwargs)
    
    def add_thermocline_annotation(self, fig: go.Figure, data: pd.DataFrame):
        """Add thermocline annotation if temperature data is available"""
        return DepthHelpers.add_thermocline_annotation(fig, data)
