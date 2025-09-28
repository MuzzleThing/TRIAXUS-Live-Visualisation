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
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, '..'))

# Import database test modules with robust fallbacks
try:
    from tests.utils import TestDatabaseHelper
except ModuleNotFoundError:
    import importlib.util
    import pathlib
    utils_path = pathlib.Path(project_root).parent / 'utils.py'
    spec = importlib.util.spec_from_file_location('tests_utils', str(utils_path))
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    TestDatabaseHelper = getattr(mod, 'TestDatabaseHelper')
try:
    from tests.unit.database.test_connectivity import run_connectivity_unit_tests
    from tests.unit.database.test_schema import run_schema_unit_tests
    from tests.unit.database.test_models_and_mappers import run_models_and_mappers_unit_tests
except ModuleNotFoundError:
    import importlib.util
    import pathlib

    tests_dir = pathlib.Path(project_root).parent
    connectivity_path = tests_dir / 'unit' / 'database' / 'test_connectivity.py'
    schema_path = tests_dir / 'unit' / 'database' / 'test_schema.py'
    models_mappers_path = tests_dir / 'unit' / 'database' / 'test_models_and_mappers.py'

    def _load_func(module_path: pathlib.Path, func_name: str):
        spec = importlib.util.spec_from_file_location(module_path.stem, str(module_path))
        mod = importlib.util.module_from_spec(spec)
        assert spec and spec.loader
        spec.loader.exec_module(mod)
        return getattr(mod, func_name)

    run_connectivity_unit_tests = _load_func(connectivity_path, 'run_connectivity_unit_tests')
    run_schema_unit_tests = _load_func(schema_path, 'run_schema_unit_tests')
    run_models_and_mappers_unit_tests = _load_func(models_mappers_path, 'run_models_and_mappers_unit_tests')


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
        
        ok = run_connectivity_unit_tests()
        results = {"Connectivity": {"status": "PASSED" if ok else "FAILED"}}
        self.test_results["Connectivity"] = results["Connectivity"]
        return results
    
    def run_schema_tests(self) -> Dict[str, Any]:
        """Run database schema tests"""
        print("\n" + "=" * 60)
        print("RUNNING DATABASE SCHEMA TESTS")
        print("=" * 60)
        
        ok = run_schema_unit_tests()
        results = {"Schema": {"status": "PASSED" if ok else "FAILED"}}
        self.test_results["Schema"] = results["Schema"]
        return results
    
    def run_mapping_tests(self) -> Dict[str, Any]:
        """Run database mapping tests"""
        print("\n" + "=" * 60)
        print("RUNNING DATABASE MAPPING TESTS")
        print("=" * 60)
        
        ok = run_models_and_mappers_unit_tests()
        results = {"Mapping": {"status": "PASSED" if ok else "FAILED"}}
        self.test_results["Mapping"] = results["Mapping"]
        return results
    
    # Operations tests are covered elsewhere; intentionally omitted
    
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
        """Clean database for fresh testing (delegates to shared helper)."""
        print("Cleaning database via tests.utils helper...")
        return TestDatabaseHelper.clean_database()
    
    def generate_summary(self, total_time: float):
        """Generate test summary"""
        print("\n" + "=" * 60)
        print("DATABASE TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        total_passed = sum(1 for r in self.test_results.values() if r.get("status") == "PASSED")
        
        for category_name, category_results in self.test_results.items():
            status = category_results.get("status")
            print(f"{category_name}: {status}")
        
        success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\nOverall Results:")
        print(f"  Total Tests: {total_tests}")
        print(f"  Passed: {total_passed}")
        print(f"  Failed: {total_tests - total_passed}")
        print(f"  Success Rate: {success_rate:.1f}%")
        print(f"  Total Time: {total_time:.2f}s")
        
        print("=" * 60)


def main():
    """Main function for database testing"""
    parser = argparse.ArgumentParser(description="TRIAXUS Database Testing")
    parser.add_argument("--clean-db", action="store_true", help="Clean database before testing")
    parser.add_argument("--category", 
                       choices=["connectivity", "schema", "mapping"], 
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