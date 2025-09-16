#!/usr/bin/env python3
"""
TRIAXUS Visualization System - Complete End-to-End Test Script

This script performs a comprehensive test of the entire TRIAXUS system including:
- Database connectivity and initialization
- Data generation and storage
- Data retrieval and visualization
- All test suites execution

Usage:
    python run_full_test.py [--clean-db] [--skip-tests]

Options:
    --clean-db    Clean database before testing
    --skip-tests  Skip individual test suite execution
"""

import os
import sys
import time
import argparse
from datetime import datetime
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def setup_environment():
    """Setup test environment variables"""
    print("Setting up test environment...")
    
    # Set database environment variables
    os.environ['DB_ENABLED'] = 'true'
    os.environ['DATABASE_URL'] = 'postgresql://steven@localhost:5432/triaxus_db'
    
    # Add current directory to Python path
    current_dir = str(Path(__file__).parent)
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    
    print("Environment setup complete")

def test_database_connectivity():
    """Test database connectivity and initialization using dedicated database tests"""
    print("\nTesting Database Connectivity...")
    
    try:
        # Use the dedicated database test module
        from tests.unit.database.test_connectivity import DatabaseConnectivityTester
        
        tester = DatabaseConnectivityTester()
        results = tester.run_all_tests()
        
        # Check if all connectivity tests passed
        all_passed = all(result.get("status") == "PASSED" for result in results.values())
        
        if all_passed:
            print("PASS: All database connectivity tests passed")
            
            # Get database stats for additional info
            from triaxus.data.database_source import DatabaseDataSource
            db = DatabaseDataSource()
            if db.is_available():
                stats = db.get_stats()
                print(f"Database stats: {stats['total_records']} records")
                return True, db
            else:
                return True, None
        else:
            print("FAIL: Some database connectivity tests failed")
            return False, None
            
    except Exception as e:
        print(f"FAIL: Database connectivity test failed: {e}")
        return False, None

def clean_database(db):
    """Clean database for fresh test"""
    print("\nCleaning database...")
    
    try:
        # Check if tables exist before cleaning
        with db.connection_manager.get_session() as session:
            from triaxus.database.models import OceanographicData, DataSource
            
            # Check if oceanographic_data table exists and has data
            try:
                oceanographic_count = session.query(OceanographicData).count()
                if oceanographic_count > 0:
                    session.query(OceanographicData).delete()
                    print(f"Cleared {oceanographic_count} records from oceanographic_data table")
                else:
                    print("oceanographic_data table is already empty")
            except Exception as e:
                print(f"Oceanographic data table may not exist: {e}")
            
            # Check if data_sources table exists and has data
            try:
                sources_count = session.query(DataSource).count()
                if sources_count > 0:
                    session.query(DataSource).delete()
                    print(f"Cleared {sources_count} records from data_sources table")
                else:
                    print("data_sources table is already empty")
            except Exception as e:
                print(f"Data sources table may not exist: {e}")
            
            session.commit()
        
        print("PASS: Database cleaned successfully")
        return True
        
    except Exception as e:
        print(f"FAIL: Database cleanup failed: {e}")
        return False

def test_data_generation_and_storage():
    """Test data generation and storage to database"""
    print("\nTesting Data Generation and Storage...")
    
    try:
        from triaxus.data.simple_data_generator import PlotTestDataGenerator
        from triaxus.data.database_source import DatabaseDataSource
        
        # Initialize components
        generator = PlotTestDataGenerator()
        db = DatabaseDataSource()
        
        # Generate Australia West Coast data
        print("Generating Australia West Coast oceanographic data...")
        test_data = generator.generate_plot_test_data(duration_hours=2.0, points_per_hour=15)
        print(f"Generated {len(test_data)} data points")
        
        # Show data summary
        print(f"Data columns: {list(test_data.columns)}")
        print(f"Depth range: {test_data['depth'].min():.1f} - {test_data['depth'].max():.1f} meters")
        print(f"Latitude range: {test_data['latitude'].min():.3f} - {test_data['latitude'].max():.3f}")
        print(f"Longitude range: {test_data['longitude'].min():.3f} - {test_data['longitude'].max():.3f}")
        print(f"Time range: {test_data['time'].min()} to {test_data['time'].max()}")
        
        # Store data to database
        print("Storing data to database...")
        success = db.store_data(test_data, 'full_test_australia_west_coast.csv')
        
        if success:
            print("PASS: Data stored successfully")
            
            # Check database stats after storage
            stats = db.get_stats()
            print(f"Database stats after storage:")
            print(f"   Total records: {stats['total_records']}")
            print(f"   Date range: {stats['date_range']['start']} to {stats['date_range']['end']}")
            print(f"   Depth range: {stats['depth_range']['min']:.1f} - {stats['depth_range']['max']:.1f} meters")
            print(f"   Geographic bounds: {stats['geographic_bounds']}")
            print(f"   Source files: {list(stats['source_files'].keys())}")
            
            return True, db
        else:
            print("FAIL: Data storage failed")
            return False, None
            
    except Exception as e:
        print(f"FAIL: Data generation and storage test failed: {e}")
        import traceback
        traceback.print_exc()
        return False, None

def test_data_retrieval_and_visualization():
    """Test data retrieval from database and visualization generation"""
    print("\nTesting Data Retrieval and Visualization...")
    
    try:
        from triaxus.data.database_source import DatabaseDataSource
        from triaxus import TriaxusVisualizer
        
        db = DatabaseDataSource()
        visualizer = TriaxusVisualizer()
        
        # Load data from database
        print("Loading data from database...")
        loaded_data = db.load_data(limit=50)
        print(f"Loaded {len(loaded_data)} records")
        
        if len(loaded_data) > 0:
            print(f"Data columns: {list(loaded_data.columns)}")
            print(f"First record:")
            print(f"   Time: {loaded_data.iloc[0]['time']}")
            print(f"   Depth: {loaded_data.iloc[0]['depth']:.1f}m")
            print(f"   Location: ({loaded_data.iloc[0]['latitude']:.3f}, {loaded_data.iloc[0]['longitude']:.3f})")
            print(f"   Temperature: {loaded_data.iloc[0]['tv290c']:.1f}C")
            print(f"   Salinity: {loaded_data.iloc[0]['sal00']:.1f} PSU")
            
            # Create visualizations
            print("Creating visualizations...")
            
            # Ensure output directory exists
            output_dir = Path("tests/output")
            output_dir.mkdir(exist_ok=True)
            
            # Create time series plot
            print("Creating time series plot...")
            html_output = visualizer.create_plot('time_series', loaded_data, 
                                                output_file='tests/output/full_test_time_series.html')
            print(f"PASS: Time series plot saved to: {html_output}")
            
            # Create depth profile plot
            print("Creating depth profile plot...")
            html_output = visualizer.create_plot('depth_profile', loaded_data, 
                                                output_file='tests/output/full_test_depth_profile.html')
            print(f"PASS: Depth profile plot saved to: {html_output}")
            
            # Create map plot
            print("Creating map plot...")
            html_output = visualizer.create_plot('map', loaded_data, 
                                                output_file='tests/output/full_test_map.html')
            print(f"PASS: Map plot saved to: {html_output}")
            
            # Check if files were created
            output_files = [
                'tests/output/full_test_time_series.html',
                'tests/output/full_test_depth_profile.html', 
                'tests/output/full_test_map.html'
            ]
            
            print("\nFile creation status:")
            all_files_created = True
            for file_path in output_files:
                if os.path.exists(file_path):
                    size = os.path.getsize(file_path)
                    print(f"PASS: {file_path} created ({size:,} bytes)")
                else:
                    print(f"FAIL: {file_path} not found")
                    all_files_created = False
            
            return all_files_created
        else:
            print("FAIL: No data available for visualization")
            return False
            
    except Exception as e:
        print(f"FAIL: Data retrieval and visualization test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_test_suites():
    """Run all test suites"""
    print("\nRunning Test Suites...")
    
    try:
        # Run main test suite
        print("Running main test suite...")
        import subprocess
        result = subprocess.run([sys.executable, 'test_runner.py'], 
                              capture_output=True, text=True, cwd=Path(__file__).parent)
        
        if result.returncode == 0:
            print("PASS: Main test suite")
            print("Test summary:")
            # Extract summary from output
            lines = result.stdout.split('\n')
            for line in lines:
                if 'Total tests:' in line or 'Passed:' in line or 'Success rate:' in line:
                    print(f"   {line.strip()}")
        else:
            print("FAIL: Main test suite")
            print(f"Error output: {result.stderr}")
            return False
        
        return True
        
    except Exception as e:
        print(f"FAIL: Test suite execution failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_output_files():
    """Check generated output files"""
    print("\nChecking Generated Output Files...")
    
    try:
        output_dir = Path("tests/output")
        if not output_dir.exists():
            print("FAIL: Output directory does not exist")
            return False
        
        # Count HTML files
        html_files = list(output_dir.glob("*.html"))
        print(f"Found {len(html_files)} HTML files in tests/output/")
        
        # Show file sizes
        total_size = 0
        for file_path in html_files:
            size = file_path.stat().st_size
            total_size += size
            print(f"   {file_path.name}: {size:,} bytes")
        
        print(f"Total output size: {total_size:,} bytes ({total_size/1024/1024:.1f} MB)")
        
        # Check for our specific test files
        test_files = [
            'full_test_time_series.html',
            'full_test_depth_profile.html',
            'full_test_map.html'
        ]
        
        print("\nChecking specific test files:")
        all_test_files_exist = True
        for test_file in test_files:
            file_path = output_dir / test_file
            if file_path.exists():
                size = file_path.stat().st_size
                print(f"PASS: {test_file}: {size:,} bytes")
            else:
                print(f"FAIL: {test_file}: Not found")
                all_test_files_exist = False
        
        return all_test_files_exist
        
    except Exception as e:
        print(f"FAIL: Output file check failed: {e}")
        return False

def main():
    """Main test execution function"""
    parser = argparse.ArgumentParser(description='TRIAXUS Complete End-to-End Test')
    parser.add_argument('--clean-db', action='store_true', 
                       help='Clean database before testing')
    parser.add_argument('--skip-tests', action='store_true', 
                       help='Skip individual test suite execution')
    
    args = parser.parse_args()
    
    print("TRIAXUS Visualization System - Complete End-to-End Test")
    print("=" * 60)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    start_time = time.time()
    
    # Setup environment
    setup_environment()
    
    # Test database connectivity
    db_connected, db = test_database_connectivity()
    if not db_connected:
        print("\nCRITICAL: Database connectivity failed. Exiting.")
        sys.exit(1)
    
    # Clean database if requested
    if args.clean_db:
        if not clean_database(db):
            print("\nCRITICAL: Database cleanup failed. Exiting.")
            sys.exit(1)
    
    # Test data generation and storage
    data_stored, db = test_data_generation_and_storage()
    if not data_stored:
        print("\nCRITICAL: Data generation and storage failed. Exiting.")
        sys.exit(1)
    
    # Test data retrieval and visualization
    visualization_success = test_data_retrieval_and_visualization()
    if not visualization_success:
        print("\nCRITICAL: Data retrieval and visualization failed. Exiting.")
        sys.exit(1)
    
    # Run test suites (unless skipped)
    if not args.skip_tests:
        test_suites_success = run_test_suites()
        if not test_suites_success:
            print("\nWARNING: Some test suites failed, but core functionality works.")
    else:
        print("\nSkipping test suite execution (--skip-tests flag)")
    
    # Check output files
    output_check_success = check_output_files()
    
    # Final summary
    end_time = time.time()
    duration = end_time - start_time
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total duration: {duration:.2f} seconds")
    print()
    
    # Status summary
    print("Test Results:")
    print(f"Database Connectivity: {'PASS' if db_connected else 'FAIL'}")
    print(f"Data Generation & Storage: {'PASS' if data_stored else 'FAIL'}")
    print(f"Data Retrieval & Visualization: {'PASS' if visualization_success else 'FAIL'}")
    if not args.skip_tests:
        print(f"Test Suites: {'PASS' if test_suites_success else 'FAIL'}")
    print(f"Output Files: {'PASS' if output_check_success else 'FAIL'}")
    
    # Overall result
    all_core_tests_passed = db_connected and data_stored and visualization_success and output_check_success
    
    if all_core_tests_passed:
        print("\nSUCCESS: All core tests passed!")
        print("TRIAXUS system is fully functional")
        sys.exit(0)
    else:
        print("\nFAILURE: Some core tests failed")
        print("Please check the error messages above")
        sys.exit(1)

if __name__ == '__main__':
    main()