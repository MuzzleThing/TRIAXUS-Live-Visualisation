"""
Theme Manager for TRIAXUS visualization system

This module handles theme management including color schemes,
templates, and variable-specific colors.
"""

from typing import Dict, Any, List, Optional
import logging

from dynaconf import Dynaconf

logger = logging.getLogger(__name__)


class ThemeManager:
    """Manages themes and color configurations"""

    def __init__(self, settings: Dynaconf, yaml_config: Optional[Dict] = None):
        """
        Initialize ThemeManager

        Args:
            settings: Dynaconf settings instance
            yaml_config: Fallback YAML configuration
        """
        self.settings = settings
        self._yaml_config = yaml_config
        
        # Get default theme from configuration
        default_theme = self.settings.get("theme", "oceanographic")
        if not default_theme and self._yaml_config:
            default_theme = self._yaml_config.get("theme", "oceanographic")
        
        self._current_theme = default_theme

    def get_available_themes(self) -> List[str]:
        """Get list of available themes"""
        themes = []

        # Get themes from configuration
        theme_configs = self.settings.get("colors.themes", {})
        themes.extend(list(theme_configs.keys()))

        # Add default themes if not found
        default_themes = ["default", "oceanographic", "dark", "high_contrast"]
        for theme in default_themes:
            if theme not in themes:
                themes.append(theme)

        return themes

    def get_current_theme(self) -> str:
        """Get current theme name"""
        return self._current_theme

    def set_theme(self, theme_name: str):
        """Set current theme"""
        available_themes = self.get_available_themes()
        if theme_name in available_themes:
            self._current_theme = theme_name
            logger.info(f"Theme changed to: {theme_name}")
        else:
            logger.warning(
                f"Theme '{theme_name}' not available. Available themes: {available_themes}"
            )

    def get_style_config(self, theme_name: Optional[str] = None) -> Dict[str, Any]:
        """Get style configuration for theme"""
        if theme_name is None:
            theme_name = self._current_theme

        # Try to get theme config from dynaconf first
        theme_config = self.settings.get(f"colors.themes.{theme_name}", {})
        
        # If dynaconf fails, try yaml fallback
        if not theme_config and self._yaml_config:
            colors_config = self._yaml_config.get("colors", {})
            themes_config = colors_config.get("themes", {})
            theme_config = themes_config.get(theme_name, {})
        
        if theme_config:
            # Determine template based on theme
            template = self._get_template_for_theme(theme_name)
            
            return {
                "colors": theme_config,
                "template": template,
            }

        # Return empty config if no theme found
        return {
            "colors": {},
            "template": "plotly_white",
        }

    def _get_template_for_theme(self, theme_name: str) -> str:
        """Get plotly template for theme"""
        template_mapping = {
            "dark": "plotly_dark",
            "high_contrast": "plotly_white",
            "oceanographic": "plotly_white",
            "default": "plotly_white",
        }
        return template_mapping.get(theme_name, "plotly_white")

    def get_variable_colors(self, theme: Optional[str] = None) -> Dict[str, str]:
        """Get variable-specific colors for theme"""
        if theme is None:
            theme = self._current_theme

        # Try to get from dynaconf config
        variables_config = self.settings.get("colors.variables", {})
        result = {}

        for var_name, var_colors in variables_config.items():
            if isinstance(var_colors, dict):
                if theme in var_colors:
                    result[var_name] = var_colors[theme]
                elif "default" in var_colors:
                    result[var_name] = var_colors["default"]

        if result:
            return result

        # Try YAML fallback for variable colors
        if self._yaml_config:
            yaml_variables = self._yaml_config.get("colors", {}).get("variables", {})
            for var_name, var_colors in yaml_variables.items():
                if isinstance(var_colors, dict):
                    if theme in var_colors:
                        result[var_name] = var_colors[theme]
                    elif "default" in var_colors:
                        result[var_name] = var_colors["default"]

        return result

    def get_color_config(self, theme: Optional[str] = None) -> Dict[str, Any]:
        """Get complete color configuration for theme"""
        if theme is None:
            theme = self._current_theme

        style_config = self.get_style_config(theme)
        return {
            "theme_colors": style_config.get("colors", {}),
            "variable_colors": self.get_variable_colors(theme),
        }
