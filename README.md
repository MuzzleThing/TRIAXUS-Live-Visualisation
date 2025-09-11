# TRIAXUS Visualization System

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Plotly](https://img.shields.io/badge/Plotly-5.0+-green.svg)](https://plotly.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A modern, configuration-driven visualization toolkit for oceanographic research. It provides four primary plot types: time series, contour, depth profile, and map trajectory plots. The system integrates themes, supports Mapbox (online) and OpenStreetMap fallback (offline), and ships with a convenient Typer-based CLI.

## Key Features

- Four plot types: time series, contour, depth profile, map trajectory
- Map integration: Mapbox styles with automatic offline fallbacks
- Professional themes: oceanographic (default), dark, default, high_contrast
- Real-time visualization mode and status indicator (time series)
- Configuration-driven architecture (Dynaconf), no hard-coded values
- High-quality HTML outputs with bundled Plotly.js
- Modern CLI with rich progress messages and examples
- Clean, modular architecture; reduced duplication; maintainable codebase
- Built-in synthetic data generator (including Australia region trajectories)

## Quick Start

### Install dependencies

```bash
pip install -r requirements.txt
```

### Basic usage

```bash
# Time series
python triaxus-plot time-series --output time_series.html

# Contour (use existing column names, e.g. tv290C)
python triaxus-plot contour --variable tv290C --output contour.html

# Depth profile
python triaxus-plot depth-profile --variables tv290C,sal00 --output depth_profile.html

# Map (Mapbox if token available, otherwise fallback)
python triaxus-plot map --output map.html
```

### Help

```bash
./triaxus-plot --help
./triaxus-plot time-series --help
```

## Plot Types

### 1) Time Series
Display ocean variables over time. Supports multiple variables and real-time updates.

```bash
# Basic
./triaxus-plot time-series --output basic.html

# Multi-variable (use available columns)
./triaxus-plot time-series --variables tv290C,sal00,sbeox0Mm_L --output multi.html

# Real-time monitoring
./triaxus-plot time-series --real-time --status Running --output realtime.html
```

Notes:
- Supported example columns from the built-in generator: `tv290C`, `sal00`, `sbeox0Mm_L`, `flECO-AFL`, `ph`
- Common options: `--time-range "YYYY-MM-DD HH:MM:SS,YYYY-MM-DD HH:MM:SS"`, `--depth-range "min,max"`, `--theme`, `--width`, `--height`

### 2) Contour
2D distribution in time-depth space with interpolation and automatic fallback.

```bash
# Temperature contour (using available column)
./triaxus-plot contour --variable tv290C --output temp_contour.html

# With depth range
./triaxus-plot contour --variable tv290C --depth-range "20,80" --output temp_contour_filtered.html
```

Notes:
- If interpolation fails (QHull precision), the plot automatically falls back to a scatter representation and still outputs successfully.

### 3) Depth Profile
Oceanographic convention (depth axis inverted). Supports multiple variables, depth zones, and thermocline detection.

```bash
# Basic
./triaxus-plot depth-profile --variables tv290C --output temp_profile.html

# Multi-variable
./triaxus-plot depth-profile --variables tv290C,sal00,sbeox0Mm_L --output multi_profile.html

# With depth zones
./triaxus-plot depth-profile --variables tv290C,sal00 --depth-zones --output zones_profile.html

# With thermocline detection
./triaxus-plot depth-profile --variables tv290C --thermocline --output thermocline_profile.html
```

### 4) Map Trajectory
Display GPS trajectory and positions with configurable base maps.

```bash
# Basic
./triaxus-plot map --output map_basic.html

# Time-filtered
./triaxus-plot map --time-range "2024-01-01 08:00:00,2024-01-01 18:00:00" --output map_filtered.html

# Specific styles (if Mapbox token configured)
./triaxus-plot map --map-style satellite-streets --output map_satellite_streets.html
./triaxus-plot map --map-style satellite --output map_satellite.html
./triaxus-plot map --map-style streets --output map_streets.html
./triaxus-plot map --map-style dark --output map_dark.html

# Offline fallback / OSM-like
./triaxus-plot map --map-style open-street-map --output map_osm_offline.html
```

Notes:
- If a Mapbox token is configured, Mapbox styles render online.
- Without a token or when using offline styles, the plot falls back to offline/`scattergeo` modes.
- Trajectory direction markers (simple triangle markers) are added at intervals; the count is configurable in config.

## CLI Reference (selected)

- Common options: `--output`, `--theme {oceanographic,dark,default,high_contrast}`, `--width`, `--height`, `--title`, `--verbose`
- Time series data generation: `--daily-data`, `--day`, `--data-hours`, `--data-points`, `--points-per-hour`
- Contour: `--variable`, `--depth-range`, optional `--annotations`
- Depth profile: `--variables`, `--depth-range`, `--depth-zones`, `--thermocline`
- Map: `--time-range`, `--map-style`

Run help for each command to see the full list.

## Themes

Available themes:
- oceanographic (default)
- dark
- default
- high_contrast

Examples:

```bash
./triaxus-plot time-series --theme dark --output dark_plot.html
./triaxus-plot time-series --theme high_contrast --output contrast_plot.html
```

## Configuration

The system uses Dynaconf to load `configs/default.yaml` and optionally a custom override (e.g., `configs/custom.yaml`). Top-level keys are uppercased by Dynaconf.

Highlights:
- Plot defaults (dimensions, styles)
- Themes and variable colors
- Map settings (Mapbox token, default style, offline styles)
- Data generation defaults (hours, points, seed)

Example overrides (`configs/custom.yaml`):

```yaml
# Theme override
theme: "dark"

# Map overrides (example keys; see default.yaml for full structure)
MAPBOX:
  token: "YOUR_MAPBOX_TOKEN"

map_plot:
  defaults:
    arrow_count: 10
```

## Troubleshooting

- Contour interpolation failed: This is expected sometimes; the plot will fall back to a scatter representation and still be generated.
- Mapbox token not provided: The CLI will warn and use offline/scattergeo fallback.
- Variable names: Use existing columns from the generator, e.g., `tv290C`, `sal00`, `sbeox0Mm_L`, `flECO-AFL`, `ph`.
- Custom size not applying (maps): Passing `--width`/`--height` works; the logic prioritizes CLI dimensions over defaults.

## Project Structure (high level)

```
triaxus-plotter/
├── triaxus-plot                 # CLI entry (executable)
├── cli_typer.py                 # CLI implementation
├── triaxus/
│   ├── visualizer.py            # Unified plotting API
│   ├── plotters/
│   │   ├── time_series.py
│   │   ├── depth_profile.py
│   │   ├── contour.py
│   │   ├── map_plot.py
│   │   └── map_helpers.py
│   └── core/config/             # Config managers (Dynaconf-backed)
├── configs/
│   ├── default.yaml
│   └── custom.yaml (optional)
└── docs/
    └── README_EN.md             # This file
```

## Quick Verification

```bash
# Minimal end-to-end checks
python triaxus-plot time-series --output demo_time_series.html
python triaxus-plot contour --variable tv290C --output demo_contour.html
python triaxus-plot map --output demo_map.html
python triaxus-plot depth-profile --variables tv290C,sal00 --output demo_depth.html
```

## Tests

```bash
# Run the full test suite (generates HTML into tests/output/)
python tests/run_tests.py

# Run split tests (same coverage, separate imports)
python tests/run_split_tests.py
```

Notes:
- Tests are organized under `tests/plots/`, `tests/maps/`, and `tests/themes/`.
- Outputs are written to `tests/output/` and can be opened directly in a browser.

## License

MIT License. See `LICENSE` for details.
