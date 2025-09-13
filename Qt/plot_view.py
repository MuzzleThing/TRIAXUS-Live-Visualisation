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
import os

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
        with open(initial_file, 'w') as f:
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
            
            # Handle different plot types
            for i, trace in enumerate(data):
                print(f"Processing trace {i+1}: type='{trace.type}', name='{trace.name}'")
                
                if trace.type == 'scatter':
                    # Skip the first trace if it's plotting the same variable against itself
                    # (e.g., time vs time, depth vs depth)
                    if (trace.name and hasattr(trace, 'x') and hasattr(trace, 'y') and 
                        trace.x is not None and trace.y is not None):
                        
                        # Check if x and y are the same (indicating same variable plotted against itself)
                        try:
                            x_vals = list(trace.x)
                            y_vals = list(trace.y)
                            
                            # Skip if plotting same values (like time vs time)
                            if trace.name.lower() in ['time'] and i == 0:
                                print(f"  Skipping trace '{trace.name}' (likely time vs time)")
                                continue
                                
                            # Convert datetime strings to numeric if needed
                            if isinstance(x_vals[0], str):
                                # If x is datetime strings, use index instead
                                x_vals = list(range(len(x_vals)))
                                print(f"  Converted datetime x-axis to indices")
                            
                            # Plot the trace
                            ax.plot(x_vals, y_vals, label=trace.name, marker='o', markersize=2)
                            print(f"  ✅ Plotted trace '{trace.name}'")
                            
                        except Exception as trace_error:
                            print(f"  ❌ Failed to plot trace '{trace.name}': {trace_error}")
                            continue
                    
                elif trace.type == 'contour':
                    try:
                        # For contour plots, we need to handle the interpolation issues
                        print(f"  Processing contour data...")
                        
                        # Get the original x, y, z data
                        x_data = trace.x
                        y_data = trace.y 
                        z_data = trace.z
                        
                        print(f"    Original data sizes: x={len(x_data) if x_data is not None else 0}, y={len(y_data) if y_data is not None else 0}, z={len(z_data) if z_data is not None else 0}")
                        
                        # Plotly contour data structure is different from matplotlib
                        # Plotly stores x, y as 1D arrays and z as 2D array
                        # Matplotlib needs x, y, z to be same size for tricontour, or x, y as meshgrid for contour
                        
                        if x_data is not None and y_data is not None and z_data is not None:
                            # Convert timestamps to indices if they're too large or if they're datetime objects
                            try:
                                # Try to check if x_data contains very large numbers (timestamps) or datetime objects
                                x_converted = False
                                if len(x_data) > 0:
                                    # Check if it's datetime objects or very large numbers
                                    first_x = x_data[0]
                                    if hasattr(first_x, 'timestamp'):  # datetime object
                                        x_data = list(range(len(x_data)))
                                        x_converted = True
                                        print(f"    Converted datetime x values to indices")
                                    elif isinstance(first_x, (int, float)) and first_x > 1e15:  # Large timestamp
                                        x_data = list(range(len(x_data)))
                                        x_converted = True
                                        print(f"    Converted large x values to indices")
                            except Exception as x_convert_error:
                                print(f"    X conversion failed: {x_convert_error}, using indices")
                                x_data = list(range(len(x_data)))
                                x_converted = True
                            
                            # Method 1: Try creating a meshgrid approach
                            try:
                                import numpy as np
                                
                                # If z is a 2D array, use it directly with meshgrid
                                if hasattr(z_data, '__len__') and len(z_data) > 0:
                                    if hasattr(z_data[0], '__len__'):  # 2D array
                                        # z is 2D, create appropriate x,y meshgrids
                                        x_mesh, y_mesh = np.meshgrid(
                                            np.linspace(min(x_data), max(x_data), len(z_data[0])),
                                            np.linspace(min(y_data), max(y_data), len(z_data))
                                        )
                                        contour = ax.contourf(x_mesh, y_mesh, z_data, levels=15)
                                        ax.contour(x_mesh, y_mesh, z_data, levels=15, colors='black', alpha=0.4, linewidths=0.5)
                                        self.matplotlib_figure.colorbar(contour, ax=ax)
                                        print(f"    ✅ Created meshgrid contour plot")
                                    else:
                                        # z is 1D, use scatter with color mapping
                                        # Make sure all arrays are the same length
                                        min_len = min(len(x_data), len(y_data), len(z_data))
                                        x_data = x_data[:min_len]
                                        y_data = y_data[:min_len]
                                        z_data = z_data[:min_len]
                                        
                                        scatter = ax.scatter(x_data, y_data, c=z_data, cmap='viridis', s=50)
                                        self.matplotlib_figure.colorbar(scatter, ax=ax)
                                        print(f"    ✅ Created scatter contour plot (1D z data)")
                                else:
                                    raise ValueError("Empty z data")
                                    
                            except Exception as meshgrid_error:
                                print(f"    Meshgrid approach failed: {meshgrid_error}")
                                # Method 2: Fallback to simple scatter plot
                                raise meshgrid_error
                        else:
                            raise ValueError("Missing x, y, or z data")
                            
                    except Exception as contour_error:
                        print(f"  ❌ Contour plot failed: {contour_error}")
                        # Fallback to scatter plot using available data
                        try:
                            if hasattr(trace, 'z') and trace.z is not None:
                                # Just plot z values as a line
                                z_vals = trace.z if hasattr(trace.z, '__len__') else [trace.z]
                                if len(z_vals) > 0 and hasattr(z_vals[0], '__len__'):  # 2D array, flatten it
                                    z_vals = [item for sublist in z_vals for item in sublist]
                                ax.plot(range(len(z_vals)), z_vals, label=f"Contour data", marker='o', markersize=2)
                                print(f"  📊 Used line plot fallback for contour")
                            else:
                                ax.text(0.5, 0.5, 'Contour data unavailable', 
                                       ha='center', va='center', transform=ax.transAxes)
                                print(f"  📝 Showed no data message")
                        except Exception as fallback_error:
                            print(f"  ❌ Even fallback failed: {fallback_error}")
                            ax.text(0.5, 0.5, f'Contour error:\n{str(contour_error)}', 
                                   ha='center', va='center', transform=ax.transAxes, color='red')
                        
                elif trace.type == 'heatmap':
                    try:
                        # Heatmap plots
                        im = ax.imshow(trace.z, aspect='auto', origin='lower')
                        self.matplotlib_figure.colorbar(im, ax=ax)
                        print(f"  ✅ Created heatmap")
                    except Exception as heatmap_error:
                        print(f"  ❌ Heatmap failed: {heatmap_error}")
            
            # Set labels and title
            if layout.title:
                title_text = layout.title.text if hasattr(layout.title, 'text') else str(layout.title)
                ax.set_title(title_text)
            if layout.xaxis and layout.xaxis.title:
                xlabel_text = layout.xaxis.title.text if hasattr(layout.xaxis.title, 'text') else str(layout.xaxis.title)
                ax.set_xlabel(xlabel_text)
            if layout.yaxis and layout.yaxis.title:
                ylabel_text = layout.yaxis.title.text if hasattr(layout.yaxis.title, 'text') else str(layout.yaxis.title)
                ax.set_ylabel(ylabel_text)
            
            # Add legend if there are multiple valid traces
            if len([t for t in data if t.type == 'scatter']) > 1:
                ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            
            # Adjust layout and refresh
            self.matplotlib_figure.tight_layout()
            self.canvas.draw()
            
        except Exception as e:
            print(f"Error converting Plotly to Matplotlib: {e}")
            import traceback
            traceback.print_exc()
            
            # Show error message
            self.matplotlib_figure.clear()
            ax = self.matplotlib_figure.add_subplot(111)
            ax.text(0.5, 0.5, f'Error converting plot:\n{str(e)}', 
                    horizontalalignment='center', verticalalignment='center',
                    transform=ax.transAxes, fontsize=12, color='red')
            ax.set_xticks([])
            ax.set_yticks([])
            self.canvas.draw()
    
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
                    margin: 20px auto;
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
            plot_path = self.generate_html_plot("contour", variable="tv290C")
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