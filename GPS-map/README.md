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

Requires Python 3.x. No additional Python packages are required.

```bash
# Run the script to generate HTML
python triaxus_map.py
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

## Customization

* **Default Map Center**: Set `mapState.center` in the HTML script to change the initial map location
* **Sample Data**: The `sampleData` array contains placeholder data and can be replaced with actual GPS/sample data
* **Styling**: CSS can be modified inside the HTML string for colors, fonts, or layout

## Notes

* This script does **not** handle CNV file parsing or real-time data collection; these are managed separately
* The map is fully offline; no external libraries or tiles are required
* The HTML output can also be opened directly in a browser for testing
