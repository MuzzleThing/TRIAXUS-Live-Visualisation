# TRIAXUS Visualization System

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Plotly](https://img.shields.io/badge/Plotly-5.0+-green.svg)](https://plotly.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A modern, configuration-driven visualization toolkit for oceanographic research. It provides four primary plot types: time series, contour, depth profile, and map trajectory plots. The system integrates themes, supports Mapbox (online) and OpenStreetMap fallback (offline), and ships with a convenient Typer-based CLI.

## Key Features

- **Four Plot Types**: time series, contour, depth profile, map trajectory
- **Database Integration**: PostgreSQL support for data storage and retrieval
- **Oceanographic Data**: Complete oceanographic data including Temperature, Salinity, Oxygen, Fluorescence, and pH with proper geographic coordinates
- **Map Integration**: Mapbox styles with automatic offline fallbacks
- **Professional Themes**: oceanographic (default), dark, default, high_contrast
- **Real-time Visualization**: End-to-end real-time pipeline (simulator → processor → API → web dashboard)
- **Configuration-driven**: Dynaconf-based, no hard-coded values
- **High-quality Outputs**: HTML with bundled Plotly.js
- **Modern CLI**: Rich progress messages and comprehensive options
- **Clean Architecture**: Modular, maintainable codebase
- **Built-in Data Generator**: Synthetic oceanographic data including regional trajectories
- **Quality Control & Archiving**: Configurable validation rules with automated archival outputs
- **Comprehensive Testing**: Full test suite with organized output structure

## Quick Start

### Install dependencies (with venv)

```bash
# Create and activate virtual environment (macOS/Linux)
python3 -m venv .venv
source .venv/bin/activate

# Or on Windows (PowerShell)
# python -m venv .venv
# .venv\\Scripts\\Activate.ps1

# Install project dependencies into the venv
pip install -r requirements.txt
```

### Real-time Quick Start

One-click start the full real-time pipeline (data simulator, CNV realtime processor, API server) inside the activated venv:

```bash
python scripts/start_realtime_pipeline.py --config configs/realtime_test.yaml
```

Then open the web dashboard:

```
http://127.0.0.1:8080/
```

Notes:
- Default refresh interval: 1 minute (configurable from the dashboard)
- Time granularity options: 5m, 15m, 30m, 1h, 6h, 12h, 24h
- Timezone support: Browser Local, UTC, Australia/Sydney, Asia/Shanghai, Australia/Perth
- Data filtering uses UTC; display is in local time on the frontend
- Supports all 5 oceanographic variables: Temperature, Salinity, Oxygen, Fluorescence, pH
- Variable-based plot selection: View all variables or filter by specific variable
- Three plot types per variable: Time Series, Depth Profile, and Contour plots

Stop the pipeline (in the same activated venv):

```bash
python scripts/stop_realtime_pipeline.py
```

Manual (alternative) start for debugging:

```bash
# 1) Start the simulator (writes live_*.cnv)
python live_data_feed_simulation/simulation.py --output testdataQC/live_realtime_demo.cnv --interval 5

# 2) Start the realtime processor
python -m triaxus.data.cnv_realtime_processor --config configs/realtime_test.yaml

# 3) Start the API server (serves dashboard and JSON endpoints)
python realtime/realtime_api_server.py --port 8080
```

Key configuration: `configs/realtime_test.yaml`

![Dashboard](pictures/realtime_dashboard.jpeg)

### Database Setup

For full installation and configuration, see the Database sections in `docs/CONFIGURATION_GUIDE.md` (sections 4–6).

Quick install (macOS/Linux):

```bash
# macOS (Homebrew)
brew install postgresql@14 && brew services start postgresql@14

# Linux (Debian/Ubuntu)
sudo apt-get update && sudo apt-get install -y postgresql postgresql-contrib
sudo systemctl enable postgresql && sudo systemctl start postgresql
```

Initialize a database (example; adjust creds as needed):

```bash
createdb triaxus_db
export DATABASE_URL="postgresql://username:password@localhost:5432/triaxus_db"
psql "$DATABASE_URL" -f triaxus/database/sql/init_database.sql
```

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

See more details in `docs/CONFIGURATION_GUIDE.md`.

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
python triaxus-plot depth-profile --variables tv290c,sal00,sbeox0mm_l,fleco_afl,ph --output depth_profile.html
python triaxus-plot map --output map.html

# Regional survey examples with all variables
python triaxus-plot map --title "Oceanographic Survey" --output survey_map.html
python triaxus-plot time-series --variables tv290c,sal00,sbeox0mm_l,fleco_afl,ph --title "Oceanographic Data" --output timeseries.html

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

# Create plots programmatically with all variables
time_series_html = viz.create_plot("time_series", data, variables=["tv290c", "sal00", "sbeox0mm_l", "fleco_afl", "ph"])
contour_html = viz.create_plot("contour", data, variable="tv290c")
depth_html = viz.create_plot("depth_profile", data, variables=["tv290c", "sal00", "sbeox0mm_l", "fleco_afl", "ph"])
map_html = viz.create_plot("map", data, title="Oceanographic Survey")

# Get Plotly Figure for custom modifications
figure = viz.create_plot_figure("time_series", data, variables=["tv290c", "fleco_afl", "ph"])
figure.update_layout(title="Custom Oceanographic Analysis")
figure.show()
```

For detailed Python API examples and advanced usage, see [API_USAGE.md](docs/API_USAGE.md).

### Help

```bash
./triaxus-plot --help
./triaxus-plot time-series --help
```


## Oceanographic Variables

The system supports five complete oceanographic variables:

| Variable | Field Name | Description | Units |
|----------|------------|-------------|-------|
| Temperature | `tv290c` | Water temperature | °C |
| Salinity | `sal00` | Practical salinity | PSU |
| Oxygen | `sbeox0mm_l` | Dissolved oxygen | mg/L |
| Fluorescence | `fleco_afl` | Chlorophyll fluorescence | mg/m³ |
| pH | `ph` | Water acidity | pH units |

All variables support the three main plot types:
- **Time Series**: Temporal evolution of each variable
- **Depth Profile**: Vertical distribution vs depth
- **Contour**: Spatial distribution with depth contours

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
- Variable names: Use existing columns from the generator, e.g., `tv290c` (Temperature), `sal00` (Salinity), `sbeox0mm_l` (Oxygen), `fleco_afl` (Fluorescence), `ph` (pH).
- Custom size not applying (maps): Passing `--width`/`--height` works; the logic prioritizes CLI dimensions over defaults.
- Real-time pipeline shows no data: ensure simulator, processor, and API server are running; try stopping, deleting the realtime state file, and starting again.
- Dashboard manual refresh not working: browser cache can interfere; the dashboard uses `no-cache` headers and logs refresh events to the console.

### Log Files

All system logs are stored in the `logs/` directory:
- **Real-time Processing**: `logs/cnv_realtime_processing.log`
- **Batch Processing**: `logs/cnv_batch_processing.log`
- **API Server**: `logs/api_server.log`
- **Watcher Service**: `logs/cnv_watcher.log` (if using daemon mode)

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
├── realtime/                              # Real-time web dashboard and API server
│   ├── dashboard.html                     # Dashboard (served at /)
│   ├── dashboard.css                      # Dashboard styles
│   ├── dashboard.js                       # Dashboard main entry point
│   ├── js/                                # Modular JavaScript components
│   │   ├── api.js                         # API communication module
│   │   ├── timezone.js                    # Timezone handling module
│   │   ├── data-filter.js                 # Data filtering module
│   │   ├── plots.js                       # Plotting logic module
│   │   └── ui-controls.js                 # UI controls module
│   └── realtime_api_server.py             # HTTP server for dashboard and data
├── scripts/                               # Helper scripts
│   ├── start_realtime_pipeline.py         # One-click start for realtime pipeline
│   ├── stop_realtime_pipeline.py          # One-click stop for realtime pipeline
│   ├── setup_environment.sh               # Environment setup script
│   ├── run_all_tests.sh                   # Run all tests script
│   ├── cleanup_environment.sh             # Cleanup script
│   └── quick_demo.sh                      # Quick demo script
├── logs/                                  # System log files
│   ├── cnv_realtime_processing.log        # Real-time processor logs
│   ├── cnv_batch_processing.log           # Batch processor logs
│   ├── api_server.log                     # API server logs
│   └── cnv_watcher.log                    # Watcher service logs
├── live_data_feed_simulation/              # Data simulation and generation
│   └── simulation.py                      # CNV file live-feed simulator with 5 variables
├── testdataQC/                            # Test data directory
└── triaxus-plot                           # CLI entry point (executable)
```

## Quick Verification

```bash
# Minimal end-to-end checks with all variables
python triaxus-plot time-series --variables tv290c,sal00,sbeox0mm_l,fleco_afl,ph --output demo_time_series.html
python triaxus-plot contour --variable fleco_afl --output demo_contour.html
python triaxus-plot map --output demo_map.html
python triaxus-plot depth-profile --variables tv290c,sal00,sbeox0mm_l,fleco_afl,ph --output demo_depth.html
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
- **All Variables**: Full support for Temperature, Salinity, Oxygen, Fluorescence, and pH
- **Theme Testing**: All themes (oceanographic, dark, default, high_contrast)
- **Data Quality**: Various data scenarios and edge cases
- **Output Validation**: All HTML files generated in organized structure

## License

MIT License. See `LICENSE` for details.

