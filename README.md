# TRIAXUS Visualization System

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Plotly](https://img.shields.io/badge/Plotly-5.0+-green.svg)](https://plotly.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A modern, configuration-driven visualization toolkit for oceanographic research. It provides four primary plot types: time series, contour, depth profile, and map trajectory plots. The system integrates themes, supports Mapbox (online) and OpenStreetMap fallback (offline), and ships with a convenient Typer-based CLI.

## Key Features

- **Four Plot Types**: time series, contour, depth profile, map trajectory
- **Database Integration**: PostgreSQL support for data storage and retrieval
- **Oceanographic Data**: Realistic oceanographic data with proper geographic coordinates
- **Map Integration**: Mapbox styles with automatic offline fallbacks
- **Professional Themes**: oceanographic (default), dark, default, high_contrast
- **Real-time Visualization**: Time series with status indicators
- **Configuration-driven**: Dynaconf-based, no hard-coded values
- **High-quality Outputs**: HTML with bundled Plotly.js
- **Modern CLI**: Rich progress messages and comprehensive options
- **Clean Architecture**: Modular, maintainable codebase
- **Built-in Data Generator**: Synthetic oceanographic data including regional trajectories
- **Quality Control & Archiving**: Configurable validation rules with automated archival outputs
- **Comprehensive Testing**: Full test suite with organized output structure

## Quick Start

### Install dependencies

```bash
pip install -r requirements.txt
```

### Database Setup (Optional)

The system supports PostgreSQL database integration:

1. **Set up PostgreSQL database**:
   ```bash
   createdb triaxus_db
   export DATABASE_URL="postgresql://username:password@localhost:5432/triaxus_db"
   ```

2. **Use database in Python**:
   ```python
   from triaxus.data.database_source import DatabaseDataSource
   
   db = DatabaseDataSource()
   if db.is_available():
       # Load oceanographic data
       data = db.load_data(limit=100)
       print(f"Loaded {len(data)} oceanographic records")
       
       # Store new data
       db.store_data(data, "my_survey.csv")
   ```

3. **Database Integration with Visualization**:
   ```python
   from triaxus import TriaxusVisualizer
   from triaxus.data.database_source import DatabaseDataSource
   
   # Load data from database
   db = DatabaseDataSource()
   viz = TriaxusVisualizer()
   
   if db.is_available():
       data = db.load_data(limit=20)  # Oceanographic data
       
       # Create visualizations
       viz.create_plot('map', data, output_file='survey_map.html')
       viz.create_plot('time_series', data, output_file='timeseries.html')
   ```

### CLI Usage

```bash
# Basic plot generation
python triaxus-plot time-series --output time_series.html
python triaxus-plot contour --variable tv290c --output contour.html
python triaxus-plot depth-profile --variables tv290c,sal00 --output depth_profile.html
python triaxus-plot map --output map.html

# Regional survey examples
python triaxus-plot map --title "Oceanographic Survey" --output survey_map.html
python triaxus-plot time-series --variables tv290c,sal00 --title "Oceanographic Data" --output timeseries.html

# Get help
python triaxus-plot --help
python triaxus-plot time-series --help
python triaxus-plot list-variables  # List available variables
python triaxus-plot themes          # List available themes
python triaxus-plot examples        # Show usage examples
```

For detailed CLI examples and advanced usage, see [CLI_USAGE.md](docs/CLI_USAGE.md).

### Python API Usage

```python
from triaxus import TriaxusVisualizer
from triaxus.data.database_source import DatabaseDataSource
from triaxus.data import create_plot_test_data

# Initialize visualizer
viz = TriaxusVisualizer(theme="oceanographic")

# Option 1: Use database data
db = DatabaseDataSource()
if db.is_available():
    data = db.load_data(limit=20)  # Oceanographic data
    print(f"Loaded {len(data)} oceanographic records")
else:
    # Option 2: Generate sample data
    data = create_plot_test_data(hours=2.0)

# Create plots programmatically
time_series_html = viz.create_plot("time_series", data, variables=["tv290c", "sal00"])
contour_html = viz.create_plot("contour", data, variable="tv290c")
depth_html = viz.create_plot("depth_profile", data, variables=["tv290c", "sal00"])
map_html = viz.create_plot("map", data, title="Oceanographic Survey")

# Get Plotly Figure for custom modifications
figure = viz.create_plot_figure("time_series", data, variables=["tv290c"])
figure.update_layout(title="Custom Oceanographic Analysis")
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
- Variable names: Use existing columns from the generator, e.g., `tv290c`, `sal00`, `sbeox0mm_l`, `fleco_afl`, `ph`.
- Custom size not applying (maps): Passing `--width`/`--height` works; the logic prioritizes CLI dimensions over defaults.

## Project Structure

```
triaxus-plotter/
├── triaxus-plot                           # CLI entry point (executable)
├── cli_typer.py                           # CLI implementation
├── settings.py                            # Global settings
├── requirements.txt                       # Python dependencies
├── pyproject.toml                         # Project configuration
├── LICENSE                                # MIT License
├── README.md                              # Project documentation
├── configs/                               # Configuration files
│   ├── default.yaml                       # Default configuration (do not edit)
│   ├── custom.yaml                        # Custom overrides (optional)
│   ├── examples/                          # Configuration examples
│   │   ├── custom.example.yaml            # Example for user overrides
│   │   └── database.example.yaml          # Example for database settings
│   └── themes/                            # Theme definitions
│       ├── oceanographic.yaml             # Oceanographic theme
│       ├── dark.yaml                      # Dark theme
│       └── high_contrast.yaml             # High contrast theme
├── docs/                                  # Documentation
│   ├── API_USAGE.md                       # Detailed Python API reference
│   ├── CLI_USAGE.md                       # Detailed CLI usage guide
│   └── DATABASE_USAGE.md                  # Database integration guide
├── env.example                            # Environment variable template
├── tests/                                 # Test suite
│   ├── __init__.py                        # Test package init
│   ├── test_runner.py                     # Main test runner
│   ├── test_runner_quick.py               # Quick test runner
│   ├── test_comprehensive.py              # Comprehensive E2E tests
│   ├── test_database.py                   # Database test runner
│   ├── unit/                              # Unit tests
│   │   ├── test_models_and_mappers.py    # Models/mappers tests
│   │   ├── test_data_quality.py           # Data quality tests
│   │   ├── database/                      # Database-specific tests
│   │   │   ├── test_connectivity.py       # DB connectivity tests
│   │   │   ├── test_schema.py             # DB schema tests
│   │   │   ├── test_mapping.py            # Data mapping tests
│   │   │   └── test_operations.py         # DB operations tests
│   │   ├── plots/                         # Plot component tests
│   │   └── themes/                        # Theme tests
│   ├── integration/                       # Integration tests
│   │   ├── test_integration.py            # DB integration tests
│   │   └── maps/                          # Map visualization tests
│   │       └── test_map_trajectory.py     # Map trajectory tests
│   └── output/                            # Generated test outputs (HTML)
├── triaxus/                               # Main package
│   ├── __init__.py                        # Package init
│   ├── visualizer.py                      # Unified plotting API
│   ├── core/                              # Core functionality
│   │   ├── __init__.py                    # Subpackage init
│   │   ├── base_plotter.py                # Abstract plotter base class
│   │   ├── data_validator.py              # Input data validation
│   │   ├── error_handler.py               # Plotting error handling
│   │   └── config/                        # Configuration managers
│   │       ├── __init__.py                # Subpackage init
│   │       ├── manager.py                 # Main config manager (Dynaconf)
│   │       ├── theme_manager.py           # Theme config manager
│   │       ├── plot_config_manager.py     # Plot config manager
│   │       ├── data_config_manager.py     # Data config manager
│   │       └── ui_config_manager.py       # UI config manager
│   ├── data/                              # Data processing
│   │   ├── __init__.py                    # Subpackage init
│   │   ├── simple_data_generator.py       # Synthetic data generator
│   │   ├── processor.py                   # Data processing utilities
│   │   ├── sampler.py                     # Sampling utilities
│   │   └── database_source.py             # Database data source
│   ├── database/                          # Database integration
│   │   ├── __init__.py                    # Subpackage init
│   │   ├── config_manager.py              # DB configuration manager
│   │   ├── connection_manager.py          # DB engine/session management
│   │   ├── initializer.py                 # Schema initialization
│   │   ├── mappers.py                     # DataFrame↔ORM mappers
│   │   ├── models.py                      # SQLAlchemy ORM models
│   │   ├── repositories.py                # Repository access layer
│   │   └── sql/                           # SQL assets
│   │       └── init_database.sql          # SQL initialization script
│   ├── plotters/                          # Plot implementations
│   │   ├── __init__.py                    # Subpackage init
│   │   ├── plotter_factory.py             # Plotter factory
│   │   ├── time_series.py                 # Time series plotter
│   │   ├── time_series_helpers.py         # Time series helpers
│   │   ├── depth_profile.py               # Depth profile plotter
│   │   ├── depth_helpers.py               # Depth helpers
│   │   ├── contour.py                     # Contour plotter
│   │   ├── contour_helpers.py             # Contour helpers
│   │   ├── map_plot.py                    # Map trajectory plotter
│   │   └── map_helpers.py                 # Map helpers
│   └── utils/                             # Utilities
│       ├── __init__.py                    # Subpackage init
│       └── html_generator.py              # HTML writer for plots
└── triaxus-plot                           # CLI entry point (executable)
```

## Quick Verification

```bash
# Minimal end-to-end checks
python triaxus-plot time-series --output demo_time_series.html
python triaxus-plot contour --variable tv290c --output demo_contour.html
python triaxus-plot map --output demo_map.html
python triaxus-plot depth-profile --variables tv290c,sal00 --output demo_depth.html
```

## Tests

```bash
# Run the full test suite (generates HTML into tests/output/)
python tests/test_runner.py

# Run quick tests (database connectivity and basic operations)
python tests/test_runner_quick.py

# Run comprehensive E2E tests
python tests/test_comprehensive.py

# Run database-specific tests
python tests/test_database.py

# Run specific test modules
python tests/integration/maps/test_map_trajectory.py  # Map trajectory tests
python tests/integration/test_integration.py          # Database integration tests
python tests/unit/test_models_and_mappers.py          # Models/mappers tests
```

### Test Organization

- **`tests/unit/`**: Unit tests for individual components
- **`tests/integration/`**: Integration tests for system components
- **`tests/output/`**: All generated HTML test files
- **`tests/test_runner.py`**: Main test runner with comprehensive coverage
- **`tests/test_runner_quick.py`**: Quick test runner for development
- **`tests/test_comprehensive.py`**: End-to-end comprehensive tests
- **`tests/test_database.py`**: Dedicated database testing

### Test Features

- **Oceanographic Data**: Map tests use realistic oceanographic data
- **Database Integration**: Full database functionality testing
- **All Plot Types**: Complete coverage of time series, contour, depth profile, and map plots
- **Theme Testing**: All themes (oceanographic, dark, default, high_contrast)
- **Data Quality**: Various data scenarios and edge cases
- **Output Validation**: All HTML files generated in organized structure

## License

MIT License. See `LICENSE` for details.

