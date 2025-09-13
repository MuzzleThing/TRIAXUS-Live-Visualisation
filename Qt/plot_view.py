import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from triaxus.visualizer import TriaxusVisualizer
from triaxus.data import create_plot_test_data
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QListWidget, QListWidgetItem, QSplitter)
from PySide6.QtCore import Qt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

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
        """Create the main plot display area with matplotlib canvas"""
        plot_widget = QWidget()
        plot_layout = QVBoxLayout()
        
        # Create matplotlib figure and canvas
        self.matplotlib_figure = Figure(figsize=(10, 8))
        self.canvas = FigureCanvas(self.matplotlib_figure)
        
        # Add some initial text
        ax = self.matplotlib_figure.add_subplot(111)
        ax.text(0.5, 0.5, 'Select a plot type from the menu', 
                horizontalalignment='center', verticalalignment='center',
                transform=ax.transAxes, fontsize=14)
        ax.set_xticks([])
        ax.set_yticks([])
        
        plot_layout.addWidget(self.canvas)
        plot_widget.setLayout(plot_layout)
        
        return plot_widget
    
    def plotly_to_matplotlib(self, plotly_fig):
        """Convert Plotly figure to Matplotlib figure"""
        try:
            # Clear the current figure
            self.matplotlib_figure.clear()
            
            # Extract data from Plotly figure
            data = plotly_fig.data
            layout = plotly_fig.layout
            
            # Create matplotlib subplot
            ax = self.matplotlib_figure.add_subplot(111)
            
            # Handle different plot types
            for trace in data:
                if trace.type == 'scatter':
                    # Time series and line plots
                    ax.plot(trace.x, trace.y, label=trace.name, marker='o', markersize=2)
                elif trace.type == 'contour':
                    # Contour plots
                    ax.contourf(trace.x, trace.y, trace.z)
                    ax.contour(trace.x, trace.y, trace.z, colors='black', alpha=0.4, linewidths=0.5)
                elif trace.type == 'heatmap':
                    # Heatmap plots
                    im = ax.imshow(trace.z, aspect='auto', origin='lower')
                    self.matplotlib_figure.colorbar(im, ax=ax)
                # Add more trace types as needed
            
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
            
            # Add legend if there are multiple traces
            if len(data) > 1:
                ax.legend()
            
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
        
        # Show loading message
        self.matplotlib_figure.clear()
        ax = self.matplotlib_figure.add_subplot(111)
        ax.text(0.5, 0.5, f'Loading {plot_type}...', 
                horizontalalignment='center', verticalalignment='center',
                transform=ax.transAxes, fontsize=14)
        ax.set_xticks([])
        ax.set_yticks([])
        self.canvas.draw()
        
        # Create the appropriate plot
        if plot_type == "Time Series":
            self.create_time_series_plot()
        elif plot_type == "Contour Plot":
            self.create_contour_plot()
        elif plot_type == "Depth Profile":
            self.create_depth_profile_plot()
    
    def create_time_series_plot(self):
        """Create a time series plot"""
        try:
            print("Starting time series plot creation...")
            
            # Generate test data
            print("Generating test data...")
            data = create_plot_test_data()
            print(f"Test data shape: {data.shape}")
            
            # Create plot figure using TriaxusVisualizer
            print("Creating plot figure with TriaxusVisualizer...")
            plotly_figure = self.visualizer.create_plot_figure("time_series", data)
            print("Plot figure created successfully")
            
            # Convert to matplotlib and display
            print("Converting to matplotlib...")
            self.plotly_to_matplotlib(plotly_figure)
            print("Plot creation completed")
            
        except Exception as e:
            print(f"Exception occurred: {e}")
            import traceback
            traceback.print_exc()
            
            # Show error in matplotlib
            self.matplotlib_figure.clear()
            ax = self.matplotlib_figure.add_subplot(111)
            ax.text(0.5, 0.5, f'Error creating time series plot:\n{str(e)}', 
                    horizontalalignment='center', verticalalignment='center',
                    transform=ax.transAxes, fontsize=12, color='red')
            ax.set_xticks([])
            ax.set_yticks([])
            self.canvas.draw()

    def create_contour_plot(self):
        """Create a contour plot"""
        try:
            print("Starting contour plot creation...")
            
            # Generate test data
            data = create_plot_test_data()
            print(f"Test data shape: {data.shape}")
            
            # Create plot figure using TriaxusVisualizer
            print("Creating contour plot figure...")
            plotly_figure = self.visualizer.create_plot_figure("contour", data, variable="tv290C")
            print("Contour plot figure created successfully")
            
            # Convert to matplotlib and display
            print("Converting to matplotlib...")
            self.plotly_to_matplotlib(plotly_figure)
            print("Contour plot creation completed")
            
        except Exception as e:
            print(f"Exception in contour plot: {e}")
            import traceback
            traceback.print_exc()
            
            # Show error in matplotlib
            self.matplotlib_figure.clear()
            ax = self.matplotlib_figure.add_subplot(111)
            ax.text(0.5, 0.5, f'Error creating contour plot:\n{str(e)}', 
                    horizontalalignment='center', verticalalignment='center',
                    transform=ax.transAxes, fontsize=12, color='red')
            ax.set_xticks([])
            ax.set_yticks([])
            self.canvas.draw()

    def create_depth_profile_plot(self):
        """Create a depth profile plot"""
        try:
            print("Starting depth profile plot creation...")
            
            # Generate test data
            data = create_plot_test_data()
            print(f"Test data shape: {data.shape}")
            
            # Create plot figure using TriaxusVisualizer
            print("Creating depth profile plot figure...")
            plotly_figure = self.visualizer.create_plot_figure("depth_profile", data)
            print("Depth profile plot figure created successfully")
            
            # Convert to matplotlib and display
            print("Converting to matplotlib...")
            self.plotly_to_matplotlib(plotly_figure)
            print("Depth profile plot creation completed")
            
        except Exception as e:
            print(f"Exception in depth profile plot: {e}")
            import traceback
            traceback.print_exc()
            
            # Show error in matplotlib
            self.matplotlib_figure.clear()
            ax = self.matplotlib_figure.add_subplot(111)
            ax.text(0.5, 0.5, f'Error creating depth profile plot:\n{str(e)}', 
                    horizontalalignment='center', verticalalignment='center',
                    transform=ax.transAxes, fontsize=12, color='red')
            ax.set_xticks([])
            ax.set_yticks([])
            self.canvas.draw()