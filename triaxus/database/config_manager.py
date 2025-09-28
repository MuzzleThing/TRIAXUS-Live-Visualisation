"""
Simple and Secure Database Configuration Manager

This module provides a simplified, secure database configuration management
using Dynaconf's built-in security features with minimal complexity.
"""

import os
import logging
from typing import Dict, Any, Optional
from dynaconf import Dynaconf

logger = logging.getLogger(__name__)


class SecureDatabaseConfigManager:
    """Simple and secure database configuration manager using Dynaconf"""

    def __init__(self, config_manager: Optional[Dynaconf] = None):
        """
        Initialize SecureDatabaseConfigManager
        
        Args:
            config_manager: Dynaconf instance for configuration access
        """
        self.config_manager = config_manager
        self.logger = logging.getLogger(__name__)
        
        # If no config manager provided, try to get from main config
        if self.config_manager is None:
            try:
                from ..core.config import ConfigManager
                main_config = ConfigManager()
                self.config_manager = main_config.settings
            except Exception as e:
                self.logger.warning(f"Could not get main config manager: {e}")

    def get_database_config(self) -> Dict[str, Any]:
        """
        Get database configuration with security enhancements
        
        Returns:
            Dictionary containing database configuration
        """
        try:
            # Get configuration from Dynaconf (automatically handles .env files)
            if self.config_manager:
                db_config = self.config_manager.get('database', {})
            else:
                db_config = self._get_default_database_config()

            # Apply environment variable overrides (Dynaconf handles this automatically)
            config = self._apply_env_overrides(db_config)
            
            # Validate and set defaults
            config = self._validate_and_set_defaults(config)
            
            # Log security warnings
            self._log_security_warnings(config)
            
            return config
            
        except Exception as e:
            self.logger.warning(f"Failed to load database config: {e}")
            return self._get_default_database_config()

    def _apply_env_overrides(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply environment variable overrides (simplified)
        
        Args:
            config: Base configuration dictionary
            
        Returns:
            Configuration with environment overrides
        """
        enhanced_config = config.copy()
        
        # Environment variables take highest priority
        if os.getenv('DATABASE_URL'):
            enhanced_config['url'] = os.getenv('DATABASE_URL')
        
        if os.getenv('DB_ENABLED'):
            enhanced_config['enabled'] = os.getenv('DB_ENABLED').lower() in ('true', '1', 'yes', 'on')
        
        return enhanced_config

    def _get_default_database_config(self) -> Dict[str, Any]:
        """Get default database configuration"""
        return {
            'enabled': False,
            'url': 'postgresql://user:password@localhost:5432/triaxus_db',
            'echo': False,
            'pool_size': 5,
            'max_overflow': 10,
            'pool_timeout': 30,
            'pool_recycle': 3600,
            'table': {
                'name': 'oceanographic_data',
                'indexes': ['datetime', 'depth', 'latitude', 'longitude']
            }
        }

    def _validate_and_set_defaults(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate configuration and set defaults for missing values
        
        Args:
            config: Configuration dictionary to validate
            
        Returns:
            Validated configuration with defaults
        """
        defaults = self._get_default_database_config()
        
        # Merge with defaults
        validated_config = defaults.copy()
        validated_config.update(config)
        
        # Validate required fields
        if validated_config.get('enabled', False):
            if not validated_config.get('url'):
                raise ValueError("Database enabled but no URL provided")
        
        return validated_config

    def _log_security_warnings(self, config: Dict[str, Any]) -> None:
        """
        Log security warnings for configuration
        
        Args:
            config: Configuration dictionary to check
        """
        if config.get('enabled', False):
            url = config.get('url', '')
            
            # Check for default credentials
            if 'user:password' in url:
                self.logger.warning("Using default database credentials. Change for production!")
            
            if 'localhost' in url and os.getenv('DATABASE_URL') is None:
                self.logger.warning("Using localhost database. Consider using environment variables for production.")

    def get_connection_url(self) -> str:
        """
        Get database connection URL
        
        Returns:
            Database connection URL string
        """
        config = self.get_database_config()
        return config.get('url', 'postgresql://user:password@localhost:5432/triaxus_db')

    def is_database_enabled(self) -> bool:
        """
        Check if database is enabled
        
        Returns:
            True if database is enabled, False otherwise
        """
        config = self.get_database_config()
        return config.get('enabled', False)

    def get_table_config(self) -> Dict[str, Any]:
        """
        Get table configuration
        
        Returns:
            Dictionary containing table configuration
        """
        config = self.get_database_config()
        return config.get('table', {
            'name': 'oceanographic_data',
            'indexes': ['datetime', 'depth', 'latitude', 'longitude']
        })

    def get_pool_config(self) -> Dict[str, Any]:
        """
        Get connection pool configuration
        
        Returns:
            Dictionary containing pool configuration
        """
        config = self.get_database_config()
        return {
            'pool_size': config.get('pool_size', 5),
            'max_overflow': config.get('max_overflow', 10),
            'pool_timeout': config.get('pool_timeout', 30),
            'pool_recycle': config.get('pool_recycle', 3600),
            'echo': config.get('echo', False)
        }

    def validate_connection_url(self, url: str) -> bool:
        """
        Validate database connection URL format
        
        Args:
            url: Database connection URL to validate
            
        Returns:
            True if URL format is valid, False otherwise
        """
        try:
            # Support both PostgreSQL and SQLite
            if url.startswith('postgresql://'):
                return '@' in url and ':' in url
            elif url.startswith('sqlite://'):
                return True
            else:
                return False
        except Exception:
            return False

    def get_security_recommendations(self) -> list:
        """
        Get simple security recommendations
        
        Returns:
            List of security recommendations
        """
        recommendations = []
        config = self.get_database_config()
        
        if config.get('enabled', False):
            url = config.get('url', '')
            
            if 'user:password' in url:
                recommendations.append("Change default database credentials")
            
            if 'localhost' in url and not os.getenv('DATABASE_URL'):
                recommendations.append("Use DATABASE_URL environment variable for production")
        
        return recommendations
