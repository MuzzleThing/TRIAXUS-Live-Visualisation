"""
Contour Plotter for TRIAXUS visualization system

This module provides contour plotting functionality for TRIAXUS data.
"""

import pandas as pd
import plotly.graph_objects as go
import numpy as np
from scipy.interpolate import griddata
from typing import Optional, Dict, Any, Tuple
import logging

from ..core.base_plotter import BasePlotter
from ..core.config import ConfigManager
from .contour_helpers import ContourHelpers


class ContourPlotter(BasePlotter):
    """Contour plotter for TRIAXUS visualization system"""
    
    def __init__(self, config_manager: ConfigManager):
        """
        Initialize ContourPlotter
        
        Args:
            config_manager: Configuration manager instance
        """
        super().__init__(config_manager)
        self.logger = logging.getLogger(__name__)
    
    def get_plot_type(self) -> str:
        """Get the plot type identifier"""
        return 'contour'
    
    def get_required_columns(self) -> list:
        """Get required data columns for contour plot"""
        return ['time', 'depth']
    
    def create_plot(self, data: pd.DataFrame, variable: str, **kwargs) -> go.Figure:
        """
        Create contour plot
        
        Args:
            data: Input data
            variable: Variable to plot
            **kwargs: Additional plot parameters
            
        Returns:
            Plotly figure object
        """
        try:
            # Validate and process data
            validated_data = self.validate_data(data)
            processed_data = self.process_data(validated_data)
            
            # Check if variable exists
            if variable not in processed_data.columns:
                raise ValueError(f"Variable '{variable}' not found in data")
            
            # Create the plot
            fig = self._create_contour_plot(processed_data, variable, **kwargs)
            
            self.logger.info(f"Contour plot created for variable: {variable}")
            return fig
            
        except Exception as e:
            self.logger.error(f"Failed to create contour plot: {e}")
            raise
    
    def _create_contour_plot(self, data: pd.DataFrame, variable: str, **kwargs) -> go.Figure:
        """Create the actual contour plot"""
        # Get configuration
        config = self.get_plot_config()
        contour_config = config.get('contour', {})
        
        # Prepare data for contour plotting
        x_data, y_data, z_data = ContourHelpers.prepare_contour_data(data, variable)
        
        # Create contour plot
        fig = go.Figure()
        
        # Add contour trace
        contour_trace = go.Contour(
            x=x_data,
            y=y_data,
            z=z_data,
            colorscale=contour_config.get('colorscale', 'Viridis'),
            showscale=contour_config.get('show_colorbar', True),
            colorbar=dict(
                title=variable
            ),
            hovertemplate=f'<b>{variable}</b><br>' +
                         'Time: %{x}<br>' +
                         'Depth: %{y} m<br>' +
                         'Value: %{z}<br>' +
                         '<extra></extra>'
        )
        
        fig.add_trace(contour_trace)
        
        # Update layout
        self._update_contour_layout(fig, variable, **kwargs)
        
        return fig
    
    def _prepare_contour_data(self, data: pd.DataFrame, variable: str) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Prepare data for contour plotting with interpolation"""
        # Remove rows with missing values
        clean_data = data[['time', 'depth', variable]].dropna()
        
        if len(clean_data) < 3:
            raise ValueError("Insufficient data for contour plotting")
        
        # Convert time to datetime if it's not already
        if not pd.api.types.is_datetime64_any_dtype(clean_data['time']):
            clean_data['time'] = pd.to_datetime(clean_data['time'])
        
        # Convert time to numeric for interpolation (but keep original for display)
        time_numeric = pd.to_numeric(clean_data['time'])
        time_original = clean_data['time']
        depth_values = clean_data['depth'].values
        variable_values = clean_data[variable].values
        
        # Create regular grid
        time_min, time_max = time_numeric.min(), time_numeric.max()
        depth_min, depth_max = depth_values.min(), depth_values.max()
        
        # Determine grid resolution
        n_time_points = min(100, len(clean_data) // 2)
        n_depth_points = min(100, len(clean_data) // 2)
        
        time_grid = np.linspace(time_min, time_max, n_time_points)
        depth_grid = np.linspace(depth_min, depth_max, n_depth_points)
        
        # Create meshgrid
        time_mesh, depth_mesh = np.meshgrid(time_grid, depth_grid)
        
        # Interpolate data onto regular grid
        try:
            # Use scipy's griddata for interpolation
            points = np.column_stack((time_numeric, depth_values))
            z_interpolated = griddata(
                points, 
                variable_values, 
                (time_mesh, depth_mesh), 
                method='linear',
                fill_value=np.nan
            )
        except Exception as e:
            self.logger.warning(f"Interpolation failed: {e}, using scatter plot fallback")
            # Fallback to scatter plot if interpolation fails
            return self._create_scatter_fallback(clean_data, variable)
        
        # Convert numeric time grid back to datetime for display
        time_grid_datetime = pd.to_datetime(time_grid)
        
        return time_grid_datetime, depth_grid, z_interpolated
    
    def _create_scatter_fallback(self, data: pd.DataFrame, variable: str) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Create scatter plot fallback when interpolation fails"""
        # Convert time to datetime if it's not already
        if not pd.api.types.is_datetime64_any_dtype(data['time']):
            data['time'] = pd.to_datetime(data['time'])
        
        time_numeric = pd.to_numeric(data['time'])
        depth_values = data['depth'].values
        variable_values = data[variable].values
        
        # Create a simple grid for scatter plot
        time_grid = np.linspace(time_numeric.min(), time_numeric.max(), 50)
        depth_grid = np.linspace(depth_values.min(), depth_values.max(), 50)
        
        # Create meshgrid
        time_mesh, depth_mesh = np.meshgrid(time_grid, depth_grid)
        
        # Create a simple interpolation using nearest neighbor
        z_interpolated = np.full_like(time_mesh, np.nan)
        
        for i in range(len(time_grid)):
            for j in range(len(depth_grid)):
                # Find nearest data point
                distances = np.sqrt((time_numeric - time_grid[i])**2 + (depth_values - depth_grid[j])**2)
                nearest_idx = np.argmin(distances)
                z_interpolated[j, i] = variable_values[nearest_idx]
        
        # Convert numeric time grid back to datetime for display
        time_grid_datetime = pd.to_datetime(time_grid)
        
        return time_grid_datetime, depth_grid, z_interpolated
    
    def _update_contour_layout(self, fig: go.Figure, variable: str, **kwargs):
        """Update layout for contour plot"""
        config = self.get_plot_config()
        
        # Get title
        title = kwargs.get('title', f'TRIAXUS Contour Plot - {variable}')
        
        # Update layout
        fig.update_layout(
            title=title,
            height=config.get('plot_height', 600),
            width=config.get('plot_width', 800),
            template='plotly_white'
        )
        
        # Update x-axis (time)
        fig.update_xaxes(
            title='Time',
            showgrid=True,
            gridwidth=1,
            gridcolor='lightgray',
            type='date',
            tickformat='%H:%M\n%Y-%m-%d'
        )
        
        # Update y-axis (depth) - reversed for depth
        fig.update_yaxes(
            title='Depth (m)',
            showgrid=True,
            gridwidth=1,
            gridcolor='lightgray',
            autorange="reversed"  # Depth axis reversed
        )
        
        # Add annotations if requested
        if kwargs.get('add_annotations', False):
            ContourHelpers.add_contour_annotations(fig, variable)
    
    
    def create_heatmap(self, data: pd.DataFrame, variable: str, **kwargs) -> go.Figure:
        """Create a heatmap version of the contour plot"""
        return ContourHelpers.create_heatmap(self, data, variable, **kwargs)
    
    def add_contour_lines(self, fig: go.Figure, data: pd.DataFrame, variable: str, **kwargs):
        """Add contour lines to existing plot"""
        return ContourHelpers.add_contour_lines(self, fig, data, variable, **kwargs)
    
    def get_contour_statistics(self, data: pd.DataFrame, variable: str) -> Dict[str, float]:
        """Get statistics for contour plot data"""
        return ContourHelpers.get_contour_statistics(data, variable)
    
    def create_contour_with_scatter(self, data: pd.DataFrame, variable: str, **kwargs) -> go.Figure:
        """Create contour plot with original data points overlaid"""
        return ContourHelpers.create_contour_with_scatter(self, data, variable, **kwargs)
