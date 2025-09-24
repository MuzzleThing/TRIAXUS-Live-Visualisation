#!/usr/bin/env python3
"""
TRIAXUS GPS Map Generator - Production Version
Complete offline map implementation with proper zoom scaling
"""

def get_map_html():
    """
    Generate complete HTML string for TRIAXUS GPS map.
    
    Returns:
        str: Complete HTML document with embedded CSS and JavaScript
    """
    
    html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TRIAXUS GPS Map</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        html, body {
            height: 100%;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }

        #map {
            width: 100%;
            height: 100vh;
            background: linear-gradient(135deg, #0D47A1 0%, #1565C0 25%, #1976D2 50%, #1E88E5 75%, #2196F3 100%);
            position: relative;
            overflow: hidden;
            cursor: grab;
        }

        #map:active {
            cursor: grabbing;
        }

        .map-container {
            width: 100%;
            height: 100%;
            position: relative;
            transition: transform 0.3s ease;
        }

        .sample-point {
            position: absolute;
            border-radius: 50%;
            border: 3px solid white;
            cursor: pointer;
            transition: all 0.3s ease;
            z-index: 100;
        }

        .sample-point:hover {
            transform: scale(1.3);
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.4);
        }

        .ship-marker {
            position: absolute;
            width: 40px;
            height: 40px;
            background: linear-gradient(135deg, #4caf50, #388e3c);
            border: 4px solid white;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            font-size: 20px;
            cursor: pointer;
            z-index: 200;
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0% { box-shadow: 0 4px 15px rgba(76, 175, 80, 0.6); }
            50% { box-shadow: 0 4px 25px rgba(76, 175, 80, 0.8); }
            100% { box-shadow: 0 4px 15px rgba(76, 175, 80, 0.6); }
        }

        .track-line {
            position: absolute;
            stroke: #64b5f6;
            stroke-width: 3;
            stroke-opacity: 0.8;
            stroke-dasharray: 10, 5;
            fill: none;
            z-index: 50;
        }

        .popup {
            position: absolute;
            background: rgba(15, 25, 40, 0.95);
            backdrop-filter: blur(15px);
            border: 1px solid rgba(100, 181, 246, 0.4);
            border-radius: 12px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
            color: white;
            padding: 16px;
            min-width: 200px;
            font-size: 14px;
            line-height: 1.6;
            z-index: 1000;
            display: none;
        }

        .popup.show {
            display: block;
        }

        .popup-title {
            font-size: 16px;
            font-weight: bold;
            color: #64b5f6;
            margin-bottom: 12px;
            padding-bottom: 8px;
            border-bottom: 1px solid rgba(100, 181, 246, 0.3);
        }

        .popup-row {
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
            padding: 4px 0;
        }

        .popup-label {
            color: #b3b3b3;
            font-size: 13px;
            font-weight: 500;
        }

        .popup-value {
            font-weight: 600;
            font-size: 14px;
        }

        .temp-value { color: #ff5722; }
        .salinity-value { color: #2196f3; }
        .depth-value { color: #ff9800; }
        .coordinate-value { color: #4caf50; }
        .time-value { color: #9c27b0; }

        .popup-close {
            position: absolute;
            top: 8px;
            right: 12px;
            background: none;
            border: none;
            color: white;
            font-size: 18px;
            cursor: pointer;
            padding: 0;
            width: 20px;
            height: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .popup-close:hover {
            color: #ff5722;
        }

        .custom-control-container {
            position: absolute;
            top: 10px;
            right: 10px;
            z-index: 1000;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }

        .control-button {
            background: rgba(15, 25, 40, 0.95);
            backdrop-filter: blur(15px);
            border: 1px solid rgba(100, 181, 246, 0.4);
            border-radius: 8px;
            color: white;
            padding: 10px 12px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 500;
            transition: all 0.3s ease;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            min-width: 120px;
            text-align: center;
        }

        .control-button:hover {
            background: rgba(25, 35, 50, 0.98);
            border-color: rgba(100, 181, 246, 0.6);
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(0, 0, 0, 0.4);
        }

        .zoom-controls {
            position: absolute;
            top: 10px;
            left: 10px;
            z-index: 1000;
            display: flex;
            flex-direction: column;
            background: rgba(255, 255, 255, 0.9);
            border-radius: 4px;
            overflow: hidden;
            box-shadow: 0 1px 5px rgba(0,0,0,0.65);
        }

        .zoom-button {
            width: 30px;
            height: 30px;
            background: white;
            border: none;
            border-bottom: 1px solid #ccc;
            cursor: pointer;
            font-size: 18px;
            font-weight: bold;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #333;
        }

        .zoom-button:last-child {
            border-bottom: none;
        }

        .zoom-button:hover {
            background: #f4f4f4;
        }

        .points-panel {
            position: absolute;
            top: 10px;
            right: 150px;
            z-index: 1000;
            background: rgba(15, 25, 40, 0.95);
            backdrop-filter: blur(15px);
            border: 1px solid rgba(100, 181, 246, 0.4);
            border-radius: 8px;
            padding: 15px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            width: 250px;
            max-height: 400px;
            overflow-y: auto;
            display: none;
        }

        .points-panel.show {
            display: block;
        }

        .panel-title {
            color: #64b5f6;
            font-size: 16px;
            font-weight: bold;
            margin-bottom: 15px;
            text-align: center;
            border-bottom: 1px solid rgba(100, 181, 246, 0.3);
            padding-bottom: 8px;
        }

        .point-item {
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(100, 181, 246, 0.2);
            border-radius: 6px;
            padding: 10px;
            margin-bottom: 8px;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .point-item:hover {
            background: rgba(100, 181, 246, 0.2);
            border-color: rgba(100, 181, 246, 0.4);
            transform: translateX(5px);
        }

        .point-number {
            color: #64b5f6;
            font-weight: bold;
            font-size: 14px;
        }

        .point-info {
            color: #b3b3b3;
            font-size: 12px;
            margin-top: 4px;
        }

        .point-temp {
            color: #ff5722;
        }

        .map-info {
            position: absolute;
            bottom: 10px;
            left: 10px;
            color: rgba(255, 255, 255, 0.8);
            font-size: 12px;
            background: rgba(0, 0, 0, 0.3);
            padding: 5px 10px;
            border-radius: 4px;
        }
    </style>
</head>
<body>
    <div id="map">
        <div id="map-container" class="map-container">
            <!-- Sample points and track will be generated here -->
        </div>
        
        <div class="zoom-controls">
            <button class="zoom-button" onclick="zoomIn()">+</button>
            <button class="zoom-button" onclick="zoomOut()">−</button>
        </div>
        
        <div class="map-info">
            Center: <span id="center-coords">0.0°, 0.0°</span> | 
            Zoom: <span id="zoom-level">8</span>
        </div>
    </div>
    
    <div class="custom-control-container">
        <button id="locate-btn" class="control-button">Locate Current</button>
        <button id="points-btn" class="control-button">Sample Points</button>
    </div>
    
    <div id="points-panel" class="points-panel">
        <div class="panel-title">Sample Points List</div>
        <div id="points-list"></div>
    </div>
    
    <div id="popup" class="popup">
        <button class="popup-close" onclick="closePopup()">×</button>
        <div id="popup-content"></div>
    </div>
    
    <script>
        // TRIAXUS GPS Map - Complete offline version
        
        // Map state
        var mapState = {
            center: [-33.8688, 151.2093],
            zoom: 4,
            minZoom: 4,
            maxZoom: 16,
            isDragging: false,
            startX: 0,
            startY: 0,
            startCenter: [-33.8688, 151.2093]
        };
        
        var isPointsPanelOpen = false;
        
        // Sample data - Pacific Ocean research cruise
        var sampleData = [
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
        
        // Improved coordinate conversion with proper scaling
        function latLngToPixel(lat, lng, zoom, centerLat, centerLng) {
            // Web Mercator projection with proper scaling
            var earthRadius = 6378137; // Earth radius in meters
            var pixelsPerMeter = Math.pow(2, zoom) / (2 * Math.PI * earthRadius / 256);
            
            // Convert to radians
            var latRad = lat * Math.PI / 180;
            var lngRad = lng * Math.PI / 180;
            var centerLatRad = centerLat * Math.PI / 180;
            var centerLngRad = centerLng * Math.PI / 180;
            
            // Web Mercator projection
            var x = earthRadius * lngRad;
            var y = earthRadius * Math.log(Math.tan(Math.PI / 4 + latRad / 2));
            
            var centerX = earthRadius * centerLngRad;
            var centerY = earthRadius * Math.log(Math.tan(Math.PI / 4 + centerLatRad / 2));
            
            // Convert to pixels
            var pixelX = (x - centerX) * pixelsPerMeter;
            var pixelY = (centerY - y) * pixelsPerMeter; // Flip Y axis
            
            return { x: pixelX, y: pixelY };
        }
        
        // Get temperature color
        function getTemperatureColor(temp) {
            if (temp >= 18) return '#f44336';
            if (temp >= 15) return '#ff9800';
            if (temp >= 12) return '#2196f3';
            return '#9c27b0';
        }
        
        // Update map display
        function updateMap() {
            var container = document.getElementById('map-container');
            var mapElement = document.getElementById('map');
            var mapWidth = mapElement.clientWidth;
            var mapHeight = mapElement.clientHeight;
            
            // Clear container
            container.innerHTML = '';
            
            // Create SVG for track line
            var svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
            svg.style.position = 'absolute';
            svg.style.width = '100%';
            svg.style.height = '100%';
            svg.style.top = '0';
            svg.style.left = '0';
            svg.style.zIndex = '50';
            
            // Create track line path
            var trackPath = '';
            for (var i = 0; i < sampleData.length; i++) {
                var point = latLngToPixel(
                    sampleData[i].lat, 
                    sampleData[i].lng, 
                    mapState.zoom, 
                    mapState.center[0], 
                    mapState.center[1]
                );
                var x = point.x + mapWidth / 2;
                var y = point.y + mapHeight / 2;
                
                if (i === 0) {
                    trackPath += 'M ' + x + ' ' + y;
                } else {
                    trackPath += ' L ' + x + ' ' + y;
                }
            }
            
            var trackElement = document.createElementNS('http://www.w3.org/2000/svg', 'path');
            trackElement.setAttribute('d', trackPath);
            trackElement.setAttribute('stroke', '#64b5f6');
            trackElement.setAttribute('stroke-width', '3');
            trackElement.setAttribute('stroke-opacity', '0.8');
            trackElement.setAttribute('stroke-dasharray', '10, 5');
            trackElement.setAttribute('fill', 'none');
            svg.appendChild(trackElement);
            container.appendChild(svg);
            
            // Add sample points
            for (var i = 0; i < sampleData.length; i++) {
                var data = sampleData[i];
                var point = latLngToPixel(
                    data.lat, 
                    data.lng, 
                    mapState.zoom, 
                    mapState.center[0], 
                    mapState.center[1]
                );
                
                var x = point.x + mapWidth / 2;
                var y = point.y + mapHeight / 2;
                
                var marker = document.createElement('div');
                marker.className = 'sample-point';
                marker.style.left = (x - 8) + 'px';
                marker.style.top = (y - 8) + 'px';
                marker.style.width = '16px';
                marker.style.height = '16px';
                marker.style.backgroundColor = getTemperatureColor(data.temp);
                marker.dataset.index = i;
                
                marker.onclick = function() {
                    showPopup(parseInt(this.dataset.index));
                };
                
                container.appendChild(marker);
            }
            
            // Add ship marker (last point)
            var lastPoint = sampleData[sampleData.length - 1];
            var shipPos = latLngToPixel(
                lastPoint.lat, 
                lastPoint.lng, 
                mapState.zoom, 
                mapState.center[0], 
                mapState.center[1]
            );
            var shipX = shipPos.x + mapWidth / 2;
            var shipY = shipPos.y + mapHeight / 2;
            
            var ship = document.createElement('div');
            ship.className = 'ship-marker';
            ship.innerHTML = '⚓';
            ship.style.left = (shipX - 20) + 'px';
            ship.style.top = (shipY - 20) + 'px';
            ship.onclick = function() {
                showShipPopup();
            };
            
            container.appendChild(ship);
            
            // Update coordinate display
            document.getElementById('center-coords').textContent = 
                mapState.center[0].toFixed(2) + '°, ' + mapState.center[1].toFixed(2) + '°';
            document.getElementById('zoom-level').textContent = mapState.zoom;
        }
        
        // Show popup
        function showPopup(index) {
            var data = sampleData[index];
            var popup = document.getElementById('popup');
            var content = document.getElementById('popup-content');
            
            content.innerHTML = 
                '<div class="popup-title">TRIAXUS Point #' + (index + 1) + '</div>' +
                '<div class="popup-row">' +
                    '<span class="popup-label">Time:</span>' +
                    '<span class="popup-value time-value">' + data.time + '</span>' +
                '</div>' +
                '<div class="popup-row">' +
                    '<span class="popup-label">Temperature:</span>' +
                    '<span class="popup-value temp-value">' + data.temp.toFixed(1) + '°C</span>' +
                '</div>' +
                '<div class="popup-row">' +
                    '<span class="popup-label">Salinity:</span>' +
                    '<span class="popup-value salinity-value">' + data.salinity.toFixed(1) + ' PSU</span>' +
                '</div>' +
                '<div class="popup-row">' +
                    '<span class="popup-label">Depth:</span>' +
                    '<span class="popup-value depth-value">' + data.depth + 'm</span>' +
                '</div>' +
                '<div class="popup-row">' +
                    '<span class="popup-label">Coordinates:</span>' +
                    '<span class="popup-value coordinate-value">' + 
                        data.lat.toFixed(4) + '°, ' + data.lng.toFixed(4) + '°</span>' +
                '</div>';
            
            popup.className = 'popup show';
            popup.style.left = '50%';
            popup.style.top = '30%';
            popup.style.transform = 'translate(-50%, -50%)';
        }
        
        // Show ship popup
        function showShipPopup() {
            var lastPoint = sampleData[sampleData.length - 1];
            var popup = document.getElementById('popup');
            var content = document.getElementById('popup-content');
            
            content.innerHTML = 
                '<div class="popup-title">⚓ You are here!</div>' +
                '<div class="popup-row">' +
                    '<span class="popup-label">Current Position:</span>' +
                    '<span class="popup-value coordinate-value">' + 
                        lastPoint.lat.toFixed(4) + '°, ' + lastPoint.lng.toFixed(4) + '°</span>' +
                '</div>' +
                '<div class="popup-row">' +
                    '<span class="popup-label">Last Sample:</span>' +
                    '<span class="popup-value time-value">' + lastPoint.time + '</span>' +
                '</div>' +
                '<div class="popup-row">' +
                    '<span class="popup-label">Total Points:</span>' +
                    '<span class="popup-value">' + sampleData.length + ' points</span>' +
                '</div>';
            
            popup.className = 'popup show';
            popup.style.left = '50%';
            popup.style.top = '30%';
            popup.style.transform = 'translate(-50%, -50%)';
        }
        
        // Close popup
        function closePopup() {
            document.getElementById('popup').className = 'popup';
        }
        
        // Zoom functions
        function zoomIn() {
            if (mapState.zoom < mapState.maxZoom) {
                mapState.zoom++;
                updateMap();
            }
        }
        
        function zoomOut() {
            if (mapState.zoom > mapState.minZoom) {
                mapState.zoom--;
                updateMap();
            }
        }
        
        // Map dragging
        function initMapEvents() {
            var map = document.getElementById('map');
            
            map.addEventListener('mousedown', function(e) {
                mapState.isDragging = true;
                mapState.startX = e.clientX;
                mapState.startY = e.clientY;
                mapState.startCenter = [mapState.center[0], mapState.center[1]];
                e.preventDefault();
            });
            
            document.addEventListener('mousemove', function(e) {
                if (!mapState.isDragging) return;
                
                var dx = e.clientX - mapState.startX;
                var dy = e.clientY - mapState.startY;
                
                // Improved drag sensitivity
                var earthRadius = 6378137;
                var pixelsPerMeter = Math.pow(2, mapState.zoom) / (2 * Math.PI * earthRadius / 256);
                var metersPerPixel = 1 / pixelsPerMeter;
                
                var deltaLat = dy * metersPerPixel * (180 / (Math.PI * earthRadius));
                var deltaLng = -dx * metersPerPixel * (180 / (Math.PI * earthRadius)) / Math.cos(mapState.startCenter[0] * Math.PI / 180);
                
                // Apply coordinate limits - hard boundaries for both directions
                var newLat = mapState.startCenter[0] + deltaLat;
                var newLng = mapState.startCenter[1] + deltaLng;
                
                // Limit latitude to -85 to 85 degrees
                newLat = Math.max(-85, Math.min(85, newLat));
                
                // Limit longitude to -180 to 180 degrees (hard boundary, no wrapping)
                newLng = Math.max(-180, Math.min(180, newLng));
                
                mapState.center = [newLat, newLng];
                
                updateMap();
            });
            
            document.addEventListener('mouseup', function() {
                mapState.isDragging = false;
            });
            
            map.addEventListener('wheel', function(e) {
                e.preventDefault();
                if (e.deltaY > 0) {
                    zoomOut();
                } else {
                    zoomIn();
                }
            });
        }
        
        // Control buttons
        function initControls() {
            document.getElementById('locate-btn').addEventListener('click', function() {
                var lastPoint = sampleData[sampleData.length - 1];
                mapState.center = [lastPoint.lat, lastPoint.lng];
                mapState.zoom = 12;
                updateMap();
                setTimeout(showShipPopup, 500);
            });
            
            document.getElementById('points-btn').addEventListener('click', function() {
                var panel = document.getElementById('points-panel');
                isPointsPanelOpen = !isPointsPanelOpen;
                panel.className = isPointsPanelOpen ? 'points-panel show' : 'points-panel';
            });
        }
        
        // Render points list
        function renderPointsList() {
            var pointsList = document.getElementById('points-list');
            pointsList.innerHTML = '';
            
            for (var i = 0; i < sampleData.length; i++) {
                var point = sampleData[i];
                var item = document.createElement('div');
                item.className = 'point-item';
                item.innerHTML = 
                    '<div class="point-number">Sample Point #' + (i + 1) + '</div>' +
                    '<div class="point-info">' +
                        'Time: ' + point.time + ' | ' +
                        '<span class="point-temp">' + point.temp.toFixed(1) + '°C</span>' +
                    '</div>' +
                    '<div class="point-info">' +
                        'Depth: ' + point.depth + 'm | Salinity: ' + point.salinity.toFixed(1) + ' PSU' +
                    '</div>';
                
                item.dataset.index = i;
                item.onclick = function() {
                    var index = parseInt(this.dataset.index);
                    var pointData = sampleData[index];
                    mapState.center = [pointData.lat, pointData.lng];
                    mapState.zoom = 12;
                    updateMap();
                    setTimeout(function() { showPopup(index); }, 500);
                    
                    isPointsPanelOpen = false;
                    document.getElementById('points-panel').className = 'points-panel';
                };
                
                pointsList.appendChild(item);
            }
        }
        
        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            initMapEvents();
            initControls();
            renderPointsList();
            updateMap();
        });
    </script>
</body>
</html>'''
    
    return html_content


if __name__ == "__main__":
    html_content = get_map_html()
    with open("triaxus_map.html", 'w', encoding='utf-8') as f:
        f.write(html_content)
