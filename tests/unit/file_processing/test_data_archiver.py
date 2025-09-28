"""
Unit tests for data archiver
"""

import pytest
import tempfile
import pandas as pd
import json
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from triaxus.data.archiver import DataArchiver


class TestDataArchiver:
    """Test data archiver functionality"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
        
        # Create test data
        self.test_data = self._create_test_data()
        
        # Create archiver instance
        self.archiver = DataArchiver()
    
    def _create_test_data(self):
        """Create test data"""
        base_time = datetime(2024, 1, 1, 12, 0, 0)
        time_series = [base_time + timedelta(hours=i) for i in range(10)]
        
        return pd.DataFrame({
            'time': time_series,
            'depth': [i * 2 for i in range(10)],
            'latitude': [45.0 + i * 0.1 for i in range(10)],
            'longitude': [-120.0 + i * 0.1 for i in range(10)],
            'tv290c': [15.0 + i * 0.1 for i in range(10)],
            'sal00': [35.0 + i * 0.01 for i in range(10)],
            'sbeox0mm_l': [8.0 + i * 0.05 for i in range(10)],
            'fleco_afl': [0.5 + i * 0.02 for i in range(10)],
            'ph': [8.1 + i * 0.01 for i in range(10)]
        })
    
    def teardown_method(self):
        """Cleanup test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_archiver_initialization(self):
        """Test data archiver initialization"""
        print("Testing data archiver initialization...")
        
        archiver = DataArchiver()
        assert archiver is not None
        print("  PASS: Data archiver initialization")
    
    def test_csv_archiving(self):
        """Test CSV archiving"""
        print("Testing CSV archiving...")
        
        output_file = self.temp_path / "test_archive.csv"
        
        # Test CSV archiving
        result = self.archiver.archive_to_csv(self.test_data, str(output_file))
        
        assert result is True, "CSV archiving should succeed"
        assert output_file.exists(), "CSV file should be created"
        
        # Verify file content
        archived_data = pd.read_csv(output_file)
        assert len(archived_data) == len(self.test_data), "Archived data should have same length"
        assert len(archived_data.columns) == len(self.test_data.columns), "Archived data should have same columns"
        
        print("  PASS: CSV archiving")
    
    def test_compressed_csv_archiving(self):
        """Test compressed CSV archiving"""
        print("Testing compressed CSV archiving...")
        
        output_file = self.temp_path / "test_archive.csv.gz"
        
        # Test compressed CSV archiving
        result = self.archiver.archive_to_csv(self.test_data, str(output_file), compress=True)
        
        assert result is True, "Compressed CSV archiving should succeed"
        assert output_file.exists(), "Compressed CSV file should be created"
        
        # Verify file content
        archived_data = pd.read_csv(output_file, compression='gzip')
        assert len(archived_data) == len(self.test_data), "Archived data should have same length"
        assert len(archived_data.columns) == len(self.test_data.columns), "Archived data should have same columns"
        
        print("  PASS: Compressed CSV archiving")
    
    def test_quality_report_archiving(self):
        """Test quality report archiving"""
        print("Testing quality report archiving...")
        
        # Create test quality report
        quality_report = {
            'total_records': len(self.test_data),
            'duplicate_count': 0,
            'missing_values': {
                'depth': 0,
                'latitude': 0,
                'longitude': 0,
                'tv290c': 0,
                'sal00': 0,
                'sbeox0mm_l': 0,
                'fleco_afl': 0,
                'ph': 0
            },
            'data_quality': 'good',
            'processing_timestamp': datetime.now().isoformat()
        }
        
        output_file = self.temp_path / "quality_report.json"
        
        # Test quality report archiving
        result = self.archiver.archive_quality_report(quality_report, str(output_file))
        
        assert result is True, "Quality report archiving should succeed"
        assert output_file.exists(), "Quality report file should be created"
        
        # Verify file content
        with open(output_file, 'r') as f:
            archived_report = json.load(f)
        
        assert archived_report['total_records'] == quality_report['total_records'], "Quality report should be correct"
        assert archived_report['data_quality'] == quality_report['data_quality'], "Data quality should be correct"
        
        print("  PASS: Quality report archiving")
    
    def test_metadata_archiving(self):
        """Test metadata archiving"""
        print("Testing metadata archiving...")
        
        # Create test metadata
        metadata = {
            'source_file': 'test_file.cnv',
            'processing_date': datetime.now().isoformat(),
            'data_range': {
                'start_time': self.test_data['time'].min().isoformat(),
                'end_time': self.test_data['time'].max().isoformat(),
                'min_depth': float(self.test_data['depth'].min()),
                'max_depth': float(self.test_data['depth'].max())
            },
            'variables': list(self.test_data.columns),
            'total_records': len(self.test_data)
        }
        
        output_file = self.temp_path / "metadata.json"
        
        # Test metadata archiving
        result = self.archiver.archive_metadata(metadata, str(output_file))
        
        assert result is True, "Metadata archiving should succeed"
        assert output_file.exists(), "Metadata file should be created"
        
        # Verify file content
        with open(output_file, 'r') as f:
            archived_metadata = json.load(f)
        
        assert archived_metadata['source_file'] == metadata['source_file'], "Metadata should be correct"
        assert archived_metadata['total_records'] == metadata['total_records'], "Total records should be correct"
        
        print("  PASS: Metadata archiving")
    
    def test_database_archiving(self):
        """Test database archiving"""
        print("Testing database archiving...")
        
        # Mock database connection
        with patch('triaxus.data.archiver.DatabaseDataSource') as mock_db:
            mock_db_instance = Mock()
            mock_db.return_value = mock_db_instance
            mock_db_instance.store_data.return_value = True
            
            # Test database archiving
            result = self.archiver.archive_to_database(self.test_data, 'test_source')
            
            assert result is True, "Database archiving should succeed"
            assert mock_db_instance.store_data.called, "Database store should be called"
        
        print("  PASS: Database archiving")
    
    def test_comprehensive_archiving(self):
        """Test comprehensive archiving"""
        print("Testing comprehensive archiving...")
        
        # Create test metadata and quality report
        metadata = {
            'source_file': 'comprehensive_test.cnv',
            'processing_date': datetime.now().isoformat(),
            'total_records': len(self.test_data)
        }
        
        quality_report = {
            'total_records': len(self.test_data),
            'data_quality': 'good'
        }
        
        # Test comprehensive archiving
        result = self.archiver.archive_comprehensive(
            self.test_data,
            str(self.temp_path / "comprehensive"),
            metadata=metadata,
            quality_report=quality_report,
            compress=True
        )
        
        assert result is True, "Comprehensive archiving should succeed"
        
        # Verify all files were created
        csv_file = self.temp_path / "comprehensive.csv.gz"
        metadata_file = self.temp_path / "comprehensive_metadata.json"
        quality_file = self.temp_path / "comprehensive_quality.json"
        
        assert csv_file.exists(), "CSV file should be created"
        assert metadata_file.exists(), "Metadata file should be created"
        assert quality_file.exists(), "Quality report file should be created"
        
        print("  PASS: Comprehensive archiving")
    
    def test_error_handling(self):
        """Test error handling"""
        print("Testing error handling...")
        
        # Test with invalid output path
        invalid_path = "/invalid/path/that/does/not/exist/test.csv"
        
        try:
            result = self.archiver.archive_to_csv(self.test_data, invalid_path)
            assert result is False, "Should return False for invalid path"
        except Exception as e:
            assert "No such file" in str(e) or "Permission denied" in str(e), "Should raise appropriate error"
        
        # Test with empty data
        empty_data = pd.DataFrame()
        
        try:
            result = self.archiver.archive_to_csv(empty_data, str(self.temp_path / "empty.csv"))
            assert result is False, "Should return False for empty data"
        except Exception as e:
            assert "Empty" in str(e) or "No data" in str(e), "Should raise appropriate error"
        
        print("  PASS: Error handling")


def test_data_archiver_integration():
    """Integration test for data archiver"""
    print("Testing data archiver integration...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create test data
        test_data = pd.DataFrame({
            'time': [datetime.now() - timedelta(hours=i) for i in range(5)],
            'depth': [i * 2 for i in range(5)],
            'latitude': [45.0] * 5,
            'longitude': [-120.0] * 5,
            'tv290c': [15.0 + i * 0.1 for i in range(5)],
            'sal00': [35.0 + i * 0.01 for i in range(5)],
            'sbeox0mm_l': [8.0 + i * 0.05 for i in range(5)],
            'fleco_afl': [0.5 + i * 0.02 for i in range(5)],
            'ph': [8.1 + i * 0.01 for i in range(5)]
        })
        
        archiver = DataArchiver()
        
        # Test CSV archiving
        csv_file = temp_path / "integration_test.csv"
        result = archiver.archive_to_csv(test_data, str(csv_file))
        assert result is True, "CSV archiving should succeed"
        assert csv_file.exists(), "CSV file should be created"
        
        # Test metadata archiving
        metadata = {
            'source_file': 'integration_test.cnv',
            'total_records': len(test_data)
        }
        metadata_file = temp_path / "integration_metadata.json"
        result = archiver.archive_metadata(metadata, str(metadata_file))
        assert result is True, "Metadata archiving should succeed"
        assert metadata_file.exists(), "Metadata file should be created"
        
        # Test quality report archiving
        quality_report = {
            'total_records': len(test_data),
            'data_quality': 'good'
        }
        quality_file = temp_path / "integration_quality.json"
        result = archiver.archive_quality_report(quality_report, str(quality_file))
        assert result is True, "Quality report archiving should succeed"
        assert quality_file.exists(), "Quality report file should be created"
        
        print("  PASS: Integration test")


if __name__ == "__main__":
    # Run tests
    test_instance = TestDataArchiver()
    test_instance.setup_method()
    
    try:
        test_instance.test_archiver_initialization()
        test_instance.test_csv_archiving()
        test_instance.test_compressed_csv_archiving()
        test_instance.test_quality_report_archiving()
        test_instance.test_metadata_archiving()
        test_instance.test_database_archiving()
        test_instance.test_comprehensive_archiving()
        test_instance.test_error_handling()
        
        test_data_archiver_integration()
        
        print("\nAll data archiver tests passed!")
        
    finally:
        test_instance.teardown_method()
