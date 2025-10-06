import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from triaxus.visualizer import TriaxusVisualizer
from triaxus.data import create_plot_test_data
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QListWidget, QListWidgetItem, QSplitter)
from PySide6.QtCore import Qt, QUrl
from PySide6.QtWebEngineWidgets import QWebEngineView
import tempfile


class PlotView(QWidget):
    def __init__(self):
        super().__init__()
        try:
            # Initialize TRIAXUS visualizer with error handling
            print("Initializing TriaxusVisualizer...")
            self.visualizer = TriaxusVisualizer()
            print("TriaxusVisualizer initialized successfully")
        except Exception as e:
            print(f"Failed to initialize TriaxusVisualizer: {e}")
            self.visualizer = None
        self.init_ui()

    def init_ui(self):
        # Main horizontal layout
        main_layout = QHBoxLayout()

        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Horizontal)

        # Side menu for plot types
        self.plot_menu = self.create_plot_menu()
        splitter.addWidget(self.plot_menu)

        # Main plot area
        self.plot_area = self.create_plot_area()
        splitter.addWidget(self.plot_area)

        # Set splitter proportions (30% menu, 70% plot area)
        splitter.setSizes([200, 600])

        main_layout.addWidget(splitter)
        self.setLayout(main_layout)

    def create_plot_menu(self):
        """Create the side menu with plot type options"""
        menu_widget = QWidget()
        menu_layout = QVBoxLayout()

        # Menu title
        title = QLabel("Plot Types")
        title.setStyleSheet("font-weight: bold; font-size: 14px; margin: 10px;")
        menu_layout.addWidget(title)

        # Plot type list
        self.plot_list = QListWidget()
        plot_types = [
            "Time Series",
            "Contour Plot",
            "Depth Profile"
        ]

        for plot_type in plot_types:
            item = QListWidgetItem(plot_type)
            self.plot_list.addItem(item)

        # Connect selection event
        self.plot_list.itemClicked.connect(self.on_plot_type_selected)

        menu_layout.addWidget(self.plot_list)
        menu_widget.setLayout(menu_layout)

        return menu_widget

    def create_plot_area(self):
        """Create the main plot display area with QWebEngineView for HTML plots"""
        plot_widget = QWidget()
        plot_layout = QVBoxLayout()

        # Create QWebEngineView for displaying HTML plots
        self.web_view = QWebEngineView()

        # Create a temporary directory for storing plot HTML files
        self.temp_dir = tempfile.mkdtemp(prefix="triaxus_plots_")

        # Set initial HTML content
        initial_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>TRIAXUS Plot</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                    background-color: #f5f5f5;
                }
                .message {
                    text-align: center;
                    font-size: 18px;
                    color: #666;
                }
            </style>
        </head>
        <body>
            <div class="message">
                <h2>TRIAXUS Plot Viewer</h2>
                <p>Select a plot type from the menu to begin</p>
            </div>
        </body>
        </html>
        """

        # Save initial HTML and load it
        initial_file = os.path.join(self.temp_dir, "initial.html")
        with open(initial_file, 'w', encoding='utf-8') as f:
            f.write(initial_html)

        self.web_view.load(QUrl.fromLocalFile(initial_file))

        plot_layout.addWidget(self.web_view)
        plot_widget.setLayout(plot_layout)

        return plot_widget

    def generate_html_plot(self, plot_type, variable=None):
        """Generate HTML plot using TriaxusVisualizer and save to temp directory"""
        try:
            print(f"Generating {plot_type} plot...")

            # Generate test data
            data = create_plot_test_data()
            print(f"Test data shape: {data.shape}")

            # Create plot figure using TriaxusVisualizer
            if plot_type == "contour" and variable:
                plotly_figure = self.visualizer.create_plot_figure(plot_type, data, variable=variable)
            else:
                plotly_figure = self.visualizer.create_plot_figure(plot_type, data)

            # Convert to HTML
            html_content = plotly_figure.to_html(
                include_plotlyjs=True,  # Include Plotly.js inline for offline use
                config={
                    'displayModeBar': True,  # Show the toolbar with zoom, pan, etc.
                    'displaylogo': False,   # Remove Plotly logo
                    'modeBarButtonsToRemove': [],  # Keep all buttons
                    'toImageButtonOptions': {
                        'format': 'png',
                        'filename': f'triaxus_{plot_type}_plot',
                        'height': 600,
                        'width': 800,
                        'scale': 1
                    }
                }
            )

            # Save HTML to temp file
            plot_filename = f"{plot_type}_{variable if variable else 'plot'}.html"
            plot_path = os.path.join(self.temp_dir, plot_filename)

            with open(plot_path, 'w', encoding='utf-8') as f:
                f.write(html_content)

            print(f"HTML plot saved to: {plot_path}")
            return plot_path

        except Exception as e:
            print(f"Error generating HTML plot: {e}")
            import traceback
            traceback.print_exc()

            # Create error HTML
            error_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Plot Error</title>
                <style>
                    body {{ font-family: Arial, sans-serif; padding: 20px; }}
                    .error {{ color: red; background-color: #ffe6e6; padding: 15px; border-radius: 5px; }}
                </style>
            </head>
            <body>
                <div class="error">
                    <h3>Error creating {plot_type} plot</h3>
                    <p>{str(e)}</p>
                </div>
            </body>
            </html>
            """

            error_path = os.path.join(self.temp_dir, f"error_{plot_type}.html")
            with open(error_path, 'w', encoding='utf-8') as f:
                f.write(error_html)

            return error_path

    def on_plot_type_selected(self, item):
        """Handle plot type selection"""
        plot_type = item.text()

        # Show loading message in web view
        loading_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Loading Plot</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                    background-color: #f5f5f5;
                }}
                .loading {{
                    text-align: center;
                    font-size: 18px;
                    color: #666;
                }}
                .spinner {{
                    border: 4px solid #f3f3f3;
                    border-top: 4px solid #3498db;
                    border-radius: 50%;
                    width: 40px;
                    height: 40px;
                    animation: spin 2s linear infinite;
                    margin: 20px auto.
                }}
                @keyframes spin {{
                    0% {{ transform: rotate(0deg); }}
                    100% {{ transform: rotate(360deg); }}
                }}
            </style>
        </head>
        <body>
            <div class="loading">
                <h2>Loading {plot_type}...</h2>
                <div class="spinner"></div>
                <p>Please wait while the plot is being generated</p>
            </div>
        </body>
        </html>
        """

        # Save and load loading HTML
        loading_file = os.path.join(self.temp_dir, "loading.html")
        with open(loading_file, 'w', encoding='utf-8') as f:
            f.write(loading_html)
        self.web_view.load(QUrl.fromLocalFile(loading_file))

        # Generate and load the appropriate plot
        if plot_type == "Time Series":
            plot_path = self.generate_html_plot("time_series")
        elif plot_type == "Contour Plot":
            plot_path = self.generate_html_plot("contour", variable="tv290c")
        elif plot_type == "Depth Profile":
            plot_path = self.generate_html_plot("depth_profile")
        else:
            print(f"Unknown plot type: {plot_type}")
            return

        # Load the generated plot
        if plot_path:
            self.web_view.load(QUrl.fromLocalFile(plot_path))

    def cleanup_temp_files(self):
        """Clean up temporary plot files"""
        try:
            import shutil
            if hasattr(self, 'temp_dir') and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
                print(f"Cleaned up temporary directory: {self.temp_dir}")
        except Exception as e:
            print(f"Error cleaning up temp files: {e}")

    def __del__(self):
        """Destructor to clean up resources"""
        self.cleanup_temp_files()