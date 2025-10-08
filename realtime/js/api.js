/**
 * API Data Fetching Module
 * Handles communication with the backend API
 */

class DataAPI {
    constructor() {
        this.baseUrl = '/api';
    }

    /**
     * Fetch latest oceanographic data
     * @param {number} limit - Maximum number of records to fetch
     * @param {Object} options - Additional query options
     * @returns {Promise<Object>} API response with data
     */
    async fetchLatestData(limit = 1000, options = {}) {
        try {
            console.log('Fetching data from API...');
            
            const params = new URLSearchParams({
                limit: limit.toString(),
                ...options
            });
            
            const response = await fetch(`${this.baseUrl}/latest_data?${params}`, {
                cache: 'no-cache',
                headers: {
                    'Cache-Control': 'no-cache'
                }
            });
            
            console.log('Response status:', response.status);
            const result = await response.json();
            
            console.log('API Response:', {
                success: result.success, 
                count: result.count, 
                dataLength: result.data?.length
            });
            
            return result;
        } catch (error) {
            console.error('API fetch error:', error);
            throw new Error(`Connection Error: ${error.message}`);
        }
    }

    /**
     * Get system status
     * @returns {Promise<Object>} System status information
     */
    async getStatus() {
        try {
            const response = await fetch(`${this.baseUrl}/status`);
            return await response.json();
        } catch (error) {
            console.error('Status fetch error:', error);
            return { success: false, error: error.message };
        }
    }

    /**
     * Validate API response
     * @param {Object} result - API response
     * @returns {boolean} True if response is valid
     */
    validateResponse(result) {
        return result && result.success && Array.isArray(result.data);
    }
}

// Export for use in other modules
window.DataAPI = DataAPI;
