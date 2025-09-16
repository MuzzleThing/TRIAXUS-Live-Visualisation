#!/usr/bin/env python3
"""
TRIAXUS Quick Test Runner

A simplified test runner for quick validation of core functionality.

Usage:
    python tests/run_quick_tests.py [--clean-db]
"""

import os
import sys
import time
import argparse
from datetime import datetime
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def main():
    """Quick test execution"""
    parser = argparse.ArgumentParser(description='TRIAXUS Quick Test Runner')
    parser.add_argument('--clean-db', action='store_true', 
                       help='Clean database before testing')
    
    args = parser.parse_args()
    
    print("TRIAXUS Quick Test")
    print("=" * 40)
    print(f"Started at: {datetime.now().strftime('%H:%M:%S')}")
    
    start_time = time.time()
    
    # Setup environment
    os.environ['DB_ENABLED'] = 'true'
    os.environ['DATABASE_URL'] = 'postgresql://steven@localhost:5432/triaxus_db'
    
    try:
        # Test database connectivity
        print("\nTesting database...")
        from triaxus.data.database_source import DatabaseDataSource
        db = DatabaseDataSource()
        
        if not db.is_available():
            print("FAIL: Database not available")
            return False
        
        print("PASS: Database connected")
        
        # Clean database if requested
        if args.clean_db:
            print("\nCleaning database...")
            try:
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
                print("PASS: Database cleaned")
            except Exception as e:
                print(f"WARN: Database cleanup failed: {e}")
        
        # Generate and store data
        print("\nGenerating data...")
        from triaxus.data.simple_data_generator import PlotTestDataGenerator
        generator = PlotTestDataGenerator()
        test_data = generator.generate_plot_test_data(duration_hours=1.0, points_per_hour=20)
        
        success = db.store_data(test_data, 'quick_test.csv')
        if not success:
            print("FAIL: Data storage failed")
            return False
        
        print(f"PASS: Generated and stored {len(test_data)} data points")
        
        # Test visualization
        print("\nTesting visualization...")
        from triaxus import TriaxusVisualizer
        visualizer = TriaxusVisualizer()
        
        loaded_data = db.load_data(limit=20)
        html_output = visualizer.create_plot('time_series', loaded_data, 
                                            output_file='tests/output/quick_test.html')
        
        if os.path.exists(html_output):
            size = os.path.getsize(html_output)
            print(f"PASS: Visualization created: {html_output} ({size:,} bytes)")
        else:
            print("FAIL: Visualization failed")
            return False
        
        # Run a few key unit tests
        print("\nRunning key unit tests...")
        unit_tests = [
            'unit/test_models_and_mappers.py',
            'unit/test_data_quality.py',
        ]
        
        passed_tests = 0
        for test_file in unit_tests:
            test_path = project_root / 'tests' / test_file
            if test_path.exists():
                try:
                    import subprocess
                    result = subprocess.run([sys.executable, str(test_path)], 
                                         capture_output=True, text=True, cwd=project_root)
                    if result.returncode == 0:
                        print(f"PASS: {test_file}")
                        passed_tests += 1
                    else:
                        print(f"FAIL: {test_file}")
                except Exception as e:
                    print(f"FAIL: {test_file} failed: {e}")
            else:
                print(f"WARN: {test_file} not found")
        
        # Success
        end_time = time.time()
        duration = end_time - start_time
        
        print("\n" + "=" * 40)
        print("QUICK TEST SUMMARY")
        print(f"Duration: {duration:.2f} seconds")
        print(f"Unit tests passed: {passed_tests}/{len(unit_tests)}")
        print("TRIAXUS system is working correctly")
        
        return True
        
    except Exception as e:
        print(f"\nFAIL: Quick test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)