/**
 * Timezone Handling Module
 * Manages timezone conversions and display formatting
 */

class TimezoneManager {
    constructor() {
        this.selectedTimezone = 'browser';
    }

    /**
     * Set the selected timezone
     * @param {string} timezone - Timezone identifier
     */
    setTimezone(timezone) {
        this.selectedTimezone = timezone || 'browser';
    }

    /**
     * Get the selected timezone
     * @returns {string} Current timezone
     */
    getTimezone() {
        return this.selectedTimezone;
    }

    /**
     * Convert ISO time string to display date in selected timezone
     * @param {string} isoStr - ISO time string (e.g., "2025-10-08T13:47:07Z")
     * @returns {Date} Converted date object
     */
    toDisplayDate(isoStr) {
        const utc = new Date(isoStr); // absolute instant (API is UTC Z)
        
        if (!this.selectedTimezone || this.selectedTimezone === 'UTC') {
            // For UTC mode, show actual UTC time
            const utcYear = utc.getUTCFullYear();
            const utcMonth = utc.getUTCMonth();
            const utcDate = utc.getUTCDate();
            const utcHours = utc.getUTCHours();
            const utcMinutes = utc.getUTCMinutes();
            const utcSeconds = utc.getUTCSeconds();
            
            // Create a date that displays UTC time as local time
            const adjustedDate = new Date(utcYear, utcMonth, utcDate, utcHours, utcMinutes, utcSeconds);
            
            console.log(`UTC conversion: ${isoStr} -> ${adjustedDate.toLocaleString()}`);
            return adjustedDate;
        }
        
        if (this.selectedTimezone === 'browser') {
            // For browser local, let browser handle conversion
            return utc;
        }
        
        // For other timezones, use Intl.DateTimeFormat
        try {
            const formatter = new Intl.DateTimeFormat('en-CA', {
                timeZone: this.selectedTimezone,
                year: 'numeric',
                month: '2-digit', 
                day: '2-digit',
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit',
                hour12: false
            });
            
            const parts = formatter.formatToParts(utc);
            const year = parts.find(p => p.type === 'year').value;
            const month = parts.find(p => p.type === 'month').value;
            const day = parts.find(p => p.type === 'day').value;
            const hour = parts.find(p => p.type === 'hour').value;
            const minute = parts.find(p => p.type === 'minute').value;
            const second = parts.find(p => p.type === 'second').value;
            
            return new Date(year, month - 1, day, hour, minute, second);
        } catch (e) {
            console.warn(`Timezone conversion failed for ${this.selectedTimezone}:`, e);
            return utc;
        }
    }

    /**
     * Get display timezone label with offset
     * @returns {string} Formatted timezone label
     */
    getDisplayTimezoneLabel() {
        if (this.selectedTimezone && this.selectedTimezone !== 'browser') {
            try {
                const fmt = new Intl.DateTimeFormat('en-US', { 
                    timeZone: this.selectedTimezone, 
                    timeZoneName: 'shortOffset' 
                });
                const parts = fmt.formatToParts(new Date());
                const tzPart = parts.find(p => p.type === 'timeZoneName');
                const offset = tzPart ? tzPart.value.replace('GMT', 'UTC') : '';
                return `${this.selectedTimezone} (${offset})`;
            } catch (e) {
                return `${this.selectedTimezone}`;
            }
        }
        
        // Browser local
        try {
            const tzName = Intl.DateTimeFormat().resolvedOptions().timeZone || 'Local';
            const now = new Date();
            const offsetMin = -now.getTimezoneOffset();
            const sign = offsetMin >= 0 ? '+' : '-';
            const absMin = Math.abs(offsetMin);
            const hours = String(Math.floor(absMin / 60)).padStart(1, '0');
            const mins = String(absMin % 60).padStart(2, '0');
            return `${tzName} (UTC${sign}${hours}${mins === '00' ? '' : ':' + mins})`;
        } catch (e) {
            const offsetMin = -new Date().getTimezoneOffset();
            const sign = offsetMin >= 0 ? '+' : '-';
            const hours = Math.floor(Math.abs(offsetMin) / 60);
            return `Local (UTC${sign}${hours})`;
        }
    }

    /**
     * Get time range title for plots
     * @param {string} timeGranularity - Time range (e.g., '1h', '24h')
     * @returns {string} Formatted title
     */
    getTimeRangeTitle(timeGranularity) {
        const displayTz = this.selectedTimezone === 'UTC' ? 'UTC' : this.getDisplayTimezoneLabel();
        return timeGranularity === 'all' ? 
               `All Data (${displayTz})` : 
               `Last ${timeGranularity.toUpperCase()} (${displayTz})`;
    }
}

// Export for use in other modules
window.TimezoneManager = TimezoneManager;
