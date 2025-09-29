/**
 * TRIAXUS Real-time Oceanographic Dashboard JavaScript
 * 
 * This module handles all interactive functionality for the real-time dashboard,
 * including data fetching, plot updates, and user interface controls.
 */

// Global state variables
let refreshInterval;
let currentData = [];
let mapZoomLevel = 18;

/**
 * Initialize the dashboard when DOM is loaded
 */
document.addEventListener('DOMContentLoaded', function() {
    setupEventListeners();
    fetchData();
    startAutoRefresh();
});

/**
 * Set up all event listeners for user interactions
 */
function setupEventListeners() {
    // Refresh rate control
    document.getElementById('refreshRate').addEventListener('change', function() {
        clearInterval(refreshInterval);
        startAutoRefresh();
    });

    // Plot type visibility control
    document.getElementById('plotType').addEventListener('change', function() {
        updatePlotVisibility();
    });

    // Time granularity control
    document.getElementById('timeGranularity').addEventListener('change', function() {
        console.log('Time granularity changed to:', this.value);
        if (currentData.length > 0) {
            updateAllPlots();
        }
    });

    // Map zoom control
    document.getElementById('mapZoom').addEventListener('change', function() {
        mapZoomLevel = parseInt(this.value);
        if (currentData.length > 0) {
            updateMapPlot();
        }
    });

    // Manual refresh button
    document.getElementById('manualRefresh').addEventListener('click', function() {
        console.log('Manual refresh clicked');
        console.log('Current time:', new Date().toISOString());
        fetchData();
    });
}

/**
 * Start auto-refresh based on selected interval
 */
function startAutoRefresh() {
    const rate = parseInt(document.getElementById('refreshRate').value);
    
    // Clear existing interval
    if (refreshInterval) {
        clearInterval(refreshInterval);
        refreshInterval = null;
    }
    
    // Start new interval only if rate > 0 (not manual mode)
    if (rate > 0) {
        refreshInterval = setInterval(fetchData, rate);
        console.log(`Auto-refresh started with ${rate}ms interval`);
    } else {
        console.log('Manual refresh mode enabled');
    }
}

/**
 * Update plot visibility based on selected plot type
 */
function updatePlotVisibility() {
    const plotType = document.getElementById('plotType').value;
    const chartsSection = document.querySelector('.charts-section');
    const mapSection = document.querySelector('.map-section');
    
    if (plotType === 'all') {
        chartsSection.style.display = 'grid';
        mapSection.style.display = 'flex';
    } else if (plotType === 'timeseries') {
        chartsSection.style.display = 'grid';
        mapSection.style.display = 'none';
    } else if (plotType === 'profile') {
        chartsSection.style.display = 'grid';
        mapSection.style.display = 'none';
    } else if (plotType === 'map') {
        chartsSection.style.display = 'none';
        mapSection.style.display = 'flex';
    }
}

/**
 * Fetch latest data from the API
 */
async function fetchData() {
    try {
        console.log('Fetching data from API...');
        const response = await fetch('/api/latest_data?limit=1000', {
            cache: 'no-cache',
            headers: {
                'Cache-Control': 'no-cache'
            }
        });
        console.log('Response status:', response.status);
        const result = await response.json();
        
        console.log('API Response:', {success: result.success, count: result.count, dataLength: result.data?.length});
        
        if (result.success && result.data) {
            currentData = result.data;
            
            // Debug: Show sample data times
            if (currentData.length > 0) {
                console.log('Sample data times:');
                for (let i = 0; i < Math.min(3, currentData.length); i++) {
                    const time = new Date(currentData[i].time);
                    console.log(`  Record ${i}: ${currentData[i].time} -> ${time.toISOString()}`);
                }
            }
            
            updateStatus('Connected', result.count, new Date().toLocaleTimeString());
            updateAllPlots();
        } else {
            updateStatus('Error: ' + (result.error || 'Unknown error'), 0, new Date().toLocaleTimeString());
        }
    } catch (error) {
        console.error('Fetch error:', error);
        updateStatus('Connection Error: ' + error.message, 0, new Date().toLocaleTimeString());
    }
}

/**
 * Update status bar with current connection and data information
 */
function updateStatus(status, count, time) {
    document.getElementById('statusText').textContent = status;
    document.getElementById('recordCount').textContent = count;
    document.getElementById('lastUpdate').textContent = time;
    
    // Update manual refresh button state
    const manualButton = document.getElementById('manualRefresh');
    const refreshRate = parseInt(document.getElementById('refreshRate').value);
    if (refreshRate === 0) {
        manualButton.style.background = '#e3f2fd';
        manualButton.style.borderColor = '#2196f3';
        manualButton.textContent = 'Manual Refresh (Active)';
    } else {
        manualButton.style.background = '#f8f9fa';
        manualButton.style.borderColor = '#ddd';
        manualButton.textContent = 'Manual Refresh';
    }
}

/**
 * Update all plots with current data
 */
function updateAllPlots() {
    if (currentData.length === 0) return;

    updateTimeSeriesPlots();
    updateProfilePlot();
    updateMapPlot();
}

/**
 * Filter data based on selected time granularity
 */
function getTimeFilteredData() {
    const timeGranularity = document.getElementById('timeGranularity').value;
    
    // For real-time testing, we need to adjust time filtering since data timestamps are in +08:00
    // but we want to show recent data regardless of timezone
    const nowUTC = new Date();
    console.log(`Current UTC time: ${nowUTC.toISOString()}`);
    
    if (currentData.length > 0) {
        const firstTime = new Date(currentData[0].time);
        const lastTime = new Date(currentData[currentData.length - 1].time);
        console.log(`Data time range: ${firstTime.toISOString()} to ${lastTime.toISOString()}`);
    }
    
    // For testing purposes, if data is older than 1 hour, show all data for '1h' selection
    // This allows testing with simulated data that might be hours old
    if (currentData.length > 0) {
        const latestDataTime = new Date(currentData[currentData.length - 1].time);
        const dataAgeHours = (nowUTC.getTime() - latestDataTime.getTime()) / (1000 * 60 * 60);
        
        if (dataAgeHours > 1 && (timeGranularity === '5m' || timeGranularity === '15m' || timeGranularity === '30m' || timeGranularity === '1h' || timeGranularity === '6h')) {
            console.log(`Data is ${dataAgeHours.toFixed(1)} hours old, showing all data for testing`);
            return currentData;
        }
    }
    
    let cutoffTimeUTC;
    
    switch (timeGranularity) {
        case '5m':
            cutoffTimeUTC = new Date(nowUTC.getTime() - 5 * 60 * 1000);
            break;
        case '15m':
            cutoffTimeUTC = new Date(nowUTC.getTime() - 15 * 60 * 1000);
            break;
        case '30m':
            cutoffTimeUTC = new Date(nowUTC.getTime() - 30 * 60 * 1000);
            break;
        case '1h':
            cutoffTimeUTC = new Date(nowUTC.getTime() - 1 * 60 * 60 * 1000);
            break;
        case '6h':
            cutoffTimeUTC = new Date(nowUTC.getTime() - 6 * 60 * 60 * 1000);
            break;
        case '12h':
            cutoffTimeUTC = new Date(nowUTC.getTime() - 12 * 60 * 60 * 1000);
            break;
        case '24h':
            cutoffTimeUTC = new Date(nowUTC.getTime() - 24 * 60 * 60 * 1000);
            break;
        case '3d':
            cutoffTimeUTC = new Date(nowUTC.getTime() - 3 * 24 * 60 * 60 * 1000);
            break;
        case '7d':
            cutoffTimeUTC = new Date(nowUTC.getTime() - 7 * 24 * 60 * 60 * 1000);
            break;
        case '30d':
            cutoffTimeUTC = new Date(nowUTC.getTime() - 30 * 24 * 60 * 60 * 1000);
            break;
        case 'all':
        default:
            return currentData;
    }
    
    console.log(`Cutoff time for ${timeGranularity}: ${cutoffTimeUTC.toISOString()}`);
    
    const filtered = currentData.filter(d => {
        const dataTime = new Date(d.time);
        const isInRange = dataTime >= cutoffTimeUTC;
        if (!isInRange && currentData.indexOf(d) < 5) { // Debug first few records
            console.log(`Record ${currentData.indexOf(d)}: ${dataTime.toISOString()} < ${cutoffTimeUTC.toISOString()}`);
        }
        return isInRange;
    });
    
    console.log(`Filtered ${filtered.length} records from ${currentData.length} total`);
    return filtered;
}

/**
 * Determine data timezone from time string
 */
function getDataTimezone(timeStr) {
    if (timeStr.includes('+08:00')) {
        return 'CST (UTC+8)';
    } else if (timeStr.includes('+00:00') || timeStr.includes('Z')) {
        return 'UTC';
    } else if (timeStr.includes('-')) {
        return 'Local';
    }
    return 'UTC';
}

/**
 * Update time series plots (temperature, salinity, oxygen)
 */
function updateTimeSeriesPlots() {
    const filteredData = getTimeFilteredData();
    const times = filteredData.map(d => new Date(d.time)).filter(t => !isNaN(t));
    const temps = filteredData.map(d => d.tv290c).filter(v => v !== null);
    const salinities = filteredData.map(d => d.sal00).filter(v => v !== null);
    const oxygens = filteredData.map(d => d.sbeox0mm_l).filter(v => v !== null);
    
    console.log(`Time filtering: ${filteredData.length} records from ${currentData.length} total`);
    if (times.length > 0) {
        console.log(`Time range: ${times[0].toISOString()} to ${times[times.length-1].toISOString()}`);
    }
    
    // For better visualization, limit to reasonable number of points
    const maxPoints = 500;
    if (times.length > maxPoints) {
        const step = Math.ceil(times.length / maxPoints);
        const sampledTimes = [];
        const sampledTemps = [];
        const sampledSalinities = [];
        const sampledOxygens = [];
        
        for (let i = 0; i < times.length; i += step) {
            sampledTimes.push(times[i]);
            sampledTemps.push(temps[i]);
            sampledSalinities.push(salinities[i]);
            sampledOxygens.push(oxygens[i]);
        }
        
        times.splice(0, times.length, ...sampledTimes);
        temps.splice(0, temps.length, ...sampledTemps);
        salinities.splice(0, salinities.length, ...sampledSalinities);
        oxygens.splice(0, oxygens.length, ...sampledOxygens);
    }

    // Determine data timezone and create title
    const dataTimezone = filteredData.length > 0 && filteredData[0].time ? 
                        getDataTimezone(filteredData[0].time) : 'UTC';
    const timeGranularity = document.getElementById('timeGranularity').value;
    const timeRangeTitle = timeGranularity === 'all' ? 
                          `All Data (${dataTimezone})` : 
                          `Last ${timeGranularity.toUpperCase()} (${dataTimezone})`;
    
    // Temperature plot
    Plotly.react('temp-plot', [{
        x: times,
        y: temps,
        type: 'scatter',
        mode: 'lines+markers',
        name: 'Temperature',
        line: {color: '#e74c3c', width: 2},
        marker: {size: 4}
    }], {
        title: `Temperature vs Time (${timeRangeTitle})`,
        xaxis: {
            title: `Time (${dataTimezone})`,
            type: 'date',
            tickformat: timeGranularity === '5m' || timeGranularity === '15m' || timeGranularity === '30m' || timeGranularity === '1h' || timeGranularity === '6h' ? '%H:%M:%S' : 
                       timeGranularity === '12h' || timeGranularity === '24h' ? '%m/%d %H:%M' : 
                       '%m/%d'
        },
        yaxis: {title: 'Temperature (°C)'},
        margin: {t: 40, r: 20, b: 40, l: 50}
    });

    // Salinity plot
    Plotly.react('salinity-plot', [{
        x: times,
        y: salinities,
        type: 'scatter',
        mode: 'lines+markers',
        name: 'Salinity',
        line: {color: '#3498db', width: 2},
        marker: {size: 4}
    }], {
        title: `Salinity vs Time (${timeRangeTitle})`,
        xaxis: {
            title: `Time (${dataTimezone})`,
            type: 'date',
            tickformat: timeGranularity === '5m' || timeGranularity === '15m' || timeGranularity === '30m' || timeGranularity === '1h' || timeGranularity === '6h' ? '%H:%M:%S' : 
                       timeGranularity === '12h' || timeGranularity === '24h' ? '%m/%d %H:%M' : 
                       '%m/%d'
        },
        yaxis: {title: 'Salinity (PSU)'},
        margin: {t: 40, r: 20, b: 40, l: 50}
    });

    // Oxygen plot
    Plotly.react('oxygen-plot', [{
        x: times,
        y: oxygens,
        type: 'scatter',
        mode: 'lines+markers',
        name: 'Oxygen',
        line: {color: '#2ecc71', width: 2},
        marker: {size: 4}
    }], {
        title: `Oxygen vs Time (${timeRangeTitle})`,
        xaxis: {
            title: `Time (${dataTimezone})`,
            type: 'date',
            tickformat: timeGranularity === '5m' || timeGranularity === '15m' || timeGranularity === '30m' || timeGranularity === '1h' || timeGranularity === '6h' ? '%H:%M:%S' : 
                       timeGranularity === '12h' || timeGranularity === '24h' ? '%m/%d %H:%M' : 
                       '%m/%d'
        },
        yaxis: {title: 'Oxygen (mg/L)'},
        margin: {t: 40, r: 20, b: 40, l: 50}
    });
}

/**
 * Update depth profile plot
 */
function updateProfilePlot() {
    const filteredData = getTimeFilteredData();
    const depths = filteredData.map(d => d.depth).filter(v => v !== null);
    const temps = filteredData.map(d => d.tv290c).filter(v => v !== null);
    
    // Determine data timezone and create title
    const dataTimezone = filteredData.length > 0 && filteredData[0].time ? 
                        getDataTimezone(filteredData[0].time) : 'UTC';
    const timeGranularity = document.getElementById('timeGranularity').value;
    const timeRangeTitle = timeGranularity === 'all' ? 
                          `All Data (${dataTimezone})` : 
                          `Last ${timeGranularity.toUpperCase()} (${dataTimezone})`;

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
            colorbar: {title: 'Temperature (°C)'}
        }
    }], {
        title: `Temperature vs Depth (${timeRangeTitle})`,
        xaxis: {title: 'Temperature (°C)'},
        yaxis: {title: 'Depth (m)', autorange: 'reversed'},
        margin: {t: 40, r: 20, b: 40, l: 50}
    });
}

/**
 * Update map plot with trajectory and current position
 */
function updateMapPlot() {
    const filteredData = getTimeFilteredData();
    const lats = filteredData.map(d => d.latitude).filter(v => v !== null && v !== undefined);
    const lons = filteredData.map(d => d.longitude).filter(v => v !== null && v !== undefined);
    const temperatures = filteredData.map(d => d.tv290c).filter(v => v !== null && v !== undefined);

    console.log('Map data:', {lats: lats.length, lons: lons.length, temps: temperatures.length});
    console.log('Sample coords:', {lat: lats[0], lon: lons[0]});
    console.log('All lats:', lats.slice(0, 5));
    console.log('All lons:', lons.slice(0, 5));

    if (lats.length === 0 || lons.length === 0) {
        console.log('No valid coordinates for map');
        return;
    }

    // Use the most recent position as center (current position)
    const centerLat = lats[lats.length - 1];
    const centerLon = lons[lons.length - 1];

    console.log('Map center (current position):', {centerLat, centerLon, zoom: mapZoomLevel});

    try {
        // Trajectory line
        const trajectoryTrace = {
            type: 'scattermapbox',
            lat: lats,
            lon: lons,
            mode: 'lines',
            line: {color: '#3498db', width: 3},
            name: 'Trajectory',
            showlegend: false
        };

        // History position points
        const historyTrace = {
            type: 'scattermapbox',
            lat: lats.slice(0, -1), // All points except the last one
            lon: lons.slice(0, -1),
            mode: 'markers',
            marker: {
                size: 6,
                color: temperatures.slice(0, -1),
                colorscale: 'Viridis',
                colorbar: {title: 'Temperature (°C)'},
                opacity: 0.6
            },
            name: 'History',
            showlegend: false
        };

        // Current position point (red dot)
        const currentTrace = {
            type: 'scattermapbox',
            lat: [lats[lats.length - 1]], // Last point
            lon: [lons[lons.length - 1]],
            mode: 'markers',
            marker: {
                size: 15,
                color: '#e74c3c',
                symbol: 'circle',
                opacity: 1.0,
                line: {
                    color: '#ffffff',
                    width: 2
                }
            },
            name: 'Current Position',
            showlegend: false,
            hovertemplate: '<b>Current Position</b><br>' +
                          'Lat: %{lat:.5f}<br>' +
                          'Lon: %{lon:.5f}<br>' +
                          'Temp: ' + (temperatures[temperatures.length - 1] || 'N/A') + '°C<br>' +
                          '<extra></extra>'
        };

        // Determine data timezone and create title
        const dataTimezone = filteredData.length > 0 && filteredData[0].time ? 
                            getDataTimezone(filteredData[0].time) : 'UTC';
        const timeGranularity = document.getElementById('timeGranularity').value;
        const timeRangeTitle = timeGranularity === 'all' ? 
                              `All Data (${dataTimezone})` : 
                              `Last ${timeGranularity.toUpperCase()} (${dataTimezone})`;
        
        const layout = {
            mapbox: {
                style: 'open-street-map',
                center: {lat: centerLat, lon: centerLon},
                zoom: mapZoomLevel
            },
            title: `Oceanographic Track - Real-time Position (${timeRangeTitle})`,
            margin: {t: 40, r: 20, b: 20, l: 20}
        };

        const config = {
            mapboxAccessToken: 'pk.eyJ1IjoibWFwYm94IiwiYSI6ImNpejY4NXVycTA2emYycXBndHRqcmZ3N3gifQ.rJcFIG214AriISLbB6B5aw'
        };

        console.log('Plotting map with traces:', [trajectoryTrace, historyTrace, currentTrace]);
        console.log('Layout:', layout);
        console.log('Config:', config);

        Plotly.react('map-plot', [trajectoryTrace, historyTrace, currentTrace], layout, config);
        console.log('Map plot updated successfully with current position marker');
    } catch (error) {
        console.error('Map plot error:', error);
    }
}
