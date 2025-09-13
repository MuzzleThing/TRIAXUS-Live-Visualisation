from PySide6.QtWidgets import QMainWindow, QApplication, QTabWidget, QWidget, QVBoxLayout
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import QUrl
import sys
import os
import socket
import threading
import http.server
import socketserver
from plot_view import PlotView


# This class is a local server to serve the html content for the map view.
# It is necessary to use such a server instead of loading the local html file directly
# Because Qt Web Engine is built upon Chromium, which forbid cross-origin requests.
# That obstructs the local map html from requesting online resources such as map tiles.
class EmbeddedServer:
    def __init__(self, port=8000):
        self.port = port
        self.server = None
        self.server_thread = None
        self.running = False
        self.serve_directory = None
        
    def start_server(self, directory):
        """Start the HTTP server in a separate thread"""
        if self.running:
            return
            
        self.serve_directory = directory
        
        try:
            # Create custom handler that serves from specific directory
            class CustomHandler(http.server.SimpleHTTPRequestHandler):
                def __init__(self, *args, **kwargs):
                    super().__init__(*args, directory=directory, **kwargs)
            
            # Create server
            self.server = socketserver.TCPServer(("", self.port), CustomHandler)
            
            # Start server in a separate thread
            self.server_thread = threading.Thread(target=self.server.serve_forever)
            self.server_thread.daemon = True
            self.server_thread.start()
            
            self.running = True
            print(f"Server started on http://localhost:{self.port}")
            print(f"Serving directory: {directory}")
            
        except OSError as e:
            if e.errno == 98:  # Address already in use
                print(f"Port {self.port} is already in use")
            else:
                print(f"Failed to start server: {e}")
        except Exception as e:
            print(f"Failed to start server: {e}")
    
    def stop_server(self):
        """Stop the HTTP server"""
        if self.server and self.running:
            self.server.shutdown()
            self.server.server_close()
            if self.server_thread:
                self.server_thread.join()
            self.running = False
            print("Server stopped")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TRIAXUS Visualiser")
        
        # Initialize embedded server
        self.server = EmbeddedServer(port=8000)
        
        # Start server from the project root directory
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.server.start_server(project_root)

        # Create the tab widget
        tab_widget = QTabWidget()

        # Map view
        map_view = QWebEngineView()

        # Determine which map to load based on internet connectivity
        if has_internet():
            map_url = "http://localhost:8000/GPS-map/online/map.html"
        else:
            map_url = "http://localhost:8000/GPS-map/offline/map.html"
            
        map_view.load(QUrl(map_url))
        tab_widget.addTab(map_view, "Map")

        # Plot view
        plot_view = PlotView()
        tab_widget.addTab(plot_view, "Plot")

        self.setCentralWidget(tab_widget)
    
    def closeEvent(self, event):
        """Handle application close event"""
        # Stop the embedded server when closing the app
        if self.server:
            self.server.stop_server()
        super().closeEvent(event)

# This function determines whether an Internet connection is available by attempting to connnect to Googles DNS server.
# The purpose of this function is to help decide whether the app should load the online version of the map
def has_internet(host="8.8.8.8", port=53, timeout=3):
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except Exception:
        return False

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())