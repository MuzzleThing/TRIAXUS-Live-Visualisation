/**
 * Enhanced Plot Rendering Module
 * Handles all Plotly chart rendering for multiple variables and chart types
 */

class PlotManager {
    constructor(timezoneManager, dataFilter) {
        this.timezoneManager = timezoneManager;
        this.dataFilter = dataFilter;
        this.mapZoomLevel = 18;
        
        // Define available variables and their properties
        this.variables = {
            temperature: {
                field: 'tv290c',
                unit: '°C',
                color: '#e74c3c',
                name: 'Temperature',
                colorscale: 'Viridis'
            },
            salinity: {
                field: 'sal00',
                unit: 'PSU',
                color: '#3498db',
                name: 'Salinity',
                colorscale: 'Blues'
            },
            oxygen: {
                field: 'sbeox0mm_l',
                unit: 'μmol/L',
                color: '#2ecc71',
                name: 'Oxygen',
                colorscale: 'Greens'
            },
            fluorescence: {
                field: 'fleco_afl',
                unit: 'mg/m³',
                color: '#f39c12',
                name: 'Fluorescence',
                colorscale: 'Oranges'
            },
            ph: {
                field: 'ph',
                unit: '',
                color: '#9b59b6',
                name: 'pH',
                colorscale: 'Purples'
            }
        };
    }

    /**
     * Set map zoom level
     * @param {number} zoom - Zoom level
     */
    setMapZoom(zoom) {
        this.mapZoomLevel = zoom;
    }

    /**
     * Update time series plot for a specific variable
     * @param {string} variable - Variable name (temperature, salinity, etc.)
     */
    updateTimeSeriesPlot(variable) {
        const varConfig = this.variables[variable];
        if (!varConfig) return;

        const timeGranularity = document.getElementById('timeGranularity').value;
        const filteredData = this.dataFilter.getTimeFilteredData(timeGranularity);
        
        // Convert times using timezone manager
        const times = filteredData.map(d => {
            return this.timezoneManager.toDisplayDate(d.time);
        }).filter(t => !isNaN(t));
        
        const values = filteredData.map(d => d[varConfig.field]).filter(v => v !== null);
        
        // Sample data if too many points
        const sampledData = this.dataFilter.sampleData(times, values);
        
        const displayTz = this.timezoneManager.selectedTimezone === 'UTC' ? 'UTC' : this.timezoneManager.getDisplayTimezoneLabel();
        const timeRangeTitle = this.timezoneManager.getTimeRangeTitle(timeGranularity);
        const tickFormat = this.dataFilter.getTimeTickFormat(timeGranularity);
        
        Plotly.react(`${variable}-timeseries-plot`, [{
            x: sampledData.times,
            y: sampledData.values,
            type: 'scatter',
            mode: 'lines+markers',
            name: varConfig.name,
            line: { color: varConfig.color, width: 2 },
            marker: { size: 4 }
        }], {
            title: `${varConfig.name} Time Series (${timeRangeTitle})`,
            xaxis: {
                title: `Time (${displayTz})`,
                type: 'date',
                tickformat: tickFormat
            },
            yaxis: { title: `${varConfig.name} (${varConfig.unit})` },
            margin: { t: 40, r: 20, b: 40, l: 50 }
        });
    }

    /**
     * Update depth profile plot for a specific variable
     * @param {string} variable - Variable name
     */
    updateDepthProfilePlot(variable) {
        const varConfig = this.variables[variable];
        if (!varConfig) return;

        const timeGranularity = document.getElementById('timeGranularity').value;
        const filteredData = this.dataFilter.getTimeFilteredData(timeGranularity);
        
        const depths = filteredData.map(d => d.depth).filter(v => v !== null);
        const values = filteredData.map(d => d[varConfig.field]).filter(v => v !== null);
        
        const timeRangeTitle = this.timezoneManager.getTimeRangeTitle(timeGranularity);
        
        Plotly.react(`${variable}-profile-plot`, [{
            x: values,
            y: depths,
            type: 'scatter',
            mode: 'markers',
            name: `${varConfig.name} Profile`,
            marker: {
                color: values,
                colorscale: varConfig.colorscale,
                size: 6,
                colorbar: { title: `${varConfig.name} (${varConfig.unit})` }
            }
        }], {
            title: `${varConfig.name} Depth Profile (${timeRangeTitle})`,
            xaxis: { title: `${varConfig.name} (${varConfig.unit})` },
            yaxis: { title: 'Depth (m)', autorange: 'reversed' },
            margin: { t: 40, r: 20, b: 40, l: 50 }
        });
    }

    /**
     * Update contour plot for a specific variable
     * @param {string} variable - Variable name
     */
    updateContourPlot(variable) {
        const varConfig = this.variables[variable];
        if (!varConfig) return;

        const timeGranularity = document.getElementById('timeGranularity').value;
        const filteredData = this.dataFilter.getTimeFilteredData(timeGranularity);
        
        if (filteredData.length === 0) return;
        
        // Prepare data for contour plot (depth vs time)
        const times = filteredData.map(d => this.timezoneManager.toDisplayDate(d.time));
        const depths = filteredData.map(d => d.depth).filter(v => v !== null);
        const values = filteredData.map(d => d[varConfig.field]).filter(v => v !== null);
        
        // Create regular grid for contour
        const timeRange = Math.max(...times) - Math.min(...times);
        const depthRange = Math.max(...depths) - Math.min(...depths);
        
        const timeGrid = [];
        const depthGrid = [];
        const valueGrid = [];
        
        // Create grid points
        const timeSteps = Math.min(50, times.length);
        const depthSteps = Math.min(30, depths.length);
        
        for (let i = 0; i < timeSteps; i++) {
            const t = Math.min(...times) + (timeRange * i / (timeSteps - 1));
            timeGrid.push(t);
        }
        
        for (let i = 0; i < depthSteps; i++) {
            const d = Math.min(...depths) + (depthRange * i / (depthSteps - 1));
            depthGrid.push(d);
        }
        
        // Interpolate values for grid
        for (let i = 0; i < depthSteps; i++) {
            const row = [];
            for (let j = 0; j < timeSteps; j++) {
                // Simple nearest neighbor interpolation
                let minDist = Infinity;
                let closestValue = 0;
                
                for (let k = 0; k < filteredData.length; k++) {
                    const timeDist = Math.abs(times[k] - timeGrid[j]);
                    const depthDist = Math.abs(depths[k] - depthGrid[i]);
                    const dist = Math.sqrt(timeDist * timeDist + depthDist * depthDist);
                    
                    if (dist < minDist) {
                        minDist = dist;
                        closestValue = values[k];
                    }
                }
                row.push(closestValue);
            }
            valueGrid.push(row);
        }
        
        const timeRangeTitle = this.timezoneManager.getTimeRangeTitle(timeGranularity);
        const displayTz = this.timezoneManager.selectedTimezone === 'UTC' ? 'UTC' : this.timezoneManager.getDisplayTimezoneLabel();
        
        Plotly.react(`${variable}-contour-plot`, [{
            z: valueGrid,
            x: timeGrid,
            y: depthGrid,
            type: 'contour',
            colorscale: varConfig.colorscale,
            colorbar: {
                title: `${varConfig.name} (${varConfig.unit})`,
                titleside: 'right'
            },
            contours: {
                showlines: true,
                showlabels: true,
                labelfont: { size: 10 }
            },
            line: {
                width: 1,
                color: 'rgba(255,255,255,0.3)'
            }
        }], {
            title: `${varConfig.name} Contour (${timeRangeTitle})`,
            xaxis: {
                title: `Time (${displayTz})`,
                type: 'date',
                tickformat: this.dataFilter.getTimeTickFormat(timeGranularity)
            },
            yaxis: {
                title: 'Depth (m)',
                autorange: 'reversed'
            },
            margin: { t: 40, r: 60, b: 40, l: 50 }
        });
    }

    /**
     * Update map plot with trajectory and current position
     */
    updateMapPlot() {
        const timeGranularity = document.getElementById('timeGranularity').value;
        const filteredData = this.dataFilter.getTimeFilteredData(timeGranularity);
        
        const lats = filteredData.map(d => d.latitude).filter(v => v !== null && v !== undefined);
        const lons = filteredData.map(d => d.longitude).filter(v => v !== null && v !== undefined);
        const temperatures = filteredData.map(d => d.tv290c).filter(v => v !== null && v !== undefined);

        if (lats.length === 0 || lons.length === 0) {
            console.log('No valid coordinates for map');
            return;
        }

        const centerLat = lats[lats.length - 1];
        const centerLon = lons[lons.length - 1];

        try {
            const timeRangeTitle = this.timezoneManager.getTimeRangeTitle(timeGranularity);
            
            const layout = {
                mapbox: {
                    style: 'open-street-map',
                    center: { lat: centerLat, lon: centerLon },
                    zoom: this.mapZoomLevel
                },
                title: `Oceanographic Track - Real-time Position (${timeRangeTitle})`,
                margin: { t: 40, r: 20, b: 20, l: 20 }
            };

            const config = {
                mapboxAccessToken: 'pk.eyJ1IjoibWFwYm94IiwiYSI6ImNpejY4NXVycTA2emYycXBndHRqcmZ3N3gifQ.rJcFIG214AriISLbB6B5aw'
            };

            // Create traces
            const traces = [
                // Trajectory line
                {
                    type: 'scattermapbox',
                    lat: lats,
                    lon: lons,
                    mode: 'lines',
                    line: { color: '#3498db', width: 3 },
                    name: 'Trajectory',
                    showlegend: false
                },
                // History points
                {
                    type: 'scattermapbox',
                    lat: lats.slice(0, -1),
                    lon: lons.slice(0, -1),
                    mode: 'markers',
                    marker: {
                        size: 6,
                        color: temperatures.slice(0, -1),
                        colorscale: 'Viridis',
                        colorbar: { title: 'Temperature (°C)' },
                        opacity: 0.6
                    },
                    name: 'History',
                    showlegend: false
                },
                // Current position
                {
                    type: 'scattermapbox',
                    lat: [lats[lats.length - 1]],
                    lon: [lons[lons.length - 1]],
                    mode: 'markers',
                    marker: {
                        size: 15,
                        color: '#e74c3c',
                        symbol: 'circle',
                        opacity: 1.0,
                        line: { color: '#ffffff', width: 2 }
                    },
                    name: 'Current Position',
                    showlegend: false,
                    hovertemplate: '<b>Current Position</b><br>' +
                                  'Lat: %{lat:.5f}<br>' +
                                  'Lon: %{lon:.5f}<br>' +
                                  'Temp: ' + (temperatures[temperatures.length - 1] || 'N/A') + '°C<br>' +
                                  '<extra></extra>'
                }
            ];

            Plotly.react('map-plot', traces, layout, config);
            console.log('Map plot updated successfully');
        } catch (error) {
            console.error('Map plot error:', error);
        }
    }

    /**
     * Update all plots
     */
    updateAllPlots() {
        if (this.dataFilter.getData().length === 0) return;
        
        // Update all variable charts
        Object.keys(this.variables).forEach(variable => {
            this.updateTimeSeriesPlot(variable);
            this.updateDepthProfilePlot(variable);
            this.updateContourPlot(variable);
        });
        
        // Update map
        this.updateMapPlot();
    }
}

// Export for use in other modules
window.PlotManager = PlotManager;
