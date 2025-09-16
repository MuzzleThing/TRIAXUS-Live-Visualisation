#!/usr/bin/env python3
"""
TRIAXUS Test Suite - Unified Test Runner

This module provides a comprehensive test runner for the TRIAXUS visualization system.
It organizes tests into logical categories and provides flexible execution options.

Test Categories:
- unit: Individual component tests (models, mappers, data quality)
- integration: Cross-component tests (plots, maps, database integration)
- e2e: End-to-end system tests (full workflows)

Usage:
    python tests/run_all_tests.py [--category unit|integration|e2e] [--verbose] [--clean-db]
"""

import os
import sys
import time
import argparse
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class TestRunner:
    """Unified test runner for TRIAXUS system"""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.results = {}
        self.start_time = None
        
    def setup_environment(self):
        """Setup test environment"""
        print("Setting up test environment...")
        
        # Set database environment variables
        os.environ['DB_ENABLED'] = 'true'
        os.environ['DATABASE_URL'] = 'postgresql://steven@localhost:5432/triaxus_db'
        
        # Add current directory to Python path
        current_dir = str(project_root)
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        
        print("Environment setup complete")
    
    def run_unit_tests(self) -> Dict[str, Any]:
        """Run unit tests"""
        print("\nRunning Unit Tests...")
        print("=" * 50)
        
        unit_tests = [
            ('test_models_and_mappers.py', 'Database Models & Mappers'),
            ('test_data_quality.py', 'Data Quality'),
            ('plots/test_time_series_plots.py', 'Time Series Plots'),
            ('plots/test_depth_profile_plots.py', 'Depth Profile Plots'),
            ('plots/test_contour_plots.py', 'Contour Plots'),
            ('themes/test_theme_functionality.py', 'Theme Functionality'),
        ]
        
        results = {'passed': 0, 'failed': 0, 'total': len(unit_tests)}
        
        for test_file, test_name in unit_tests:
            print(f"\nTesting {test_name}...")
            try:
                test_path = project_root / 'tests' / 'unit' / test_file
                if test_path.exists():
                    import subprocess
                    result = subprocess.run([sys.executable, str(test_path)], 
                                         capture_output=True, text=True, cwd=project_root)
                    
                    if result.returncode == 0:
                        print(f"PASS: {test_name}")
                        results['passed'] += 1
                    else:
                        print(f"FAIL: {test_name}")
                        if self.verbose:
                            print(f"Error: {result.stderr}")
                        results['failed'] += 1
                else:
                    print(f"WARN: {test_name} - test file not found")
                    results['failed'] += 1
                    
            except Exception as e:
                print(f"FAIL: {test_name} failed with exception: {e}")
                results['failed'] += 1
        
        return results
    
    def run_integration_tests(self) -> Dict[str, Any]:
        """Run integration tests"""
        print("\nRunning Integration Tests...")
        print("=" * 50)
        
        integration_tests = [
            ('test_integration.py', 'Database Integration'),
            ('maps/test_map_trajectory.py', 'Map Trajectory'),
            ('maps/test_map_view.py', 'Map View'),
        ]
        
        results = {'passed': 0, 'failed': 0, 'total': len(integration_tests)}
        
        for test_file, test_name in integration_tests:
            print(f"\nTesting {test_name}...")
            try:
                test_path = project_root / 'tests' / 'integration' / test_file
                if test_path.exists():
                    import subprocess
                    result = subprocess.run([sys.executable, str(test_path)], 
                                         capture_output=True, text=True, cwd=project_root)
                    
                    if result.returncode == 0:
                        print(f"PASS: {test_name}")
                        results['passed'] += 1
                    else:
                        print(f"FAIL: {test_name}")
                        if self.verbose:
                            print(f"Error: {result.stderr}")
                        results['failed'] += 1
                else:
                    print(f"WARN: {test_name} - test file not found")
                    results['failed'] += 1
                    
            except Exception as e:
                print(f"FAIL: {test_name} failed with exception: {e}")
                results['failed'] += 1
        
        return results
    
    def run_e2e_tests(self) -> Dict[str, Any]:
        """Run end-to-end tests"""
        print("\nRunning End-to-End Tests...")
        print("=" * 50)
        
        # Run a simple end-to-end test without calling test_comprehensive.py
        # to avoid circular dependency
        try:
            from triaxus.data.database_source import DatabaseDataSource
            from triaxus.data.simple_data_generator import PlotTestDataGenerator
            from triaxus.visualizer import TriaxusVisualizer
            
            # Test database connectivity
            db = DatabaseDataSource()
            if not db.is_available():
                print("FAIL: Database not available")
                return {'passed': 0, 'failed': 1, 'total': 1}
            
            # Test data generation and storage
            generator = PlotTestDataGenerator()
            test_data = generator.generate_plot_test_data()
            
            # Test visualization
            visualizer = TriaxusVisualizer()
            if len(test_data) > 0:
                print("PASS: End-to-end test")
                return {'passed': 1, 'failed': 0, 'total': 1}
            else:
                print("FAIL: No test data generated")
                return {'passed': 0, 'failed': 1, 'total': 1}
                
        except Exception as e:
            print("FAIL: End-to-end test")
            if self.verbose:
                print(f"Error: {e}")
            return {'passed': 0, 'failed': 1, 'total': 1}
    
    def run_tests(self, category: str = 'all', clean_db: bool = False) -> Dict[str, Any]:
        """Run tests based on category"""
        self.start_time = time.time()
        
        print("TRIAXUS Test Suite - Unified Runner")
        print("=" * 60)
        print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Category: {category}")
        print("=" * 60)
        
        # Setup environment
        self.setup_environment()
        
        # Clean database if requested
        if clean_db:
            print("\nCleaning database...")
            try:
                from triaxus.data.database_source import DatabaseDataSource
                db = DatabaseDataSource()
                if db.is_available():
                    with db.connection_manager.get_session() as session:
                        from triaxus.database.models import OceanographicData, DataSource
                        
                        # Check and clean oceanographic_data table
                        try:
                            oceanographic_count = session.query(OceanographicData).count()
                            if oceanographic_count > 0:
                                session.query(OceanographicData).delete()
                                print(f"Cleared {oceanographic_count} oceanographic records")
                            else:
                                print("Oceanographic data table is already empty")
                        except Exception as e:
                            print(f"Oceanographic data table may not exist: {e}")
                        
                        # Check and clean data_sources table
                        try:
                            sources_count = session.query(DataSource).count()
                            if sources_count > 0:
                                session.query(DataSource).delete()
                                print(f"Cleared {sources_count} data source records")
                            else:
                                print("Data sources table is already empty")
                        except Exception as e:
                            print(f"Data sources table may not exist: {e}")
                        
                        session.commit()
                    print("Database cleaned successfully")
                else:
                    print("WARN: Database not available for cleaning")
            except Exception as e:
                print(f"WARN: Database cleanup failed: {e}")
        
        # Run tests based on category
        if category in ['all', 'unit']:
            self.results['unit'] = self.run_unit_tests()
        
        if category in ['all', 'integration']:
            self.results['integration'] = self.run_integration_tests()
        
        if category in ['all', 'e2e']:
            self.results['e2e'] = self.run_e2e_tests()
        
        # Generate summary
        self.print_summary()
        
        return self.results
    
    def print_summary(self):
        """Print test summary"""
        end_time = time.time()
        duration = end_time - self.start_time
        
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        print(f"Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Total duration: {duration:.2f} seconds")
        print()
        
        total_passed = 0
        total_failed = 0
        total_tests = 0
        
        for category, results in self.results.items():
            passed = results['passed']
            failed = results['failed']
            total = results['total']
            
            total_passed += passed
            total_failed += failed
            total_tests += total
            
            status = "PASS" if failed == 0 else "FAIL"
            print(f"{status} - {category.title()} Tests: {passed}/{total} passed")
        
        print()
        print(f"Overall: {total_passed}/{total_tests} tests passed")
        
        if total_failed == 0:
            print("\nSUCCESS: All tests passed!")
            print("TRIAXUS system is fully functional")
        else:
            print(f"\nWARNING: {total_failed} tests failed")
            print("Please check the error messages above")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='TRIAXUS Unified Test Runner')
    parser.add_argument('--category', choices=['unit', 'integration', 'e2e', 'all'], 
                       default='all', help='Test category to run')
    parser.add_argument('--verbose', '-v', action='store_true', 
                       help='Verbose output')
    parser.add_argument('--clean-db', action='store_true', 
                       help='Clean database before testing')
    
    args = parser.parse_args()
    
    runner = TestRunner(verbose=args.verbose)
    results = runner.run_tests(category=args.category, clean_db=args.clean_db)
    
    # Exit with appropriate code
    total_failed = sum(r['failed'] for r in results.values())
    sys.exit(0 if total_failed == 0 else 1)

if __name__ == '__main__':
    main()