"""
Time Series Plotter Helpers for TRIAXUS visualization system

This module provides helper functions for time series plotting functionality.
"""

import pandas as pd
import plotly.graph_objects as go
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class TimeSeriesHelpers:
    """Helper class for time series plotting functionality"""
    
    @staticmethod
    def add_annotations(fig: go.Figure, variables: List[str], **kwargs):
        """Add annotations to the plot"""
        # Add data source annotation
        data_source = kwargs.get('data_source', 'TRIAXUS')
        fig.add_annotation(
            xref="paper", yref="paper",
            x=0.02, y=0.98,
            xanchor="left", yanchor="top",
            text=f"Data Source: {data_source}",
            showarrow=False,
            font=dict(size=10, color="gray")
        )
        
        # Add variable count annotation
        fig.add_annotation(
            xref="paper", yref="paper",
            x=0.98, y=0.98,
            xanchor="right", yanchor="top",
            text=f"{len(variables)} variables",
            showarrow=False,
            font=dict(size=10, color="gray")
        )
        
        # Add time range annotation if specified
        time_range = kwargs.get('time_range')
        if time_range and len(time_range) == 2:
            start_time, end_time = time_range
            if start_time and end_time:
                fig.add_annotation(
                    xref="paper", yref="paper",
                    x=0.02, y=0.02,
                    xanchor="left", yanchor="bottom",
                    text=f"Time Range: {start_time} to {end_time}",
                    showarrow=False,
                    font=dict(size=9, color="gray")
                )
        
        # Add depth range annotation if specified
        depth_range = kwargs.get('depth_range')
        if depth_range and len(depth_range) == 2:
            min_depth, max_depth = depth_range
            if min_depth is not None and max_depth is not None:
                fig.add_annotation(
                    xref="paper", yref="paper",
                    x=0.98, y=0.02,
                    xanchor="right", yanchor="bottom",
                    text=f"Depth Range: {min_depth}m to {max_depth}m",
                    showarrow=False,
                    font=dict(size=9, color="gray")
                )
    
    @staticmethod
    def add_realtime_status(fig: go.Figure, **kwargs):
        """Add real-time status annotation"""
        realtime_status = kwargs.get('realtime_status', 'Running')
        status_color = 'green' if realtime_status == 'Running' else 'red'
        
        fig.add_annotation(
            xref="paper", yref="paper",
            x=0.5, y=0.95,
            xanchor="center", yanchor="top",
            text=f"Real-time Update: {realtime_status}",
            showarrow=False,
            font=dict(size=12, color=status_color, family="Arial Black"),
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor=status_color,
            borderwidth=2
        )
    
    @staticmethod
    def add_statistical_annotations(fig: go.Figure, data: pd.DataFrame, variables: List[str]):
        """Add statistical annotations to the plot"""
        for i, variable in enumerate(variables):
            if variable not in data.columns:
                continue
            
            var_data = data[variable].dropna()
            if len(var_data) == 0:
                continue
            
            # Calculate statistics
            mean_val = var_data.mean()
            std_val = var_data.std()
            min_val = var_data.min()
            max_val = var_data.max()
            
            # Add annotation
            annotation_text = f"Mean: {mean_val:.2f}<br>Std: {std_val:.2f}<br>Range: [{min_val:.2f}, {max_val:.2f}]"
            
            fig.add_annotation(
                xref="paper", yref="paper",
                x=0.98, y=0.95 - i * 0.1,
                xanchor="right", yanchor="top",
                text=annotation_text,
                showarrow=False,
                font=dict(size=9, color="gray"),
                bgcolor="rgba(255,255,255,0.8)",
                bordercolor="gray",
                borderwidth=1
            )
    
    @staticmethod
    def get_plot_statistics(data: pd.DataFrame, variables: List[str]) -> Dict[str, Dict[str, float]]:
        """Get statistics for the plotted variables"""
        stats = {}
        
        for variable in variables:
            if variable not in data.columns:
                continue
            
            var_data = data[variable].dropna()
            if len(var_data) == 0:
                continue
            
            stats[variable] = {
                'count': len(var_data),
                'mean': float(var_data.mean()),
                'std': float(var_data.std()),
                'min': float(var_data.min()),
                'max': float(var_data.max()),
                'median': float(var_data.median()),
                'q25': float(var_data.quantile(0.25)),
                'q75': float(var_data.quantile(0.75))
            }
        
        return stats
    
    @staticmethod
    def get_standard_variables() -> List[str]:
        """Get list of standard TRIAXUS variables"""
        return ['temperature', 'salinity', 'oxygen', 'fluorescence', 'ph']
    
    @staticmethod
    def create_multi_variable_plot(plotter, data: pd.DataFrame, variables: List[str], **kwargs) -> go.Figure:
        """Create a multi-variable time series plot with shared x-axis"""
        return plotter.create_plot(data, variables, **kwargs)
    
    @staticmethod
    def create_single_variable_plot(plotter, data: pd.DataFrame, variable: str, **kwargs) -> go.Figure:
        """Create a single variable time series plot"""
        return plotter.create_plot(data, [variable], **kwargs)
    
    @staticmethod
    def create_industry_standard_plot(plotter, data: pd.DataFrame, **kwargs) -> go.Figure:
        """
        Create industry standard time series plot with standard variables
        
        Args:
            plotter: TimeSeriesPlotter instance
            data: Input data
            **kwargs: Additional parameters including:
                - selected_variables: List of selected variables (default: all standard)
                - data_source: Data source type
                - time_range: Time range tuple
                - depth_range: Depth range tuple
                - real_time_update: Boolean for real-time mode
                - realtime_status: Status string ('Running', 'Stopped')
                
        Returns:
            Plotly figure object
        """
        # Get selected variables or use all standard variables
        selected_vars = kwargs.get('selected_variables', TimeSeriesHelpers.get_standard_variables())
        
        # Filter to only include variables that exist in data
        available_vars = [var for var in selected_vars if var in data.columns]
        
        if not available_vars:
            raise ValueError("None of the selected variables are available in the data")
        
        # Set default parameters for industry standard plot
        industry_kwargs = {
            'data_source': kwargs.get('data_source', 'Mixed (Historical + Real-time)'),
            'title': 'TRIAXUS Industry Standard Time Series Plot',
            'add_annotations': True,
            'show_statistics': kwargs.get('show_statistics', False),
            'height': kwargs.get('height', 700),
            'width': kwargs.get('width', 1000)
        }
        
        # Merge with user-provided kwargs
        industry_kwargs.update(kwargs)
        
        return plotter.create_plot(data, available_vars, **industry_kwargs)
