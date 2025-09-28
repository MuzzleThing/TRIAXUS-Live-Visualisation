"""
Unit tests for CNV file reader
"""

import pytest
import tempfile
import pandas as pd
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch

from triaxus.data.cnv_reader import CNVFileReader


class TestCNVFileReader:
    """Test CNV file reader functionality"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
        
        # Create test CNV file
        self.test_cnv_file = self.temp_path / "test_file.cnv"
        self._create_test_cnv_file()
        
        # Create reader instance
        self.reader = CNVFileReader()
    
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
* nvalues: 5
* columns = time, depSM, t090C, c0S/m, sal00, sbeox0Mm/L, flECO-AFL
# name 0 = timeS: Time, Elapsed [seconds]
# name 1 = depSM: Depth [salt water, m]
# name 2 = t090C: Temperature [ITS-90, deg C]
# name 3 = c0S/m: Conductivity [S/m]
# name 4 = sal00: Salinity, Practical [PSU]
# name 5 = sbeox0Mm/L: Oxygen, SBE 43 [umol/kg]
# name 6 = flECO-AFL: Fluorescence, WET Labs ECO-AFL/FL [mg/m^3]
# span 0 = 0.000000, 0.000000
# span 1 = 0.000000, 0.000000
# span 2 = 0.000000, 0.000000
# span 3 = 0.000000, 0.000000
# span 4 = 0.000000, 0.000000
# span 5 = 0.000000, 0.000000
# span 6 = 0.000000, 0.000000
# interval = seconds: 0.250000
# datcnv_date = 05-Jan-2024 12:00:00
# datcnv_time = 05-Jan-2024 12:00:00
# start_time = 05-Jan-2024 12:00:00
# bad_flag = -9.990e-29
*END*
0.000000, 1.000, 15.2345, 3.45678, 35.1234, 8.1234, 0.5432
0.250000, 2.000, 15.1234, 3.45678, 35.0987, 8.0987, 0.5432
0.500000, 3.000, 15.0123, 3.45678, 35.0741, 8.0741, 0.5432
0.750000, 4.000, 14.9012, 3.45678, 35.0495, 8.0495, 0.5432
1.000000, 5.000, 14.7901, 3.45678, 35.0249, 8.0249, 0.5432
"""
        self.test_cnv_file.write_text(cnv_content)
    
    def teardown_method(self):
        """Cleanup test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_reader_initialization(self):
        """Test CNV reader initialization"""
        print("Testing CNV reader initialization...")
        
        reader = CNVFileReader()
        assert reader is not None
        print("  PASS: CNV reader initialization")
    
    def test_cnv_file_reading(self):
        """Test CNV file reading"""
        print("Testing CNV file reading...")
        
        # Test file reading
        data, metadata = self.reader.read_cnv_file(str(self.test_cnv_file))
        
        assert data is not None, "Data should be loaded"
        assert metadata is not None, "Metadata should be loaded"
        assert len(data) == 5, "Should have 5 data rows"
        assert len(data.columns) == 7, "Should have 7 columns"
        
        # Check column names
        expected_columns = ['time', 'depSM', 't090C', 'c0S/m', 'sal00', 'sbeox0Mm/L', 'flECO-AFL']
        for col in expected_columns:
            assert col in data.columns, f"Column {col} should be present"
        
        print("  PASS: CNV file reading")
    
    def test_metadata_extraction(self):
        """Test metadata extraction"""
        print("Testing metadata extraction...")
        
        data, metadata = self.reader.read_cnv_file(str(self.test_cnv_file))
        
        # Check metadata
        assert 'start_time' in metadata, "Start time should be in metadata"
        assert 'nquan' in metadata, "Number of quantities should be in metadata"
        assert 'nvalues' in metadata, "Number of values should be in metadata"
        assert 'file_type' in metadata, "File type should be in metadata"
        
        # Check specific values
        assert metadata['nquan'] == 7, "Should have 7 quantities"
        assert metadata['nvalues'] == 5, "Should have 5 values"
        assert metadata['file_type'] == 'ascii', "Should be ASCII file type"
        
        print("  PASS: Metadata extraction")
    
    def test_data_types(self):
        """Test data type handling"""
        print("Testing data type handling...")
        
        data, metadata = self.reader.read_cnv_file(str(self.test_cnv_file))
        
        # Check data types
        assert pd.api.types.is_numeric_dtype(data['depSM']), "Depth should be numeric"
        assert pd.api.types.is_numeric_dtype(data['t090C']), "Temperature should be numeric"
        assert pd.api.types.is_numeric_dtype(data['c0S/m']), "Conductivity should be numeric"
        assert pd.api.types.is_numeric_dtype(data['sal00']), "Salinity should be numeric"
        assert pd.api.types.is_numeric_dtype(data['sbeox0Mm/L']), "Oxygen should be numeric"
        assert pd.api.types.is_numeric_dtype(data['flECO-AFL']), "Fluorescence should be numeric"
        
        print("  PASS: Data type handling")
    
    def test_time_parsing(self):
        """Test time parsing"""
        print("Testing time parsing...")
        
        data, metadata = self.reader.read_cnv_file(str(self.test_cnv_file))
        
        # Check time column
        assert 'time' in data.columns, "Time column should be present"
        assert pd.api.types.is_numeric_dtype(data['time']), "Time should be numeric (seconds)"
        
        # Check time values
        assert data['time'].min() == 0.0, "First time should be 0.0"
        assert data['time'].max() == 1.0, "Last time should be 1.0"
        
        print("  PASS: Time parsing")
    
    def test_error_handling(self):
        """Test error handling"""
        print("Testing error handling...")
        
        # Test with non-existent file
        try:
            self.reader.read_cnv_file("nonexistent.cnv")
            assert False, "Should raise an error for non-existent file"
        except Exception as e:
            assert "No such file" in str(e) or "FileNotFoundError" in str(e), "Should raise file not found error"
        
        # Test with invalid CNV file
        invalid_file = self.temp_path / "invalid.cnv"
        invalid_file.write_text("This is not a valid CNV file")
        
        try:
            self.reader.read_cnv_file(str(invalid_file))
            assert False, "Should raise an error for invalid CNV file"
        except Exception as e:
            assert "Invalid" in str(e) or "Error" in str(e), "Should raise invalid file error"
        
        print("  PASS: Error handling")
    
    def test_large_file_handling(self):
        """Test large file handling"""
        print("Testing large file handling...")
        
        # Create a larger test file
        large_file = self.temp_path / "large_test.cnv"
        self._create_large_cnv_file(large_file, 1000)
        
        # Test reading large file
        data, metadata = self.reader.read_cnv_file(str(large_file))
        
        assert data is not None, "Large file data should be loaded"
        assert len(data) == 1000, "Should have 1000 data rows"
        assert metadata is not None, "Large file metadata should be loaded"
        
        print("  PASS: Large file handling")
    
    def _create_large_cnv_file(self, file_path, num_rows):
        """Create a large CNV file for testing"""
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


def test_cnv_reader_integration():
    """Integration test for CNV reader"""
    print("Testing CNV reader integration...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create test CNV file
        test_file = temp_path / "integration_test.cnv"
        test_file.write_text("""* Sea-Bird SBE 19plus V 2.2.2
* 05-Jan-2024 12:00:00
* file_type: ascii
* nquan: 7
* nvalues: 3
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
""")
        
        reader = CNVFileReader()
        
        # Test reading
        data, metadata = reader.read_cnv_file(str(test_file))
        
        assert data is not None, "Data should be loaded"
        assert metadata is not None, "Metadata should be loaded"
        assert len(data) == 3, "Should have 3 data rows"
        assert len(data.columns) == 7, "Should have 7 columns"
        
        # Test data processing
        processed_data = data.copy()
        processed_data['datetime'] = pd.to_datetime('2024-01-05 12:00:00') + pd.to_timedelta(processed_data['time'], unit='s')
        
        assert 'datetime' in processed_data.columns, "Datetime column should be added"
        assert len(processed_data) == 3, "Processed data should have 3 rows"
        
        print("  PASS: Integration test")


if __name__ == "__main__":
    # Run tests
    test_instance = TestCNVFileReader()
    test_instance.setup_method()
    
    try:
        test_instance.test_reader_initialization()
        test_instance.test_cnv_file_reading()
        test_instance.test_metadata_extraction()
        test_instance.test_data_types()
        test_instance.test_time_parsing()
        test_instance.test_error_handling()
        test_instance.test_large_file_handling()
        
        test_cnv_reader_integration()
        
        print("\nAll CNV reader tests passed!")
        
    finally:
        test_instance.teardown_method()
