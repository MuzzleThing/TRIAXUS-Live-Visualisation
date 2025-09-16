"""
Database initialization script for TRIAXUS visualization system

This script provides utilities for initializing the database, creating tables,
and managing database schema.
"""

import logging
from typing import Optional
from sqlalchemy import create_engine, text, MetaData, Table, Column, DateTime, Float, String, UUID, Index
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.exc import SQLAlchemyError
import uuid
from datetime import datetime

from .config_manager import SecureDatabaseConfigManager
from .connection_manager import DatabaseConnectionManager
from .models import Base

logger = logging.getLogger(__name__)


class DatabaseInitializer:
    """Handles database initialization and schema management"""

    def __init__(self, config_manager: Optional[SecureDatabaseConfigManager] = None):
        """
        Initialize DatabaseInitializer
        
        Args:
            config_manager: SecureDatabaseConfigManager instance
        """
        self.config_manager = config_manager or SecureDatabaseConfigManager()
        self.connection_manager = DatabaseConnectionManager(self.config_manager)
        self.logger = logging.getLogger(__name__)

    def initialize_database(self) -> bool:
        """
        Initialize database connection and create tables if needed
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            # Connect to database
            if not self.connection_manager.connect():
                self.logger.error("Failed to connect to database")
                return False

            # Create tables
            if not self.create_tables():
                self.logger.error("Failed to create tables")
                return False

            # Verify tables exist
            if not self.verify_tables():
                self.logger.error("Failed to verify tables")
                return False

            self.logger.info("Database initialization completed successfully")
            return True

        except Exception as e:
            self.logger.error(f"Database initialization failed: {e}")
            return False

    def create_tables(self) -> bool:
        """
        Create database tables using SQLAlchemy ORM models
        
        Returns:
            True if tables created successfully, False otherwise
        """
        try:
            if not self.connection_manager.engine:
                self.logger.error("Database engine not available")
                return False
            
            # Create all tables defined in models
            Base.metadata.create_all(self.connection_manager.engine)
            
            self.logger.info("Database tables created successfully using ORM models")
            return True
            
        except SQLAlchemyError as e:
            self.logger.error(f"Error creating tables: {e}")
            return False

    def create_indexes(self) -> bool:
        """
        Create database indexes (now handled by ORM models)
        
        Returns:
            True (indexes are created automatically with tables)
        """
        # Indexes are now defined in the ORM models and created automatically
        self.logger.info("Indexes are created automatically with ORM models")
        return True

    def verify_tables(self) -> bool:
        """
        Verify that required tables exist
        
        Returns:
            True if tables exist, False otherwise
        """
        try:
            engine = self.connection_manager.get_engine()
            if not engine:
                return False

            table_config = self.config_manager.get_table_config()
            table_name = table_config['name']

            # Check if table exists
            check_table_sql = """
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = :table_name
            );
            """

            with engine.connect() as conn:
                result = conn.execute(text(check_table_sql), {"table_name": table_name})
                exists = result.fetchone()[0]

            if exists:
                self.logger.info(f"Table '{table_name}' verified")
                return True
            else:
                self.logger.error(f"Table '{table_name}' does not exist")
                return False

        except Exception as e:
            self.logger.error(f"Failed to verify tables: {e}")
            return False

    def drop_tables(self) -> bool:
        """
        Drop database tables (use with caution!)
        
        Returns:
            True if tables dropped successfully, False otherwise
        """
        try:
            engine = self.connection_manager.get_engine()
            if not engine:
                return False

            table_config = self.config_manager.get_table_config()
            table_name = table_config['name']

            # Drop table
            drop_table_sql = f"DROP TABLE IF EXISTS {table_name};"

            with engine.connect() as conn:
                conn.execute(text(drop_table_sql))
                conn.commit()

            self.logger.warning(f"Table '{table_name}' dropped")
            return True

        except Exception as e:
            self.logger.error(f"Failed to drop tables: {e}")
            return False

    def get_table_info(self) -> dict:
        """
        Get information about database tables
        
        Returns:
            Dictionary containing table information
        """
        try:
            engine = self.connection_manager.get_engine()
            if not engine:
                return {"error": "No database engine available"}

            table_config = self.config_manager.get_table_config()
            table_name = table_config['name']

            # Get table information
            info_sql = """
            SELECT 
                column_name,
                data_type,
                is_nullable,
                column_default
            FROM information_schema.columns 
            WHERE table_name = :table_name
            ORDER BY ordinal_position;
            """

            with engine.connect() as conn:
                result = conn.execute(text(info_sql), {"table_name": table_name})
                columns = result.fetchall()

            # Get row count
            count_sql = f"SELECT COUNT(*) FROM {table_name};"
            with engine.connect() as conn:
                result = conn.execute(text(count_sql))
                row_count = result.fetchone()[0]

            return {
                "table_name": table_name,
                "columns": [dict(row._mapping) for row in columns],
                "row_count": row_count,
                "status": "active"
            }

        except Exception as e:
            self.logger.error(f"Failed to get table info: {e}")
            return {"error": str(e)}

    def cleanup(self) -> None:
        """Cleanup resources"""
        self.connection_manager.disconnect()
