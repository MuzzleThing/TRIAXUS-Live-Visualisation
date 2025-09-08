"""
Map Plotter Helpers for TRIAXUS visualization system

This module provides helper functions for map plotting functionality.
"""

import pandas as pd
import plotly.graph_objects as go
from typing import Dict, Any, Tuple
import logging

logger = logging.getLogger(__name__)


class MapHelpers:
    """Helper class for map plotting functionality"""
    
    @staticmethod
    def add_trajectory_line(fig: go.Figure, data: pd.DataFrame, line_config: Dict[str, Any]):
        """Add trajectory line to Mapbox plot"""
        line_trace = go.Scattermapbox(
            lat=data['latitude'],
            lon=data['longitude'],
            mode='lines',
            line=dict(
                color=line_config.get('color', '#D32F2F'),
                width=line_config.get('width', 3)
            ),
            name='TRIAXUS Track',
            hovertemplate='<b>TRIAXUS Track</b><br>' +
                         'Lat: %{lat:.4f}<br>' +
                         'Lon: %{lon:.4f}<br>' +
                         '<extra></extra>'
        )
        fig.add_trace(line_trace)
    
    @staticmethod
    def add_trajectory_line_geo(fig: go.Figure, data: pd.DataFrame, line_config: Dict[str, Any]):
        """Add trajectory line to scattergeo plot"""
        line_trace = go.Scattergeo(
            lat=data['latitude'],
            lon=data['longitude'],
            mode='lines',
            line=dict(
                color=line_config.get('color', '#D32F2F'),
                width=line_config.get('width', 3)
            ),
            name='TRIAXUS Track',
            hovertemplate='<b>TRIAXUS Track</b><br>' +
                         'Lat: %{lat:.4f}<br>' +
                         'Lon: %{lon:.4f}<br>' +
                         '<extra></extra>'
        )
        fig.add_trace(line_trace)
    
    @staticmethod
    def add_data_points(fig: go.Figure, data: pd.DataFrame, marker_config: Dict[str, Any]):
        """Add data points to Mapbox plot"""
        marker_trace = go.Scattermapbox(
            lat=data['latitude'],
            lon=data['longitude'],
            mode='markers',
            marker=dict(
                size=marker_config.get('size', 8),
                color=marker_config.get('current_color', '#1976D2'),
                opacity=marker_config.get('opacity', 0.8)
            ),
            name='Data Points',
            hovertemplate='<b>Data Point</b><br>' +
                         'Lat: %{lat:.4f}<br>' +
                         'Lon: %{lon:.4f}<br>' +
                         'Time: %{customdata}<br>' +
                         '<extra></extra>',
            customdata=data['time']
        )
        fig.add_trace(marker_trace)
    
    @staticmethod
    def add_data_points_geo(fig: go.Figure, data: pd.DataFrame, marker_config: Dict[str, Any]):
        """Add data points to scattergeo plot"""
        marker_trace = go.Scattergeo(
            lat=data['latitude'],
            lon=data['longitude'],
            mode='markers',
            marker=dict(
                size=marker_config.get('size', 8),
                color=marker_config.get('current_color', '#1976D2'),
                opacity=marker_config.get('opacity', 0.8)
            ),
            name='Data Points',
            hovertemplate='<b>Data Point</b><br>' +
                         'Lat: %{lat:.4f}<br>' +
                         'Lon: %{lon:.4f}<br>' +
                         'Time: %{customdata}<br>' +
                         '<extra></extra>',
            customdata=data['time']
        )
        fig.add_trace(marker_trace)
    
    @staticmethod
    def add_start_end_markers(fig: go.Figure, data: pd.DataFrame, marker_config: Dict[str, Any]):
        """Add start and end markers to Mapbox plot"""
        if len(data) == 0:
            return
        
        # Start marker
        start_trace = go.Scattermapbox(
            lat=[data['latitude'].iloc[0]],
            lon=[data['longitude'].iloc[0]],
            mode='markers',
            marker=dict(
                size=marker_config.get('start_size', 12),
                color=marker_config.get('start_color', '#43A047'),
                symbol='circle'
            ),
            name='Start',
            hovertemplate='<b>Start Point</b><br>' +
                         'Lat: %{lat:.4f}<br>' +
                         'Lon: %{lon:.4f}<br>' +
                         '<extra></extra>'
        )
        fig.add_trace(start_trace)
        
        # End marker
        if len(data) > 1:
            end_trace = go.Scattermapbox(
                lat=[data['latitude'].iloc[-1]],
                lon=[data['longitude'].iloc[-1]],
                mode='markers',
                marker=dict(
                    size=marker_config.get('end_size', 12),
                    color=marker_config.get('end_color', '#D32F2F'),
                    symbol='circle'
                ),
                name='End',
                hovertemplate='<b>End Point</b><br>' +
                             'Lat: %{lat:.4f}<br>' +
                             'Lon: %{lon:.4f}<br>' +
                             '<extra></extra>'
            )
            fig.add_trace(end_trace)
    
    @staticmethod
    def add_start_end_markers_geo(fig: go.Figure, data: pd.DataFrame, marker_config: Dict[str, Any]):
        """Add start and end markers to scattergeo plot"""
        if len(data) == 0:
            return
        
        # Start marker
        start_trace = go.Scattergeo(
            lat=[data['latitude'].iloc[0]],
            lon=[data['longitude'].iloc[0]],
            mode='markers',
            marker=dict(
                size=marker_config.get('start_size', 12),
                color=marker_config.get('start_color', '#43A047'),
                symbol='circle'
            ),
            name='Start',
            hovertemplate='<b>Start Point</b><br>' +
                         'Lat: %{lat:.4f}<br>' +
                         'Lon: %{lon:.4f}<br>' +
                         '<extra></extra>'
        )
        fig.add_trace(start_trace)
        
        # End marker
        if len(data) > 1:
            end_trace = go.Scattergeo(
                lat=[data['latitude'].iloc[-1]],
                lon=[data['longitude'].iloc[-1]],
                mode='markers',
                marker=dict(
                    size=marker_config.get('end_size', 12),
                    color=marker_config.get('end_color', '#D32F2F'),
                    symbol='circle'
                ),
                name='End',
                hovertemplate='<b>End Point</b><br>' +
                             'Lat: %{lat:.4f}<br>' +
                             'Lon: %{lon:.4f}<br>' +
                             '<extra></extra>'
            )
            fig.add_trace(end_trace)
    
    @staticmethod
    def calculate_zoom_level(lat_span: float, lon_span: float, zoom_config: Dict[str, Any]) -> int:
        """Calculate appropriate zoom level based on data span"""
        max_span = max(lat_span, lon_span)
        auto_zoom = zoom_config.get('auto_zoom', {})
        
        if max_span > auto_zoom.get('very_wide', 2.0):
            return 6
        elif max_span > auto_zoom.get('wide', 1.0):
            return 8
        elif max_span > auto_zoom.get('medium', 0.5):
            return 10
        elif max_span > auto_zoom.get('small', 0.2):
            return 12
        else:
            return 14
    
    @staticmethod
    def get_style_config(map_config: Dict[str, Any], map_style: str) -> Tuple[Dict[str, str], str]:
        """Get style configuration for scattergeo plots"""
        # Get colors from config file
        colors = map_config.get('colors', {
            'land': 'lightgray',
            'ocean': 'lightblue',
            'lakes': 'lightblue',
            'rivers': 'lightblue'
        })
        
        # Get projection from config file
        projection = map_config.get('projection', 'equirectangular')
        
        return colors, projection
    
    @staticmethod
    def is_offline_map_style(map_style: str) -> bool:
        """Check if the map style is an offline style"""
        return map_style == 'open-street-map'
