# plot_view.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QListWidget, QListWidgetItem, QSplitter)
from PySide6.QtCore import Qt

class PlotView(QWidget):
    def __init__(self):
        super().__init__()
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
        """Create the main plot display area"""
        plot_widget = QWidget()
        plot_layout = QVBoxLayout()
        
        # Default content
        self.plot_label = QLabel("Select a plot type from the menu")
        self.plot_label.setAlignment(Qt.AlignCenter)
        self.plot_label.setStyleSheet("font-size: 16px; color: #666;")
        
        plot_layout.addWidget(self.plot_label)
        plot_widget.setLayout(plot_layout)
        
        return plot_widget
    
    def on_plot_type_selected(self, item):
        """Handle plot type selection"""
        plot_type = item.text()
        self.plot_label.setText(f"Selected: {plot_type}")
        
        # Here you would implement the actual plot creation
        # For example:
        if plot_type == "Time Series":
            self.create_time_series_plot()
        elif plot_type == "Contour Plot":
            self.create_contour_plot()
        elif plot_type == "Depth Profile":
            self.create_depth_profile_plot()
        # ... etc
    
    def create_time_series_plot(self):
        """Create a time series plot"""
        # TODO:
        self.plot_label.setText("Time Series Plot\n(Implementation goes here)")
    
    def create_contour_plot(self):
        """Create a contour plot"""
        # TODO:
        self.plot_label.setText("Contour Plot\n(Implementation goes here)")
    
    def create_depth_profile_plot(self):
        """Create a depth profile plot"""
        # TODO:
        self.plot_label.setText("Depth Profile Plot\n(Implementation goes here)")
    
    def update_plot(self, data):
        """Method to update the plot with new data"""
        # TODO:
        pass