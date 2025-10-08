/**
 * Main Dashboard Controller
 * Orchestrates all dashboard components and manages the application lifecycle
 */

class Dashboard {
    constructor() {
        // Initialize modules
        this.api = new DataAPI();
        this.timezoneManager = new TimezoneManager();
        this.dataFilter = new DataFilter();
        this.plotManager = new PlotManager(this.timezoneManager, this.dataFilter);
        this.uiControls = new UIControls(this.plotManager, this.timezoneManager, this.dataFilter);
        
        // Make dashboard globally accessible for event handlers
        window.dashboard = this;
    }

    /**
     * Initialize the dashboard when DOM is loaded
     */
    initialize() {
        this.uiControls.setupEventListeners();
        this.refreshData();
        this.uiControls.startAutoRefresh();
    }

    /**
     * Fetch and process latest data from API
     */
    async refreshData() {
        try {
            const result = await this.api.fetchLatestData(1000);
            
            if (this.api.validateResponse(result)) {
                this.dataFilter.setData(result.data);
                
                // Debug: Show sample data times
                if (result.data.length > 0) {
                    console.log('Sample data times:');
                    for (let i = 0; i < Math.min(3, result.data.length); i++) {
                        const time = new Date(result.data[i].time);
                        console.log(`  Record ${i}: ${result.data[i].time} -> ${time.toISOString()}`);
                    }
                }
                
                this.uiControls.updateStatus('Connected', result.count, new Date().toLocaleTimeString());
                this.plotManager.updateAllPlots();
            } else {
                this.uiControls.updateStatus('Error: ' + (result.error || 'Unknown error'), 0, new Date().toLocaleTimeString());
            }
        } catch (error) {
            console.error('Data refresh error:', error);
            this.uiControls.updateStatus(error.message, 0, new Date().toLocaleTimeString());
        }
    }

    /**
     * Get current data for external access
     * @returns {Array} Current data array
     */
    getCurrentData() {
        return this.dataFilter.getData();
    }

    /**
     * Get API instance for external access
     * @returns {DataAPI} API instance
     */
    getAPI() {
        return this.api;
    }

    /**
     * Get timezone manager for external access
     * @returns {TimezoneManager} Timezone manager instance
     */
    getTimezoneManager() {
        return this.timezoneManager;
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    const dashboard = new Dashboard();
    dashboard.initialize();
});

// Export for potential external use
window.Dashboard = Dashboard;
