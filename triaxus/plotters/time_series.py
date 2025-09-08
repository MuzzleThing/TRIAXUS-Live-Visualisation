"""
Time Series Plotter for TRIAXUS visualization system

This module provides time series plotting functionality for TRIAXUS data.
"""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import List, Optional, Dict, Any
import logging

from ..core.base_plotter import BasePlotter
from ..core.config import ConfigManager
from .time_series_helpers import TimeSeriesHelpers


class TimeSeriesPlotter(BasePlotter):
    """Time series plotter for TRIAXUS visualization system"""
    
    def __init__(self, config_manager: ConfigManager):
        """
        Initialize TimeSeriesPlotter
        
        Args:
            config_manager: Configuration manager instance
        """
        super().__init__(config_manager)
        self.logger = logging.getLogger(__name__)
    
    def get_plot_type(self) -> str:
        """Get the plot type identifier"""
        return 'time_series'
    
    def get_required_columns(self) -> List[str]:
        """Get required data columns for time series plot"""
        return ['time', 'depth']
    
    def create_plot(self, data: pd.DataFrame, variables: Optional[List[str]] = None, **kwargs) -> go.Figure:
        """
        Create time series plot
        
        Args:
            data: Input data
            variables: List of variables to plot
            **kwargs: Additional plot parameters including:
                - data_source: Data source type (e.g., 'Mixed', 'Historical', 'Real-time')
                - time_range: Tuple of (start_time, end_time) or None for all data
                - depth_range: Tuple of (min_depth, max_depth) or None for all depths
                - real_time_update: Boolean indicating if this is real-time data
                - title: Custom plot title
                - show_statistics: Boolean to show statistical annotations
                - line_width: Line width for traces
                - marker_size: Marker size for data points
                - show_legend: Boolean to show/hide legend
                - height: Plot height
                - width: Plot width
                
        Returns:
            Plotly figure object
        """
        try:
            # Validate and process data
            validated_data = self.validate_data(data)
            processed_data = self.process_data(validated_data)
            
            # Apply time and depth filtering if specified
            filtered_data = self._apply_filters(processed_data, **kwargs)
            
            # Get variables to plot
            if variables is None:
                variables = self.get_available_variables(filtered_data)
            
            if not variables:
                raise ValueError("No variables available for plotting")
            
            # Create the plot
            fig = self._create_time_series_plot(filtered_data, variables, **kwargs)
            
            self.logger.info(f"Time series plot created with variables: {variables}")
            return fig
            
        except Exception as e:
            self.logger.error(f"Failed to create time series plot: {e}")
            raise
    
    def _apply_filters(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        """Apply time and depth filters to data"""
        filtered_data = data.copy()
        
        # Apply time range filter
        time_range = kwargs.get('time_range')
        if time_range and len(time_range) == 2:
            start_time, end_time = time_range
            if start_time and end_time:
                filtered_data = filtered_data[
                    (filtered_data['time'] >= start_time) & 
                    (filtered_data['time'] <= end_time)
                ]
        
        # Apply depth range filter
        depth_range = kwargs.get('depth_range')
        if depth_range and len(depth_range) == 2:
            min_depth, max_depth = depth_range
            if min_depth is not None and max_depth is not None:
                filtered_data = filtered_data[
                    (filtered_data['depth'] >= min_depth) & 
                    (filtered_data['depth'] <= max_depth)
                ]
        
        return filtered_data
    
    def _create_time_series_plot(self, data: pd.DataFrame, variables: List[str], **kwargs) -> go.Figure:
        """Create the actual time series plot"""
        # Get configuration
        config = self.get_plot_config()
        theme_colors = self.get_theme_colors()
        
        # Create subplots if multiple variables
        if len(variables) > 1:
            fig = make_subplots(
                rows=len(variables),
                cols=1,
                subplot_titles=[f"{var} vs Time" for var in variables],
                vertical_spacing=0.05,
                shared_xaxes=True
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
                x=data['time'],
                y=data[variable],
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
                             'Time: %{x}<br>' +
                             'Value: %{y}<br>' +
                             '<extra></extra>'
            )
            
            if len(variables) > 1:
                fig.add_trace(trace, row=i+1, col=1)
            else:
                fig.add_trace(trace)
        
        # Update layout
        self._update_time_series_layout(fig, variables, **kwargs)
        
        return fig
    
    def _update_time_series_layout(self, fig: go.Figure, variables: List[str], **kwargs):
        """Update layout for time series plot"""
        config = self.get_plot_config()
        
        # Get title with data source information
        data_source = kwargs.get('data_source', 'TRIAXUS')
        base_title = kwargs.get('title', f'TRIAXUS Industry Standard Time Series Plot')
        title = f"{base_title} - Data Source: {data_source}"
        
        # Get layout parameters from kwargs or config
        height = kwargs.get('height', config.get('plot_height', 600))
        width = kwargs.get('width', config.get('plot_width', 800))
        show_legend = kwargs.get('show_legend', config.get('show_legend', True))
        
        # Get theme layout configuration
        theme_layout = self.get_theme_layout()
        
        # Determine template based on theme
        template = self._get_plotly_template()
        
        # Update layout
        fig.update_layout(
            title=dict(
                text=title,
                x=0.5,
                xanchor='center',
                font=dict(
                    size=16, 
                    color=theme_layout.get('text_color', '#2E3440'),
                    family=theme_layout.get('font_family', 'Arial, sans-serif')
                )
            ),
            height=height,
            width=width,
            showlegend=show_legend,
            template=template,
            hovermode='x unified',
            margin=dict(l=60, r=60, t=80, b=60),
            plot_bgcolor=theme_layout.get('background_color', 'white'),
            paper_bgcolor=theme_layout.get('background_color', 'white')
        )
        
        # Update x-axis (time)
        if len(variables) > 1:
            # For multiple variables, only show time title on the last subplot
            for i, variable in enumerate(variables):
                show_title = (i == len(variables) - 1)  # Only last subplot shows time title
                fig.update_xaxes(
                    title='Time' if show_title else '',
                    showgrid=True,
                    gridwidth=1,
                    gridcolor=theme_layout.get('grid_color', 'lightgray'),
                    row=i+1,
                    col=1
                )
        else:
            # For single variable, show time title normally
            fig.update_xaxes(
                title='Time',
                showgrid=True,
                gridwidth=1,
                gridcolor=theme_layout.get('grid_color', 'lightgray')
            )
        
        # Update y-axes
        if len(variables) > 1:
            for i, variable in enumerate(variables):
                fig.update_yaxes(
                    title=f'{variable}',
                    showgrid=True,
                    gridwidth=1,
                    gridcolor=theme_layout.get('grid_color', 'lightgray'),
                    row=i+1,
                    col=1
                )
        else:
            fig.update_yaxes(
                title=variables[0] if variables else 'Value',
                showgrid=True,
                gridwidth=1,
                gridcolor=theme_layout.get('grid_color', 'lightgray')
            )
        
        # Add annotations if needed
        if kwargs.get('add_annotations', False):
            TimeSeriesHelpers.add_annotations(fig, variables, **kwargs)
        
        # Add real-time status annotation
        if kwargs.get('real_time_update', False):
            TimeSeriesHelpers.add_realtime_status(fig, **kwargs)
    
    def create_multi_variable_plot(self, data: pd.DataFrame, variables: List[str], **kwargs) -> go.Figure:
        """Create a multi-variable time series plot with shared x-axis"""
        return TimeSeriesHelpers.create_multi_variable_plot(self, data, variables, **kwargs)
    
    def create_single_variable_plot(self, data: pd.DataFrame, variable: str, **kwargs) -> go.Figure:
        """Create a single variable time series plot"""
        return TimeSeriesHelpers.create_single_variable_plot(self, data, variable, **kwargs)
    
    def add_statistical_annotations(self, fig: go.Figure, data: pd.DataFrame, variables: List[str]):
        """Add statistical annotations to the plot"""
        return TimeSeriesHelpers.add_statistical_annotations(fig, data, variables)
    
    def get_plot_statistics(self, data: pd.DataFrame, variables: List[str]) -> Dict[str, Dict[str, float]]:
        """Get statistics for the plotted variables"""
        return TimeSeriesHelpers.get_plot_statistics(data, variables)
    
    def get_standard_variables(self) -> List[str]:
        """Get list of standard TRIAXUS variables"""
        return TimeSeriesHelpers.get_standard_variables()
    
    def create_industry_standard_plot(self, data: pd.DataFrame, **kwargs) -> go.Figure:
        """Create industry standard time series plot with standard variables"""
        return TimeSeriesHelpers.create_industry_standard_plot(self, data, **kwargs)
