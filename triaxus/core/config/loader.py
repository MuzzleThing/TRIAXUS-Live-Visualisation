"""
Configuration Loader for TRIAXUS visualization system

This module handles loading configuration from external YAML/JSON files
with support for multiple configuration sources and validation.
"""

import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, Union
import logging

logger = logging.getLogger(__name__)


class ConfigLoader:
    """Loads configuration from external files"""
    
    def __init__(self, config_dir: Optional[Union[str, Path]] = None):
        """
        Initialize ConfigLoader
        
        Args:
            config_dir: Directory containing configuration files
        """
        self.config_dir = Path(config_dir) if config_dir else Path("configs")
        self._cache: Dict[str, Any] = {}
    
    def load_config(self, config_path: Optional[Union[str, Path]] = None) -> Optional[Dict[str, Any]]:
        """
        Load configuration from file
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            Configuration dictionary or None if loading fails
        """
        if config_path is None:
            config_path = self.config_dir / "default.yaml"
        
        config_path = Path(config_path)
        
        # Check cache first
        cache_key = str(config_path)
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        try:
            if not config_path.exists():
                logger.warning(f"Configuration file not found: {config_path}")
                return None
            
            with open(config_path, 'r', encoding='utf-8') as f:
                if config_path.suffix.lower() in ['.yaml', '.yml']:
                    config = yaml.safe_load(f)
                elif config_path.suffix.lower() == '.json':
                    config = json.load(f)
                else:
                    logger.error(f"Unsupported configuration file format: {config_path.suffix}")
                    return None
            
            # Cache the loaded configuration
            self._cache[cache_key] = config
            logger.info(f"Configuration loaded from: {config_path}")
            return config
            
        except Exception as e:
            logger.error(f"Failed to load configuration from {config_path}: {e}")
            return None
    
    def load_merged_config(self, custom_config_path: Optional[Union[str, Path]] = None) -> Optional[Dict[str, Any]]:
        """
        Load and merge default configuration with custom overrides
        
        Args:
            custom_config_path: Path to custom configuration file
            
        Returns:
            Merged configuration dictionary or None if loading fails
        """
        # Load default configuration
        default_config = self.load_config()
        if default_config is None:
            logger.error("Failed to load default configuration")
            return None
        
        # If no custom config specified, return default
        if custom_config_path is None:
            return default_config
        
        # Load custom configuration
        custom_config = self.load_config(custom_config_path)
        if custom_config is None:
            logger.warning(f"Failed to load custom configuration from {custom_config_path}, using default")
            return default_config
        
        # Merge configurations (custom overrides default)
        merged_config = self._deep_merge(default_config, custom_config)
        logger.info(f"Configuration merged: default + {custom_config_path}")
        return merged_config
    
    def _deep_merge(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deep merge two dictionaries, with override values taking precedence
        
        Args:
            base: Base dictionary
            override: Override dictionary
            
        Returns:
            Merged dictionary
        """
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def load_theme_config(self, theme_name: str) -> Optional[Dict[str, Any]]:
        """
        Load theme-specific configuration
        
        Args:
            theme_name: Name of the theme
            
        Returns:
            Theme configuration dictionary or None if loading fails
        """
        theme_path = self.config_dir / "themes" / f"{theme_name}.yaml"
        return self.load_config(theme_path)
    
    def load_all_themes(self) -> Dict[str, Dict[str, Any]]:
        """
        Load all available theme configurations
        
        Returns:
            Dictionary mapping theme names to their configurations
        """
        themes = {}
        themes_dir = self.config_dir / "themes"
        
        if not themes_dir.exists():
            logger.warning(f"Themes directory not found: {themes_dir}")
            return themes
        
        for theme_file in themes_dir.glob("*.yaml"):
            theme_name = theme_file.stem
            theme_config = self.load_config(theme_file)
            if theme_config:
                themes[theme_name] = theme_config
        
        return themes
    
    def clear_cache(self):
        """Clear configuration cache"""
        self._cache.clear()
        logger.info("Configuration cache cleared")
    
    def get_available_configs(self) -> list:
        """
        Get list of available configuration files
        
        Returns:
            List of configuration file paths
        """
        configs = []
        
        # Main config files
        for pattern in ["*.yaml", "*.yml", "*.json"]:
            configs.extend(self.config_dir.glob(pattern))
        
        # Theme configs
        themes_dir = self.config_dir / "themes"
        if themes_dir.exists():
            for pattern in ["*.yaml", "*.yml", "*.json"]:
                configs.extend(themes_dir.glob(pattern))
        
        return [str(config) for config in configs]
