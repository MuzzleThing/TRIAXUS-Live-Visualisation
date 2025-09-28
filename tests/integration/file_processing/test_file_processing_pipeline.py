"""
Integration tests for file processing pipeline
"""

import pytest
import tempfile
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from triaxus.data.cnv_reader import CNVFileReader
from triaxus.data.processor import DataProcessor
from triaxus.data.archiver import DataArchiver


class TestFileProcessingPipeline:
    """Test file processing pipeline integration"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
        
        # Create test CNV file
        self.test_cnv_file = self.temp_path / "pipeline_test.cnv"
        self._create_test_cnv_file()
        
        # Create components
        self.reader = CNVFileReader()
        self.processor = DataProcessor()
        self.archiver = DataArchiver()
    
    def _create_test_cnv_file(self):
        """Create a test CNV file"""
        cnv_content = """* Sea-Bird SBE 19plus V 2.2.2  SERIAL NO. 01907508
* 05-Jan-2024 12:00:00
* temperature: SBE 3F
* conductivity: SBE 4C
* pressure: SBE 29
* time: SBE 9
* status: SBE 9
* file_type: ascii
* nquan: 7
* nvalues: 10
* columns = time, depSM, t090C, c0S/m, sal00, sbeox0Mm/L, flECO-AFL
# name 0 = timeS: Time, Elapsed [seconds]
# name 1 = depSM: Depth [salt water, m]
# name 2 = t090C: Temperature [ITS-90, deg C]
# name 3 = c0S/m: Conductivity [S/m]
# name 4 = sal00: Salinity, Practical [PSU]
# name 5 = sbeox0Mm/L: Oxygen, SBE 43 [umol/kg]
# name 6 = flECO-AFL: Fluorescence, WET Labs ECO-AFL/FL [mg/m^3]
*END*
0.000000, 1.000, 15.2345, 3.45678, 35.1234, 8.1234, 0.5432
0.250000, 2.000, 15.1234, 3.45678, 35.0987, 8.0987, 0.5432
0.500000, 3.000, 15.0123, 3.45678, 35.0741, 8.0741, 0.5432
0.750000, 4.000, 14.9012, 3.45678, 35.0495, 8.0495, 0.5432
1.000000, 5.000, 14.7901, 3.45678, 35.0249, 8.0249, 0.5432
1.250000, 6.000, 14.6790, 3.45678, 35.0003, 8.0003, 0.5432
1.500000, 7.000, 14.5679, 3.45678, 34.9757, 7.9757, 0.5432
1.750000, 8.000, 14.4568, 3.45678, 34.9511, 7.9511, 0.5432
2.000000, 9.000, 14.3457, 3.45678, 34.9265, 7.9265, 0.5432
2.250000, 10.000, 14.2346, 3.45678, 34.9019, 7.9019, 0.5432
"""
        self.test_cnv_file.write_text(cnv_content)
    
    def teardown_method(self):
        """Cleanup test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_cnv_to_processed_data_pipeline(self):
        """Test CNV file to processed data pipeline"""
        print("Testing CNV to processed data pipeline...")
        
        # Step 1: Read CNV file
        raw_data, metadata = self.reader.read_cnv_file(str(self.test_cnv_file))
        
        assert raw_data is not None, "Raw data should be loaded"
        assert metadata is not None, "Metadata should be loaded"
        assert len(raw_data) == 10, "Should have 10 data rows"
        
        # Step 2: Process data
        processing_config = {
            'missing_values': 'interpolate',
            'required_columns': ['time', 'depSM', 't090C', 'c0S/m', 'sal00', 'sbeox0Mm/L', 'flECO-AFL'],
            'filters': {
                'depSM': {'type': 'range', 'value': [0, 1000]}
            }
        }
        
        processed_data = self.processor.process(raw_data, processing_config=processing_config)
        
        assert processed_data is not None, "Processed data should be created"
        assert len(processed_data) > 0, "Processed data should not be empty"
        
        # Check column normalization
        expected_columns = ['time', 'depth', 'latitude', 'longitude', 'tv290c', 'sal00', 'sbeox0mm_l', 'fleco_afl', 'ph']
        for col in expected_columns:
            if col in processed_data.columns:
                assert col in processed_data.columns, f"Column {col} should be normalized"
        
        print("  PASS: CNV to processed data pipeline")
    
    def test_processed_data_to_archive_pipeline(self):
        """Test processed data to archive pipeline"""
        print("Testing processed data to archive pipeline...")
        
        # Read and process data
        raw_data, metadata = self.reader.read_cnv_file(str(self.test_cnv_file))
        processed_data = self.processor.process(raw_data)
        
        # Step 3: Archive data
        archive_path = self.temp_path / "pipeline_archive"
        
        # Create metadata for archiving
        archive_metadata = {
            'source_file': str(self.test_cnv_file),
            'processing_date': datetime.now().isoformat(),
            'data_range': {
                'start_time': processed_data['time'].min().isoformat() if 'time' in processed_data.columns else None,
                'end_time': processed_data['time'].max().isoformat() if 'time' in processed_data.columns else None,
                'min_depth': float(processed_data['depth'].min()) if 'depth' in processed_data.columns else None,
                'max_depth': float(processed_data['depth'].max()) if 'depth' in processed_data.columns else None
            },
            'variables': list(processed_data.columns),
            'total_records': len(processed_data)
        }
        
        # Create quality report
        quality_report = {
            'total_records': len(processed_data),
            'duplicate_count': 0,
            'missing_values': {col: int(processed_data[col].isna().sum()) for col in processed_data.columns},
            'data_quality': 'good',
            'processing_timestamp': datetime.now().isoformat()
        }
        
        # Archive comprehensive
        result = self.archiver.archive_comprehensive(
            processed_data,
            str(archive_path),
            metadata=archive_metadata,
            quality_report=quality_report,
            compress=True
        )
        
        assert result is True, "Comprehensive archiving should succeed"
        
        # Verify archive files
        csv_file = self.temp_path / "pipeline_archive.csv.gz"
        metadata_file = self.temp_path / "pipeline_archive_metadata.json"
        quality_file = self.temp_path / "pipeline_archive_quality.json"
        
        assert csv_file.exists(), "CSV archive should be created"
        assert metadata_file.exists(), "Metadata archive should be created"
        assert quality_file.exists(), "Quality report archive should be created"
        
        print("  PASS: Processed data to archive pipeline")
    
    def test_complete_pipeline(self):
        """Test complete file processing pipeline"""
        print("Testing complete pipeline...")
        
        # Complete pipeline: CNV -> Process -> Archive
        raw_data, metadata = self.reader.read_cnv_file(str(self.test_cnv_file))
        processed_data = self.processor.process(raw_data)
        
        # Archive with metadata
        archive_metadata = {
            'source_file': str(self.test_cnv_file),
            'processing_date': datetime.now().isoformat(),
            'total_records': len(processed_data)
        }
        
        quality_report = {
            'total_records': len(processed_data),
            'data_quality': 'good'
        }
        
        result = self.archiver.archive_comprehensive(
            processed_data,
            str(self.temp_path / "complete_pipeline"),
            metadata=archive_metadata,
            quality_report=quality_report
        )
        
        assert result is True, "Complete pipeline should succeed"
        
        # Verify data integrity
        archived_data = pd.read_csv(self.temp_path / "complete_pipeline.csv")
        assert len(archived_data) == len(processed_data), "Archived data should match processed data"
        
        print("  PASS: Complete pipeline")
    
    def test_pipeline_with_database(self):
        """Test pipeline with database archiving"""
        print("Testing pipeline with database...")
        
        # Read and process data
        raw_data, metadata = self.reader.read_cnv_file(str(self.test_cnv_file))
        processed_data = self.processor.process(raw_data)
        
        # Mock database archiving
        with patch('triaxus.data.archiver.DatabaseDataSource') as mock_db:
            mock_db_instance = Mock()
            mock_db.return_value = mock_db_instance
            mock_db_instance.store_data.return_value = True
            
            # Archive to database
            result = self.archiver.archive_to_database(processed_data, 'pipeline_test')
            
            assert result is True, "Database archiving should succeed"
            assert mock_db_instance.store_data.called, "Database store should be called"
        
        print("  PASS: Pipeline with database")
    
    def test_pipeline_error_handling(self):
        """Test pipeline error handling"""
        print("Testing pipeline error handling...")
        
        # Test with invalid CNV file
        invalid_file = self.temp_path / "invalid.cnv"
        invalid_file.write_text("This is not a valid CNV file")
        
        try:
            raw_data, metadata = self.reader.read_cnv_file(str(invalid_file))
            assert False, "Should raise error for invalid CNV file"
        except Exception as e:
            assert "Invalid" in str(e) or "Error" in str(e), "Should raise appropriate error"
        
        # Test with empty processed data
        empty_data = pd.DataFrame()
        
        try:
            result = self.archiver.archive_to_csv(empty_data, str(self.temp_path / "empty.csv"))
            assert result is False, "Should return False for empty data"
        except Exception as e:
            assert "Empty" in str(e) or "No data" in str(e), "Should raise appropriate error"
        
        print("  PASS: Pipeline error handling")
    
    def test_pipeline_performance(self):
        """Test pipeline performance with larger dataset"""
        print("Testing pipeline performance...")
        
        # Create larger test file
        large_file = self.temp_path / "large_pipeline_test.cnv"
        self._create_large_cnv_file(large_file, 1000)
        
        # Test pipeline with larger dataset
        start_time = datetime.now()
        
        raw_data, metadata = self.reader.read_cnv_file(str(large_file))
        processed_data = self.processor.process(raw_data)
        
        archive_metadata = {
            'source_file': str(large_file),
            'total_records': len(processed_data)
        }
        
        result = self.archiver.archive_comprehensive(
            processed_data,
            str(self.temp_path / "large_pipeline"),
            metadata=archive_metadata
        )
        
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        assert result is True, "Large dataset pipeline should succeed"
        assert processing_time < 30, "Pipeline should complete within 30 seconds"
        assert len(processed_data) == 1000, "Should process all 1000 records"
        
        print(f"  PASS: Pipeline performance (processed 1000 records in {processing_time:.2f}s)")
    
    def _create_large_cnv_file(self, file_path, num_rows):
        """Create a large CNV file for performance testing"""
        header = """* Sea-Bird SBE 19plus V 2.2.2  SERIAL NO. 01907508
* 05-Jan-2024 12:00:00
* file_type: ascii
* nquan: 7
* nvalues: {num_rows}
* columns = time, depSM, t090C, c0S/m, sal00, sbeox0Mm/L, flECO-AFL
# name 0 = timeS: Time, Elapsed [seconds]
# name 1 = depSM: Depth [salt water, m]
# name 2 = t090C: Temperature [ITS-90, deg C]
# name 3 = c0S/m: Conductivity [S/m]
# name 4 = sal00: Salinity, Practical [PSU]
# name 5 = sbeox0Mm/L: Oxygen, SBE 43 [umol/kg]
# name 6 = flECO-AFL: Fluorescence, WET Labs ECO-AFL/FL [mg/m^3]
*END*
""".format(num_rows=num_rows)
        
        data_lines = []
        for i in range(num_rows):
            time_val = i * 0.25
            depth = 1.0 + i * 0.1
            temp = 15.0 + i * 0.01
            cond = 3.45678
            sal = 35.0 + i * 0.001
            oxy = 8.0 + i * 0.01
            fluo = 0.5 + i * 0.001
            
            data_lines.append(f"{time_val:.6f}, {depth:.3f}, {temp:.4f}, {cond:.5f}, {sal:.4f}, {oxy:.4f}, {fluo:.4f}")
        
        content = header + "\n".join(data_lines)
        file_path.write_text(content)


def test_file_processing_pipeline_integration():
    """Integration test for file processing pipeline"""
    print("Testing file processing pipeline integration...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create test CNV file
        test_file = temp_path / "integration_pipeline_test.cnv"
        test_file.write_text("""* Sea-Bird SBE 19plus V 2.2.2
* 05-Jan-2024 12:00:00
* file_type: ascii
* nquan: 7
* nvalues: 5
* columns = time, depSM, t090C, c0S/m, sal00, sbeox0Mm/L, flECO-AFL
# name 0 = timeS: Time, Elapsed [seconds]
# name 1 = depSM: Depth [salt water, m]
# name 2 = t090C: Temperature [ITS-90, deg C]
# name 3 = c0S/m: Conductivity [S/m]
# name 4 = sal00: Salinity, Practical [PSU]
# name 5 = sbeox0Mm/L: Oxygen, SBE 43 [umol/kg]
# name 6 = flECO-AFL: Fluorescence, WET Labs ECO-AFL/FL [mg/m^3]
*END*
0.000000, 1.000, 15.2345, 3.45678, 35.1234, 8.1234, 0.5432
0.250000, 2.000, 15.1234, 3.45678, 35.0987, 8.0987, 0.5432
0.500000, 3.000, 15.0123, 3.45678, 35.0741, 8.0741, 0.5432
0.750000, 4.000, 14.9012, 3.45678, 35.0495, 8.0495, 0.5432
1.000000, 5.000, 14.7901, 3.45678, 35.0249, 8.0249, 0.5432
""")
        
        # Create components
        reader = CNVFileReader()
        processor = DataProcessor()
        archiver = DataArchiver()
        
        # Test complete pipeline
        raw_data, metadata = reader.read_cnv_file(str(test_file))
        assert raw_data is not None, "Raw data should be loaded"
        assert len(raw_data) == 5, "Should have 5 data rows"
        
        processed_data = processor.process(raw_data)
        assert processed_data is not None, "Processed data should be created"
        assert len(processed_data) > 0, "Processed data should not be empty"
        
        # Archive data
        result = archiver.archive_to_csv(processed_data, str(temp_path / "integration_test.csv"))
        assert result is True, "CSV archiving should succeed"
        
        # Verify archive
        archived_data = pd.read_csv(temp_path / "integration_test.csv")
        assert len(archived_data) == len(processed_data), "Archived data should match processed data"
        
        print("  PASS: Integration test")


if __name__ == "__main__":
    # Run tests
    test_instance = TestFileProcessingPipeline()
    test_instance.setup_method()
    
    try:
        test_instance.test_cnv_to_processed_data_pipeline()
        test_instance.test_processed_data_to_archive_pipeline()
        test_instance.test_complete_pipeline()
        test_instance.test_pipeline_with_database()
        test_instance.test_pipeline_error_handling()
        test_instance.test_pipeline_performance()
        
        test_file_processing_pipeline_integration()
        
        print("\nAll file processing pipeline tests passed!")
        
    finally:
        test_instance.teardown_method()
