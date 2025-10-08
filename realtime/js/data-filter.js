/**
 * Data Filtering Module
 * Handles time-based data filtering and processing
 */

class DataFilter {
    constructor() {
        this.currentData = [];
    }

    /**
     * Set current data array
     * @param {Array} data - Array of data records
     */
    setData(data) {
        this.currentData = data || [];
    }

    /**
     * Get current data array
     * @returns {Array} Current data
     */
    getData() {
        return this.currentData;
    }

    /**
     * Filter data based on time granularity
     * @param {string} timeGranularity - Time range to filter
     * @returns {Array} Filtered data
     */
    getTimeFilteredData(timeGranularity = '1h') {
        if (!this.currentData || this.currentData.length === 0) {
            return [];
        }

        const nowUTC = new Date();
        console.log(`Current UTC time: ${nowUTC.toISOString()}`);
        
        if (this.currentData.length > 0) {
            const firstTime = new Date(this.currentData[0].time);
            const lastTime = new Date(this.currentData[this.currentData.length - 1].time);
            console.log(`Data time range: ${firstTime.toISOString()} to ${lastTime.toISOString()}`);
        }
        
        // For testing purposes, if data is older than 1 hour, show all data
        if (this.currentData.length > 0) {
            const latestDataTime = new Date(this.currentData[this.currentData.length - 1].time);
            const dataAgeHours = (nowUTC.getTime() - latestDataTime.getTime()) / (1000 * 60 * 60);
            
            if (dataAgeHours > 1 && ['5m', '15m', '30m', '1h', '6h'].includes(timeGranularity)) {
                console.log(`Data is ${dataAgeHours.toFixed(1)} hours old, showing all data for testing`);
                return this.currentData;
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
                return this.currentData;
        }
        
        console.log(`Cutoff time for ${timeGranularity}: ${cutoffTimeUTC.toISOString()}`);
        
        const filtered = this.currentData.filter(d => {
            const dataTime = new Date(d.time);
            const isInRange = dataTime >= cutoffTimeUTC;
            if (!isInRange && this.currentData.indexOf(d) < 5) {
                console.log(`Record ${this.currentData.indexOf(d)}: ${dataTime.toISOString()} < ${cutoffTimeUTC.toISOString()}`);
            }
            return isInRange;
        });
        
        console.log(`Filtered ${filtered.length} records from ${this.currentData.length} total`);
        return filtered;
    }

    /**
     * Get time tick format based on granularity
     * @param {string} timeGranularity - Time range
     * @returns {string} Tick format for Plotly
     */
    getTimeTickFormat(timeGranularity) {
        if (['5m', '15m', '30m', '1h', '6h'].includes(timeGranularity)) {
            return '%H:%M:%S';
        } else if (['12h', '24h'].includes(timeGranularity)) {
            return '%m/%d %H:%M';
        } else {
            return '%m/%d';
        }
    }

    /**
     * Sample data for better visualization (limit points)
     * @param {Array} times - Time array
     * @param {Array} values - Value arrays
     * @param {number} maxPoints - Maximum number of points
     * @returns {Object} Sampled data
     */
    sampleData(times, values, maxPoints = 500) {
        if (times.length <= maxPoints) {
            return { times, values };
        }
        
        const step = Math.ceil(times.length / maxPoints);
        const sampledTimes = [];
        const sampledValues = [];
        
        for (let i = 0; i < times.length; i += step) {
            sampledTimes.push(times[i]);
            sampledValues.push(values[i]);
        }
        
        return { times: sampledTimes, values: sampledValues };
    }
}

// Export for use in other modules
window.DataFilter = DataFilter;
