#!/usr/bin/env python3
"""
Unit tests for TRIAXUS GPS Map Generator
Tests the HTML generation and content validation
"""

import unittest
import re
from bs4 import BeautifulSoup
import tempfile
import os
from unittest.mock import patch, mock_open

# Import the module to test
import sys
sys.path.append('.')
from triaxus_map import get_map_html


class TestTriaxusMapGenerator(unittest.TestCase):
    """Test suite for TRIAXUS GPS Map Generator"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.html_content = get_map_html()
        self.soup = BeautifulSoup(self.html_content, 'html.parser')
    
    def test_get_map_html_returns_string(self):
        """Test that get_map_html returns a string"""
        self.assertIsInstance(self.html_content, str)
        self.assertGreater(len(self.html_content), 0)
    
    def test_html_structure_is_valid(self):
        """Test that generated HTML has proper structure"""
        # Check for essential HTML elements
        self.assertIsNotNone(self.soup.find('html'))
        self.assertIsNotNone(self.soup.find('head'))
        self.assertIsNotNone(self.soup.find('body'))
        self.assertIsNotNone(self.soup.find('title'))
        
        # Check title content
        title = self.soup.find('title')
        self.assertEqual(title.string, 'TRIAXUS GPS Map')
    
    def test_meta_tags_present(self):
        """Test that required meta tags are present"""
        meta_charset = self.soup.find('meta', attrs={'charset': 'UTF-8'})
        self.assertIsNotNone(meta_charset)
        
        meta_viewport = self.soup.find('meta', attrs={'name': 'viewport'})
        self.assertIsNotNone(meta_viewport)
        self.assertEqual(meta_viewport.get('content'), 'width=device-width, initial-scale=1.0')
    
    def test_css_styles_included(self):
        """Test that CSS styles are properly included"""
        style_tag = self.soup.find('style')
        self.assertIsNotNone(style_tag)
        
        css_content = style_tag.string
        
        # Check for key CSS classes
        essential_classes = [
            '#map', '.map-container', '.sample-point', '.ship-marker',
            '.track-line', '.popup', '.zoom-controls', '.control-button'
        ]
        
        for css_class in essential_classes:
            self.assertIn(css_class, css_content, f"CSS class {css_class} not found")
    
    def test_required_dom_elements_present(self):
        """Test that all required DOM elements are present"""
        # Main map container
        map_div = self.soup.find('div', id='map')
        self.assertIsNotNone(map_div)
        
        # Map container inside main div
        map_container = self.soup.find('div', id='map-container')
        self.assertIsNotNone(map_container)
        self.assertIn('map-container', map_container.get('class', []))
        
        # Control elements
        zoom_controls = self.soup.find('div', class_='zoom-controls')
        self.assertIsNotNone(zoom_controls)
        
        # Zoom buttons
        zoom_buttons = self.soup.find_all('button', class_='zoom-button')
        self.assertEqual(len(zoom_buttons), 2)
        self.assertEqual(zoom_buttons[0].string, '+')
        self.assertEqual(zoom_buttons[1].string, '−')
        
        # Custom controls
        control_container = self.soup.find('div', class_='custom-control-container')
        self.assertIsNotNone(control_container)
        
        locate_btn = self.soup.find('button', id='locate-btn')
        self.assertIsNotNone(locate_btn)
        self.assertEqual(locate_btn.string, 'Locate Current')
        
        points_btn = self.soup.find('button', id='points-btn')
        self.assertIsNotNone(points_btn)
        self.assertEqual(points_btn.string, 'Sample Points')
    
    def test_popup_elements_present(self):
        """Test that popup elements are properly structured"""
        popup = self.soup.find('div', id='popup')
        self.assertIsNotNone(popup)
        self.assertIn('popup', popup.get('class', []))
        
        popup_close = self.soup.find('button', class_='popup-close')
        self.assertIsNotNone(popup_close)
        self.assertEqual(popup_close.string, '×')
        
        popup_content = self.soup.find('div', id='popup-content')
        self.assertIsNotNone(popup_content)
    
    def test_points_panel_present(self):
        """Test that points panel is properly structured"""
        points_panel = self.soup.find('div', id='points-panel')
        self.assertIsNotNone(points_panel)
        self.assertIn('points-panel', points_panel.get('class', []))
        
        panel_title = self.soup.find('div', class_='panel-title')
        self.assertIsNotNone(panel_title)
        self.assertEqual(panel_title.string, 'Sample Points List')
        
        points_list = self.soup.find('div', id='points-list')
        self.assertIsNotNone(points_list)
    
    def test_map_info_display(self):
        """Test that map info display is present"""
        map_info = self.soup.find('div', class_='map-info')
        self.assertIsNotNone(map_info)
        
        center_coords = self.soup.find('span', id='center-coords')
        self.assertIsNotNone(center_coords)
        
        zoom_level = self.soup.find('span', id='zoom-level')
        self.assertIsNotNone(zoom_level)
    
    def test_javascript_functions_present(self):
        """Test that essential JavaScript functions are included"""
        script_tag = self.soup.find('script')
        self.assertIsNotNone(script_tag)
        
        js_content = script_tag.string
        
        # Check for essential JavaScript functions
        essential_functions = [
            'latLngToPixel', 'getTemperatureColor', 'updateMap',
            'showPopup', 'showShipPopup', 'closePopup',
            'zoomIn', 'zoomOut', 'initMapEvents', 'initControls'
        ]
        
        for function_name in essential_functions:
            pattern = rf'function\s+{function_name}\s*\('
            self.assertTrue(
                re.search(pattern, js_content),
                f"JavaScript function {function_name} not found"
            )
    
    def test_sample_data_structure(self):
        """Test that sample data is properly structured in JavaScript"""
        script_tag = self.soup.find('script')
        js_content = script_tag.string
        
        # Check for sample data array
        self.assertIn('var sampleData = [', js_content)
        
        # Check for expected data properties
        data_properties = ['lat', 'lng', 'temp', 'salinity', 'depth', 'time']
        for prop in data_properties:
            self.assertIn(prop, js_content, f"Sample data property {prop} not found")
    
    def test_map_state_initialization(self):
        """Test that map state is properly initialized"""
        script_tag = self.soup.find('script')
        js_content = script_tag.string
        
        # Check for map state object
        self.assertIn('var mapState = {', js_content)
        
        # Check for essential map state properties
        state_properties = ['center', 'zoom', 'minZoom', 'maxZoom', 'isDragging']
        for prop in state_properties:
            self.assertIn(prop, js_content, f"Map state property {prop} not found")
    
    def test_event_listeners_setup(self):
        """Test that event listeners are properly set up"""
        script_tag = self.soup.find('script')
        js_content = script_tag.string
        
        # Check for event listener setup
        event_patterns = [
            r'addEventListener\(["\']click["\']',
            r'addEventListener\(["\']mousedown["\']',
            r'addEventListener\(["\']mousemove["\']',
            r'addEventListener\(["\']mouseup["\']',
            r'addEventListener\(["\']wheel["\']',
            r'addEventListener\(["\']DOMContentLoaded["\']'
        ]
        
        for pattern in event_patterns:
            self.assertTrue(
                re.search(pattern, js_content),
                f"Event listener pattern {pattern} not found"
            )
    
    def test_onclick_handlers_present(self):
        """Test that onclick handlers are properly set"""
        # Check for onclick attributes in HTML
        zoom_in_btn = self.soup.find('button', onclick='zoomIn()')
        self.assertIsNotNone(zoom_in_btn)
        
        zoom_out_btn = self.soup.find('button', onclick='zoomOut()')
        self.assertIsNotNone(zoom_out_btn)
        
        close_btn = self.soup.find('button', onclick='closePopup()')
        self.assertIsNotNone(close_btn)
    
    def test_css_animations_present(self):
        """Test that CSS animations are defined"""
        style_tag = self.soup.find('style')
        css_content = style_tag.string
        
        # Check for keyframe animations
        self.assertIn('@keyframes pulse', css_content)
        self.assertIn('animation: pulse 2s infinite', css_content)
    
    def test_responsive_design_elements(self):
        """Test that responsive design elements are present"""
        style_tag = self.soup.find('style')
        css_content = style_tag.string
        
        # Check for responsive CSS properties
        responsive_elements = [
            'width: 100%',
            'height: 100vh',
            'box-sizing: border-box',
            'position: relative'
        ]
        
        for element in responsive_elements:
            self.assertIn(element, css_content)
    
    def test_color_scheme_consistency(self):
        """Test that color scheme is consistently applied"""
        style_tag = self.soup.find('style')
        css_content = style_tag.string
        
        # Check for consistent color usage
        expected_colors = [
            '#64b5f6',  # Primary blue
            '#4caf50',  # Green
            '#ff5722',  # Orange/red
            '#2196f3',  # Blue variants
        ]
        
        for color in expected_colors:
            self.assertIn(color, css_content, f"Color {color} not found in CSS")
    
    def test_accessibility_features(self):
        """Test for basic accessibility features"""
        # Check for proper cursor styles
        style_tag = self.soup.find('style')
        css_content = style_tag.string
        
        self.assertIn('cursor: pointer', css_content)
        self.assertIn('cursor: grab', css_content)
        self.assertIn('cursor: grabbing', css_content)
        
        # Check for focus and hover states
        self.assertIn(':hover', css_content)
    
    def test_svg_elements_for_tracks(self):
        """Test that SVG elements are properly set up for track lines"""
        script_tag = self.soup.find('script')
        js_content = script_tag.string
        
        # Check for SVG creation and manipulation
        svg_patterns = [
            r'createElementNS\(["\']http://www\.w3\.org/2000/svg["\']',
            r'setAttribute\(["\']stroke["\']',
            r'setAttribute\(["\']stroke-width["\']',
            r'setAttribute\(["\']d["\']'
        ]
        
        for pattern in svg_patterns:
            self.assertTrue(
                re.search(pattern, js_content),
                f"SVG pattern {pattern} not found"
            )


class TestTriaxusMapFileOperations(unittest.TestCase):
    """Test file operations and integration"""
    
    def test_html_file_creation(self):
        """Test HTML file creation when run as main"""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = os.path.join(temp_dir, 'test_triaxus_map.html')
            
            # Mock the file operations
            with patch('builtins.open', mock_open()) as mock_file:
                # Simulate running as main
                html_content = get_map_html()
                
                # Simulate file writing
                with open(test_file, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                
                # Verify the mock was called correctly
                mock_file.assert_called_with(test_file, 'w', encoding='utf-8')
    
    def test_html_content_length(self):
        """Test that generated HTML content has reasonable length"""
        html_content = get_map_html()
        
        # HTML should be substantial (at least 20KB)
        self.assertGreater(len(html_content), 20000)
        
        # But not unreasonably large (less than 200KB)
        self.assertLess(len(html_content), 200000)
    
    def test_html_content_encoding(self):
        """Test that HTML content is properly encoded"""
        html_content = get_map_html()
        
        # Should be valid UTF-8
        try:
            html_content.encode('utf-8')
            encoding_valid = True
        except UnicodeEncodeError:
            encoding_valid = False
        
        self.assertTrue(encoding_valid, "HTML content is not valid UTF-8")


class TestTriaxusMapValidation(unittest.TestCase):
    """Test content validation and data integrity"""
    
    def setUp(self):
        self.html_content = get_map_html()
    
    def test_no_placeholder_content(self):
        """Test that there are no placeholder or TODO comments"""
        placeholders = ['TODO', 'FIXME', 'XXX', 'PLACEHOLDER', 'TBD']
        
        for placeholder in placeholders:
            self.assertNotIn(placeholder, self.html_content.upper())
    
    def test_coordinate_bounds_validation(self):
        """Test that coordinates in sample data are within valid bounds"""
        # Extract sample data from JavaScript
        import re
        lat_matches = re.findall(r'lat:\s*(-?\d+\.?\d*)', self.html_content)
        lng_matches = re.findall(r'lng:\s*(-?\d+\.?\d*)', self.html_content)
        
        for lat_str in lat_matches:
            lat = float(lat_str)
            self.assertGreaterEqual(lat, -90, f"Latitude {lat} is below -90")
            self.assertLessEqual(lat, 90, f"Latitude {lat} is above 90")
        
        for lng_str in lng_matches:
            lng = float(lng_str)
            self.assertGreaterEqual(lng, -180, f"Longitude {lng} is below -180")
            self.assertLessEqual(lng, 180, f"Longitude {lng} is above 180")
    
    def test_temperature_data_validation(self):
        """Test that temperature data is within reasonable ranges"""
        import re
        temp_matches = re.findall(r'temp:\s*(-?\d+\.?\d*)', self.html_content)
        
        for temp_str in temp_matches:
            temp = float(temp_str)
            # Ocean temperatures should be reasonable (-2°C to 35°C)
            self.assertGreaterEqual(temp, -2, f"Temperature {temp} is unreasonably low")
            self.assertLessEqual(temp, 35, f"Temperature {temp} is unreasonably high")
    
    def test_depth_data_validation(self):
        """Test that depth data is positive and reasonable"""
        import re
        depth_matches = re.findall(r'depth:\s*(\d+)', self.html_content)
        
        for depth_str in depth_matches:
            depth = int(depth_str)
            self.assertGreater(depth, 0, f"Depth {depth} should be positive")
            self.assertLess(depth, 11000, f"Depth {depth} exceeds ocean maximum")
    
    def test_time_format_validation(self):
        """Test that time format is consistent"""
        import re
        time_matches = re.findall(r"time:\s*['\"]([^'\"]+)['\"]", self.html_content)
        
        time_pattern = re.compile(r'^\d{2}:\d{2}:\d{2}$')
        
        for time_str in time_matches:
            self.assertTrue(
                time_pattern.match(time_str),
                f"Time format {time_str} doesn't match HH:MM:SS"
            )


if __name__ == '__main__':
    # Create a test suite combining all test classes
    test_classes = [
        TestTriaxusMapGenerator,
        TestTriaxusMapFileOperations, 
        TestTriaxusMapValidation
    ]
    
    suite = unittest.TestSuite()
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run the tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print(f"\nFAILURES:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback.split(chr(10))[-2]}")
    
    if result.errors:
        print(f"\nERRORS:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback.split(chr(10))[-2]}")
