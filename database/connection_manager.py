"""
Database Connection Manager for TRIAXUS visualization system

This module provides PostgreSQL database connection management with connection pooling,
health checks, and error handling.
"""

from typing import Optional, Dict, Any
import logging
from contextlib import contextmanager
from sqlalchemy import create_engine, Engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from sqlalchemy.exc import SQLAlchemyError, OperationalError

from .config_manager import SecureDatabaseConfigManager

logger = logging.getLogger(__name__)


class DatabaseConnectionManager:
    """Manages PostgreSQL database connections with pooling and health checks"""

    def __init__(self, config_manager: Optional[SecureDatabaseConfigManager] = None):
        """
        Initialize DatabaseConnectionManager
        
        Args:
            config_manager: SecureDatabaseConfigManager instance
        """
        self.config_manager = config_manager or SecureDatabaseConfigManager()
        self.engine: Optional[Engine] = None
        self.session_factory: Optional[sessionmaker] = None
        self.logger = logging.getLogger(__name__)

    def connect(self) -> bool:
        """
        Establish database connection
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            if not self.config_manager.is_database_enabled():
                self.logger.info("Database is disabled in configuration")
                return False

            # Get configuration
            connection_url = self.config_manager.get_connection_url()
            pool_config = self.config_manager.get_pool_config()

            # Validate URL
            if not self.config_manager.validate_connection_url(connection_url):
                self.logger.error(f"Invalid database connection URL: {connection_url}")
                return False

            # Create engine with connection pooling
            self.engine = create_engine(
                connection_url,
                poolclass=QueuePool,
                pool_size=pool_config['pool_size'],
                max_overflow=pool_config['max_overflow'],
                pool_timeout=pool_config['pool_timeout'],
                pool_recycle=pool_config['pool_recycle'],
                echo=pool_config['echo']
            )

            # Create session factory
            self.session_factory = sessionmaker(bind=self.engine)

            # Test connection
            if self._test_connection():
                self.logger.info("Database connection established successfully")
                return True
            else:
                self.logger.error("Database connection test failed")
                return False

        except Exception as e:
            self.logger.error(f"Failed to establish database connection: {e}")
            return False

    def disconnect(self) -> None:
        """Close database connection and cleanup resources"""
        try:
            if self.engine:
                self.engine.dispose()
                self.engine = None
                self.session_factory = None
                self.logger.info("Database connection closed")
        except Exception as e:
            self.logger.error(f"Error closing database connection: {e}")

    def health_check(self) -> bool:
        """
        Check database connection health
        
        Returns:
            True if connection is healthy, False otherwise
        """
        try:
            if not self.engine:
                return False

            # Test with a simple query
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                return result.fetchone()[0] == 1

        except Exception as e:
            self.logger.warning(f"Database health check failed: {e}")
            return False

    def _test_connection(self) -> bool:
        """
        Test database connection with a simple query
        
        Returns:
            True if test successful, False otherwise
        """
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                return True
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False

    def is_connected(self) -> bool:
        """
        Check if database connection is available
        
        Returns:
            True if connected, False otherwise
        """
        try:
            if not self.engine:
                return False
            
            # Test connection with a simple query
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
            
        except Exception as e:
            self.logger.error(f"Connection check failed: {e}")
            return False

    @contextmanager
    def get_session(self):
        """
        Get database session context manager
        
        Yields:
            SQLAlchemy Session instance
            
        Raises:
            SQLAlchemyError: If session creation fails
        """
        if not self.session_factory:
            raise SQLAlchemyError("Database not connected. Call connect() first.")

        session = self.session_factory()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            self.logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()

    def get_engine(self) -> Optional[Engine]:
        """
        Get SQLAlchemy engine instance
        
        Returns:
            SQLAlchemy Engine instance or None if not connected
        """
        return self.engine

    def get_session_factory(self) -> Optional[sessionmaker]:
        """
        Get session factory
        
        Returns:
            SQLAlchemy sessionmaker instance or None if not connected
        """
        return self.session_factory

    def execute_raw_sql(self, sql: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """
        Execute raw SQL query
        
        Args:
            sql: SQL query string
            params: Optional query parameters
            
        Returns:
            Query result
            
        Raises:
            SQLAlchemyError: If query execution fails
        """
        if not self.engine:
            raise SQLAlchemyError("Database not connected. Call connect() first.")

        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(sql), params or {})
                return result.fetchall()
        except Exception as e:
            self.logger.error(f"Raw SQL execution failed: {e}")
            raise

    def get_connection_info(self) -> Dict[str, Any]:
        """
        Get current connection information
        
        Returns:
            Dictionary containing connection information
        """
        if not self.engine:
            return {"connected": False}

        try:
            url = self.engine.url
            return {
                "connected": True,
                "database": url.database,
                "host": url.host,
                "port": url.port,
                "username": url.username,
                "driver": url.drivername,
                "pool_size": self.engine.pool.size(),
                "checked_out": self.engine.pool.checkedout(),
                "overflow": self.engine.pool.overflow()
            }
        except Exception as e:
            self.logger.error(f"Failed to get connection info: {e}")
            return {"connected": False, "error": str(e)}

    def reconnect(self) -> bool:
        """
        Reconnect to database
        
        Returns:
            True if reconnection successful, False otherwise
        """
        self.logger.info("Attempting to reconnect to database...")
        self.disconnect()
        return self.connect()
