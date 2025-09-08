"""
Data Sampler for TRIAXUS visualization system

This module provides data sampling functionality for TRIAXUS data.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List, Tuple
import logging

from ..core.config import ConfigManager


class DataSampler:
    """Data sampler for TRIAXUS data processing"""
    
    def __init__(self, config_manager: Optional[ConfigManager] = None):
        """
        Initialize DataSampler
        
        Args:
            config_manager: Configuration manager instance
        """
        self.config_manager = config_manager or ConfigManager()
        self.logger = logging.getLogger(__name__)
    
    def sample_data(self, data: pd.DataFrame, sampling_config: Dict[str, Any]) -> pd.DataFrame:
        """
        Sample data based on configuration
        
        Args:
            data: Input data
            sampling_config: Sampling configuration
            
        Returns:
            Sampled data
        """
        try:
            sampling_method = sampling_config.get('method', 'random')
            sample_size = sampling_config.get('size', 1000)
            
            if sampling_method == 'random':
                return self._random_sample(data, sample_size)
            elif sampling_method == 'systematic':
                return self._systematic_sample(data, sample_size)
            elif sampling_method == 'stratified':
                return self._stratified_sample(data, sampling_config)
            elif sampling_method == 'time_based':
                return self._time_based_sample(data, sampling_config)
            elif sampling_method == 'depth_based':
                return self._depth_based_sample(data, sampling_config)
            else:
                self.logger.warning(f"Unknown sampling method: {sampling_method}")
                return data
            
        except Exception as e:
            self.logger.error(f"Data sampling failed: {e}")
            raise
    
    def _random_sample(self, data: pd.DataFrame, sample_size: int) -> pd.DataFrame:
        """Random sampling"""
        if len(data) <= sample_size:
            return data
        
        sampled = data.sample(n=sample_size, random_state=42)
        self.logger.info(f"Random sampling: {len(sampled)} samples from {len(data)} data points")
        return sampled
    
    def _systematic_sample(self, data: pd.DataFrame, sample_size: int) -> pd.DataFrame:
        """Systematic sampling"""
        if len(data) <= sample_size:
            return data
        
        step = len(data) // sample_size
        indices = list(range(0, len(data), step))[:sample_size]
        sampled = data.iloc[indices]
        
        self.logger.info(f"Systematic sampling: {len(sampled)} samples from {len(data)} data points")
        return sampled
    
    def _stratified_sample(self, data: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
        """Stratified sampling based on depth or time"""
        stratify_column = config.get('stratify_column', 'depth')
        sample_size = config.get('size', 1000)
        
        if stratify_column not in data.columns:
            self.logger.warning(f"Stratify column {stratify_column} not found, using random sampling")
            return self._random_sample(data, sample_size)
        
        # Create strata
        n_strata = config.get('n_strata', 5)
        data['stratum'] = pd.cut(data[stratify_column], bins=n_strata, labels=False)
        
        # Sample from each stratum
        sampled_data = []
        for stratum in range(n_strata):
            stratum_data = data[data['stratum'] == stratum]
            if len(stratum_data) > 0:
                stratum_sample_size = max(1, sample_size // n_strata)
                stratum_sample = stratum_data.sample(
                    n=min(stratum_sample_size, len(stratum_data)), 
                    random_state=42
                )
                sampled_data.append(stratum_sample)
        
        if sampled_data:
            sampled = pd.concat(sampled_data, ignore_index=True)
            sampled = sampled.drop('stratum', axis=1)
        else:
            sampled = data
        
        self.logger.info(f"Stratified sampling: {len(sampled)} samples from {len(data)} data points")
        return sampled
    
    def _time_based_sample(self, data: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
        """Time-based sampling"""
        if 'time' not in data.columns:
            self.logger.warning("No time column found, using random sampling")
            return self._random_sample(data, config.get('size', 1000))
        
        time_interval = config.get('time_interval', '1H')
        sample_size = config.get('size', 1000)
        
        # Group by time intervals and sample from each group
        data['time_group'] = pd.to_datetime(data['time']).dt.floor(time_interval)
        sampled_data = []
        
        for time_group in data['time_group'].unique():
            group_data = data[data['time_group'] == time_group]
            if len(group_data) > 0:
                group_sample_size = max(1, sample_size // len(data['time_group'].unique()))
                group_sample = group_data.sample(
                    n=min(group_sample_size, len(group_data)), 
                    random_state=42
                )
                sampled_data.append(group_sample)
        
        if sampled_data:
            sampled = pd.concat(sampled_data, ignore_index=True)
            sampled = sampled.drop('time_group', axis=1)
        else:
            sampled = data
        
        self.logger.info(f"Time-based sampling: {len(sampled)} samples from {len(data)} data points")
        return sampled
    
    def _depth_based_sample(self, data: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
        """Depth-based sampling"""
        if 'depth' not in data.columns:
            self.logger.warning("No depth column found, using random sampling")
            return self._random_sample(data, config.get('size', 1000))
        
        depth_intervals = config.get('depth_intervals', [(0, 50), (50, 100), (100, 200)])
        sample_size = config.get('size', 1000)
        
        sampled_data = []
        samples_per_interval = sample_size // len(depth_intervals)
        
        for min_depth, max_depth in depth_intervals:
            interval_data = data[(data['depth'] >= min_depth) & (data['depth'] < max_depth)]
            if len(interval_data) > 0:
                interval_sample = interval_data.sample(
                    n=min(samples_per_interval, len(interval_data)), 
                    random_state=42
                )
                sampled_data.append(interval_sample)
        
        if sampled_data:
            sampled = pd.concat(sampled_data, ignore_index=True)
        else:
            sampled = data
        
        self.logger.info(f"Depth-based sampling: {len(sampled)} samples from {len(data)} data points")
        return sampled
    
    def downsample_data(self, data: pd.DataFrame, target_size: int) -> pd.DataFrame:
        """Downsample data to target size"""
        if len(data) <= target_size:
            return data
        
        # Use systematic sampling for downsampling
        step = len(data) // target_size
        indices = list(range(0, len(data), step))[:target_size]
        downsampled = data.iloc[indices]
        
        self.logger.info(f"Downsampled from {len(data)} to {len(downsampled)} data points")
        return downsampled
    
    def upsample_data(self, data: pd.DataFrame, target_size: int) -> pd.DataFrame:
        """Upsample data to target size using interpolation"""
        if len(data) >= target_size:
            return data
        
        # Use interpolation to upsample
        upsampled = data.copy()
        
        # Interpolate numeric columns
        numeric_columns = data.select_dtypes(include=[np.number]).columns
        for col in numeric_columns:
            if col in data.columns:
                upsampled[col] = upsampled[col].interpolate(method='linear')
        
        # Repeat data to reach target size
        while len(upsampled) < target_size:
            remaining = target_size - len(upsampled)
            if remaining >= len(data):
                upsampled = pd.concat([upsampled, data], ignore_index=True)
            else:
                upsampled = pd.concat([upsampled, data.iloc[:remaining]], ignore_index=True)
        
        self.logger.info(f"Upsampled from {len(data)} to {len(upsampled)} data points")
        return upsampled
    
    def get_sampling_recommendations(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Get sampling recommendations based on data characteristics"""
        recommendations = {
            'data_size': len(data),
            'recommended_methods': [],
            'optimal_sample_size': min(1000, len(data))
        }
        
        # Check data characteristics
        has_time = 'time' in data.columns
        has_depth = 'depth' in data.columns
        has_coordinates = 'latitude' in data.columns and 'longitude' in data.columns
        
        # Recommend sampling methods
        if has_time and len(data) > 1000:
            recommendations['recommended_methods'].append('time_based')
        
        if has_depth and len(data) > 1000:
            recommendations['recommended_methods'].append('depth_based')
        
        if has_coordinates and len(data) > 1000:
            recommendations['recommended_methods'].append('stratified')
        
        # Always include random sampling as fallback
        recommendations['recommended_methods'].append('random')
        
        # Calculate optimal sample size
        if len(data) > 10000:
            recommendations['optimal_sample_size'] = 2000
        elif len(data) > 5000:
            recommendations['optimal_sample_size'] = 1000
        else:
            recommendations['optimal_sample_size'] = len(data)
        
        return recommendations
