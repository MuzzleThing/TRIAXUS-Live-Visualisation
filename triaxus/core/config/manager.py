"""
Refactored Configuration Manager for TRIAXUS visualization system

This module provides a clean, modular configuration management system
using dynaconf with separated concerns and better maintainability.
"""

from typing import Dict, Any, Optional, Union
from pathlib import Path
import logging
import yaml

from dynaconf import Dynaconf, ValidationError

from .theme_manager import ThemeManager
from .plot_config_manager import PlotConfigManager
from .data_config_manager import DataConfigManager
from .ui_config_manager import UIConfigManager

logger = logging.getLogger(__name__)


class ConfigManager:
    """Refactored configuration manager with separated concerns"""

    def __init__(
        self,
        config_dir: Optional[Union[str, Path]] = None,
        custom_config_path: Optional[Union[str, Path]] = None,
        environment: str = "default",
    ):
        """
        Initialize ConfigManager with dynaconf

        Args:
            config_dir: Directory containing configuration files
            custom_config_path: Path to custom configuration file for overrides
            environment: Environment name (default, development, production, etc.)
        """
        self.config_dir = Path(config_dir) if config_dir else Path("configs")
        self.environment = environment

        # Auto-detect custom config if not specified
        if custom_config_path is None:
            custom_config_path = self.config_dir / "custom.yaml"
            if not custom_config_path.exists():
                custom_config_path = None

        self.custom_config_path = (
            Path(custom_config_path) if custom_config_path else None
        )

        # Build settings files list
        settings_files = [str(self.config_dir / "default.yaml")]
        if self.custom_config_path and self.custom_config_path.exists():
            settings_files.append(str(self.custom_config_path))

        # Initialize dynaconf
        self.settings = Dynaconf(
            settings_files=settings_files,
            merge_enabled=True,
            merge_keys=False,  # Disable key merging to allow list replacement
            silent=False,  # Enable logging to debug
        )
        
        # Load config directly with yaml for better control over merging
        self._yaml_config = None
        try:
            with open(self.config_dir / "default.yaml", 'r') as f:
                self._yaml_config = yaml.safe_load(f)
            
            # If custom config exists, merge it manually to handle list replacement
            if self.custom_config_path and self.custom_config_path.exists():
                with open(self.custom_config_path, 'r') as f:
                    custom_config = yaml.safe_load(f)
                    self._yaml_config = self._deep_merge(self._yaml_config, custom_config)
                    logger.info(f"Loaded custom config from {self.custom_config_path}")
        except Exception as e:
            logger.warning(f"Failed to load YAML config directly: {e}")

        # Initialize specialized managers
        self.theme_manager = ThemeManager(self.settings, self._yaml_config)
        self.plot_config_manager = PlotConfigManager(self.settings, self._yaml_config)
        self.data_config_manager = DataConfigManager(self.settings, self._yaml_config)
        self.ui_config_manager = UIConfigManager(self.settings, self._yaml_config)

        logger.info(f"ConfigManager initialized for environment: {environment}")

    def _deep_merge(self, base_dict, override_dict):
        """
        Deep merge two dictionaries, with override_dict taking precedence.
        Lists are replaced entirely, not merged.
        """
        result = base_dict.copy()
        
        for key, value in override_dict.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
                
        return result

    # Theme management delegation
    def get_available_themes(self):
        """Get list of available themes"""
        return self.theme_manager.get_available_themes()

    def get_current_theme(self) -> str:
        """Get current theme name"""
        return self.theme_manager.get_current_theme()

    def set_theme(self, theme_name: str):
        """Set current theme"""
        self.theme_manager.set_theme(theme_name)

    def get_style_config(self, theme_name: Optional[str] = None) -> Dict[str, Any]:
        """Get style configuration for theme"""
        return self.theme_manager.get_style_config(theme_name)

    def get_variable_colors(self, theme: Optional[str] = None) -> Dict[str, str]:
        """Get variable-specific colors for theme"""
        return self.theme_manager.get_variable_colors(theme)

    def get_color_config(self, theme: Optional[str] = None) -> Dict[str, Any]:
        """Get color configuration for theme"""
        return self.theme_manager.get_color_config(theme)

    # Plot configuration delegation
    def get_available_plot_types(self):
        """Get list of available plot types"""
        return self.plot_config_manager.get_available_plot_types()

    def get_current_plot_type(self) -> str:
        """Get current plot type"""
        return self.plot_config_manager.get_current_plot_type()

    def set_plot_type(self, plot_type: str):
        """Set current plot type"""
        self.plot_config_manager.set_plot_type(plot_type)

    def get_plot_config(self, plot_type: Optional[str] = None) -> Dict[str, Any]:
        """Get plot configuration for plot type"""
        return self.plot_config_manager.get_plot_config(plot_type)

    def get_plot_dimensions(self) -> Dict[str, int]:
        """Get plot dimensions from configuration"""
        return self.plot_config_manager.get_plot_dimensions()

    def get_line_config(self) -> Dict[str, Any]:
        """Get line configuration"""
        return self.plot_config_manager.get_line_config()

    def get_marker_config(self) -> Dict[str, Any]:
        """Get marker configuration"""
        return self.plot_config_manager.get_marker_config()

    def get_time_series_config(self) -> Dict[str, Any]:
        """Get time series plot configuration"""
        return self.plot_config_manager.get_time_series_config()

    def get_contour_config(self) -> Dict[str, Any]:
        """Get contour plot configuration"""
        return self.plot_config_manager.get_contour_config()

    def get_depth_profile_config(self) -> Dict[str, Any]:
        """Get depth profile plot configuration"""
        return self.plot_config_manager.get_depth_profile_config()

    def get_map_config(self) -> Dict[str, Any]:
        """Get map plot configuration"""
        return self.plot_config_manager.get_map_config()

    def get_mapbox_config(self) -> Dict[str, Any]:
        """Get Mapbox configuration"""
        return self.plot_config_manager.get_mapbox_config()

    def get_map_plot_config(self) -> Dict[str, Any]:
        """Get map plot specific configuration"""
        return self.plot_config_manager.get_map_plot_config()

    # Data configuration delegation
    def get_data_config(self) -> Dict[str, Any]:
        """Get data configuration"""
        return self.data_config_manager.get_data_config()

    def get_validation_config(self) -> Dict[str, Any]:
        """Get validation configuration"""
        return self.data_config_manager.get_validation_config()

    def get_data_generation_config(self) -> Dict[str, Any]:
        """Get data generation configuration"""
        return self.data_config_manager.get_data_generation_config()

    def get_data_sampling_config(self) -> Dict[str, Any]:
        """Get data sampling configuration"""
        return self.data_config_manager.get_data_sampling_config()

    def get_archiving_config(self) -> Dict[str, Any]:
        """Get data archiving configuration"""
        return self.data_config_manager.get_archiving_config()
    
    def get_database_config(self) -> Dict[str, Any]:
        """Get database configuration"""
        return self.settings.get("database", {})
    def get_test_data_config(self) -> Dict[str, Any]:
        """Get test data configuration"""
        return self.data_config_manager.get_test_data_config()

    def get_performance_config(self) -> Dict[str, Any]:
        """Get performance configuration"""
        return self.data_config_manager.get_performance_config()

    # UI configuration delegation
    def get_font_config(self) -> Dict[str, Any]:
        """Get font configuration"""
        return self.ui_config_manager.get_font_config()

    def get_annotation_config(self) -> Dict[str, Any]:
        """Get annotation configuration"""
        return self.ui_config_manager.get_annotation_config()

    def get_status_config(self) -> Dict[str, Any]:
        """Get status configuration"""
        return self.ui_config_manager.get_status_config()

    def get_html_config(self) -> Dict[str, Any]:
        """Get HTML configuration"""
        return self.ui_config_manager.get_html_config()

    def get_files_config(self) -> Dict[str, Any]:
        """Get file I/O configuration"""
        return self.ui_config_manager.get_files_config()

    def get_statistics_config(self) -> Dict[str, Any]:
        """Get statistics configuration"""
        return self.ui_config_manager.get_statistics_config()

    def get_depth_zones_config(self) -> list:
        """Get depth zones configuration"""
        return self.ui_config_manager.get_depth_zones_config()

    # Core configuration methods
    def get_external_config(self) -> Dict[str, Any]:
        """Get external configuration (all settings)"""
        return dict(self.settings)

    def reload_external_config(self):
        """Reload external configuration from files"""
        self.settings.reload()
        logger.info("External configuration reloaded")

    # Dynaconf-specific methods
    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a setting value using dot notation"""
        return self.settings.get(key, default)

    def set_setting(self, key: str, value: Any):
        """Set a setting value using dot notation"""
        self.settings.set(key, value)

    def switch_environment(self, environment: str):
        """Switch to a different environment"""
        self.environment = environment
        self.settings.setenv(environment)
        logger.info(f"Switched to environment: {environment}")

    def get_environment(self) -> str:
        """Get current environment"""
        return self.environment

    def validate_config(self) -> bool:
        """Validate current configuration"""
        try:
            # Use YAML fallback if dynaconf fails
            config_source = self._yaml_config if self._yaml_config else self.settings
            
            # Validate that all required sections exist
            required_sections = [
                "colors",
                "plot", 
                "data_generation",
                "font",
                "annotations",
                "status",
                "performance"
            ]
            
            for section in required_sections:
                if section == "colors":
                    # Special handling for colors section
                    if not config_source.get(section) or not config_source.get(section, {}).get("themes"):
                        logger.warning(f"Missing required configuration section: {section}.themes")
                        return False
                else:
                    if not config_source.get(section):
                        logger.warning(f"Missing required configuration section: {section}")
                        return False
            
            # Validate theme configurations
            available_themes = self.get_available_themes()
            if not available_themes:
                logger.error("No themes available")
                return False
                
            # Validate current theme
            current_theme = self.get_current_theme()
            if current_theme not in available_themes:
                logger.error(f"Current theme '{current_theme}' not in available themes")
                return False
            
            logger.info("Configuration validation passed")
            return True
            
        except Exception as e:
            logger.error(f"Configuration validation failed: {e}")
            return False

    # Environment variable support
    def get_from_env(self, key: str, default: Any = None) -> Any:
        """Get value from environment variable with TRIAXUS prefix"""
        import os

        env_key = f"TRIAXUS_{key.upper()}"
        return os.getenv(env_key, default)



