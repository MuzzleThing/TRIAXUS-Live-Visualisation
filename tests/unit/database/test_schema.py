"""
Database schema tests for TRIAXUS

This module tests database schema validation, table structure, and column definitions.
"""

import os
import sys
from typing import Dict, Any, List

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from triaxus.database.connection_manager import DatabaseConnectionManager
from sqlalchemy import text


class DatabaseSchemaTester:
    """Test database schema and table structure"""
    
    def __init__(self):
        """Initialize schema tester"""
        self.connection_manager = DatabaseConnectionManager()
    
    def _ensure_connection(self):
        """Ensure database connection is established"""
        if not self.connection_manager.is_connected():
            self.connection_manager.connect()
    
    def test_table_existence(self) -> Dict[str, Any]:
        """Test if required tables exist"""
        print("Testing table existence...")
        
        self._ensure_connection()
        
        with self.connection_manager.get_session() as session:
            # Check if tables exist
            tables_query = text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name IN ('oceanographic_data', 'data_sources')
                ORDER BY table_name
            """)
            tables = session.execute(tables_query).fetchall()
            table_names = [row[0] for row in tables]
            
            print(f"Found tables: {table_names}")
            
            required_tables = ['oceanographic_data', 'data_sources']
            missing_tables = [table for table in required_tables if table not in table_names]
            
            if missing_tables:
                print(f"Missing tables: {missing_tables}")
                return {
                    "status": "FAILED",
                    "missing_tables": missing_tables,
                    "found_tables": table_names
                }
            
            return {
                "status": "PASSED",
                "found_tables": table_names,
                "all_required_tables": True
            }
    
    def test_oceanographic_data_schema(self) -> Dict[str, Any]:
        """Test oceanographic_data table schema"""
        print("Testing oceanographic_data table schema...")
        
        self._ensure_connection()
        
        with self.connection_manager.get_session() as session:
            # Get table columns
            columns_query = text("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_name = 'oceanographic_data'
                ORDER BY ordinal_position
            """)
            columns = session.execute(columns_query).fetchall()
            
            print(f"Oceanographic data columns: {len(columns)}")
            
            # Check key columns
            key_columns = {
                'id': 'uuid',
                'datetime': 'timestamp with time zone',
                'latitude': 'double precision',
                'longitude': 'double precision',
                'depth': 'double precision',
                'tv290c': 'double precision',
                'sal00': 'double precision',
                'sbeox0mm_l': 'double precision',
                'fleco_afl': 'double precision',
                'ph': 'double precision',
                'source_file': 'character varying',
                'created_at': 'timestamp with time zone'
            }
            
            found_columns = {col[0]: col[1] for col in columns}
            missing_columns = []
            wrong_type_columns = []
            
            for col_name, expected_type in key_columns.items():
                if col_name not in found_columns:
                    missing_columns.append(col_name)
                elif found_columns[col_name] != expected_type:
                    wrong_type_columns.append(f"{col_name} (expected: {expected_type}, actual: {found_columns[col_name]})")
            
            if missing_columns or wrong_type_columns:
                print(f"Schema issues:")
                if missing_columns:
                    print(f"  Missing columns: {missing_columns}")
                if wrong_type_columns:
                    print(f"  Wrong type columns: {wrong_type_columns}")
                return {
                    "status": "FAILED",
                    "missing_columns": missing_columns,
                    "wrong_type_columns": wrong_type_columns,
                    "total_columns": len(columns)
                }
            
            return {
                "status": "PASSED",
                "total_columns": len(columns),
                "key_columns_valid": True
            }
    
    def test_data_sources_schema(self) -> Dict[str, Any]:
        """Test data_sources table schema"""
        print("Testing data_sources table schema...")
        
        self._ensure_connection()
        
        with self.connection_manager.get_session() as session:
            # Get table columns
            columns_query = text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = 'data_sources'
                ORDER BY ordinal_position
            """)
            columns = session.execute(columns_query).fetchall()
            
            print(f"Data sources columns: {len(columns)}")
            
            # Check key columns
            key_columns = {
                'id': 'uuid',
                'source_file': 'character varying',
                'file_type': 'character varying',
                'file_size': 'bigint',
                'file_hash': 'character varying',
                'total_records': 'integer',
                'status': 'character varying',
                'processed_at': 'timestamp with time zone'
            }
            
            found_columns = {col[0]: col[1] for col in columns}
            missing_columns = []
            
            for col_name in key_columns.keys():
                if col_name not in found_columns:
                    missing_columns.append(col_name)
            
            if missing_columns:
                print(f"Missing key columns: {missing_columns}")
                return {
                    "status": "FAILED",
                    "missing_columns": missing_columns,
                    "total_columns": len(columns)
                }
            
            return {
                "status": "PASSED",
                "total_columns": len(columns),
                "key_columns_valid": True
            }
    
    def test_indexes(self) -> Dict[str, Any]:
        """Test database indexes"""
        print("Testing database indexes...")
        
        self._ensure_connection()
        
        with self.connection_manager.get_session() as session:
            # Check indexes on oceanographic_data
            indexes_query = text("""
                SELECT indexname, tablename, indexdef
                FROM pg_indexes
                WHERE tablename IN ('oceanographic_data', 'data_sources')
                ORDER BY tablename, indexname
            """)
            indexes = session.execute(indexes_query).fetchall()
            
            print(f"Found {len(indexes)} indexes")
            
            # Check for important indexes
            index_names = [idx[0] for idx in indexes]
            important_indexes = [
                'oceanographic_data_pkey',  # Primary key
                'data_sources_pkey'  # Primary key
            ]
            
            missing_indexes = [idx for idx in important_indexes if idx not in index_names]
            
            if missing_indexes:
                print(f"Missing important indexes: {missing_indexes}")
                return {
                    "status": "FAILED",
                    "missing_indexes": missing_indexes,
                    "total_indexes": len(indexes)
                }
            
            return {
                "status": "PASSED",
                "total_indexes": len(indexes),
                "important_indexes": True
            }
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all schema tests"""
        print("=" * 50)
        print("DATABASE SCHEMA TESTS")
        print("=" * 50)
        
        test_results = {}
        
        # Run individual tests
        tests = [
            ("Table Existence", self.test_table_existence),
            ("Oceanographic Data Schema", self.test_oceanographic_data_schema),
            ("Data Sources Schema", self.test_data_sources_schema),
            ("Indexes", self.test_indexes)
        ]
        
        for test_name, test_method in tests:
            print(f"\n--- {test_name} ---")
            try:
                result = test_method()
                test_results[test_name] = result
                status = "PASSED" if result.get("status") == "PASSED" else "FAILED"
                print(f"{status}: {test_name}")
            except Exception as e:
                test_results[test_name] = {"status": "FAILED", "error": str(e)}
                print(f"FAILED: {test_name} - {e}")
        
        # Summary
        passed = sum(1 for result in test_results.values() if result.get("status") == "PASSED")
        total = len(test_results)
        print(f"\nSchema Tests Summary: {passed}/{total} passed")
        
        return test_results


if __name__ == "__main__":
    tester = DatabaseSchemaTester()
    results = tester.run_all_tests()
