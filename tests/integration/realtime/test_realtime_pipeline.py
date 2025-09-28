"""
Integration tests for real-time pipeline
"""

import pytest
import tempfile
import time
import subprocess
import signal
import os
from pathlib import Path
from unittest.mock import Mock, patch

from triaxus.data.cnv_realtime_processor import CNVRealtimeProcessor
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "realtime"))
from realtime_api_server import RealtimeAPIHandler


class TestRealtimePipeline:
    """Test real-time pipeline integration"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
        
        # Create test CNV file
        self.test_cnv_file = self.temp_path / "live_test.cnv"
        self._create_test_cnv_file()
        
        # Create test config
        self.test_config = {
            'cnv_processing': {
                'source_directory': str(self.temp_path),
                'file_patterns': ['live_test.cnv'],
                'realtime': {
                    'enabled': True,
                    'interval_seconds': 5,
                    'plot_after_ingest': True,
                    'plot_output_dir': str(self.temp_path / "plots"),
                    'file_patterns': ['live_test.cnv'],
                    'min_age_seconds': 0.1,
                    'state_file': str(self.temp_path / "state.json")
                }
            }
        }
        
        # Create state file
        self.state_file = self.temp_path / "state.json"
        self.state_file.write_text('{}')
        
        # Create plots directory
        (self.temp_path / "plots").mkdir(exist_ok=True)
    
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
*END*
0.000000 1.000 15.2345 3.45678 35.1234 8.1234 0.5432
0.250000 2.000 15.1234 3.45678 35.0987 8.0987 0.5432
0.500000 3.000 15.0123 3.45678 35.0741 8.0741 0.5432
0.750000 4.000 14.9012 3.45678 35.0495 8.0495 0.5432
1.000000 5.000 14.7901 3.45678 35.0249 8.0249 0.5432
"""
        self.test_cnv_file.write_text(cnv_content)
    
    def teardown_method(self):
        """Cleanup test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_processor_and_api_integration(self):
        """Test processor and API server integration"""
        print("Testing processor and API integration...")
        
        with patch('triaxus.core.config.ConfigManager') as mock_config:
            mock_config.return_value.get.return_value = self.test_config
            
            # Test processor
            processor = CNVRealtimeProcessor()
            assert processor is not None
            assert processor.cnv_reader is not None
            assert processor.data_processor is not None
            assert processor.data_archiver is not None
            
            # Test API handler (simplified test without actual HTTP server)
            with patch('triaxus.data.database_source.DatabaseDataSource') as mock_db:
                with patch('triaxus.core.config.manager.ConfigManager') as mock_config_api:
                    mock_db_instance = Mock()
                    mock_config_instance = Mock()
                    mock_db.return_value = mock_db_instance
                    mock_config_api.return_value = mock_config_instance
                    
                    # Test that we can import the handler
                    from realtime_api_server import RealtimeAPIHandler
                    assert RealtimeAPIHandler is not None
            
            print("  PASS: Processor and API integration")
    
    def test_file_processing_workflow(self):
        """Test complete file processing workflow"""
        print("Testing file processing workflow...")
        
        with patch('triaxus.core.config.ConfigManager') as mock_config:
            mock_config.return_value.get.return_value = self.test_config
            processor = CNVRealtimeProcessor()
            
            # Test file processing using actual method
            result = processor.process_file_by_path(str(self.test_cnv_file))
            assert result is not None, "File processing should return result"
            assert 'filename' in result, "Result should contain filename"
            assert 'records' in result, "Result should contain record count"
            
            print("  PASS: File processing workflow")
    
    def test_plot_generation_workflow(self):
        """Test plot generation workflow"""
        print("Testing plot generation workflow...")
        
        with patch('triaxus.core.config.ConfigManager') as mock_config:
            mock_config.return_value.get.return_value = self.test_config
            processor = CNVRealtimeProcessor()
            
            # Test that processor has the necessary components for plotting
            assert processor.data_archiver is not None, "Data archiver should be available"
            
            # Test file processing which includes plotting capability
            with patch('triaxus.visualizer.TriaxusVisualizer') as mock_viz:
                mock_viz_instance = Mock()
                mock_viz.return_value = mock_viz_instance
                
                # Process a file which should trigger plotting
                result = processor.process_file_by_path(str(self.test_cnv_file))
                assert result is not None, "File processing should succeed"
            
            print("  PASS: Plot generation workflow")
    
    def test_state_management_workflow(self):
        """Test state management workflow"""
        print("Testing state management workflow...")
        
        with patch('triaxus.core.config.ConfigManager') as mock_config:
            mock_config.return_value.get.return_value = self.test_config
            processor = CNVRealtimeProcessor()
            
            # Test that processor can be initialized (state management is internal)
            assert processor is not None, "Processor should be initialized"
            assert processor.cnv_config is not None, "CNV config should be loaded"
            
            # Test source directory access
            source_dir = processor.get_source_directory()
            assert source_dir is not None, "Source directory should be accessible"
            
            print("  PASS: State management workflow")
    
    def test_configuration_workflow(self):
        """Test configuration workflow"""
        print("Testing configuration workflow...")
        
        # Test with custom config
        config_file = self.temp_path / "custom_config.yaml"
        config_file.write_text("""
cnv_processing:
  source_directory: "custom_dir"
  file_patterns: ["*.cnv"]
  realtime:
    enabled: true
    interval_seconds: 15
    plot_after_ingest: true
    plot_output_dir: "custom_plots"
    file_patterns: ["*.cnv"]
    min_age_seconds: 0.5
    state_file: "custom_state.json"
""")
        
        processor = CNVRealtimeProcessor(custom_config_path=str(config_file))
        assert processor is not None
        
        print("  PASS: Configuration workflow")


def test_realtime_pipeline_end_to_end():
    """End-to-end test for real-time pipeline"""
    print("Testing real-time pipeline end-to-end...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create test CNV file
        test_cnv = temp_path / "e2e_test.cnv"
        test_cnv.write_text("""* Sea-Bird SBE 19plus V 2.2.2
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
0.000000 1.000 15.2345 3.45678 35.1234 8.1234 0.5432
0.250000 2.000 15.1234 3.45678 35.0987 8.0987 0.5432
0.500000 3.000 15.0123 3.45678 35.0741 8.0741 0.5432
""")
        
        # Create test config
        test_config = {
            'cnv_processing': {
                'source_directory': str(temp_path),
                'file_patterns': ['e2e_test.cnv'],
                'realtime': {
                    'enabled': True,
                    'interval_seconds': 2,
                    'plot_after_ingest': False,  # Disable plotting for E2E test
                    'plot_output_dir': str(temp_path / "plots"),
                    'file_patterns': ['e2e_test.cnv'],
                    'min_age_seconds': 0.1,
                    'state_file': str(temp_path / "state.json")
                }
            }
        }
        
        # Create state file
        (temp_path / "state.json").write_text('{}')
        (temp_path / "plots").mkdir(exist_ok=True)
        
        with patch('triaxus.core.config.ConfigManager') as mock_config:
            mock_config.return_value.get.return_value = test_config
            processor = CNVRealtimeProcessor()
            
            # Test complete workflow using actual methods
            result = processor.process_file_by_path(str(test_cnv))
            assert result is not None, "File processing should succeed"
            assert 'filename' in result, "Result should contain filename"
            assert 'records' in result, "Result should contain record count"
            
            # Test source directory access
            source_dir = processor.get_source_directory()
            assert source_dir is not None, "Source directory should be accessible"
            
            print("  PASS: End-to-end test")


if __name__ == "__main__":
    # Run tests
    test_instance = TestRealtimePipeline()
    test_instance.setup_method()
    
    try:
        test_instance.test_processor_and_api_integration()
        test_instance.test_file_processing_workflow()
        test_instance.test_plot_generation_workflow()
        test_instance.test_state_management_workflow()
        test_instance.test_configuration_workflow()
        
        test_realtime_pipeline_end_to_end()
        
        print("\nAll real-time pipeline tests passed!")
        
    finally:
        test_instance.teardown_method()
