# Python API Reference

This document provides comprehensive examples and detailed usage instructions for the TRIAXUS Python API.

## Table of Contents

- [TriaxusVisualizer Class](#triaxusvisualizer-class)
- [Core Methods](#core-methods)
- [Data Generation](#data-generation)
- [Advanced Usage Examples](#advanced-usage-examples)
- [Error Handling](#error-handling)
- [Best Practices](#best-practices)

## TriaxusVisualizer Class

The main interface for programmatic plot creation.

### Initialization

```python
from triaxus import TriaxusVisualizer

# Initialize with default theme
viz = TriaxusVisualizer()

# Initialize with custom theme
viz = TriaxusVisualizer(theme="dark")

# Initialize with custom config file
viz = TriaxusVisualizer(config_path="path/to/custom.yaml", theme="oceanographic")

# Available themes: oceanographic, dark, default, high_contrast
```

### Basic Usage

```python
from triaxus.data import create_plot_test_data

# Generate sample data
data = create_plot_test_data(hours=2.0)

# Create all plot types
time_series_html = viz.create_time_series_plot(data, variables=["tv290c", "sal00"])
contour_html = viz.create_contour_plot(data, variable="tv290c")
depth_html = viz.create_depth_profile_plot(data, variables=["tv290c", "sal00"])
map_html = viz.create_map_plot(data)
```

## Core Methods

### Plot Creation Methods

#### Time Series Plot

```python
# Basic time series
html = viz.create_time_series_plot(
    data, 
    variables=["tv290c"],
    output_file="time_series.html"
)

# Multi-variable time series
html = viz.create_time_series_plot(
    data, 
    variables=["tv290c", "sal00", "sbeox0mm_l"],
    output_file="multi_time_series.html",
    title="Oceanographic Variables",
    width=1000,
    height=600
)

# Real-time monitoring
html = viz.create_time_series_plot(
    data, 
    variables=["tv290c"],
    output_file="realtime.html",
    real_time=True,
    status="Running"
)
```

#### Contour Plot

```python
# Basic contour
html = viz.create_contour_plot(
    data, 
    variable="tv290c",
    output_file="contour.html"
)

# Contour with depth filtering
html = viz.create_contour_plot(
    data, 
    variable="tv290c",
    output_file="filtered_contour.html",
    depth_range=[20, 80],
    title="Temperature Contour (20-80m)"
)

# Contour with annotations
html = viz.create_contour_plot(
    data, 
    variable="tv290c",
    output_file="annotated_contour.html",
    annotations=True
)
```

#### Depth Profile Plot

```python
# Single variable profile
html = viz.create_depth_profile_plot(
    data, 
    variables=["tv290c"],
    output_file="temp_profile.html"
)

# Multi-variable profile
html = viz.create_depth_profile_plot(
    data, 
    variables=["tv290c", "sal00", "sbeox0mm_l"],
    output_file="multi_profile.html",
    title="Multi-Variable Depth Profile"
)

# Profile with depth zones
html = viz.create_depth_profile_plot(
    data, 
    variables=["tv290C", "sal00"],
    output_file="zones_profile.html",
    depth_zones=True
)

# Profile with thermocline detection
html = viz.create_depth_profile_plot(
    data, 
    variables=["tv290c"],
    output_file="thermocline_profile.html",
    thermocline=True
)
```

#### Map Plot

```python
# Basic map
html = viz.create_map_plot(
    data, 
    output_file="map.html"
)

# Map with time filtering
html = viz.create_map_plot(
    data, 
    output_file="filtered_map.html",
    time_range=["2024-01-01 08:00:00", "2024-01-01 18:00:00"]
)

# Map with specific style (requires Mapbox token)
html = viz.create_map_plot(
    data, 
    output_file="satellite_map.html",
    map_style="satellite"
)

# Available map styles: satellite, streets, dark, open-street-map
```

### Figure Object Creation

Get Plotly Figure objects for custom modifications:

```python
# Get Plotly Figure
figure = viz.create_plot_figure("time_series", data, variables=["tv290c"])

# Customize layout
figure.update_layout(
    title="Custom Oceanographic Plot",
    xaxis_title="Time (UTC)",
    yaxis_title="Temperature (°C)",
    font=dict(size=14),
    plot_bgcolor="white"
)

# Add custom annotations
figure.add_annotation(
    x="2024-01-01 12:00:00",
    y=25,
    text="Thermocline Layer",
    showarrow=True,
    arrowhead=2,
    arrowsize=1,
    arrowwidth=2,
    arrowcolor="red"
)

# Add shapes (e.g., depth zones)
figure.add_shape(
    type="rect",
    x0="2024-01-01 10:00:00",
    x1="2024-01-01 14:00:00",
    y0=20,
    y1=50,
    fillcolor="lightblue",
    opacity=0.3,
    line=dict(width=0)
)

# Save or display
figure.write_html("custom_plot.html")
figure.show()
```

### Utility Methods

#### Theme Management

```python
# Get available themes
available_themes = viz.get_available_themes()
print(available_themes)  # ['oceanographic', 'dark', 'default', 'high_contrast']

# Change theme dynamically
viz.set_theme("dark")
dark_plot = viz.create_time_series_plot(data, output_file="dark_plot.html")

viz.set_theme("high_contrast")
contrast_plot = viz.create_time_series_plot(data, output_file="contrast_plot.html")
```

#### Plot Information

```python
# Get available plot types
plot_types = viz.get_available_plot_types()
print(plot_types)  # ['time_series', 'contour', 'depth_profile', 'map']

# Get plot capabilities
capabilities = viz.get_plot_capabilities("time_series")
print(capabilities)  # {'multi_variable': True, 'real_time': True, ...}

# Validate data for specific plot type
is_valid = viz.validate_data(data, "time_series")
print(f"Data valid for time series: {is_valid}")
```

#### Statistics and Analysis

```python
# Get plot statistics
stats = viz.get_plot_statistics(data, "time_series")
print(stats)
# {
#     'data_points': 120,
#     'variables': ['tv290c', 'sal00'],
#     'time_range': ['2024-01-01 08:00:00', '2024-01-01 10:00:00'],
#     'depth_range': [0.5, 99.5],
#     'statistics': {...}
# }
```

## Data Generation

### Built-in Data Generators

```python
from triaxus.data import (
    create_plot_test_data,
    create_daily_plot_data,
    create_quick_plot_data,
    create_map_trajectory_data
)

# Generate comprehensive test data
data = create_plot_test_data(
    hours=2.0,
    points_per_hour=10,
    seed=42  # For reproducible results
)

# Generate daily data for specific date
daily_data = create_daily_plot_data(date="2024-01-01")

# Generate quick data (1 hour, 20 points)
quick_data = create_quick_plot_data()

# Generate map trajectory data
map_data = create_map_trajectory_data(
    start_lat=-33.8, start_lon=151.2,
    end_lat=-34.0, end_lon=151.4,
    hours=1.0,
    points_per_hour=5
)
```

### Available Variables

The data generator creates the following oceanographic variables:

- `tv290c`: Temperature (°C)
- `sal00`: Salinity (PSU)
- `sbeox0mm_l`: Dissolved Oxygen (μmol/L)
- `fleco_afl`: Fluorescence (mg/m³)
- `ph`: pH

### Custom Data Integration

```python
import pandas as pd
from datetime import datetime, timedelta

# Create custom dataset
def create_custom_data():
    times = pd.date_range('2024-01-01', periods=100, freq='1min')
    depths = [i * 0.5 for i in range(1, 201)]  # 0.5m to 100m
    
    data = []
    for time in times:
        for depth in depths:
            data.append({
                'datetime': time,
                'depth': depth,
                'tv290c': 20 + depth * 0.1 + np.random.normal(0, 0.5),
                'sal00': 35 + np.random.normal(0, 0.1)
            })
    
    return pd.DataFrame(data)

# Use custom data
custom_data = create_custom_data()
plot_html = viz.create_time_series_plot(custom_data, variables=["tv290c"])
```

## Advanced Usage Examples

### Custom Dashboard

```python
# Create a dashboard with multiple plots
dashboard_html = viz.create_dashboard(
    data,
    plots=[
        {
            "type": "time_series", 
            "variables": ["tv290C"],
            "title": "Temperature Over Time"
        },
        {
            "type": "contour", 
            "variable": "tv290C",
            "title": "Temperature Contour"
        },
        {
            "type": "depth_profile", 
            "variables": ["tv290C", "sal00"],
            "title": "Depth Profile"
        },
        {
            "type": "map",
            "title": "Trajectory Map"
        }
    ],
    output_file="dashboard.html",
    layout="grid",
    title="Oceanographic Dashboard"
)
```

### Batch Processing

```python
# Process multiple datasets
datasets = [
    create_plot_test_data(hours=1.0),
    create_plot_test_data(hours=2.0),
    create_plot_test_data(hours=3.0)
]

themes = ["oceanographic", "dark", "high_contrast"]

for i, (data, theme) in enumerate(zip(datasets, themes)):
    viz.set_theme(theme)
    
    # Create multiple plot types for each dataset
    plots = {
        "time_series": viz.create_time_series_plot(
            data, 
            output_file=f"batch_{i+1}_time_series.html",
            title=f"Dataset {i+1} - Time Series"
        ),
        "contour": viz.create_contour_plot(
            data, 
            variable="tv290c",
            output_file=f"batch_{i+1}_contour.html",
            title=f"Dataset {i+1} - Contour"
        ),
        "map": viz.create_map_plot(
            data, 
            output_file=f"batch_{i+1}_map.html",
            title=f"Dataset {i+1} - Map"
        )
    }
    
    print(f"Created {len(plots)} plots for dataset {i+1}")
```

### Interactive Plot Development

```python
# Create interactive development workflow
def interactive_plot_development():
    data = create_plot_test_data(hours=1.0)
    
    # Start with basic plot
    figure = viz.create_plot_figure("time_series", data, variables=["tv290c"])
    
    # Iteratively improve
    figure.update_layout(title="Temperature Analysis")
    figure.show()
    
    # Add more variables
    figure = viz.create_plot_figure("time_series", data, variables=["tv290C", "sal00"])
    figure.update_layout(title="Temperature and Salinity")
    figure.show()
    
    # Customize styling
    figure.update_traces(
        line=dict(width=3),
        marker=dict(size=6)
    )
    
    # Final save
    figure.write_html("final_analysis.html")
    return figure

# Run interactive development
final_figure = interactive_plot_development()
```

### Configuration Management

```python
# Load custom configuration
viz_custom = TriaxusVisualizer(config_path="configs/custom.yaml")

# Access configuration values
config = viz_custom.config_manager.get_plot_config("time_series")
print(f"Default width: {config['width']}")
print(f"Default height: {config['height']}")

# Update configuration programmatically
viz_custom.config_manager.set_plot_dimensions(width=1200, height=800)
```

## Error Handling

### Basic Error Handling

```python
try:
    html = viz.create_contour_plot(data, variable="nonexistent_var")
except ValueError as e:
    print(f"Plot creation failed: {e}")
    # Handle error appropriately
```

### Comprehensive Error Handling

```python
def safe_plot_creation(viz, plot_type, data, **kwargs):
    """Safely create plots with comprehensive error handling"""
    try:
        # Validate data first
        if not viz.validate_data(data, plot_type):
            raise ValueError(f"Data validation failed for {plot_type}")
        
        # Create plot
        if plot_type == "time_series":
            return viz.create_time_series_plot(data, **kwargs)
        elif plot_type == "contour":
            return viz.create_contour_plot(data, **kwargs)
        elif plot_type == "depth_profile":
            return viz.create_depth_profile_plot(data, **kwargs)
        elif plot_type == "map":
            return viz.create_map_plot(data, **kwargs)
        else:
            raise ValueError(f"Unknown plot type: {plot_type}")
            
    except ValueError as e:
        print(f"Value error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

# Usage
result = safe_plot_creation(viz, "time_series", data, variables=["tv290c"])
if result:
    print("Plot created successfully")
else:
    print("Plot creation failed")
```

### Fallback Strategies

```python
def create_plot_with_fallback(viz, plot_type, data, **kwargs):
    """Create plot with fallback strategies"""
    try:
        # Try primary plot type
        return viz.create_plot_figure(plot_type, data, **kwargs)
    except Exception as e:
        print(f"Primary plot failed: {e}")
        
        # Fallback to scatter plot for contour
        if plot_type == "contour":
            try:
                print("Attempting scatter fallback...")
                return viz.create_plot_figure("time_series", data, **kwargs)
            except Exception as fallback_error:
                print(f"Fallback also failed: {fallback_error}")
        
        # Return None if all attempts fail
        return None
```

## Best Practices

### Performance Optimization

```python
# Reuse visualizer instance
viz = TriaxusVisualizer(theme="oceanographic")

# Batch operations
plots_to_create = [
    ("time_series", {"variables": ["tv290C"]}),
    ("contour", {"variable": "tv290C"}),
    ("depth_profile", {"variables": ["tv290C", "sal00"]}),
    ("map", {})
]

for plot_type, params in plots_to_create:
    html = viz.create_plot(plot_type, data, **params)
```

### Memory Management

```python
# Clear large datasets when done
large_data = create_plot_test_data(hours=24.0)
html = viz.create_time_series_plot(large_data, variables=["tv290c"])
del large_data  # Free memory

# Use generators for very large datasets
def data_generator():
    for hour in range(24):
        yield create_plot_test_data(hours=1.0, start_hour=hour)

for i, hour_data in enumerate(data_generator()):
    html = viz.create_time_series_plot(hour_data, variables=["tv290c"])
    # Process each hour's data
```

### Code Organization

```python
class OceanographicAnalyzer:
    """Example class showing how to organize TRIAXUS usage"""
    
    def __init__(self, theme="oceanographic"):
        self.viz = TriaxusVisualizer(theme=theme)
        self.data = None
    
    def load_data(self, hours=2.0):
        """Load oceanographic data"""
        self.data = create_plot_test_data(hours=hours)
        return self.data
    
    def analyze_temperature(self):
        """Analyze temperature patterns"""
        if self.data is None:
            raise ValueError("No data loaded")
        
        # Time series analysis
        time_series = self.viz.create_time_series_plot(
            self.data, variables=["tv290c"]
        )
        
        # Contour analysis
        contour = self.viz.create_contour_plot(
            self.data, variable="tv290c"
        )
        
        return {
            "time_series": time_series,
            "contour": contour
        }
    
    def create_report(self, output_dir="reports"):
        """Create comprehensive analysis report"""
        analysis = self.analyze_temperature()
        
        # Save all plots
        for plot_type, html in analysis.items():
            with open(f"{output_dir}/{plot_type}.html", "w") as f:
                f.write(html)
        
        return analysis

# Usage
analyzer = OceanographicAnalyzer(theme="dark")
analyzer.load_data(hours=3.0)
report = analyzer.create_report()
```

This comprehensive API documentation provides detailed examples for all aspects of the TRIAXUS Python API, from basic usage to advanced patterns and best practices.
