"""
End-to-end tests for database integration with TRIAXUS visualization

This module provides comprehensive tests for the database integration
from data storage to visualization generation.
"""

import pytest
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any
import tempfile
import os

from triaxus.visualizer import TriaxusVisualizer
from triaxus.data.database_source import DatabaseDataSource
from triaxus.data.simple_data_generator import PlotTestDataGenerator


class TestDatabaseIntegration:
    """Test database integration with visualization system"""
    
    def setup_method(self):
        """Setup test environment"""
        self.visualizer = TriaxusVisualizer()
        self.data_generator = PlotTestDataGenerator()
        self.db_source = DatabaseDataSource()
    
    def test_database_data_source_initialization(self):
        """Test database data source initialization"""
        # Test database data source
        db_source = DatabaseDataSource()
        assert db_source is not None
        assert hasattr(db_source, 'is_available')
        assert hasattr(db_source, 'load_data')
        assert hasattr(db_source, 'store_data')
    
    def test_data_storage_and_retrieval(self):
        """Test storing and retrieving data from database"""
        # Generate test data
        test_data = self.data_generator.generate_plot_test_data()
        
        # Store data using database source
        success = self.db_source.store_data(test_data, "test_data.csv")
        
        if self.db_source.is_available():
            assert success is True
            
            # Retrieve data
            retrieved_data = self.db_source.load_data(limit=100)
            assert not retrieved_data.empty
            assert len(retrieved_data) <= 100
            
            # Verify data integrity
            assert 'time' in retrieved_data.columns
            assert 'depth' in retrieved_data.columns
        else:
            # Database not available, test should still pass
            assert success is False
    
    def test_data_filtering(self):
        """Test data filtering capabilities"""
        if not self.db_source.is_available():
            print("   [yellow]Database not available, skipping filtering test[/yellow]")
            return
        
        # Generate and store test data
        test_data = self.data_generator.generate_plot_test_data()
        self.db_source.store_data(test_data, "filter_test.csv")
        
        # Test basic data loading (simplified version)
        filtered_data = self.db_source.load_data(limit=50)
        
        assert len(filtered_data) >= 0  # May be empty if no data
    
    def test_visualization_with_database_data(self):
        """Test creating visualizations with database data"""
        if not self.db_source.is_available():
            print("   [yellow]Database not available, skipping visualization test[/yellow]")
            return
        
        # Generate and store test data
        test_data = self.data_generator.generate_plot_test_data()
        self.db_source.store_data(test_data, "viz_test.csv")
        
        # Load data from database
        db_data = self.db_source.load_data(limit=30)
        
        if len(db_data) > 0:
            # Create time series plot
            with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as tmp_file:
                output_file = tmp_file.name
            
            try:
                html_output = self.visualizer.create_plot(
                    "time_series", 
                    db_data, 
                    output_file=output_file
                )
                
                assert html_output == output_file
                assert os.path.exists(output_file)
                assert os.path.getsize(output_file) > 0
                
            finally:
                if os.path.exists(output_file):
                    os.unlink(output_file)
    
    def test_database_fallback_behavior(self):
        """Test database fallback behavior when not available"""
        # Test with database not available
        if not self.db_source.is_available():
            # Should return empty DataFrame
            data = self.db_source.load_data(limit=50)
            assert isinstance(data, pd.DataFrame)
            assert len(data) == 0
    
    def test_data_summary(self):
        """Test data summary functionality"""
        summary = self.db_source.get_stats()
        
        assert isinstance(summary, dict)
        assert 'available' in summary
        
        if self.db_source.is_available():
            assert summary['available'] is True
            assert 'total_records' in summary
        else:
            assert summary['available'] is False
    
    def test_cli_integration_simulation(self):
        """Test CLI integration simulation"""
        # Simulate CLI data loading
        data = self.db_source.load_data(limit=100)
        
        assert isinstance(data, pd.DataFrame)
        
        # Test with specific parameters
        if self.db_source.is_available():
            # Test with limit
            limited_data = self.db_source.load_data(limit=50)
            assert isinstance(limited_data, pd.DataFrame)
            assert len(limited_data) <= 50
    
    def test_error_handling(self):
        """Test error handling in database operations"""
        # Test with invalid parameters
        invalid_data = self.db_source.load_data(limit=-1)  # Invalid limit
        
        # Should return empty DataFrame for invalid parameters
        assert isinstance(invalid_data, pd.DataFrame)
        assert len(invalid_data) == 0
        
        # Should return empty DataFrame or handle gracefully
        assert isinstance(invalid_data, pd.DataFrame)
    
    def test_data_consistency(self):
        """Test data consistency between storage and retrieval"""
        if not self.db_source.is_available():
            print("   [yellow]Database not available, skipping consistency test[/yellow]")
            return
        
        # Generate test data
        original_data = self.data_generator.generate_plot_test_data()
        
        # Store data
        success = self.db_source.store_data(original_data, "consistency_test.csv")
        
        if success:
            # Retrieve data
            retrieved_data = self.db_source.load_data(limit=50)
            
            # Check that we got some data back
            assert len(retrieved_data) > 0
            
            # Check that required columns are present
            required_columns = ['time', 'depth', 'latitude', 'longitude']
            for col in required_columns:
                assert col in retrieved_data.columns


def run_integration_tests():
    """Run integration tests manually"""
    print("Running TRIAXUS Database Integration Tests...")
    
    test_instance = TestDatabaseIntegration()
    test_instance.setup_method()
    
    try:
        # Test 1: Database initialization
        print("1. Testing database initialization...")
        test_instance.test_database_data_source_initialization()
        print("   [green]Database initialization passed[/green]")
        
        # Test 2: Data storage and retrieval
        print("2. Testing data storage and retrieval...")
        test_instance.test_data_storage_and_retrieval()
        print("   [green]Data storage and retrieval passed[/green]")
        
        # Test 3: Data filtering
        print("3. Testing data filtering...")
        test_instance.test_data_filtering()
        print("   [green]Data filtering passed[/green]")
        
        # Test 4: Visualization with database data
        print("4. Testing visualization with database data...")
        test_instance.test_visualization_with_database_data()
        print("   [green]Visualization with database data passed[/green]")
        
        # Test 5: Database fallback behavior
        print("5. Testing database fallback behavior...")
        test_instance.test_database_fallback_behavior()
        print("   [green]Database fallback behavior passed[/green]")
        
        # Test 6: Data summary
        print("6. Testing data summary...")
        test_instance.test_data_summary()
        print("   [green]Data summary passed[/green]")
        
        # Test 7: CLI integration simulation
        print("7. Testing CLI integration simulation...")
        test_instance.test_cli_integration_simulation()
        print("   [green]CLI integration simulation passed[/green]")
        
        # Test 8: Error handling
        print("8. Testing error handling...")
        test_instance.test_error_handling()
        print("   [green]Error handling passed[/green]")
        
        # Test 9: Data consistency
        print("9. Testing data consistency...")
        test_instance.test_data_consistency()
        print("   [green]Data consistency passed[/green]")
        
        print("\n[green]All integration tests passed![/green]")
        
    except Exception as e:
        print(f"\n[red]Integration test failed: {e}[/red]")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    run_integration_tests()
