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

logger = logging.getLogger(__name__)


class ContourHelpers:
    """Helper class for contour plotting functionality"""
    
    @staticmethod
    def prepare_contour_data(data: pd.DataFrame, variable: str) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
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
            logger.warning(f"Interpolation failed: {e}, using scatter plot fallback")
            # Fallback to scatter plot if interpolation fails
            return ContourHelpers.create_scatter_fallback(clean_data, variable)
        
        # Convert numeric time grid back to datetime for display
        time_grid_datetime = pd.to_datetime(time_grid)
        
        return time_grid_datetime, depth_grid, z_interpolated
    
    @staticmethod
    def create_scatter_fallback(data: pd.DataFrame, variable: str) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
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
    
    @staticmethod
    def add_contour_annotations(fig: go.Figure, variable: str):
        """Add annotations to contour plot"""
        # Add variable information
        fig.add_annotation(
            xref="paper", yref="paper",
            x=0.02, y=0.98,
            xanchor="left", yanchor="top",
            text=f"Variable: {variable}",
            showarrow=False,
            font=dict(size=12, color="black"),
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="gray",
            borderwidth=1
        )
        
        # Add interpolation note
        fig.add_annotation(
            xref="paper", yref="paper",
            x=0.98, y=0.02,
            xanchor="right", yanchor="bottom",
            text="Interpolated data",
            showarrow=False,
            font=dict(size=10, color="gray"),
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="gray",
            borderwidth=1
        )
    
    @staticmethod
    def create_heatmap(plotter, data: pd.DataFrame, variable: str, **kwargs) -> go.Figure:
        """Create a heatmap version of the contour plot"""
        # Get configuration
        config = plotter.get_plot_config()
        contour_config = config.get('contour', {})
        
        # Prepare data
        x_data, y_data, z_data = ContourHelpers.prepare_contour_data(data, variable)
        
        # Create heatmap
        fig = go.Figure()
        
        heatmap_trace = go.Heatmap(
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
        
        fig.add_trace(heatmap_trace)
        
        # Update layout
        plotter._update_contour_layout(fig, variable, **kwargs)
        
        return fig
    
    @staticmethod
    def add_contour_lines(plotter, fig: go.Figure, data: pd.DataFrame, variable: str, **kwargs):
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
            contours=dict(
                showlines=True,
                linewidth=1,
                linecolor='black'
            ),
            showscale=False,
            hoverinfo='skip'
        )
        
        fig.add_trace(contour_lines)
    
    @staticmethod
    def get_contour_statistics(data: pd.DataFrame, variable: str) -> Dict[str, float]:
        """Get statistics for contour plot data"""
        var_data = data[variable].dropna()
        
        return {
            'min_value': float(var_data.min()),
            'max_value': float(var_data.max()),
            'mean_value': float(var_data.mean()),
            'std_value': float(var_data.std()),
            'data_points': len(var_data),
            'time_range': float(pd.to_numeric(data['time']).max() - pd.to_numeric(data['time']).min()),
            'depth_range': float(data['depth'].max() - data['depth'].min())
        }
    
    @staticmethod
    def create_contour_with_scatter(plotter, data: pd.DataFrame, variable: str, **kwargs) -> go.Figure:
        """Create contour plot with original data points overlaid"""
        # Create base contour plot
        fig = plotter.create_plot(data, variable, **kwargs)
        
        # Add scatter points for original data
        scatter_trace = go.Scatter(
            x=pd.to_numeric(data['time']),
            y=data['depth'],
            mode='markers',
            marker=dict(
                size=4,
                color=data[variable],
                colorscale='Viridis',
                showscale=False,
                line=dict(width=1, color='black')
            ),
            name='Data Points',
            hovertemplate=f'<b>{variable}</b><br>' +
                         'Time: %{x}<br>' +
                         'Depth: %{y} m<br>' +
                         'Value: %{marker.color}<br>' +
                         '<extra></extra>'
        )
        
        fig.add_trace(scatter_trace)
        
        return fig
