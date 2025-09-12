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

### CLI Usage

```bash
# Basic plot generation
python triaxus-plot time-series --output time_series.html
python triaxus-plot contour --variable tv290C --output contour.html
python triaxus-plot depth-profile --variables tv290C,sal00 --output depth_profile.html
python triaxus-plot map --output map.html

# Get help
python triaxus-plot --help
python triaxus-plot time-series --help
```

For detailed CLI examples and advanced usage, see [CLI_USAGE.md](docs/CLI_USAGE.md).

### Python API Usage

```python
from triaxus import TriaxusVisualizer
from triaxus.data import create_plot_test_data

# Initialize visualizer
viz = TriaxusVisualizer(theme="oceanographic")

# Generate sample data
data = create_plot_test_data(hours=2.0)

# Create plots programmatically
time_series_html = viz.create_time_series_plot(data, variables=["tv290C", "sal00"])
contour_html = viz.create_contour_plot(data, variable="tv290C")
depth_html = viz.create_depth_profile_plot(data, variables=["tv290C", "sal00"])
map_html = viz.create_map_plot(data)

# Get Plotly Figure for custom modifications
figure = viz.create_plot_figure("time_series", data, variables=["tv290C"])
figure.update_layout(title="Custom Title")
figure.show()
```

For detailed Python API examples and advanced usage, see [API_USAGE.md](docs/API_USAGE.md).

### Help

```bash
./triaxus-plot --help
./triaxus-plot time-series --help
```


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

## Project Structure

```
triaxus-plotter/
├── triaxus-plot                 # CLI entry (executable)
├── cli_typer.py                 # CLI implementation
├── settings.py                  # Global settings
├── requirements.txt              # Python dependencies
├── pyproject.toml               # Project configuration
├── LICENSE                      # MIT License
├── README.md                    # This file
├── triaxus/                     # Main package
│   ├── __init__.py
│   ├── visualizer.py            # Unified plotting API
│   ├── core/                    # Core functionality
│   │   ├── __init__.py
│   │   ├── base_plotter.py      # Base plotter class
│   │   ├── data_validator.py    # Data validation
│   │   ├── error_handler.py    # Error handling
│   │   └── config/             # Configuration management
│   │       ├── __init__.py
│   │       ├── manager.py       # Main config manager
│   │       ├── theme_manager.py # Theme management
│   │       ├── plot_config_manager.py
│   │       ├── data_config_manager.py
│   │       └── ui_config_manager.py
│   ├── plotters/                # Plot implementations
│   │   ├── __init__.py
│   │   ├── plotter_factory.py   # Plotter factory
│   │   ├── time_series.py       # Time series plots
│   │   ├── time_series_helpers.py
│   │   ├── depth_profile.py     # Depth profile plots
│   │   ├── depth_helpers.py
│   │   ├── contour.py           # Contour plots
│   │   ├── contour_helpers.py
│   │   ├── map_plot.py          # Map trajectory plots
│   │   └── map_helpers.py
│   ├── data/                    # Data processing
│   │   ├── __init__.py
│   │   ├── simple_data_generator.py # Test data generation
│   │   ├── processor.py         # Data processing
│   │   └── sampler.py           # Data sampling
│   └── utils/                   # Utilities
│       ├── __init__.py
│       └── html_generator.py     # HTML generation
├── configs/                     # Configuration files
│   ├── default.yaml             # Default configuration
│   ├── custom.yaml              # Custom overrides (optional)
│   ├── examples/
│   │   └── custom.yaml          # Example custom config
│   └── themes/                  # Theme definitions
│       ├── oceanographic.yaml
│       ├── dark.yaml
│       └── high_contrast.yaml
├── tests/                       # Test suite
│   ├── __init__.py
│   ├── run_tests.py             # Main test runner
│   ├── run_split_tests.py       # Alternative test runner
│   ├── test_data_quality.py     # Data quality tests
│   ├── plots/                   # Plot-specific tests
│   │   ├── __init__.py
│   │   ├── test_time_series_plots.py
│   │   ├── test_depth_profile_plots.py
│   │   └── test_contour_plots.py
│   ├── maps/                    # Map-specific tests
│   │   ├── __init__.py
│   │   ├── test_map_trajectory.py
│   │   └── test_map_view.py
│   ├── themes/                  # Theme-specific tests
│   │   ├── __init__.py
│   │   └── test_theme_functionality.py
│   └── output/                  # Generated test outputs
│       └── *.html               # Test plot files
└── docs/                        # Documentation
    ├── API_USAGE.md             # Detailed Python API reference
    └── CLI_USAGE.md             # Detailed CLI usage guide
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
