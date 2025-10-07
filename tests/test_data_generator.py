"""
Test data generator for creating high-quality test datasets
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import random


class TestDataGenerator:
    """Generate high-quality test data for TRIAXUS system"""
    
    def __init__(self, seed: Optional[int] = None):
        """Initialize test data generator
        
        Args:
            seed: Random seed for reproducible data generation
        """
        if seed is not None:
            np.random.seed(seed)
            random.seed(seed)
        
        # Oceanographic data ranges (realistic values)
        self.data_ranges = {
            'depth': (0, 1000),  # meters
            'temperature': (-2, 35),  # degrees Celsius
            'salinity': (30, 40),  # PSU
            'oxygen': (0, 15),  # mg/L
            'fluorescence': (0, 10),  # mg/m^3
            'ph': (7.0, 9.0),  # pH units
            'latitude': (-90, 90),  # degrees
            'longitude': (-180, 180),  # degrees
        }
    
    def generate_oceanographic_data(
        self,
        num_records: int = 100,
        start_time: Optional[datetime] = None,
        time_interval: timedelta = timedelta(minutes=1),
        depth_profile: bool = True,
        add_noise: bool = True,
        add_missing_values: bool = False,
        missing_ratio: float = 0.05
    ) -> pd.DataFrame:
        """Generate realistic oceanographic data
        
        Args:
            num_records: Number of data records to generate
            start_time: Start time for data generation
            time_interval: Time interval between records
            depth_profile: Whether to generate depth profile data
            add_noise: Whether to add realistic noise
            add_missing_values: Whether to add missing values
            missing_ratio: Ratio of missing values to add
        
        Returns:
            DataFrame with oceanographic data
        """
        if start_time is None:
            start_time = datetime.now() - timedelta(hours=num_records)
        
        # Generate time series
        times = [start_time + i * time_interval for i in range(num_records)]
        
        if depth_profile:
            # Generate depth profile data (deeper = colder, higher salinity)
            depths = np.linspace(0, 100, num_records)
            temperatures = self._generate_temperature_profile(depths, add_noise)
            salinities = self._generate_salinity_profile(depths, add_noise)
            oxygen_values = self._generate_oxygen_profile(depths, add_noise)
        else:
            # Generate time series data
            depths = np.random.uniform(0, 50, num_records)
            temperatures = self._generate_temperature_timeseries(times, add_noise)
            salinities = self._generate_salinity_timeseries(times, add_noise)
            oxygen_values = self._generate_oxygen_timeseries(times, add_noise)
        
        # Generate other variables
        fluorescence = self._generate_fluorescence(depths, temperatures, add_noise)
        ph_values = self._generate_ph(temperatures, salinities, add_noise)
        
        # Generate location data (simulate vessel movement)
        latitudes, longitudes = self._generate_trajectory(num_records)
        
        # Create DataFrame
        data = pd.DataFrame({
            'time': times,
            'depth': depths,
            'latitude': latitudes,
            'longitude': longitudes,
            'tv290c': temperatures,
            'sal00': salinities,
            'sbeox0mm_l': oxygen_values,
            'fleco_afl': fluorescence,
            'ph': ph_values
        })
        
        # Add missing values if requested
        if add_missing_values:
            data = self._add_missing_values(data, missing_ratio)
        
        return data
    
    def _generate_temperature_profile(self, depths: np.ndarray, add_noise: bool) -> np.ndarray:
        """Generate temperature profile (deeper = colder)"""
        # Typical ocean temperature profile
        surface_temp = 25.0
        deep_temp = 2.0
        thermocline_depth = 50.0
        
        temperatures = surface_temp - (surface_temp - deep_temp) * np.tanh(depths / thermocline_depth)
        
        if add_noise:
            noise = np.random.normal(0, 0.5, len(depths))
            temperatures += noise
        
        return np.clip(temperatures, *self.data_ranges['temperature'])
    
    def _generate_salinity_profile(self, depths: np.ndarray, add_noise: bool) -> np.ndarray:
        """Generate salinity profile"""
        # Typical ocean salinity profile
        surface_salinity = 35.0
        deep_salinity = 34.8
        
        salinities = surface_salinity - (surface_salinity - deep_salinity) * np.exp(-depths / 100.0)
        
        if add_noise:
            noise = np.random.normal(0, 0.1, len(depths))
            salinities += noise
        
        return np.clip(salinities, *self.data_ranges['salinity'])
    
    def _generate_oxygen_profile(self, depths: np.ndarray, add_noise: bool) -> np.ndarray:
        """Generate oxygen profile (deeper = lower oxygen)"""
        # Typical ocean oxygen profile
        surface_oxygen = 8.0
        deep_oxygen = 2.0
        
        oxygen_values = surface_oxygen - (surface_oxygen - deep_oxygen) * np.exp(-depths / 200.0)
        
        if add_noise:
            noise = np.random.normal(0, 0.3, len(depths))
            oxygen_values += noise
        
        return np.clip(oxygen_values, *self.data_ranges['oxygen'])
    
    def _generate_temperature_timeseries(self, times: List[datetime], add_noise: bool) -> np.ndarray:
        """Generate temperature time series"""
        # Simulate daily temperature cycle
        base_temp = 20.0
        daily_cycle = 3.0 * np.sin(2 * np.pi * np.array([t.hour for t in times]) / 24)
        seasonal_cycle = 5.0 * np.sin(2 * np.pi * np.array([t.timetuple().tm_yday for t in times]) / 365)
        
        temperatures = base_temp + daily_cycle + seasonal_cycle
        
        if add_noise:
            noise = np.random.normal(0, 0.5, len(times))
            temperatures += noise
        
        return np.clip(temperatures, *self.data_ranges['temperature'])
    
    def _generate_salinity_timeseries(self, times: List[datetime], add_noise: bool) -> np.ndarray:
        """Generate salinity time series"""
        # Salinity is more stable than temperature
        base_salinity = 35.0
        variation = 0.5 * np.sin(2 * np.pi * np.array([t.timetuple().tm_yday for t in times]) / 365)
        
        salinities = base_salinity + variation
        
        if add_noise:
            noise = np.random.normal(0, 0.05, len(times))
            salinities += noise
        
        return np.clip(salinities, *self.data_ranges['salinity'])
    
    def _generate_oxygen_timeseries(self, times: List[datetime], add_noise: bool) -> np.ndarray:
        """Generate oxygen time series"""
        # Oxygen varies with temperature and biological activity
        base_oxygen = 6.0
        daily_cycle = 1.0 * np.sin(2 * np.pi * np.array([t.hour for t in times]) / 24)
        
        oxygen_values = base_oxygen + daily_cycle
        
        if add_noise:
            noise = np.random.normal(0, 0.3, len(times))
            oxygen_values += noise
        
        return np.clip(oxygen_values, *self.data_ranges['oxygen'])
    
    def _generate_fluorescence(self, depths: np.ndarray, temperatures: np.ndarray, add_noise: bool) -> np.ndarray:
        """Generate fluorescence data (correlated with temperature and depth)"""
        # Fluorescence is higher in surface waters and warmer temperatures
        surface_effect = np.exp(-depths / 20.0)
        temperature_effect = (temperatures - 10) / 20.0
        
        fluorescence = 2.0 * surface_effect * (1 + temperature_effect)
        
        if add_noise:
            noise = np.random.normal(0, 0.2, len(depths))
            fluorescence += noise
        
        return np.clip(fluorescence, *self.data_ranges['fluorescence'])
    
    def _generate_ph(self, temperatures: np.ndarray, salinities: np.ndarray, add_noise: bool) -> np.ndarray:
        """Generate pH data (correlated with temperature and salinity)"""
        # pH is influenced by temperature and salinity
        base_ph = 8.1
        temp_effect = (temperatures - 20) * 0.01
        sal_effect = (salinities - 35) * 0.02
        
        ph_values = base_ph + temp_effect + sal_effect
        
        if add_noise:
            noise = np.random.normal(0, 0.05, len(temperatures))
            ph_values += noise
        
        return np.clip(ph_values, *self.data_ranges['ph'])
    
    def _generate_trajectory(self, num_records: int) -> Tuple[np.ndarray, np.ndarray]:
        """Generate vessel trajectory"""
        # Start in Pacific Ocean
        start_lat = 45.0
        start_lon = -120.0
        
        # Simulate vessel movement
        lat_drift = np.random.normal(0, 0.01, num_records)
        lon_drift = np.random.normal(0, 0.01, num_records)
        
        latitudes = start_lat + np.cumsum(lat_drift)
        longitudes = start_lon + np.cumsum(lon_drift)
        
        return np.clip(latitudes, *self.data_ranges['latitude']), np.clip(longitudes, *self.data_ranges['longitude'])
    
    def _add_missing_values(self, data: pd.DataFrame, missing_ratio: float) -> pd.DataFrame:
        """Add missing values to data"""
        data_copy = data.copy()
        
        for column in data_copy.columns:
            if column != 'time':  # Don't add missing values to time
                mask = np.random.random(len(data_copy)) < missing_ratio
                data_copy.loc[mask, column] = np.nan
        
        return data_copy
    
    def generate_problematic_data(self, num_records: int = 50) -> pd.DataFrame:
        """Generate problematic data for testing error handling"""
        data = self.generate_oceanographic_data(num_records)
        
        # Add problematic values
        problematic_indices = np.random.choice(len(data), size=min(10, len(data)), replace=False)
        
        for idx in problematic_indices:
            # Add invalid values
            if np.random.random() < 0.3:
                data.loc[idx, 'depth'] = -1000  # Invalid depth
            if np.random.random() < 0.3:
                data.loc[idx, 'tv290c'] = 100  # Invalid temperature
            if np.random.random() < 0.3:
                data.loc[idx, 'sal00'] = 'invalid'  # Invalid salinity
            if np.random.random() < 0.3:
                data.loc[idx, 'sbeox0mm_l'] = np.nan  # Missing oxygen
        
        return data
    
    def generate_duplicate_data(self, num_records: int = 30) -> pd.DataFrame:
        """Generate data with duplicates for testing deduplication"""
        base_data = self.generate_oceanographic_data(num_records // 2)
        
        # Duplicate some records
        duplicates = base_data.sample(n=num_records // 2, replace=True)
        
        # Combine and shuffle
        combined_data = pd.concat([base_data, duplicates], ignore_index=True)
        combined_data = combined_data.sample(frac=1).reset_index(drop=True)
        
        return combined_data
    
    def generate_large_dataset(self, num_records: int = 10000) -> pd.DataFrame:
        """Generate large dataset for performance testing"""
        return self.generate_oceanographic_data(
            num_records=num_records,
            time_interval=timedelta(seconds=1),
            depth_profile=False,
            add_noise=True,
            add_missing_values=False
        )
    
    def generate_cnv_test_data(self, num_records: int = 100) -> str:
        """Generate CNV file content for testing"""
        data = self.generate_oceanographic_data(num_records)
        
        # Create CNV header
        header = """* Sea-Bird SBE 19plus V 2.2.2  SERIAL NO. 01907508
* 05-Jan-2024 12:00:00
* temperature: SBE 3F
* conductivity: SBE 4C
* pressure: SBE 29
* time: SBE 9
* status: SBE 9
* file_type: ascii
* nquan: 7
* nvalues: {num_records}
* columns = time, depSM, t090C, c0S/m, sal00, sbeox0Mm/L, flECO-AFL
# name 0 = timeS: Time, Elapsed [seconds]
# name 1 = depSM: Depth [salt water, m]
# name 2 = t090C: Temperature [ITS-90, deg C]
# name 3 = c0S/m: Conductivity [S/m]
# name 4 = sal00: Salinity, Practical [PSU]
# name 5 = sbeox0Mm/L: Oxygen, SBE 43 [umol/kg]
# name 6 = flECO-AFL: Fluorescence, WET Labs ECO-AFL/FL [mg/m^3]
*END*
""".format(num_records=num_records)
        
        # Create data lines
        data_lines = []
        for i, row in data.iterrows():
            time_seconds = i * 0.25
            line = f"{time_seconds:.6f}, {row['depth']:.3f}, {row['tv290c']:.4f}, 3.45678, {row['sal00']:.4f}, {row['sbeox0mm_l']:.4f}, {row['fleco_afl']:.4f}"
            data_lines.append(line)
        
        return header + "\n".join(data_lines)


def test_data_generator():
    """Test the data generator"""
    print("Testing data generator...")
    
    generator = TestDataGenerator(seed=42)
    
    # Test basic data generation
    data = generator.generate_oceanographic_data(100)
    assert len(data) == 100, "Should generate 100 records"
    assert len(data.columns) == 9, "Should have 9 columns"
    
    # Test data ranges
    assert data['depth'].min() >= 0, "Depth should be non-negative"
    assert data['tv290c'].min() >= -2, "Temperature should be within range"
    assert data['sal00'].min() >= 30, "Salinity should be within range"
    
    # Test problematic data
    problematic_data = generator.generate_problematic_data(50)
    assert len(problematic_data) == 50, "Should generate 50 problematic records"
    
    # Test duplicate data
    duplicate_data = generator.generate_duplicate_data(30)
    assert len(duplicate_data) == 30, "Should generate 30 records with duplicates"
    
    # Test large dataset
    large_data = generator.generate_large_dataset(1000)
    assert len(large_data) == 1000, "Should generate 1000 records"
    
    # Test CNV data generation
    cnv_content = generator.generate_cnv_test_data(50)
    assert "*END*" in cnv_content, "CNV content should have END marker"
    assert "nvalues: 50" in cnv_content, "CNV content should specify number of values"
    
    print("  PASS: Data generator tests")


if __name__ == "__main__":
    test_data_generator()
    print("\nAll data generator tests passed!")
