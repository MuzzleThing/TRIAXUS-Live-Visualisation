#!/usr/bin/env python3
"""
Main Database Testing Script for TRIAXUS

This script orchestrates all database tests and provides a unified interface
for database testing functionality.
"""

import os
import sys
import time
import argparse
from typing import Dict, Any, List

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import database test modules
from tests.unit.database.test_connectivity import DatabaseConnectivityTester
from tests.unit.database.test_schema import DatabaseSchemaTester
from tests.unit.database.test_mapping import DatabaseMappingTester
from tests.unit.database.test_operations import DatabaseOperationsTester


class DatabaseTestRunner:
    """Main database test runner"""
    
    def __init__(self):
        """Initialize test runner"""
        self.test_results = {}
        self.start_time = None
    
    def run_connectivity_tests(self) -> Dict[str, Any]:
        """Run database connectivity tests"""
        print("\n" + "=" * 60)
        print("RUNNING DATABASE CONNECTIVITY TESTS")
        print("=" * 60)
        
        tester = DatabaseConnectivityTester()
        results = tester.run_all_tests()
        
        self.test_results["Connectivity"] = results
        return results
    
    def run_schema_tests(self) -> Dict[str, Any]:
        """Run database schema tests"""
        print("\n" + "=" * 60)
        print("RUNNING DATABASE SCHEMA TESTS")
        print("=" * 60)
        
        tester = DatabaseSchemaTester()
        results = tester.run_all_tests()
        
        self.test_results["Schema"] = results
        return results
    
    def run_mapping_tests(self) -> Dict[str, Any]:
        """Run database mapping tests"""
        print("\n" + "=" * 60)
        print("RUNNING DATABASE MAPPING TESTS")
        print("=" * 60)
        
        tester = DatabaseMappingTester()
        results = tester.run_all_tests()
        
        self.test_results["Mapping"] = results
        return results
    
    def run_operations_tests(self) -> Dict[str, Any]:
        """Run database operations tests"""
        print("\n" + "=" * 60)
        print("RUNNING DATABASE OPERATIONS TESTS")
        print("=" * 60)
        
        tester = DatabaseOperationsTester()
        results = tester.run_all_tests()
        
        self.test_results["Operations"] = results
        return results
    
    def run_all_tests(self, clean_db: bool = False) -> Dict[str, Any]:
        """Run all database tests"""
        print("=" * 60)
        print("TRIAXUS DATABASE TESTING SUITE")
        print("=" * 60)
        
        self.start_time = time.time()
        
        if clean_db:
            print("\nCleaning database before testing...")
            self.clean_database()
        
        # Run all test categories
        test_categories = [
            ("Connectivity", self.run_connectivity_tests),
            ("Schema", self.run_schema_tests),
            ("Mapping", self.run_mapping_tests),
            ("Operations", self.run_operations_tests)
        ]
        
        for category_name, test_method in test_categories:
            try:
                print(f"\n{'='*20} {category_name} {'='*20}")
                result = test_method()
                
                # Count passed tests in this category
                passed_in_category = sum(1 for test_result in result.values() 
                                       if test_result.get("status") == "PASSED")
                total_in_category = len(result)
                
                print(f"PASSED: {category_name}: {passed_in_category}/{total_in_category} tests passed")
                
            except Exception as e:
                print(f"FAILED: {category_name}: FAILED - {e}")
                self.test_results[category_name] = {"status": "FAILED", "error": str(e)}
        
        # Generate summary
        total_time = time.time() - self.start_time
        self.generate_summary(total_time)
        
        return self.test_results
    
    def clean_database(self) -> bool:
        """Clean database for fresh testing"""
        print("Cleaning database...")
        
        try:
            from triaxus.database.connection_manager import DatabaseConnectionManager
            from triaxus.database.models import OceanographicData, DataSource
            
            connection_manager = DatabaseConnectionManager()
            if not connection_manager.is_connected():
                connection_manager.connect()
            
            with connection_manager.get_session() as session:
                # Check if tables exist before cleaning
                try:
                    oceanographic_count = session.query(OceanographicData).count()
                    if oceanographic_count > 0:
                        session.query(OceanographicData).delete()
                        print(f"Cleared {oceanographic_count} records from oceanographic_data table")
                    else:
                        print("Oceanographic data table is already empty")
                except Exception as e:
                    print(f"Oceanographic data table may not exist: {e}")
                
                try:
                    sources_count = session.query(DataSource).count()
                    if sources_count > 0:
                        session.query(DataSource).delete()
                        print(f"Cleared {sources_count} records from data_sources table")
                    else:
                        print("Data sources table is already empty")
                except Exception as e:
                    print(f"Data sources table may not exist: {e}")
                
                session.commit()
            
            print("Database cleaned successfully")
            return True
            
        except Exception as e:
            print(f"Database cleanup failed: {e}")
            return False
    
    def generate_summary(self, total_time: float):
        """Generate test summary"""
        print("\n" + "=" * 60)
        print("DATABASE TEST SUMMARY")
        print("=" * 60)
        
        total_tests = 0
        total_passed = 0
        
        for category_name, category_results in self.test_results.items():
            if isinstance(category_results, dict) and "status" not in category_results:
                # This is a category with sub-tests
                category_passed = sum(1 for test_result in category_results.values() 
                                    if test_result.get("status") == "PASSED")
                category_total = len(category_results)
                
                print(f"{category_name}: {category_passed}/{category_total} tests passed")
                total_tests += category_total
                total_passed += category_passed
            else:
                # This is a single test result
                total_tests += 1
                if category_results.get("status") == "PASSED":
                    total_passed += 1
        
        success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\nOverall Results:")
        print(f"  Total Tests: {total_tests}")
        print(f"  Passed: {total_passed}")
        print(f"  Failed: {total_tests - total_passed}")
        print(f"  Success Rate: {success_rate:.1f}%")
        print(f"  Total Time: {total_time:.2f}s")
        
        # Performance metrics
        if "Operations" in self.test_results:
            ops_results = self.test_results["Operations"]
            if "Performance" in ops_results:
                perf = ops_results["Performance"]
                if perf.get("status") == "PASSED":
                    print(f"\nPerformance Metrics:")
                    print(f"  Insert Rate: {perf.get('insert_rate', 0):.1f} records/sec")
                    print(f"  Query Rate: {perf.get('query_rate', 0):.1f} records/sec")
        
        print("=" * 60)


def main():
    """Main function for database testing"""
    parser = argparse.ArgumentParser(description="TRIAXUS Database Testing")
    parser.add_argument("--clean-db", action="store_true", help="Clean database before testing")
    parser.add_argument("--category", 
                       choices=["connectivity", "schema", "mapping", "operations"], 
                       help="Run specific test category")
    
    args = parser.parse_args()
    
    # Check environment
    if not os.getenv("DB_ENABLED"):
        print("Error: DB_ENABLED environment variable not set")
        print("Please run: export DB_ENABLED=true")
        sys.exit(1)
    
    runner = DatabaseTestRunner()
    
    if args.category:
        # Run specific test category
        test_methods = {
            "connectivity": runner.run_connectivity_tests,
            "schema": runner.run_schema_tests,
            "mapping": runner.run_mapping_tests,
            "operations": runner.run_operations_tests
        }
        
        if args.category in test_methods:
            print(f"Running {args.category} tests...")
            result = test_methods[args.category]()
            
            # Show summary for this category
            passed = sum(1 for test_result in result.values() 
                        if test_result.get("status") == "PASSED")
            total = len(result)
            print(f"\n{args.category.title()} Tests Summary: {passed}/{total} passed")
        else:
            print(f"Unknown test category: {args.category}")
            sys.exit(1)
    else:
        # Run all tests
        runner.run_all_tests(clean_db=args.clean_db)


if __name__ == "__main__":
    main()