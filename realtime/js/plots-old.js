/**
 * Plot Rendering Module
 * Handles all Plotly chart rendering and updates
 */

class PlotManager {
    constructor(timezoneManager, dataFilter) {
        this.timezoneManager = timezoneManager;
        this.dataFilter = dataFilter;
        this.mapZoomLevel = 18;
    }

    /**
     * Set map zoom level
     * @param {number} zoom - Zoom level
     */
    setMapZoom(zoom) {
        this.mapZoomLevel = zoom;
    }

    /**
     * Update time series plots (temperature, salinity, oxygen)
     */
    updateTimeSeriesPlots() {
        const timeGranularity = document.getElementById('timeGranularity').value;
        const filteredData = this.dataFilter.getTimeFilteredData(timeGranularity);
        
        // Convert times using timezone manager
        const times = filteredData.map(d => {
            return this.timezoneManager.toDisplayDate(d.time);
        }).filter(t => !isNaN(t));
        
        const temps = filteredData.map(d => d.tv290c).filter(v => v !== null);
        const salinities = filteredData.map(d => d.sal00).filter(v => v !== null);
        const oxygens = filteredData.map(d => d.sbeox0mm_l).filter(v => v !== null);
        
        console.log(`Time filtering: ${filteredData.length} records from ${this.dataFilter.getData().length} total`);
        if (times.length > 0) {
            console.log(`Time range: ${times[0].toISOString()} to ${times[times.length-1].toISOString()}`);
        }
        
        // Sample data if too many points
        const tempData = this.dataFilter.sampleData(times, temps);
        const salinityData = this.dataFilter.sampleData(times, salinities);
        const oxygenData = this.dataFilter.sampleData(times, oxygens);
        
        const displayTz = this.timezoneManager.selectedTimezone === 'UTC' ? 'UTC' : this.timezoneManager.getDisplayTimezoneLabel();
        const timeRangeTitle = this.timezoneManager.getTimeRangeTitle(timeGranularity);
        const tickFormat = this.dataFilter.getTimeTickFormat(timeGranularity);
        
        // Temperature plot
        this.renderTimeSeriesPlot('temp-plot', {
            times: tempData.times,
            values: tempData.values,
            title: `Temperature vs Time (${timeRangeTitle})`,
            yTitle: 'Temperature (°C)',
            color: '#e74c3c',
            name: 'Temperature',
            displayTz,
            tickFormat
        });
        
        // Salinity plot
        this.renderTimeSeriesPlot('salinity-plot', {
            times: salinityData.times,
            values: salinityData.values,
            title: `Salinity vs Time (${timeRangeTitle})`,
            yTitle: 'Salinity (PSU)',
            color: '#3498db',
            name: 'Salinity',
            displayTz,
            tickFormat
        });
        
        // Oxygen plot
        this.renderTimeSeriesPlot('oxygen-plot', {
            times: oxygenData.times,
            values: oxygenData.values,
            title: `Oxygen vs Time (${timeRangeTitle})`,
            yTitle: 'Oxygen (mg/L)',
            color: '#2ecc71',
            name: 'Oxygen',
            displayTz,
            tickFormat
        });
    }

    /**
     * Render a time series plot
     * @param {string} elementId - DOM element ID
     * @param {Object} config - Plot configuration
     */
    renderTimeSeriesPlot(elementId, config) {
        const { times, values, title, yTitle, color, name, displayTz, tickFormat } = config;
        
        Plotly.react(elementId, [{
            x: times,
            y: values,
            type: 'scatter',
            mode: 'lines+markers',
            name: name,
            line: { color, width: 2 },
            marker: { size: 4 }
        }], {
            title,
            xaxis: {
                title: `Time (${displayTz})`,
                type: 'date',
                tickformat: tickFormat
            },
            yaxis: { title: yTitle },
            margin: { t: 40, r: 20, b: 40, l: 50 }
        });
    }

    /**
     * Update depth profile plot
     */
    updateProfilePlot() {
        const timeGranularity = document.getElementById('timeGranularity').value;
        const filteredData = this.dataFilter.getTimeFilteredData(timeGranularity);
        
        const depths = filteredData.map(d => d.depth).filter(v => v !== null);
        const temps = filteredData.map(d => d.tv290c).filter(v => v !== null);
        
        const timeRangeTitle = this.timezoneManager.getTimeRangeTitle(timeGranularity);
        
        Plotly.react('profile-plot', [{
            x: temps,
            y: depths,
            type: 'scatter',
            mode: 'markers',
            name: 'Temperature Profile',
            marker: {
                color: temps,
                colorscale: 'Viridis',
                size: 6,
                colorbar: { title: 'Temperature (°C)' }
            }
        }], {
            title: `Temperature vs Depth (${timeRangeTitle})`,
            xaxis: { title: 'Temperature (°C)' },
            yaxis: { title: 'Depth (m)', autorange: 'reversed' },
            margin: { t: 40, r: 20, b: 40, l: 50 }
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

        console.log('Map data:', { lats: lats.length, lons: lons.length, temps: temperatures.length });

        if (lats.length === 0 || lons.length === 0) {
            console.log('No valid coordinates for map');
            return;
        }

        const centerLat = lats[lats.length - 1];
        const centerLon = lons[lons.length - 1];
        console.log('Map center (current position):', { centerLat, centerLon, zoom: this.mapZoomLevel });

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
     * Update temperature contour plot
     */
    updateContourPlot() {
        const timeGranularity = document.getElementById('timeGranularity').value;
        const filteredData = this.dataFilter.getTimeFilteredData(timeGranularity);
        
        if (filteredData.length === 0) return;
        
        // Prepare data for contour plot (depth vs time)
        const times = filteredData.map(d => this.timezoneManager.toDisplayDate(d.time));
        const depths = filteredData.map(d => d.depth).filter(v => v !== null);
        const temps = filteredData.map(d => d.tv290c).filter(v => v !== null);
        
        // Create regular grid for contour
        const timeRange = Math.max(...times) - Math.min(...times);
        const depthRange = Math.max(...depths) - Math.min(...depths);
        
        const timeGrid = [];
        const depthGrid = [];
        const tempGrid = [];
        
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
        
        // Interpolate temperature values for grid
        for (let i = 0; i < depthSteps; i++) {
            const row = [];
            for (let j = 0; j < timeSteps; j++) {
                // Simple nearest neighbor interpolation
                let minDist = Infinity;
                let closestTemp = 0;
                
                for (let k = 0; k < filteredData.length; k++) {
                    const timeDist = Math.abs(times[k] - timeGrid[j]);
                    const depthDist = Math.abs(depths[k] - depthGrid[i]);
                    const dist = Math.sqrt(timeDist * timeDist + depthDist * depthDist);
                    
                    if (dist < minDist) {
                        minDist = dist;
                        closestTemp = temps[k];
                    }
                }
                row.push(closestTemp);
            }
            tempGrid.push(row);
        }
        
        const timeRangeTitle = this.timezoneManager.getTimeRangeTitle(timeGranularity);
        const displayTz = this.timezoneManager.selectedTimezone === 'UTC' ? 'UTC' : this.timezoneManager.getDisplayTimezoneLabel();
        
        Plotly.react('contour-plot', [{
            z: tempGrid,
            x: timeGrid,
            y: depthGrid,
            type: 'contour',
            colorscale: 'Viridis',
            colorbar: {
                title: 'Temperature (°C)',
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
            title: `Temperature Contour (${timeRangeTitle})`,
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
     * Update all plots
     */
    updateAllPlots() {
        if (this.dataFilter.getData().length === 0) return;
        
        this.updateTimeSeriesPlots();
        this.updateProfilePlot();
        this.updateContourPlot();
        this.updateMapPlot();
    }
}

// Export for use in other modules
window.PlotManager = PlotManager;
