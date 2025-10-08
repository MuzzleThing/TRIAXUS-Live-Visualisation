/**
 * UI Controls Module
 * Handles user interface interactions and controls
 */

class UIControls {
    constructor(plotManager, timezoneManager, dataFilter) {
        this.plotManager = plotManager;
        this.timezoneManager = timezoneManager;
        this.dataFilter = dataFilter;
        this.refreshInterval = null;
    }

    /**
     * Set up all event listeners
     */
    setupEventListeners() {
        // Refresh rate control
        document.getElementById('refreshRate').addEventListener('change', () => {
            this.clearRefreshInterval();
            this.startAutoRefresh();
        });

        // Plot type visibility control
        document.getElementById('plotType').addEventListener('change', () => {
            this.updatePlotVisibility();
        });
        
        // Initialize plot visibility
        this.updatePlotVisibility();

        // Time granularity control
        document.getElementById('timeGranularity').addEventListener('change', (event) => {
            console.log('Time granularity changed to:', event.target.value);
            if (this.dataFilter.getData().length > 0) {
                this.plotManager.updateAllPlots();
            }
        });

        // Timezone selector
        const tzSelect = document.getElementById('timezoneSelect');
        if (tzSelect) {
            tzSelect.addEventListener('change', () => {
                this.timezoneManager.setTimezone(tzSelect.value);
                if (this.dataFilter.getData().length > 0) {
                    this.plotManager.updateAllPlots();
                }
            });
            this.timezoneManager.setTimezone(tzSelect.value || 'browser');
        }

        // Map zoom control
        document.getElementById('mapZoom').addEventListener('change', (event) => {
            this.plotManager.setMapZoom(parseInt(event.target.value));
            if (this.dataFilter.getData().length > 0) {
                this.plotManager.updateMapPlot();
            }
        });

        // Manual refresh button
        document.getElementById('manualRefresh').addEventListener('click', () => {
            console.log('Manual refresh clicked');
            console.log('Current time:', new Date().toISOString());
            // Trigger refresh - this will be handled by the main dashboard
            window.dashboard.refreshData();
        });
    }

    /**
     * Start auto-refresh based on selected interval
     */
    startAutoRefresh() {
        const rate = parseInt(document.getElementById('refreshRate').value);
        
        this.clearRefreshInterval();
        
        if (rate > 0) {
            this.refreshInterval = setInterval(() => {
                window.dashboard.refreshData();
            }, rate);
            console.log(`Auto-refresh started with ${rate}ms interval`);
        } else {
            console.log('Manual refresh mode enabled');
        }
    }

    /**
     * Clear refresh interval
     */
    clearRefreshInterval() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }
    }

    /**
     * Update plot visibility based on selected plot type
     */
    updatePlotVisibility() {
        const plotType = document.getElementById('plotType').value;
        const chartsSection = document.querySelector('.charts-section');
        const mapSection = document.querySelector('.map-section');
        
        // Hide all charts first
        const allChartBoxes = document.querySelectorAll('.chart-box[data-variable]');
        allChartBoxes.forEach(box => {
            box.style.display = 'none';
        });
        
        switch (plotType) {
            case 'all':
                chartsSection.style.display = 'grid';
                mapSection.style.display = 'flex';
                // Show all charts
                allChartBoxes.forEach(box => {
                    box.style.display = 'block';
                });
                break;
            case 'temperature':
            case 'salinity':
            case 'oxygen':
            case 'fluorescence':
            case 'ph':
                chartsSection.style.display = 'grid';
                mapSection.style.display = 'flex';
                // Show only charts for selected variable
                const variableCharts = document.querySelectorAll(`.chart-box[data-variable="${plotType}"]`);
                variableCharts.forEach(box => {
                    box.style.display = 'block';
                });
                break;
            case 'map':
                chartsSection.style.display = 'none';
                mapSection.style.display = 'flex';
                break;
        }
    }

    /**
     * Update status bar with current connection and data information
     * @param {string} status - Connection status
     * @param {number} count - Number of records
     * @param {string} time - Last update time
     */
    updateStatus(status, count, time) {
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
}

// Export for use in other modules
window.UIControls = UIControls;
