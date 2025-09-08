"""
Unified Configuration Manager for TRIAXUS visualization system

This module provides a single, clean interface for managing all system
configurations with support for external files and theme management.
"""

from typing import Dict, Any, Optional, Union
from pathlib import Path
import logging

from .loader import ConfigLoader
# Schema classes removed - using simple dict-based configuration

logger = logging.getLogger(__name__)


class ConfigManager:
    """Unified configuration manager for TRIAXUS system"""
    
    def __init__(self, config_dir: Optional[Union[str, Path]] = None, custom_config_path: Optional[Union[str, Path]] = None):
        """
        Initialize ConfigManager
        
        Args:
            config_dir: Directory containing configuration files
            custom_config_path: Path to custom configuration file for overrides
        """
        self.config_dir = Path(config_dir) if config_dir else Path("configs")
        self.custom_config_path = Path(custom_config_path) if custom_config_path else None
        
        # Initialize components
        self.loader = ConfigLoader(self.config_dir)
        
        # Current state
        self._current_theme = 'oceanographic'
        self._current_plot_type = 'time_series'
        
        # Load configurations
        self._load_configurations()
    
    def _load_configurations(self):
        """Load all configurations from files and defaults"""
        # Load main configuration (merged with custom overrides)
        main_config = self.loader.load_merged_config(self.custom_config_path)
        if main_config:
            self._merge_main_config(main_config)
        
        # Load theme configurations
        theme_configs = self.loader.load_all_themes()
        for theme_name, theme_config in theme_configs.items():
            self._merge_theme_config(theme_name, theme_config)
    
    def _merge_main_config(self, config: Dict[str, Any]):
        """Merge main configuration with defaults"""
        # Store the merged configuration for later use
        self._merged_config = config
    
    def _merge_theme_config(self, theme_name: str, config: Dict[str, Any]):
        """Merge theme-specific configuration"""
        # Theme configurations are now handled by StyleConfig
        # This method is kept for future extensibility
        pass
    
    # Theme management
    def get_available_themes(self) -> list:
        """Get list of available themes"""
        # Get themes from configuration files
        theme_configs = self.loader.load_all_themes()
        available_themes = list(theme_configs.keys())
        
        # Add custom themes from merged config
        main_config = getattr(self, '_merged_config', None)
        if main_config and 'colors' in main_config and 'themes' in main_config['colors']:
            custom_themes = main_config['colors']['themes']
            for theme_name in custom_themes.keys():
                if theme_name not in available_themes:
                    available_themes.append(theme_name)
        
        # Add default themes if not found in files
        # These are the built-in themes that should always be available
        default_themes = ['default', 'oceanographic', 'dark', 'high_contrast']
        for theme in default_themes:
            if theme not in available_themes:
                available_themes.append(theme)
        
        return available_themes
    
    def get_current_theme(self) -> str:
        """Get current theme name"""
        return self._current_theme
    
    def set_theme(self, theme_name: str):
        """Set current theme"""
        if theme_name in self.get_available_themes():
            self._current_theme = theme_name
            logger.info(f"Theme changed to: {theme_name}")
        else:
            logger.warning(f"Theme '{theme_name}' not available")
    
    def get_style_config(self, theme_name: str = None) -> Dict[str, Any]:
        """Get style configuration for theme"""
        if theme_name is None:
            theme_name = self._current_theme
        
        # Try to get theme config from files first
        theme_config = self._get_theme_config(theme_name)
        if theme_config:
            return theme_config
        
        # Fallback to default theme from config file
        main_config = getattr(self, '_merged_config', None)
        if main_config and 'colors' in main_config and 'themes' in main_config['colors']:
            themes = main_config['colors']['themes']
            if theme_name in themes:
                return {'colors': themes[theme_name], 'template': 'plotly_white'}
        
        # Final fallback to hardcoded default
        return {
            'colors': {
                'background': '#FFFFFF',
                'text': '#333333',
                'grid': '#E0E0E0',
                'primary': '#1976D2',
                'secondary': '#D32F2F',
                'accent': '#43A047'
            },
            'template': 'plotly_white'
        }
    
    def _get_theme_config(self, theme_name: str) -> Optional[Dict[str, Any]]:
        """Get theme configuration from files or custom config"""
        # Try to load theme-specific configuration
        theme_config = self.loader.load_theme_config(theme_name)
        
        # Also check for custom themes in merged config
        main_config = getattr(self, '_merged_config', None)
        if main_config and 'colors' in main_config and 'themes' in main_config['colors']:
            custom_themes = main_config['colors']['themes']
            if theme_name in custom_themes:
                theme_config = {'colors': custom_themes[theme_name]}
        
        return theme_config
    
    def _get_variable_colors(self, theme: str) -> Dict[str, str]:
        """Get variable-specific colors for theme"""
        # Try to get from config file first
        main_config = getattr(self, '_merged_config', None)
        if main_config and 'variables' in main_config:
            variables = main_config['variables']
            result = {}
            for var_name, var_colors in variables.items():
                if isinstance(var_colors, dict) and theme in var_colors:
                    result[var_name] = var_colors[theme]
                elif isinstance(var_colors, dict) and 'default' in var_colors:
                    result[var_name] = var_colors['default']
            if result:
                return result
        
        # Fallback to hardcoded colors
        variable_colors = {
            'tv290C': {
                'default': '#FF6B6B',
                'oceanographic': '#B73E3A',
                'dark': '#FF6B6B',
                'high_contrast': '#FF0000'
            },
            'flECO-AFL': {
                'default': '#4ECDC4',
                'oceanographic': '#1E88E5',
                'dark': '#4ECDC4',
                'high_contrast': '#00FF00'
            },
            'ph': {
                'default': '#45B7D1',
                'oceanographic': '#43A047',
                'dark': '#45B7D1',
                'high_contrast': '#0000FF'
            },
            'sbeox0Mm_L': {
                'default': '#96CEB4',
                'oceanographic': '#7CB342',
                'dark': '#96CEB4',
                'high_contrast': '#FFFF00'
            },
            'sal00': {
                'default': '#FFEAA7',
                'oceanographic': '#8E24AA',
                'dark': '#FFEAA7',
                'high_contrast': '#FF00FF'
            }
        }
        
        return {var: colors.get(theme, colors['default']) 
                for var, colors in variable_colors.items()}
    
    # Plot type management
    def get_available_plot_types(self) -> list:
        """Get list of available plot types"""
        return ['default', 'time_series', 'depth_profile', 'contour', 'map']
    
    def get_current_plot_type(self) -> str:
        """Get current plot type"""
        return self._current_plot_type
    
    def set_plot_type(self, plot_type: str):
        """Set current plot type"""
        if plot_type in self.get_available_plot_types():
            self._current_plot_type = plot_type
            logger.info(f"Plot type changed to: {plot_type}")
        else:
            logger.warning(f"Plot type '{plot_type}' not available")
    
    def get_plot_config(self, plot_type: str = None) -> Dict[str, Any]:
        """Get plot configuration for plot type"""
        if plot_type is None:
            plot_type = self._current_plot_type
        
        # Try to get from config file first
        main_config = getattr(self, '_merged_config', None)
        if main_config and 'plot' in main_config:
            plot_config = main_config['plot']
            return {
                'dimensions': {
                    'width': plot_config.get('default_width', 800),
                    'height': plot_config.get('default_height', 600)
                },
                'line': {
                    'width': plot_config.get('line', {}).get('default_width', 2)
                },
                'marker': {
                    'size': plot_config.get('marker', {}).get('default_size', 4)
                },
                'grid': {
                    'show': plot_config.get('grid', {}).get('show', True),
                    'color': plot_config.get('grid', {}).get('color', 'lightgray')
                }
            }
        
        # Fallback to hardcoded values
        return {
            'dimensions': {'width': 800, 'height': 600},
            'line': {'width': 2},
            'marker': {'size': 4},
            'grid': {'show': True, 'color': 'lightgray'}
        }
    
    # Data configuration
    def get_data_config(self) -> Dict[str, Any]:
        """Get data configuration"""
        return {
            'variables': ['time', 'depth', 'latitude', 'longitude', 'tv290C', 'sal00', 'sbeox0Mm_L', 'flECO-AFL', 'ph'],
            'required_variables': ['time', 'depth', 'latitude', 'longitude']
        }
    
    # Validation configuration
    def get_validation_config(self) -> Dict[str, Any]:
        """Get validation configuration"""
        return {
            'level': 'moderate',
            'log_errors': True,
            'max_errors': 100
        }
    
    # Utility methods for backward compatibility
    def get_config(self, key: Optional[str] = None) -> Any:
        """Get configuration value (backward compatibility)"""
        if key is None:
            return {
                'theme': self._current_theme,
                'plot_type': self._current_plot_type,
                'plot_width': self.get_plot_config().dimensions.width,
                'plot_height': self.get_plot_config().dimensions.height,
                'line_width': self.get_plot_config().line.width,
                'marker_size': self.get_plot_config().marker.size
            }
        
        # Handle specific keys
        if key == 'theme':
            return self._current_theme
        elif key == 'plot_type':
            return self._current_plot_type
        elif key == 'plot_width':
            return self.get_plot_config().dimensions.width
        elif key == 'plot_height':
            return self.get_plot_config().dimensions.height
        elif key == 'line_width':
            return self.get_plot_config().line.width
        elif key == 'marker_size':
            return self.get_plot_config().marker.size
        elif key == 'colors':
            return self.get_style_config().get('colors', {})
        elif key == 'layout':
            return self.get_style_config().get('colors', {})
        
        return None
    
    def set_config(self, key: str, value: Any):
        """Set configuration value (backward compatibility)"""
        if key == 'theme':
            self.set_theme(value)
        elif key == 'plot_type':
            self.set_plot_type(value)
        elif key == 'plot_width':
            self.get_plot_config().dimensions.width = value
        elif key == 'plot_height':
            self.get_plot_config().dimensions.height = value
        elif key == 'line_width':
            self.get_plot_config().line.width = value
        elif key == 'marker_size':
            self.get_plot_config().marker.size = value
    
    # External configuration methods
    def get_external_config(self) -> Dict[str, Any]:
        """Get external configuration"""
        return self.loader.load_config() or {}
    
    def reload_external_config(self):
        """Reload external configuration from files"""
        self.loader.clear_cache()
        self._load_configurations()
        logger.info("External configuration reloaded")
    
    # Convenience methods
    def get_plot_dimensions(self) -> Dict[str, int]:
        """Get plot dimensions from configuration"""
        plot_config = self.get_plot_config()
        return {
            'width': plot_config.dimensions.width,
            'height': plot_config.dimensions.height
        }
    
    def get_line_config(self) -> Dict[str, Any]:
        """Get line configuration"""
        plot_config = self.get_plot_config()
        return {
            'width': plot_config.line.width
        }
    
    def get_marker_config(self) -> Dict[str, Any]:
        """Get marker configuration"""
        plot_config = self.get_plot_config()
        return {
            'size': plot_config.marker.size
        }
    
    def get_color_config(self, theme: str = None) -> Dict[str, Any]:
        """Get color configuration for theme"""
        if theme is None:
            theme = self._current_theme
        
        style_config = self.get_style_config(theme)
        return {
            'theme_colors': style_config.get('colors', {}),
            'variable_colors': self._get_variable_colors(theme)
        }
    
    def get_map_config(self) -> Dict[str, Any]:
        """Get map configuration"""
        return self.get_plot_config('map').get_map_config()
    
    def get_font_config(self) -> Dict[str, Any]:
        """Get font configuration"""
        style_config = self.get_style_config()
        return {
            'family': 'Arial, sans-serif',
            'size': 12,
            'title_size': 14
        }
    
    def get_annotation_config(self) -> Dict[str, Any]:
        """Get annotation configuration"""
        style_config = self.get_style_config()
        return {
            'font_size': style_config.annotations.font_size,
            'color': style_config.annotations.color,
            'border_width': style_config.annotations.border_width
        }
    
    def get_status_config(self) -> Dict[str, Any]:
        """Get status configuration"""
        style_config = self.get_style_config()
        return {
            'font_size': style_config.status.font_size,
            'border_width': style_config.status.border_width,
            'colors': style_config.status.colors
        }
    
    def get_data_config_dict(self) -> Dict[str, Any]:
        """Get data configuration as dictionary"""
        data_config = self.get_data_config()
        return {
            'sampling': {
                'size': data_config.sampling.size,
                'random_seed': data_config.sampling.random_seed
            },
            'test_data': data_config.test_data,
            'data_source': data_config.data_source
        }
    
    def get_performance_config(self) -> Dict[str, Any]:
        """Get performance configuration"""
        main_config = self.get_external_config()
        if 'performance' in main_config:
            return main_config['performance']
        
        return {
            'max_data_points': 10000,
            'enable_caching': True,
            'cache_size': 100
        }
    
    def get_html_config(self) -> Dict[str, Any]:
        """Get HTML configuration"""
        main_config = self.get_external_config()
        if 'html' in main_config:
            return main_config['html']
        
        return {
            'include_plotlyjs': True,
            'div_id_prefix': 'plot_',
            'template': 'plotly_white',
            'config': {
                'displayModeBar': True,
                'displaylogo': False,
                'modeBarButtonsToRemove': ['pan2d', 'lasso2d', 'select2d']
            }
        }
