"""
Database connectivity tests for TRIAXUS

This module tests database connection, session management, and basic connectivity.
"""

import os
import sys
from typing import Dict, Any

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from triaxus.database.connection_manager import DatabaseConnectionManager
from sqlalchemy import text


class DatabaseConnectivityTester:
    """Test database connectivity and session management"""
    
    def __init__(self):
        """Initialize connectivity tester"""
        self.connection_manager = DatabaseConnectionManager()
    
    def test_connection(self) -> Dict[str, Any]:
        """Test basic database connection"""
        print("Testing database connection...")
        
        # Test connection
        if not self.connection_manager.is_connected():
            self.connection_manager.connect()
        
        connected = self.connection_manager.is_connected()
        print(f"Database connected: {connected}")
        
        return {
            "status": "PASSED" if connected else "FAILED",
            "connected": connected
        }
    
    def test_session_creation(self) -> Dict[str, Any]:
        """Test session creation and basic query"""
        print("Testing session creation...")
        
        # Ensure connection
        if not self.connection_manager.is_connected():
            self.connection_manager.connect()
        
        try:
            with self.connection_manager.get_session() as session:
                # Test basic query
                result = session.execute(text("SELECT 1 as test")).fetchone()
                query_success = result[0] == 1
                print(f"Basic query test: {query_success}")
                
                return {
                    "status": "PASSED" if query_success else "FAILED",
                    "query_success": query_success
                }
        except Exception as e:
            print(f"Session creation failed: {e}")
            return {
                "status": "FAILED",
                "error": str(e)
            }
    
    def test_connection_pool(self) -> Dict[str, Any]:
        """Test connection pool functionality"""
        print("Testing connection pool...")
        
        # Ensure connection
        if not self.connection_manager.is_connected():
            self.connection_manager.connect()
        
        try:
            # Test multiple sessions
            sessions_created = 0
            for i in range(3):
                with self.connection_manager.get_session() as session:
                    result = session.execute(text("SELECT 1")).fetchone()
                    if result[0] == 1:
                        sessions_created += 1
            
            pool_success = sessions_created == 3
            print(f"Connection pool test: {pool_success} ({sessions_created}/3 sessions)")
            
            return {
                "status": "PASSED" if pool_success else "FAILED",
                "sessions_created": sessions_created,
                "pool_success": pool_success
            }
        except Exception as e:
            print(f"Connection pool test failed: {e}")
            return {
                "status": "FAILED",
                "error": str(e)
            }
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all connectivity tests"""
        print("=" * 50)
        print("DATABASE CONNECTIVITY TESTS")
        print("=" * 50)
        
        test_results = {}
        
        # Run individual tests
        tests = [
            ("Connection", self.test_connection),
            ("Session Creation", self.test_session_creation),
            ("Connection Pool", self.test_connection_pool)
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
        print(f"\nConnectivity Tests Summary: {passed}/{total} passed")
        
        return test_results


if __name__ == "__main__":
    tester = DatabaseConnectivityTester()
    results = tester.run_all_tests()
