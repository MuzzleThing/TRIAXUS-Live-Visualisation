"""
TRIAXUS Plot Test Data Generator

A simple data generator specifically designed for testing plot functionality.
Generates realistic test data to verify plotting capabilities before backend integration.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Optional, List

from ..core.config import ConfigManager


class PlotTestDataGenerator:
    """Simple data generator for testing plot functionality"""

    def __init__(self, seed: int = None):
        """Initialize with a random seed for reproducible test data"""
        # Load configuration
        self.config_manager = ConfigManager()
        
        # Get seed from config or use default
        if seed is None:
            try:
                # Try to get random_seed from config manager
                seed = self.config_manager.data_config_manager.get_data_generation_config().get("random_seed", 42)
            except:
                try:
                    # Fallback: try direct YAML access
                    if hasattr(self.config_manager, '_yaml_config') and self.config_manager._yaml_config:
                        seed = self.config_manager._yaml_config.get("data_generation", {}).get("random_seed", 42)
                    else:
                        seed = 42
                except:
                    seed = 42  # Final fallback

        np.random.seed(seed)
        self.config = self.config_manager

    def generate_plot_test_data(
        self,
        duration_hours: float = None,
        points_per_hour: int = None,
        start_time: Optional[datetime] = None,
    ) -> pd.DataFrame:
        """
        Generate test data for plot functionality testing

        Args:
            duration_hours: How many hours of test data to generate
            points_per_hour: How many data points per hour
            start_time: When to start the test data (default: now)

        Returns:
            DataFrame with test data for plotting
        """
        # Get default values from config
        if self.config is not None:
            try:
                data_gen_config = self.config.data_config_manager.get_data_generation_config()
            except:
                data_gen_config = {}
        else:
            data_gen_config = {}

        if duration_hours is None:
            duration_hours = data_gen_config.get("default_duration_hours", 2.0)
        if points_per_hour is None:
            points_per_hour = data_gen_config.get("default_points_per_hour", 60)

        if start_time is None:
            start_time = datetime.now()

        # Calculate total points
        total_points = int(duration_hours * points_per_hour)

        # Generate time series
        time_series = [
            start_time + timedelta(hours=i / points_per_hour)
            for i in range(total_points)
        ]

        # Generate simple depth profile (undulating)
        depth_series = [
            50 + 30 * np.sin(i * 0.1) + np.random.normal(0, 2)
            for i in range(total_points)
        ]

        # Generate GPS track (simple cruise path - default location)
        lat_series = [
            35.0 + 0.1 * np.sin(i * 0.02) + np.random.normal(0, 0.01)
            for i in range(total_points)
        ]
        lon_series = [
            -120.0 + 0.2 * i / total_points + np.random.normal(0, 0.01)
            for i in range(total_points)
        ]

        # Generate oceanographic variables with realistic patterns
        temperature = [
            15.0 + 4.0 * np.sin(i * 0.05) + np.random.normal(0, 0.5)
            for i in range(total_points)
        ]
        salinity = [
            35.0 + 1.5 * np.sin(i * 0.03) + np.random.normal(0, 0.2)
            for i in range(total_points)
        ]
        oxygen = [
            8.0 + 2.0 * np.sin(i * 0.04) + np.random.normal(0, 0.3)
            for i in range(total_points)
        ]
        fluorescence = [
            0.5 + 0.3 * np.sin(i * 0.06) + np.random.normal(0, 0.1)
            for i in range(total_points)
        ]
        ph = [
            8.1 + 0.2 * np.sin(i * 0.02) + np.random.normal(0, 0.05)
            for i in range(total_points)
        ]

        # Create DataFrame
        data = pd.DataFrame(
            {
                "time": time_series,
                "depth": depth_series,
                "latitude": lat_series,
                "longitude": lon_series,
                "tv290C": temperature,  # Temperature
                "sal00": salinity,  # Salinity
                "sbeox0Mm_L": oxygen,  # Oxygen
                "flECO-AFL": fluorescence,  # Fluorescence
                "ph": ph,  # pH
            }
        )

        return data

    def generate_daily_plot_data(self, date: str = "2024-01-01") -> pd.DataFrame:
        """
        Generate a full day of test data for plot testing (24 hours)

        Args:
            date: Date string in YYYY-MM-DD format

        Returns:
            DataFrame with 24 hours of test data for plotting
        """
        start_time = datetime.strptime(date, "%Y-%m-%d")
        return self.generate_plot_test_data(
            duration_hours=24.0, points_per_hour=10, start_time=start_time
        )

    def generate_quick_plot_data(self, hours: float = 1.0) -> pd.DataFrame:
        """
        Generate quick test data for fast plot testing

        Args:
            hours: Duration in hours

        Returns:
            DataFrame with quick test data for plotting
        """
        return self.generate_plot_test_data(duration_hours=hours, points_per_hour=30)

    def generate_map_trajectory_data(
        self,
        duration_hours: float = 2.0,
        points_per_hour: int = 60,
        start_time: Optional[datetime] = None,
        region: str = "australia",
    ) -> pd.DataFrame:
        """
        Generate trajectory data specifically for map plotting

        Args:
            duration_hours: How many hours of trajectory data to generate
            points_per_hour: How many data points per hour
            start_time: When to start the trajectory (default: now)
            region: Region for trajectory ('australia', 'custom')

        Returns:
            DataFrame with trajectory data for map plotting
        """
        if start_time is None:
            start_time = datetime.now()

        # Calculate total points
        total_points = int(duration_hours * points_per_hour)

        # Generate time series
        time_series = [
            start_time + timedelta(hours=i / points_per_hour)
            for i in range(total_points)
        ]

        # Generate trajectory based on region
        if region == "australia":
            # Australian waters trajectory (Great Barrier Reef area)
            # Start near Cairns, move north along the reef
            start_lat, start_lon = -16.9, 145.8  # Near Cairns
            lat_series = [
                start_lat
                + 0.3 * i / total_points
                + 0.1 * np.sin(i * 0.05)
                + np.random.normal(0, 0.005)
                for i in range(total_points)
            ]
            lon_series = [
                start_lon
                + 0.5 * i / total_points
                + 0.05 * np.cos(i * 0.03)
                + np.random.normal(0, 0.005)
                for i in range(total_points)
            ]
        else:
            # Default to a simple cruise path
            lat_series = [
                35.0 + 0.1 * np.sin(i * 0.02) + np.random.normal(0, 0.01)
                for i in range(total_points)
            ]
            lon_series = [
                -120.0 + 0.2 * i / total_points + np.random.normal(0, 0.01)
                for i in range(total_points)
            ]

        # Generate depth profile (for trajectory context)
        depth_series = [
            50 + 30 * np.sin(i * 0.1) + np.random.normal(0, 2)
            for i in range(total_points)
        ]

        # Generate basic oceanographic variables (for context, not the main focus)
        temperature = [
            15.0 + 4.0 * np.sin(i * 0.05) + np.random.normal(0, 0.5)
            for i in range(total_points)
        ]
        salinity = [
            35.0 + 1.5 * np.sin(i * 0.03) + np.random.normal(0, 0.2)
            for i in range(total_points)
        ]

        # Create DataFrame focused on trajectory
        data = pd.DataFrame(
            {
                "time": time_series,
                "latitude": lat_series,
                "longitude": lon_series,
                "depth": depth_series,
                "tv290C": temperature,  # Temperature (for context)
                "sal00": salinity,  # Salinity (for context)
            }
        )

        return data

    def get_plot_test_info(self, data: pd.DataFrame) -> dict:
        """
        Get information about the generated plot test data

        Args:
            data: DataFrame to analyze

        Returns:
            Dictionary with basic plot test data information
        """
        return {
            "total_points": len(data),
            "duration_hours": (data["time"].max() - data["time"].min()).total_seconds()
            / 3600,
            "depth_range": f"{data['depth'].min():.1f} - {data['depth'].max():.1f} m",
            "temperature_range": f"{data['tv290C'].min():.1f} - {data['tv290C'].max():.1f} °C",
            "salinity_range": f"{data['sal00'].min():.1f} - {data['sal00'].max():.1f} PSU",
            "columns": list(data.columns),
        }


# Simple convenience functions for plot testing
def create_plot_test_data(hours: float = 2.0) -> pd.DataFrame:
    """Create test data for plot functionality testing - simplest way to get started"""
    generator = PlotTestDataGenerator()
    return generator.generate_plot_test_data(duration_hours=hours)


def create_daily_plot_data(date: str = "2024-01-01") -> pd.DataFrame:
    """Create daily test data for plot testing - simplest way to get a full day"""
    generator = PlotTestDataGenerator()
    return generator.generate_daily_plot_data(date)


def create_quick_plot_data() -> pd.DataFrame:
    """Create quick test data for fast plot testing"""
    generator = PlotTestDataGenerator()
    return generator.generate_quick_plot_data(hours=0.5)


def create_map_trajectory_data(
    region: str = "australia", hours: float = 2.0
) -> pd.DataFrame:
    """Create trajectory data specifically for map plotting"""
    generator = PlotTestDataGenerator()
    return generator.generate_map_trajectory_data(duration_hours=hours, region=region)
