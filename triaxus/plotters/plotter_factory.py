"""
Plotter Factory for TRIAXUS visualization system

This module provides factory pattern implementation for creating plotter instances.
"""

from typing import Dict, Type, Optional
import logging

from ..core.base_plotter import BasePlotter
from ..core.config import ConfigManager
from .time_series import TimeSeriesPlotter
from .depth_profile import DepthProfilePlotter
from .contour import ContourPlotter
from .map_plot import MapPlotter


class PlotterFactory:
    """Factory for creating plotter instances"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Registry of available plotters
        self._plotters: Dict[str, Type[BasePlotter]] = {
            'time_series': TimeSeriesPlotter,
            'depth_profile': DepthProfilePlotter,
            'contour': ContourPlotter,
            'map': MapPlotter
        }
        
        # Registry of plotter configurations
        self._plotter_configs: Dict[str, Dict] = {
            'time_series': {
                'name': 'Time Series Plot',
                'description': 'Plot variables against time',
                'required_columns': ['time', 'depth'],
                'optional_columns': []  # Will be populated from config
            },
            'depth_profile': {
                'name': 'Depth Profile Plot',
                'description': 'Plot variables against depth',
                'required_columns': ['depth'],
                'optional_columns': []  # Will be populated from config
            },
            'contour': {
                'name': 'Contour Plot',
                'description': '2D contour plot of variables over time and depth',
                'required_columns': ['time', 'depth'],
                'optional_columns': []  # Will be populated from config
            },
            'map': {
                'name': 'Map Plot',
                'description': 'Geographic plot of TRIAXUS track',
                'required_columns': ['latitude', 'longitude', 'time'],
                'optional_columns': []  # Will be populated from config
            }
        }
    
    @classmethod
    def create_plotter(cls, plot_type: str, config_manager: ConfigManager) -> BasePlotter:
        """
        Create a plotter instance
        
        Args:
            plot_type: Type of plotter to create
            config_manager: Configuration manager instance
            
        Returns:
            Plotter instance
            
        Raises:
            ValueError: If plot type is not supported
        """
        factory = cls()
        return factory._create_plotter(plot_type, config_manager)
    
    def _create_plotter(self, plot_type: str, config_manager: ConfigManager) -> BasePlotter:
        """Internal method to create plotter"""
        if plot_type not in self._plotters:
            available_types = list(self._plotters.keys())
            raise ValueError(f"Unknown plot type: {plot_type}. Available types: {available_types}")
        
        plotter_class = self._plotters[plot_type]
        plotter = plotter_class(config_manager)
        
        self.logger.info(f"Created {plot_type} plotter")
        return plotter
    
    def register_plotter(self, plot_type: str, plotter_class: Type[BasePlotter], config: Optional[Dict] = None):
        """
        Register a new plotter type
        
        Args:
            plot_type: Type identifier for the plotter
            plotter_class: Plotter class to register
            config: Optional configuration for the plotter
        """
        if not issubclass(plotter_class, BasePlotter):
            raise ValueError("Plotter class must inherit from BasePlotter")
        
        self._plotters[plot_type] = plotter_class
        
        if config:
            self._plotter_configs[plot_type] = config
        
        self.logger.info(f"Registered new plotter type: {plot_type}")
    
    def unregister_plotter(self, plot_type: str):
        """
        Unregister a plotter type
        
        Args:
            plot_type: Type identifier to unregister
        """
        if plot_type in self._plotters:
            del self._plotters[plot_type]
            if plot_type in self._plotter_configs:
                del self._plotter_configs[plot_type]
            self.logger.info(f"Unregistered plotter type: {plot_type}")
        else:
            self.logger.warning(f"Plotter type {plot_type} not found for unregistration")
    
    def get_available_plot_types(self) -> list:
        """Get list of available plot types"""
        return list(self._plotters.keys())
    
    def get_plotter_info(self, plot_type: str) -> Optional[Dict]:
        """Get information about a plotter type"""
        return self._plotter_configs.get(plot_type)
    
    def get_all_plotter_info(self) -> Dict[str, Dict]:
        """Get information about all plotter types"""
        return self._plotter_configs.copy()
    
    def validate_plot_type(self, plot_type: str) -> bool:
        """Validate if a plot type is supported"""
        return plot_type in self._plotters
    
    def get_required_columns(self, plot_type: str) -> list:
        """Get required columns for a plot type"""
        info = self.get_plotter_info(plot_type)
        if info:
            return info.get('required_columns', [])
        return []
    
    def get_optional_columns(self, plot_type: str, config_manager: Optional[ConfigManager] = None) -> list:
        """Get optional columns for a plot type"""
        # First try to get from config if available
        if config_manager:
            try:
                data_config = config_manager.get_data_config()
                return data_config.get_available_variables()
            except Exception:
                pass
        
        # Fallback to hardcoded info
        info = self.get_plotter_info(plot_type)
        if info:
            return info.get('optional_columns', [])
        return []
    
    def get_plotter_description(self, plot_type: str) -> str:
        """Get description for a plot type"""
        info = self.get_plotter_info(plot_type)
        if info:
            return info.get('description', 'No description available')
        return 'Unknown plot type'
    
    # Convenience methods for creating specific plotters
    @classmethod
    def create_time_series_plotter(cls, config_manager: ConfigManager) -> TimeSeriesPlotter:
        """Create a time series plotter"""
        return cls.create_plotter('time_series', config_manager)
    
    @classmethod
    def create_depth_profile_plotter(cls, config_manager: ConfigManager) -> DepthProfilePlotter:
        """Create a depth profile plotter"""
        return cls.create_plotter('depth_profile', config_manager)
    
    @classmethod
    def create_contour_plotter(cls, config_manager: ConfigManager) -> ContourPlotter:
        """Create a contour plotter"""
        return cls.create_plotter('contour', config_manager)
    
    @classmethod
    def create_map_plotter(cls, config_manager: ConfigManager) -> MapPlotter:
        """Create a map plotter"""
        return cls.create_plotter('map', config_manager)
    
    def create_all_plotters(self, config_manager: ConfigManager) -> Dict[str, BasePlotter]:
        """Create all available plotters"""
        plotters = {}
        for plot_type in self._plotters:
            plotters[plot_type] = self._create_plotter(plot_type, config_manager)
        return plotters
    
    def get_plotter_capabilities(self, plot_type: str) -> Dict[str, bool]:
        """Get capabilities of a plotter type"""
        capabilities = {
            'multi_variable': False,
            'single_variable': False,
            'interpolation': False,
            'animation': False,
            'custom_colors': False,
            'statistical_annotations': False
        }
        
        if plot_type == 'time_series':
            capabilities.update({
                'multi_variable': True,
                'single_variable': True,
                'statistical_annotations': True
            })
        elif plot_type == 'depth_profile':
            capabilities.update({
                'multi_variable': True,
                'single_variable': True,
                'statistical_annotations': True
            })
        elif plot_type == 'contour':
            capabilities.update({
                'single_variable': True,
                'interpolation': True,
                'custom_colors': True
            })
        elif plot_type == 'map':
            capabilities.update({
                'animation': True,
                'custom_colors': True
            })
        
        return capabilities
    
    def get_suitable_plotters(self, data_columns: list) -> list:
        """Get list of plotters suitable for the given data columns"""
        suitable_plotters = []
        
        for plot_type, info in self._plotter_configs.items():
            required_columns = info.get('required_columns', [])
            if all(col in data_columns for col in required_columns):
                suitable_plotters.append(plot_type)
        
        return suitable_plotters
    
    def get_plotter_recommendations(self, data_columns: list, data_shape: tuple) -> Dict[str, str]:
        """Get recommendations for which plotters to use based on data"""
        recommendations = {}
        
        # Check data characteristics
        has_time = 'time' in data_columns
        has_depth = 'depth' in data_columns
        has_coordinates = 'latitude' in data_columns and 'longitude' in data_columns
        has_variables = any(var in data_columns for var in ['tv290C', 'flECO-AFL', 'ph', 'sbeox0Mm_L', 'sal00'])
        
        # Generate recommendations
        if has_time and has_depth and has_variables:
            recommendations['contour'] = "Best for visualizing spatial-temporal patterns"
            recommendations['time_series'] = "Good for time-based analysis"
            recommendations['depth_profile'] = "Good for depth-based analysis"
        
        if has_coordinates:
            recommendations['map'] = "Essential for geographic visualization"
        
        if has_time and has_variables and not has_depth:
            recommendations['time_series'] = "Best for time-based analysis without depth"
        
        if has_depth and has_variables and not has_time:
            recommendations['depth_profile'] = "Best for depth-based analysis without time"
        
        return recommendations
