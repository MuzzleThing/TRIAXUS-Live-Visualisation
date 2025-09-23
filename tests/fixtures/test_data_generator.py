#!/usr/bin/env python3
"""
测试数据生成器
为 TRIAXUS 数据库测试生成各种类型的测试数据
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
import random
import uuid


class OceanographicTestDataGenerator:
    """海洋数据测试数据生成器"""
    
    def __init__(self, seed: int = 42):
        """初始化数据生成器"""
        self.seed = seed
        np.random.seed(seed)
        random.seed(seed)
        
        # 海洋数据的现实范围
        self.depth_range = (0, 11000)          # 深度范围 (米)
        self.latitude_range = (-90, 90)        # 纬度范围 (度)
        self.longitude_range = (-180, 180)     # 经度范围 (度)
        self.temperature_range = (-2, 40)      # 温度范围 (摄氏度)
        self.salinity_range = (0, 50)         # 盐度范围 (PSU)
        self.oxygen_range = (0, 500)          # 溶解氧范围 (μmol/kg)
        self.fluorescence_range = (0, 50)     # 荧光范围 (mg/m³)
        self.ph_range = (6.5, 8.5)           # pH 范围
    
    def generate_basic_data(self, count: int = 100) -> pd.DataFrame:
        """生成基础测试数据"""
        data = {
            'time': self._generate_timestamps(count),
            'depth': self._generate_depths(count),
            'latitude': self._generate_latitudes(count),
            'longitude': self._generate_longitudes(count),
            'tv290c': self._generate_temperatures(count),
            'sal00': self._generate_salinities(count),
            'sbeox0mm_l': self._generate_oxygen(count),
            'fleco_afl': self._generate_fluorescence(count),
            'ph': self._generate_ph(count)
        }
        
        return pd.DataFrame(data)
    
    def generate_realistic_profile_data(self, count: int = 1000) -> pd.DataFrame:
        """生成现实的海洋剖面数据（考虑深度相关性）"""
        depths = np.linspace(0, 5000, count)  # 0-5000米深度剖面
        
        # 基于深度生成相关的温度和盐度
        temperatures = self._generate_depth_correlated_temperature(depths)
        salinities = self._generate_depth_correlated_salinity(depths)
        oxygen = self._generate_depth_correlated_oxygen(depths)
        
        # 固定位置的时间序列
        base_time = datetime(2024, 1, 1, 12, 0, 0)
        timestamps = [base_time + timedelta(seconds=i*10) for i in range(count)]
        
        # 固定地理位置（模拟单点剖面）
        latitude = 45.0 + np.random.normal(0, 0.001, count)  # 小幅度变化模拟GPS误差
        longitude = -125.0 + np.random.normal(0, 0.001, count)
        
        data = {
            'time': timestamps,
            'depth': depths,
            'latitude': latitude,
            'longitude': longitude,
            'tv290c': temperatures,
            'sal00': salinities,
            'sbeox0mm_l': oxygen,
            'fleco_afl': self._generate_fluorescence(count),
            'ph': self._generate_ph(count)
        }
        
        return pd.DataFrame(data)
    
    def generate_boundary_test_data(self) -> pd.DataFrame:
        """生成边界值测试数据"""
        boundary_cases = [
            # 最小值
            {
                'time': datetime.min,
                'depth': 0.0,
                'latitude': -90.0,
                'longitude': -180.0,
                'tv290c': -2.0,
                'sal00': 0.0,
                'sbeox0mm_l': 0.0,
                'fleco_afl': 0.0,
                'ph': 6.5
            },
            # 最大值
            {
                'time': datetime.max,
                'depth': 11000.0,
                'latitude': 90.0,
                'longitude': 180.0,
                'tv290c': 40.0,
                'sal00': 50.0,
                'sbeox0mm_l': 500.0,
                'fleco_afl': 50.0,
                'ph': 8.5
            },
            # 典型海洋值
            {
                'time': datetime(2024, 6, 15, 12, 0, 0),
                'depth': 1000.0,
                'latitude': 45.0,
                'longitude': -125.0,
                'tv290c': 4.0,
                'sal00': 34.5,
                'sbeox0mm_l': 200.0,
                'fleco_afl': 2.5,
                'ph': 8.1
            }
        ]
        
        return pd.DataFrame(boundary_cases)
    
    def generate_invalid_test_data(self) -> pd.DataFrame:
        """生成无效测试数据（用于约束测试）"""
        invalid_cases = [
            # 负深度
            {
                'time': datetime.now(),
                'depth': -100.0,
                'latitude': 45.0,
                'longitude': -125.0,
                'tv290c': 15.0,
                'sal00': 35.0,
                'sbeox0mm_l': 200.0,
                'fleco_afl': 2.0,
                'ph': 8.0
            },
            # 超出范围的纬度
            {
                'time': datetime.now(),
                'depth': 100.0,
                'latitude': 95.0,  # 超出 [-90, 90] 范围
                'longitude': -125.0,
                'tv290c': 15.0,
                'sal00': 35.0,
                'sbeox0mm_l': 200.0,
                'fleco_afl': 2.0,
                'ph': 8.0
            },
            # 超出范围的经度
            {
                'time': datetime.now(),
                'depth': 100.0,
                'latitude': 45.0,
                'longitude': 185.0,  # 超出 [-180, 180] 范围
                'tv290c': 15.0,
                'sal00': 35.0,
                'sbeox0mm_l': 200.0,
                'fleco_afl': 2.0,
                'ph': 8.0
            }
        ]
        
        return pd.DataFrame(invalid_cases)
    
    def generate_performance_test_data(self, count: int = 10000) -> pd.DataFrame:
        """生成性能测试数据"""
        return self.generate_basic_data(count)
    
    def generate_stress_test_data(self, count: int = 100000) -> pd.DataFrame:
        """生成压力测试数据"""
        # 分批生成以避免内存问题
        batch_size = 10000
        batches = []
        
        for i in range(0, count, batch_size):
            batch_count = min(batch_size, count - i)
            batch_data = self.generate_basic_data(batch_count)
            batches.append(batch_data)
        
        return pd.concat(batches, ignore_index=True)
    
    def _generate_timestamps(self, count: int) -> List[datetime]:
        """生成时间戳"""
        start_time = datetime(2024, 1, 1, 0, 0, 0)
        return [start_time + timedelta(seconds=i*60) for i in range(count)]
    
    def _generate_depths(self, count: int) -> np.ndarray:
        """生成深度数据"""
        # 使用指数分布，大部分数据在浅水区
        depths = np.random.exponential(scale=500, size=count)
        depths = np.clip(depths, self.depth_range[0], self.depth_range[1])
        return depths
    
    def _generate_latitudes(self, count: int) -> np.ndarray:
        """生成纬度数据"""
        return np.random.uniform(self.latitude_range[0], self.latitude_range[1], count)
    
    def _generate_longitudes(self, count: int) -> np.ndarray:
        """生成经度数据"""
        return np.random.uniform(self.longitude_range[0], self.longitude_range[1], count)
    
    def _generate_temperatures(self, count: int) -> np.ndarray:
        """生成温度数据"""
        return np.random.uniform(self.temperature_range[0], self.temperature_range[1], count)
    
    def _generate_salinities(self, count: int) -> np.ndarray:
        """生成盐度数据"""
        # 大部分海水盐度在 34-36 PSU 之间
        return np.random.normal(35.0, 1.0, count)
    
    def _generate_oxygen(self, count: int) -> np.ndarray:
        """生成溶解氧数据"""
        return np.random.uniform(self.oxygen_range[0], self.oxygen_range[1], count)
    
    def _generate_fluorescence(self, count: int) -> np.ndarray:
        """生成荧光数据"""
        return np.random.exponential(scale=2.0, size=count)
    
    def _generate_ph(self, count: int) -> np.ndarray:
        """生成 pH 数据"""
        return np.random.normal(8.1, 0.2, count)
    
    def _generate_depth_correlated_temperature(self, depths: np.ndarray) -> np.ndarray:
        """生成与深度相关的温度数据"""
        # 简化的温度-深度关系：表层温暖，深层寒冷
        surface_temp = 20.0
        deep_temp = 2.0
        thermocline_depth = 1000.0
        
        temperatures = surface_temp - (surface_temp - deep_temp) * (1 - np.exp(-depths / thermocline_depth))
        # 添加噪声
        temperatures += np.random.normal(0, 0.5, len(depths))
        
        return np.clip(temperatures, self.temperature_range[0], self.temperature_range[1])
    
    def _generate_depth_correlated_salinity(self, depths: np.ndarray) -> np.ndarray:
        """生成与深度相关的盐度数据"""
        # 简化的盐度-深度关系
        surface_salinity = 34.0
        deep_salinity = 34.7
        
        salinities = surface_salinity + (deep_salinity - surface_salinity) * (depths / 5000.0)
        # 添加噪声
        salinities += np.random.normal(0, 0.1, len(depths))
        
        return np.clip(salinities, self.salinity_range[0], self.salinity_range[1])
    
    def _generate_depth_correlated_oxygen(self, depths: np.ndarray) -> np.ndarray:
        """生成与深度相关的溶解氧数据"""
        # 简化的氧气-深度关系：表层高，中层低，深层略高
        surface_oxygen = 300.0
        min_oxygen = 50.0
        deep_oxygen = 150.0
        
        # 氧气最小值在 500-1500 米之间
        oxygen_min_depth = 1000.0
        
        oxygen = np.where(
            depths < oxygen_min_depth,
            surface_oxygen - (surface_oxygen - min_oxygen) * (depths / oxygen_min_depth),
            min_oxygen + (deep_oxygen - min_oxygen) * ((depths - oxygen_min_depth) / (5000 - oxygen_min_depth))
        )
        
        # 添加噪声
        oxygen += np.random.normal(0, 20, len(depths))
        
        return np.clip(oxygen, self.oxygen_range[0], self.oxygen_range[1])


class DataSourceTestDataGenerator:
    """数据源测试数据生成器"""
    
    def __init__(self, seed: int = 42):
        """初始化数据源生成器"""
        self.seed = seed
        random.seed(seed)
    
    def generate_data_source_metadata(self, count: int = 10) -> List[Dict[str, Any]]:
        """生成数据源元数据"""
        data_sources = []
        
        for i in range(count):
            data_source = {
                'id': str(uuid.uuid4()),
                'source_file': f'test_file_{i:03d}.cnv',
                'file_type': 'CNV',
                'file_size': random.randint(1024, 10*1024*1024),  # 1KB - 10MB
                'file_hash': self._generate_hash(),
                'software_version': f'SBE Data Processing-Win32 {random.choice(["7.26.7.129", "7.26.6.28", "7.23.2.5"])}',
                'temperature_sn': f'03P-{random.randint(1000, 9999)}',
                'conductivity_sn': f'04C-{random.randint(1000, 9999)}',
                'number_of_scans': random.randint(1000, 50000),
                'number_of_cycles': random.randint(10, 500),
                'sample_interval': random.choice([0.25, 0.5, 1.0, 2.0]),
                'start_time': datetime.now() - timedelta(days=random.randint(1, 365)),
                'end_time': None,  # 将在后面计算
                'nmea_latitude': f'{random.uniform(40, 50):.6f} N',
                'nmea_longitude': f'{random.uniform(120, 130):.6f} W',
                'initial_depth': random.uniform(0, 10),
                'processed_at': datetime.now(),
                'status': random.choice(['processed', 'pending', 'error']),
                'error_message': None,
                'total_records': random.randint(100, 10000),
                'min_datetime': None,  # 将在后面设置
                'max_datetime': None,
                'min_depth': 0.0,
                'max_depth': random.uniform(100, 5000),
                'min_latitude': random.uniform(40, 45),
                'max_latitude': random.uniform(45, 50),
                'min_longitude': random.uniform(-130, -125),
                'max_longitude': random.uniform(-125, -120)
            }
            
            # 计算结束时间
            duration = timedelta(seconds=data_source['number_of_scans'] * data_source['sample_interval'])
            data_source['end_time'] = data_source['start_time'] + duration
            data_source['min_datetime'] = data_source['start_time']
            data_source['max_datetime'] = data_source['end_time']
            
            # 如果状态是错误，添加错误消息
            if data_source['status'] == 'error':
                data_source['error_message'] = random.choice([
                    'File format error',
                    'Corrupted data',
                    'Missing required headers',
                    'Invalid sensor configuration'
                ])
            
            data_sources.append(data_source)
        
        return data_sources
    
    def _generate_hash(self) -> str:
        """生成模拟的文件哈希"""
        import hashlib
        random_data = str(random.random()).encode()
        return hashlib.sha256(random_data).hexdigest()


class TestDataManager:
    """测试数据管理器"""
    
    def __init__(self):
        """初始化测试数据管理器"""
        self.oceanographic_generator = OceanographicTestDataGenerator()
        self.data_source_generator = DataSourceTestDataGenerator()
    
    def get_test_dataset(self, dataset_type: str, **kwargs) -> pd.DataFrame:
        """获取指定类型的测试数据集"""
        if dataset_type == 'basic':
            return self.oceanographic_generator.generate_basic_data(kwargs.get('count', 100))
        elif dataset_type == 'realistic_profile':
            return self.oceanographic_generator.generate_realistic_profile_data(kwargs.get('count', 1000))
        elif dataset_type == 'boundary':
            return self.oceanographic_generator.generate_boundary_test_data()
        elif dataset_type == 'invalid':
            return self.oceanographic_generator.generate_invalid_test_data()
        elif dataset_type == 'performance':
            return self.oceanographic_generator.generate_performance_test_data(kwargs.get('count', 10000))
        elif dataset_type == 'stress':
            return self.oceanographic_generator.generate_stress_test_data(kwargs.get('count', 100000))
        else:
            raise ValueError(f"未知的数据集类型: {dataset_type}")
    
    def get_data_source_metadata(self, count: int = 10) -> List[Dict[str, Any]]:
        """获取数据源元数据"""
        return self.data_source_generator.generate_data_source_metadata(count)
    
    def save_test_data(self, data: pd.DataFrame, filename: str, format: str = 'csv'):
        """保存测试数据到文件"""
        if format == 'csv':
            data.to_csv(filename, index=False)
        elif format == 'json':
            data.to_json(filename, orient='records', date_format='iso')
        elif format == 'parquet':
            data.to_parquet(filename, index=False)
        else:
            raise ValueError(f"不支持的文件格式: {format}")
    
    def load_test_data(self, filename: str, format: str = 'csv') -> pd.DataFrame:
        """从文件加载测试数据"""
        if format == 'csv':
            return pd.read_csv(filename, parse_dates=['time'])
        elif format == 'json':
            return pd.read_json(filename, orient='records')
        elif format == 'parquet':
            return pd.read_parquet(filename)
        else:
            raise ValueError(f"不支持的文件格式: {format}")


# 便利函数
def generate_test_data(dataset_type: str = 'basic', count: int = 100) -> pd.DataFrame:
    """生成测试数据的便利函数"""
    manager = TestDataManager()
    return manager.get_test_dataset(dataset_type, count=count)


def generate_data_sources(count: int = 10) -> List[Dict[str, Any]]:
    """生成数据源元数据的便利函数"""
    manager = TestDataManager()
    return manager.get_data_source_metadata(count)


if __name__ == "__main__":
    # 示例用法
    manager = TestDataManager()
    
    # 生成基础测试数据
    basic_data = manager.get_test_dataset('basic', count=100)
    print(f"生成基础数据: {len(basic_data)} 条记录")
    print(basic_data.head())
    
    # 生成现实剖面数据
    profile_data = manager.get_test_dataset('realistic_profile', count=500)
    print(f"\n生成剖面数据: {len(profile_data)} 条记录")
    print(profile_data.head())
    
    # 生成数据源元数据
    data_sources = manager.get_data_source_metadata(5)
    print(f"\n生成数据源元数据: {len(data_sources)} 个文件")
    for ds in data_sources[:2]:
        print(f"文件: {ds['source_file']}, 记录数: {ds['total_records']}, 状态: {ds['status']}")
