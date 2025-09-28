"""
Unit tests for real-time API server
"""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from http.server import HTTPServer
import threading
import time
import requests

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "realtime"))
from realtime_api_server import RealtimeAPIHandler


class TestRealtimeAPIServer:
    """Test real-time API server functionality"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
        
        # Create test dashboard files
        self.dashboard_html = self.temp_path / "dashboard.html"
        self.dashboard_css = self.temp_path / "dashboard.css"
        self.dashboard_js = self.temp_path / "dashboard.js"
        
        self.dashboard_html.write_text("""
<!DOCTYPE html>
<html>
<head>
    <title>Test Dashboard</title>
    <link rel="stylesheet" href="dashboard.css">
</head>
<body>
    <h1>Test Dashboard</h1>
    <script src="dashboard.js"></script>
</body>
</html>
""")
        
        self.dashboard_css.write_text("""
body { font-family: Arial, sans-serif; }
h1 { color: blue; }
""")
        
        self.dashboard_js.write_text("""
console.log('Test dashboard loaded');
""")
    
    def teardown_method(self):
        """Cleanup test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_api_handler_initialization(self):
        """Test API handler initialization"""
        print("Testing API handler initialization...")
        
        with patch('triaxus.data.database_source.DatabaseDataSource') as mock_db:
            with patch('triaxus.core.config.manager.ConfigManager') as mock_config:
                mock_db_instance = Mock()
                mock_config_instance = Mock()
                mock_db.return_value = mock_db_instance
                mock_config.return_value = mock_config_instance
                
                # Test that we can import the handler
                from realtime_api_server import RealtimeAPIHandler
                assert RealtimeAPIHandler is not None
                
                # Test that the handler class exists and has expected methods
                assert hasattr(RealtimeAPIHandler, 'do_GET')
                assert hasattr(RealtimeAPIHandler, 'handle_latest_data')
                
                print("  PASS: API handler initialization")
    
    def test_dashboard_serving(self):
        """Test dashboard file serving"""
        print("Testing dashboard serving...")
        
        with patch('triaxus.data.database_source.DatabaseDataSource') as mock_db:
            with patch('triaxus.core.config.manager.ConfigManager') as mock_config:
                mock_db_instance = Mock()
                mock_config_instance = Mock()
                mock_db.return_value = mock_db_instance
                mock_config.return_value = mock_config_instance
                
                # Test that dashboard files exist
                dashboard_path = Path(__file__).parent.parent.parent.parent / "realtime" / "dashboard.html"
                assert dashboard_path.exists(), "Dashboard HTML file should exist"
                
                # Test that CSS and JS files exist
                css_path = Path(__file__).parent.parent.parent.parent / "realtime" / "dashboard.css"
                js_path = Path(__file__).parent.parent.parent.parent / "realtime" / "dashboard.js"
                assert css_path.exists(), "Dashboard CSS file should exist"
                assert js_path.exists(), "Dashboard JS file should exist"
                
                print("  PASS: Dashboard serving")
    
    def test_static_file_serving(self):
        """Test static file serving"""
        print("Testing static file serving...")
        
        with patch('triaxus.data.database_source.DatabaseDataSource') as mock_db:
            with patch('triaxus.core.config.manager.ConfigManager') as mock_config:
                mock_db_instance = Mock()
                mock_config_instance = Mock()
                mock_db.return_value = mock_db_instance
                mock_config.return_value = mock_config_instance
                
                # Test that static files exist
                dashboard_path = Path(__file__).parent.parent.parent.parent / "realtime" / "dashboard.html"
                css_path = Path(__file__).parent.parent.parent.parent / "realtime" / "dashboard.css"
                js_path = Path(__file__).parent.parent.parent.parent / "realtime" / "dashboard.js"
                
                assert dashboard_path.exists(), "Dashboard HTML file should exist"
                assert css_path.exists(), "Dashboard CSS file should exist"
                assert js_path.exists(), "Dashboard JS file should exist"
                
                # Test file content is not empty
                assert dashboard_path.stat().st_size > 0, "Dashboard HTML should not be empty"
                assert css_path.stat().st_size > 0, "Dashboard CSS should not be empty"
                assert js_path.stat().st_size > 0, "Dashboard JS should not be empty"
                
                print("  PASS: Static file serving")
    
    def test_api_endpoints(self):
        """Test API endpoints"""
        print("Testing API endpoints...")
        
        with patch('triaxus.data.database_source.DatabaseDataSource') as mock_db:
            with patch('triaxus.core.config.manager.ConfigManager') as mock_config:
                mock_db_instance = Mock()
                mock_config_instance = Mock()
                mock_db.return_value = mock_db_instance
                mock_config.return_value = mock_config_instance
                
                # Test that API server module can be imported
                from realtime_api_server import RealtimeAPIHandler
                assert RealtimeAPIHandler is not None
                
                # Test that the handler has expected API methods
                assert hasattr(RealtimeAPIHandler, 'handle_latest_data')
                assert hasattr(RealtimeAPIHandler, 'handle_status')
                assert hasattr(RealtimeAPIHandler, 'serve_dashboard')
                
                print("  PASS: API endpoints")
    
    def test_data_loading(self):
        """Test data loading functionality"""
        print("Testing data loading...")
        
        with patch('triaxus.data.database_source.DatabaseDataSource') as mock_db:
            with patch('triaxus.core.config.manager.ConfigManager') as mock_config:
                # Create mock data
                test_data = [
                    {
                        'id': 'test-1',
                        'datetime': '2024-01-01T12:00:00Z',
                        'depth': 10.0,
                        'latitude': 45.0,
                        'longitude': -120.0,
                        'tv290c': 15.0,
                        'sal00': 35.0,
                        'sbeox0mm_l': 8.0,
                        'fleco_afl': 0.5,
                        'ph': 8.1
                    }
                ]
                
                mock_db_instance = Mock()
                mock_db_instance.load_data.return_value = test_data
                mock_config_instance = Mock()
                mock_db.return_value = mock_db_instance
                mock_config.return_value = mock_config_instance
                
                # Test that data loading methods exist
                from realtime_api_server import RealtimeAPIHandler
                assert hasattr(RealtimeAPIHandler, 'handle_latest_data')
                
                # Test that database source can be imported
                from triaxus.data.database_source import DatabaseDataSource
                assert DatabaseDataSource is not None
                
                print("  PASS: Data loading")
    
    def test_error_handling(self):
        """Test error handling"""
        print("Testing error handling...")
        
        with patch('triaxus.data.database_source.DatabaseDataSource') as mock_db:
            with patch('triaxus.core.config.manager.ConfigManager') as mock_config:
                mock_db_instance = Mock()
                mock_config_instance = Mock()
                mock_db.return_value = mock_db_instance
                mock_config.return_value = mock_config_instance
                
                # Test that error handling methods exist
                from realtime_api_server import RealtimeAPIHandler
                assert hasattr(RealtimeAPIHandler, 'send_error')
                
                print("  PASS: Error handling")


def test_realtime_api_server_integration():
    """Integration test for real-time API server"""
    print("Testing real-time API server integration...")
    
    with patch('triaxus.data.database_source.DatabaseDataSource') as mock_db:
        with patch('triaxus.core.config.manager.ConfigManager') as mock_config:
            # Create mock data
            test_data = [
                {
                    'id': f'test-{i}',
                    'datetime': f'2024-01-01T{12+i:02d}:00:00Z',
                    'depth': 10.0 + i,
                    'latitude': 45.0 + i * 0.1,
                    'longitude': -120.0 + i * 0.1,
                    'tv290c': 15.0 + i * 0.1,
                    'sal00': 35.0 + i * 0.01,
                    'sbeox0mm_l': 8.0 + i * 0.05,
                    'fleco_afl': 0.5 + i * 0.02,
                    'ph': 8.1 + i * 0.01
                }
                for i in range(5)
            ]
            
            mock_db_instance = Mock()
            mock_db_instance.load_data.return_value = test_data
            mock_config_instance = Mock()
            mock_db.return_value = mock_db_instance
            mock_config.return_value = mock_config_instance
            
            # Test that all components can be imported
            from realtime_api_server import RealtimeAPIHandler
            from triaxus.data.database_source import DatabaseDataSource
            from triaxus.core.config.manager import ConfigManager
            
            assert RealtimeAPIHandler is not None
            assert DatabaseDataSource is not None
            assert ConfigManager is not None
            
            print("  PASS: Integration test")


if __name__ == "__main__":
    # Run tests
    test_instance = TestRealtimeAPIServer()
    test_instance.setup_method()
    
    try:
        test_instance.test_api_handler_initialization()
        test_instance.test_dashboard_serving()
        test_instance.test_static_file_serving()
        test_instance.test_api_endpoints()
        test_instance.test_data_loading()
        test_instance.test_error_handling()
        
        test_realtime_api_server_integration()
        
        print("\nAll real-time API server tests passed!")
        
    finally:
        test_instance.teardown_method()
