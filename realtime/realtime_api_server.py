#!/usr/bin/env python3
"""
Real-time API server for TRIAXUS dashboard
Provides REST API endpoints for live oceanographic data
"""

import json
import time
import sys
import os
from pathlib import Path
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from triaxus.data.database_source import DatabaseDataSource
from triaxus.core.config.manager import ConfigManager

class RealtimeAPIHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        # Use shared database source to avoid repeated connections
        if not hasattr(RealtimeAPIHandler, '_db_source'):
            RealtimeAPIHandler._db_source = DatabaseDataSource()
        if not hasattr(RealtimeAPIHandler, '_config'):
            RealtimeAPIHandler._config = ConfigManager()
        
        self.config = RealtimeAPIHandler._config
        self.db_source = RealtimeAPIHandler._db_source
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path == '/api/latest_data':
            self.handle_latest_data(parsed_path)
        elif path == '/api/status':
            self.handle_status()
        elif path == '/' or path == '/dashboard.html':
            self.serve_dashboard()
        elif path == '/dashboard.css':
            self.serve_static_file('dashboard.css', 'text/css')
        elif path == '/dashboard.js':
            self.serve_static_file('dashboard.js', 'application/javascript')
        else:
            self.send_error(404, "Not Found")
    
    def handle_latest_data(self, parsed_path):
        """Provide latest oceanographic data"""
        try:
            query_params = parse_qs(parsed_path.query)
            limit = int(query_params.get('limit', ['1000'])[0])
            
            # Get latest data from database (only recent data for real-time display)
            data = self.db_source.load_data(limit=limit)
            
            # Let frontend handle time filtering - return all data for flexibility
            if not data.empty and 'time' in data.columns:
                import pandas as pd
                
                # Convert time column to datetime if it's not already
                data['time'] = pd.to_datetime(data['time'], format='ISO8601')
            
            # Convert to JSON-serializable format
            records = []
            for _, row in data.iterrows():
                # Handle time conversion properly
                time_val = row['time']
                if pd.notna(time_val):
                    if hasattr(time_val, 'isoformat'):
                        time_str = time_val.isoformat()
                    else:
                        time_str = str(time_val)
                else:
                    time_str = None
                
                record = {
                    'time': time_str,
                    'depth': float(row['depth']) if pd.notna(row['depth']) else None,
                    'latitude': float(row['latitude']) if pd.notna(row['latitude']) else None,
                    'longitude': float(row['longitude']) if pd.notna(row['longitude']) else None,
                    'tv290c': float(row['tv290c']) if pd.notna(row['tv290c']) else None,
                    'sal00': float(row['sal00']) if pd.notna(row['sal00']) else None,
                    'sbeox0mm_l': float(row['sbeox0mm_l']) if pd.notna(row['sbeox0mm_l']) else None,
                }
                records.append(record)
            
            response = {
                'success': True,
                'data': records,
                'count': len(records),
                'timestamp': datetime.now().isoformat()
            }
            
            self.send_json_response(response)
            
        except Exception as e:
            error_response = {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            self.send_json_response(error_response, status=500)
    
    def handle_status(self):
        """Provide system status"""
        try:
            # Get basic stats
            data = self.db_source.load_data(limit=10)
            status = {
                'success': True,
                'database_connected': True,
                'latest_records': len(data),
                'timestamp': datetime.now().isoformat()
            }
            self.send_json_response(status)
        except Exception as e:
            status = {
                'success': False,
                'database_connected': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            self.send_json_response(status, status=500)
    
    def serve_dashboard(self):
        """Serve the dashboard HTML"""
        try:
            dashboard_path = Path(__file__).parent / 'dashboard.html'
            if dashboard_path.exists():
                with open(dashboard_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                self.send_response(200)
                self.send_header('Content-Type', 'text/html')
                self.send_header('Content-Length', str(len(content.encode('utf-8'))))
                self.end_headers()
                self.wfile.write(content.encode('utf-8'))
            else:
                self.send_error(404, "Dashboard not found")
        except Exception as e:
            self.send_error(500, f"Error serving dashboard: {str(e)}")
    
    def serve_static_file(self, filename, content_type):
        """Serve static files (CSS, JS)"""
        try:
            file_path = Path(__file__).parent / filename
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                self.send_response(200)
                self.send_header('Content-Type', content_type)
                self.send_header('Content-Length', str(len(content.encode('utf-8'))))
                self.end_headers()
                self.wfile.write(content.encode('utf-8'))
            else:
                self.send_error(404, f"Static file {filename} not found")
        except Exception as e:
            self.send_error(500, f"Error serving static file {filename}: {str(e)}")
    
    def send_json_response(self, data, status=200):
        """Send JSON response"""
        json_data = json.dumps(data, indent=2)
        
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Content-Length', str(len(json_data.encode('utf-8'))))
        self.end_headers()
        self.wfile.write(json_data.encode('utf-8'))
    
    def log_message(self, format, *args):
        """Custom log format"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        message = f"[{timestamp}] {format % args}"
        print(message)
        
        # Also write to log file
        logs_dir = Path('logs')
        logs_dir.mkdir(exist_ok=True)
        with open(logs_dir / 'api_server.log', 'a') as f:
            f.write(message + '\n')

def run_server(port=8080):
    """Run the real-time API server"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, RealtimeAPIHandler)
    
    print(f"TRIAXUS Real-time API Server starting...")
    print(f"Dashboard: http://localhost:{port}")
    print(f"API: http://localhost:{port}/api/latest_data")
    print(f"Status: http://localhost:{port}/api/status")
    print(f"Press Ctrl+C to stop")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped")
        httpd.shutdown()

if __name__ == '__main__':
    import pandas as pd
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    run_server(port)
