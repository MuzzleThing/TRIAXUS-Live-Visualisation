class SimpleTriaxusMap {
    constructor() {
        this.map = null;
        this.trackLine = null;
        this.samplePoints = [];
        this.shipMarker = null;
        
        this.init();
    }

    init() {
        this.initMap();
        this.addSampleData();
        this.addTrackLine();
        this.addShipMarker();
    }

    initMap() {
        // Initialize the map, default is Perth
        this.map = L.map('map', {
            center: [-32.0, 114.0], 
            zoom: 8
        });

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 18,
            minZoom: 2,
            attribution: '© OpenStreetMap contributors'
        }).addTo(this.map);
    }

    addSampleData() {
        // Adding simulated sampling points for demonstration
        const sampleData = [
            { lat: -31.2, lng: 114.3, temp: 19.5, salinity: 35.4, depth: 45, time: '08:15:30' },
            { lat: -31.8, lng: 114.1, temp: 18.2, salinity: 35.2, depth: 85, time: '08:42:15' },
            { lat: -32.3, lng: 113.8, temp: 17.1, salinity: 35.0, depth: 125, time: '09:18:45' },
            { lat: -31.6, lng: 113.5, temp: 16.8, salinity: 34.9, depth: 160, time: '09:51:20' },
            { lat: -30.9, lng: 114.2, temp: 20.1, salinity: 35.3, depth: 65, time: '10:28:10' },
            { lat: -32.7, lng: 114.4, temp: 15.9, salinity: 34.8, depth: 195, time: '11:05:35' },
            { lat: -31.4, lng: 113.2, temp: 16.2, salinity: 34.7, depth: 180, time: '11:42:50' },
            { lat: -30.6, lng: 113.9, temp: 19.8, salinity: 35.1, depth: 75, time: '12:20:15' },
            { lat: -32.1, lng: 113.1, temp: 15.4, salinity: 34.5, depth: 220, time: '12:58:40' },
            { lat: -33.2, lng: 114.8, temp: 14.7, salinity: 34.6, depth: 240, time: '13:35:25' },
            { lat: -30.3, lng: 114.6, temp: 21.2, salinity: 35.5, depth: 35, time: '14:12:10' },
            { lat: -31.9, lng: 112.8, temp: 14.8, salinity: 34.4, depth: 265, time: '14:49:55' }
        ];

        sampleData.forEach((point, index) => {
            this.addSamplePoint(point, index);
        });
    }

    addSamplePoint(data, index) {
        // Color determined by sea water temperature
        const color = this.getTemperatureColor(data.temp);
        
        // Create point marker
        const marker = L.circleMarker([data.lat, data.lng], {
            radius: 8,
            fillColor: color,
            color: 'white',
            weight: 3,
            opacity: 1,
            fillOpacity: 0.9
        });

        // Pop-up box information
        const popupContent = `
            <div class="data-popup-title">TRIAXUS Point #${index + 1}</div>
            <div class="data-row">
                <span class="data-label">Time:</span>
                <span class="data-value time-value">${data.time}</span>
            </div>
            <div class="data-row">
                <span class="data-label">Temperature:</span>
                <span class="data-value temp-value">${data.temp.toFixed(1)}°C</span>
            </div>
            <div class="data-row">
                <span class="data-label">Salinity:</span>
                <span class="data-value salinity-value">${data.salinity.toFixed(1)} PSU</span>
            </div>
            <div class="data-row">
                <span class="data-label">Depth:</span>
                <span class="data-value depth-value">${data.depth}m</span>
            </div>
            <div class="data-row">
                <span class="data-label">Coordinate:</span>
                <span class="data-value coordinate-value">${data.lat.toFixed(4)}°, ${data.lng.toFixed(4)}°</span>
            </div>
        `;

        marker.bindPopup(popupContent, {
            closeButton: true,
            maxWidth: 250
        });

        // Mouse events for popup
        marker.on('mouseover', function() {
            this.openPopup();
        });

        marker.on('mouseout', function() {
            setTimeout(() => {
                this.closePopup();
            }, 2000);
        });

        marker.addTo(this.map);
        this.samplePoints.push({ marker, data });
    }

    addTrackLine() {
        // Draw the track line connecting the sampling points
        const trackCoordinates = this.samplePoints.map(point => [point.data.lat, point.data.lng]);
        
        this.trackLine = L.polyline(trackCoordinates, {
            color: '#64b5f6',
            weight: 3,
            opacity: 0.7,
            dashArray: '10, 5',
            lineJoin: 'round',
            lineCap: 'round'
        }).addTo(this.map);
    }

    addShipMarker() {
        // ship marker for the latest sampling point
        const lastPoint = this.samplePoints[this.samplePoints.length - 1];
        if (!lastPoint) return;

        const shipIcon = L.divIcon({
            html: '<div class="ship-marker">🚢</div>',
            className: 'custom-ship-marker',
            iconSize: [32, 32],
            iconAnchor: [16, 16]
        });

        this.shipMarker = L.marker([lastPoint.data.lat, lastPoint.data.lng], {
            icon: shipIcon,
            zIndexOffset: 1000
        }).addTo(this.map);

        this.shipMarker.bindPopup(`
            <div class="data-popup-title">🚢 You are here!</div>
            <div class="data-row">
                <span class="data-label">Current location:</span>
                <span class="data-value coordinate-value">${lastPoint.data.lat.toFixed(4)}°, ${lastPoint.data.lng.toFixed(4)}°</span>
            </div>
            <div class="data-row">
                <span class="data-label">Final sampling:</span>
                <span class="data-value time-value">${lastPoint.data.time}</span>
            </div>
            <div class="data-row">
                <span class="data-label">Total points:</span>
                <span class="data-value">${this.samplePoints.length} points</span>
            </div>
        `);
    }

    getTemperatureColor(temp) {
        if (temp >= 18) return '#f44336';
        if (temp >= 15) return '#ff9800';
        if (temp >= 12) return '#2196f3';
        return '#9c27b0';
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new SimpleTriaxusMap();
});
