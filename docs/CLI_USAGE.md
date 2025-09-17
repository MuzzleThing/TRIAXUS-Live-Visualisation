# CLI Usage Guide

This document provides comprehensive examples and detailed usage instructions for the TRIAXUS command-line interface.

## Table of Contents

- [Basic Usage](#basic-usage)
- [Plot Types](#plot-types)
- [Command Reference](#command-reference)
- [Advanced Examples](#advanced-examples)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)

## Basic Usage

### Installation and Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Make CLI executable (if needed)
chmod +x triaxus-plot
```

### General Syntax

```bash
python triaxus-plot <plot-type> [options] --output <filename>
```

### Common Options

```bash
# Output and styling
--output <file>           # Output HTML file
--theme <theme>           # Theme: oceanographic, dark, default, high_contrast
--width <pixels>          # Plot width
--height <pixels>         # Plot height
--title <text>            # Custom title
--verbose                 # Verbose output

# Data generation
--data-hours <hours>      # Hours of data to generate
--data-points <points>    # Total data points
--points-per-hour <pph>   # Points per hour
--daily-data              # Generate daily data
--day <YYYY-MM-DD>        # Specific date for daily data
```

## Plot Types

### 1) Time Series

Display ocean variables over time. Supports multiple variables and real-time updates.

#### Basic Usage

```bash
# Single variable
python triaxus-plot time-series --output basic.html

# Multiple variables
python triaxus-plot time-series --variables tv290c,sal00,sbeox0mm_l --output multi.html

# With custom styling
python triaxus-plot time-series --variables tv290c --theme dark --width 1000 --height 600 --output styled.html
```

#### Advanced Options

```bash
# Real-time monitoring
python triaxus-plot time-series --real-time --status Running --output realtime.html

# Time range filtering
python triaxus-plot time-series --time-range "2024-01-01 08:00:00,2024-01-01 18:00:00" --output filtered.html

# Depth range filtering
python triaxus-plot time-series --depth-range "20,80" --output depth_filtered.html

# Custom data generation
python triaxus-plot time-series --data-hours 3.0 --points-per-hour 15 --output custom_data.html

# Daily data
python triaxus-plot time-series --daily-data --day "2024-01-15" --output daily.html
```

#### Available Variables

Supported variables from the built-in generator:
- `tv290c`: Temperature (°C)
- `sal00`: Salinity (PSU)
- `sbeox0mm_l`: Dissolved Oxygen (μmol/L)
- `fleco_afl`: Fluorescence (mg/m³)
- `ph`: pH

### 2) Contour

2D distribution in time-depth space with interpolation and automatic fallback.

#### Basic Usage

```bash
# Temperature contour
python triaxus-plot contour --variable tv290c --output temp_contour.html

# Salinity contour
python triaxus-plot contour --variable sal00 --output salinity_contour.html

# Oxygen contour
python triaxus-plot contour --variable sbeox0mm_l --output oxygen_contour.html
```

#### Advanced Options

```bash
# With depth filtering
python triaxus-plot contour --variable tv290c --depth-range "20,80" --output filtered_contour.html

# With annotations
python triaxus-plot contour --variable tv290c --annotations --output annotated_contour.html

# Custom styling
python triaxus-plot contour --variable tv290c --theme high_contrast --width 1200 --height 800 --output styled_contour.html

# Time range filtering
python triaxus-plot contour --variable tv290c --time-range "2024-01-01 10:00:00,2024-01-01 14:00:00" --output time_filtered.html
```

#### Notes

- If interpolation fails (QHull precision error), the plot automatically falls back to a scatter representation and still outputs successfully
- This is expected behavior for certain data distributions

### 3) Depth Profile

Oceanographic convention (depth axis inverted). Supports multiple variables, depth zones, and thermocline detection.

#### Basic Usage

```bash
# Single variable profile
python triaxus-plot depth-profile --variables tv290c --output temp_profile.html

# Multi-variable profile
python triaxus-plot depth-profile --variables tv290c,sal00,sbeox0mm_l --output multi_profile.html

# Temperature and salinity
python triaxus-plot depth-profile --variables tv290c,sal00 --output temp_sal_profile.html
```

#### Advanced Options

```bash
# With depth zones
python triaxus-plot depth-profile --variables tv290c,sal00 --depth-zones --output zones_profile.html

# With thermocline detection
python triaxus-plot depth-profile --variables tv290c --thermocline --output thermocline_profile.html

# Combined features
python triaxus-plot depth-profile --variables tv290c,sal00 --depth-zones --thermocline --output advanced_profile.html

# Depth range filtering
python triaxus-plot depth-profile --variables tv290c --depth-range "10,50" --output shallow_profile.html

# Custom styling
python triaxus-plot depth-profile --variables tv290c,sal00 --theme dark --width 800 --height 1000 --output styled_profile.html
```

### 4) Map Trajectory

Display GPS trajectory and positions with configurable base maps.

#### Basic Usage

```bash
# Basic map
python triaxus-plot map --output map_basic.html

# With custom title
python triaxus-plot map --title "Oceanographic Survey" --output survey_map.html
```

#### Map Styles

```bash
# Mapbox styles (requires token in config)
python triaxus-plot map --map-style satellite --output satellite_map.html
python triaxus-plot map --map-style streets --output streets_map.html
python triaxus-plot map --map-style dark --output dark_map.html

# Offline/fallback styles
python triaxus-plot map --map-style open-street-map --output osm_map.html
```

#### Advanced Options

```bash
# Time filtering
python triaxus-plot map --time-range "2024-01-01 08:00:00,2024-01-01 18:00:00" --output filtered_map.html

# Custom dimensions
python triaxus-plot map --width 1200 --height 800 --output large_map.html

# Different themes
python triaxus-plot map --theme high_contrast --output contrast_map.html
```

#### Notes

- If a Mapbox token is configured in `configs/custom.yaml`, Mapbox styles render online
- Without a token or when using offline styles, the plot falls back to offline/`scattergeo` modes
- Trajectory direction markers are added at intervals; the count is configurable in config

## Command Reference

### Global Options

```bash
--help                    # Show help message
--version                 # Show version
--verbose                 # Verbose output
--config <file>           # Custom config file
```

### Time Series Options

```bash
--variables <vars>        # Comma-separated variables
--real-time               # Enable real-time mode
--status <status>         # Status indicator text
--time-range <range>      # Time range filter
--depth-range <range>     # Depth range filter
--data-hours <hours>      # Hours of data
--data-points <points>    # Total data points
--points-per-hour <pph>   # Points per hour
--daily-data              # Generate daily data
--day <date>              # Specific date
```

### Contour Options

```bash
--variable <var>          # Variable to plot
--depth-range <range>     # Depth range filter
--annotations             # Add annotations
--time-range <range>      # Time range filter
```

### Depth Profile Options

```bash
--variables <vars>        # Comma-separated variables
--depth-range <range>     # Depth range filter
--depth-zones             # Add depth zones
--thermocline             # Detect thermocline
```

### Map Options

```bash
--map-style <style>       # Map style
--time-range <range>      # Time range filter
```

### Common Plot Options

```bash
--output <file>           # Output HTML file
--theme <theme>           # Theme selection
--width <pixels>          # Plot width
--height <pixels>         # Plot height
--title <text>            # Custom title
```

## Advanced Examples

### Batch Processing

```bash
# Generate multiple plot types
python triaxus-plot time-series --variables tv290c --output batch_time_series.html
python triaxus-plot contour --variable tv290c --output batch_contour.html
python triaxus-plot depth-profile --variables tv290c,sal00 --output batch_profile.html
python triaxus-plot map --output batch_map.html
```

### Theme Variations

```bash
# Generate same plot with different themes
python triaxus-plot time-series --theme oceanographic --output theme_oceanographic.html
python triaxus-plot time-series --theme dark --output theme_dark.html
python triaxus-plot time-series --theme default --output theme_default.html
python triaxus-plot time-series --theme high_contrast --output theme_high_contrast.html
```

### Data Quality Testing

```bash
# Test different data scenarios
python triaxus-plot time-series --data-hours 0.5 --output quick_test.html
python triaxus-plot time-series --data-hours 24.0 --output daily_test.html
python triaxus-plot time-series --points-per-hour 5 --output sparse_test.html
python triaxus-plot time-series --points-per-hour 60 --output dense_test.html
```

### Custom Configurations

```bash
# Use custom config file
python triaxus-plot time-series --config configs/custom.yaml --output custom_config.html

# Override specific settings
python triaxus-plot map --width 1500 --height 1000 --theme dark --output large_dark_map.html
```

### Variable Combinations

```bash
# Temperature and salinity analysis
python triaxus-plot time-series --variables tv290c,sal00 --output temp_sal_ts.html
python triaxus-plot depth-profile --variables tv290c,sal00 --depth-zones --output temp_sal_profile.html

# Oxygen and fluorescence analysis
python triaxus-plot time-series --variables sbeox0mm_l,fleco_afl --output oxygen_fluorescence.html
python triaxus-plot contour --variable sbeox0mm_l --output oxygen_contour.html
```

## Configuration

### Config File Locations

The CLI loads configuration from:
1. `configs/default.yaml` (default settings)
2. `configs/custom.yaml` (optional overrides)

### Custom Configuration Example

Create `configs/custom.yaml`:

```yaml
# Theme override
theme: "dark"

# Mapbox configuration
MAPBOX:
  token: "YOUR_MAPBOX_TOKEN"

# Map plot settings
map_plot:
  defaults:
    arrow_count: 10
    style: "satellite"

# Plot dimensions
plot_dimensions:
  width: 1200
  height: 800
```

### Environment Variables

```bash
# Set Mapbox token via environment
export MAPBOX_TOKEN="your_token_here"
python triaxus-plot map --output map.html
```

## Troubleshooting

### Common Issues

#### 1. Contour Interpolation Failed

```
Warning: Interpolation failed: QH6154 QHull precision error
```

**Solution**: This is expected behavior. The plot will automatically fall back to a scatter representation and still generate successfully.

#### 2. Mapbox Token Not Provided

```
Warning: Mapbox token not found, using offline fallback
```

**Solution**: 
- Add token to `configs/custom.yaml`:
  ```yaml
  MAPBOX:
    token: "your_token_here"
  ```
- Or use offline styles: `--map-style open-street-map`

#### 3. Variable Not Found

```
Error: Variable 'nonexistent_var' not found in data
```

**Solution**: Use available variables: `tv290c`, `sal00`, `sbeox0mm_l`, `fleco_afl`, `ph`

#### 4. File Permission Errors

```
Error: Permission denied writing to output file
```

**Solution**: 
- Check file permissions
- Use different output directory
- Run with appropriate permissions

### Debug Mode

```bash
# Enable verbose output for debugging
python triaxus-plot time-series --verbose --output debug.html
```

### Help Commands

```bash
# General help
python triaxus-plot --help

# Command-specific help
python triaxus-plot time-series --help
python triaxus-plot contour --help
python triaxus-plot depth-profile --help
python triaxus-plot map --help
```

### Performance Tips

```bash
# For large datasets, use fewer points
python triaxus-plot time-series --points-per-hour 10 --output efficient.html

# For quick testing, use shorter time ranges
python triaxus-plot time-series --data-hours 0.5 --output quick_test.html
```

This comprehensive CLI guide provides detailed examples and troubleshooting information for all aspects of the TRIAXUS command-line interface.
