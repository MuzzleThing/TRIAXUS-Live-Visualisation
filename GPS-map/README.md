# TRIAXUS GPS Map Generator

## Overview

The **TRIAXUS GPS Map Generator** is a fully offline, HTML/CSS/JavaScript-based map system packaged in a Python function. It renders a zoomable and draggable map for visualizing GPS locations, ship positions, and sample points collected during TRIAXUS oceanographic research cruises.

The main purpose of this script is to provide a **complete HTML map** as a string that can be embedded in any frontend or application.

## Features

* Fully offline map with a blue gradient background
* Zoom in/out and drag to explore different map areas
* Displays sample points with interactive popups showing:
   * Time of sample
   * Temperature
   * Salinity
   * Depth
   * Coordinates
* Shows ship location with a pulse animation and popup
* List panel for all sample points with clickable navigation

## Installation

Requires Python 3.x. No additional Python packages are required for the main script.

For testing, install the required dependencies:

```bash
# Install testing dependencies
pip install beautifulsoup4

# Alternative command if 'pip' doesn't work
py -m pip install beautifulsoup4
```

```bash
# Run the script to generate HTML
python triaxus_map.py

# Alternative command if 'python' doesn't work
py triaxus_map.py
```

## Usage

```python
from triaxus_map import get_map_html

# Generate HTML string for the map
html_content = get_map_html()

# Save to a file if needed
with open("triaxus_map.html", "w", encoding="utf-8") as f:
    f.write(html_content)
```

## Testing

The project includes comprehensive unit tests to ensure code quality and functionality. The test suite covers:

### Test Categories

* **HTML Structure Validation** - Verifies proper HTML document structure, meta tags, and DOM elements
* **CSS Styling Tests** - Ensures all necessary CSS classes, animations, and responsive design elements are present
* **JavaScript Function Tests** - Validates all core JavaScript functions and event handlers
* **Data Validation** - Checks oceanographic data ranges, coordinate bounds, and format consistency
* **File Operations** - Tests HTML generation and file encoding

### Running Tests

```bash
# Run the complete test suite
python test_triaxus_map.py

# Alternative command if 'python' doesn't work
py test_triaxus_map.py
```

### Test Results

The test suite includes 26 comprehensive tests covering:
- 18 core functionality tests (HTML/CSS/JavaScript)
- 3 file operation tests
- 5 data validation tests

Expected output:
```
Ran 26 tests in 0.034s
OK
============================================================
TEST SUMMARY
============================================================
Tests run: 26
Failures: 0
Errors: 0
Success rate: 100.0%
```

### Test Coverage

* **Structure Integrity** - HTML document completeness and validity
* **Functional Completeness** - All interactive features and event handlers
* **Data Quality** - Oceanographic measurements within scientific ranges
* **Responsive Design** - Mobile compatibility and accessibility features
* **Browser Compatibility** - Cross-platform HTML/CSS/JS standards

## Customization

* **Default Map Center**: Set `mapState.center` in the HTML script to change the initial map location
* **Sample Data**: The `sampleData` array contains placeholder data and can be replaced with actual GPS/sample data
* **Styling**: CSS can be modified inside the HTML string for colors, fonts, or layout

## Development

### Code Quality

The codebase maintains high standards with:
- Comprehensive unit testing (100% pass rate)
- English code comments for maintainability
- Proper error handling and data validation
- Responsive design principles

### Contributing

When making changes to the code:
1. Run the test suite to ensure no regressions
2. Update tests if adding new functionality
3. Maintain the existing code style and commenting conventions

## Notes

* This script does **not** handle CNV file parsing or real-time data collection; these are managed separately
* The map is fully offline; no external libraries or tiles are required
* The HTML output can also be opened directly in a browser for testing
