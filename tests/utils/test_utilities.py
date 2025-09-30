#!/usr/bin/env python3
"""
Database testing utilities
Provides commonly used utility functions and classes for database tests
"""

import os
import sys
import time
import logging
import psutil
import threading
from contextlib import contextmanager
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from triaxus.database.connection_manager import DatabaseConnectionManager
from triaxus.database.models import OceanographicData, DataSource


class DatabaseTestHelper:
    """Database test helper class"""
    
    def __init__(self):
        """Initialize test helper"""
        self.connection_manager = DatabaseConnectionManager()
        self.logger = logging.getLogger(__name__)
    
    def ensure_connection(self) -> bool:
        """Ensure database connection"""
        if not self.connection_manager.is_connected():
            return self.connection_manager.connect()
        return True
    
    def clean_test_data(self) -> bool:
        """Clean test data"""
        try:
            if not self.ensure_connection():
                return False
            
            with self.connection_manager.get_session() as session:
                # Clean oceanographic data
                oceanographic_count = session.query(OceanographicData).count()
                if oceanographic_count > 0:
                    session.query(OceanographicData).delete()
                    self.logger.info(f"清理了 {oceanographic_count} 条海洋数据记录")
                
                # Clean data sources
                sources_count = session.query(DataSource).count()
                if sources_count > 0:
                    session.query(DataSource).delete()
                    self.logger.info(f"清理了 {sources_count} 条数据源记录")
                
                session.commit()
            
            return True
        
        except Exception as e:
            self.logger.error(f"清理测试数据失败: {e}")
            return False
    
    def get_table_count(self, table_name: str) -> int:
        """Get record count from a table"""
        try:
            if not self.ensure_connection():
                return -1
            
            with self.connection_manager.get_session() as session:
                if table_name == 'oceanographic_data':
                    return session.query(OceanographicData).count()
                elif table_name == 'data_sources':
                    return session.query(DataSource).count()
                else:
                    # Use raw SQL query
                    from sqlalchemy import text
                    result = session.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                    return result.scalar()
        
        except Exception as e:
            self.logger.error(f"获取表 {table_name} 记录数失败: {e}")
            return -1
    
    def verify_data_integrity(self, sample_data: pd.DataFrame) -> Dict[str, Any]:
        """Validate data integrity"""
        integrity_results = {
            'total_records': len(sample_data),
            'null_values': {},
            'constraint_violations': {},
            'data_quality_issues': []
        }
        
        # Check null values
        for column in sample_data.columns:
            null_count = sample_data[column].isnull().sum()
            if null_count > 0:
                integrity_results['null_values'][column] = null_count
        
        # Check constraint violations
        if 'depth' in sample_data.columns:
            negative_depths = (sample_data['depth'] < 0).sum()
            if negative_depths > 0:
                integrity_results['constraint_violations']['negative_depth'] = negative_depths
        
        if 'latitude' in sample_data.columns:
            invalid_lat = ((sample_data['latitude'] < -90) | (sample_data['latitude'] > 90)).sum()
            if invalid_lat > 0:
                integrity_results['constraint_violations']['invalid_latitude'] = invalid_lat
        
        if 'longitude' in sample_data.columns:
            invalid_lon = ((sample_data['longitude'] < -180) | (sample_data['longitude'] > 180)).sum()
            if invalid_lon > 0:
                integrity_results['constraint_violations']['invalid_longitude'] = invalid_lon
        
        return integrity_results
    
    @contextmanager
    def temporary_data(self, data: pd.DataFrame):
        """Temporary data context manager"""
        from triaxus.database.mappers import DataMapper
        
        mapper = DataMapper()
        models = mapper.dataframe_to_models(data, "temp_test_data.csv")
        
        try:
            # Insert temporary data
            if self.ensure_connection():
                with self.connection_manager.get_session() as session:
                    session.add_all(models)
                    session.commit()
            
            yield models
        
        finally:
            # Clean up temporary data
            try:
                if self.ensure_connection():
                    with self.connection_manager.get_session() as session:
                        for model in models:
                            session.delete(model)
                        session.commit()
            except Exception as e:
                self.logger.warning(f"清理临时数据失败: {e}")


class PerformanceMonitor:
    """Performance monitor"""
    
    def __init__(self):
        """Initialize performance monitor"""
        self.metrics = {}
        self.start_time = None
        self.monitoring = False
        self.monitor_thread = None
    
    def start_monitoring(self, interval: float = 1.0):
        """Start performance monitoring"""
        self.start_time = time.time()
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, args=(interval,))
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
    
    def stop_monitoring(self) -> Dict[str, Any]:
        """Stop performance monitoring and return results"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        
        return self._calculate_summary()
    
    def _monitor_loop(self, interval: float):
        """Monitoring loop"""
        while self.monitoring:
            try:
                timestamp = time.time() - self.start_time
                
                # Collect system metrics
                cpu_percent = psutil.cpu_percent(interval=0.1)
                memory = psutil.virtual_memory()
                disk_io = psutil.disk_io_counters()
                net_io = psutil.net_io_counters()
                
                self.metrics[timestamp] = {
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory.percent,
                    'memory_used_mb': memory.used / (1024 * 1024),
                    'disk_read_mb': disk_io.read_bytes / (1024 * 1024) if disk_io else 0,
                    'disk_write_mb': disk_io.write_bytes / (1024 * 1024) if disk_io else 0,
                    'net_sent_mb': net_io.bytes_sent / (1024 * 1024) if net_io else 0,
                    'net_recv_mb': net_io.bytes_recv / (1024 * 1024) if net_io else 0
                }
                
                time.sleep(interval)
            
            except Exception as e:
                logging.error(f"性能监控错误: {e}")
                break
    
    def _calculate_summary(self) -> Dict[str, Any]:
        """Compute performance summary"""
        if not self.metrics:
            return {}
        
        # Convert to DataFrame for easier computation
        df = pd.DataFrame.from_dict(self.metrics, orient='index')
        
        summary = {
            'duration': max(self.metrics.keys()) if self.metrics else 0,
            'cpu': {
                'avg': df['cpu_percent'].mean(),
                'max': df['cpu_percent'].max(),
                'min': df['cpu_percent'].min()
            },
            'memory': {
                'avg_percent': df['memory_percent'].mean(),
                'max_percent': df['memory_percent'].max(),
                'avg_used_mb': df['memory_used_mb'].mean(),
                'max_used_mb': df['memory_used_mb'].max()
            },
            'disk_io': {
                'total_read_mb': df['disk_read_mb'].iloc[-1] - df['disk_read_mb'].iloc[0] if len(df) > 1 else 0,
                'total_write_mb': df['disk_write_mb'].iloc[-1] - df['disk_write_mb'].iloc[0] if len(df) > 1 else 0
            },
            'network_io': {
                'total_sent_mb': df['net_sent_mb'].iloc[-1] - df['net_sent_mb'].iloc[0] if len(df) > 1 else 0,
                'total_recv_mb': df['net_recv_mb'].iloc[-1] - df['net_recv_mb'].iloc[0] if len(df) > 1 else 0
            }
        }
        
        return summary


class BenchmarkTimer:
    """Benchmark timer"""
    
    def __init__(self, name: str = "Benchmark"):
        """Initialize timer"""
        self.name = name
        self.start_time = None
        self.end_time = None
        self.measurements = []
    
    def start(self):
        """Start timing"""
        self.start_time = time.perf_counter()
    
    def stop(self) -> float:
        """Stop timing and return elapsed time"""
        if self.start_time is None:
            raise ValueError("计时器未启动")
        
        self.end_time = time.perf_counter()
        duration = self.end_time - self.start_time
        self.measurements.append(duration)
        return duration
    
    def reset(self):
        """Reset timer"""
        self.start_time = None
        self.end_time = None
    
    def get_statistics(self) -> Dict[str, float]:
        """Get statistics"""
        if not self.measurements:
            return {}
        
        measurements = np.array(self.measurements)
        return {
            'count': len(measurements),
            'total': measurements.sum(),
            'mean': measurements.mean(),
            'median': np.median(measurements),
            'std': measurements.std(),
            'min': measurements.min(),
            'max': measurements.max(),
            'p95': np.percentile(measurements, 95),
            'p99': np.percentile(measurements, 99)
        }
    
    @contextmanager
    def measure(self):
        """Timing context manager"""
        self.start()
        try:
            yield self
        finally:
            self.stop()


class TestDataValidator:
    """Test data validator"""
    
    @staticmethod
    def validate_oceanographic_data(data: pd.DataFrame) -> Dict[str, Any]:
        """Validate oceanographic data"""
        validation_results = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'statistics': {}
        }
        
        required_columns = ['time', 'depth', 'latitude', 'longitude']
        
        # Check required columns
        missing_columns = [col for col in required_columns if col not in data.columns]
        if missing_columns:
            validation_results['valid'] = False
            validation_results['errors'].append(f"缺少必需列: {missing_columns}")
        
        # Check data ranges
        if 'depth' in data.columns:
            negative_depths = data[data['depth'] < 0]
            if not negative_depths.empty:
                validation_results['valid'] = False
                validation_results['errors'].append(f"发现 {len(negative_depths)} 个负深度值")
        
        if 'latitude' in data.columns:
            invalid_lat = data[(data['latitude'] < -90) | (data['latitude'] > 90)]
            if not invalid_lat.empty:
                validation_results['valid'] = False
                validation_results['errors'].append(f"发现 {len(invalid_lat)} 个无效纬度值")
        
        if 'longitude' in data.columns:
            invalid_lon = data[(data['longitude'] < -180) | (data['longitude'] > 180)]
            if not invalid_lon.empty:
                validation_results['valid'] = False
                validation_results['errors'].append(f"发现 {len(invalid_lon)} 个无效经度值")
        
        # Check data quality
        null_counts = data.isnull().sum()
        high_null_columns = null_counts[null_counts > len(data) * 0.5]
        if not high_null_columns.empty:
            validation_results['warnings'].append(f"以下列有超过50%的空值: {high_null_columns.index.tolist()}")
        
        # Compute statistics
        validation_results['statistics'] = {
            'total_records': len(data),
            'null_values': null_counts.to_dict(),
            'data_types': data.dtypes.to_dict()
        }
        
        return validation_results
    
    @staticmethod
    def validate_test_results(results: Dict[str, Any]) -> bool:
        """Validate test result format"""
        required_fields = ['status']
        
        for test_name, result in results.items():
            if not isinstance(result, dict):
                return False
            
            for field in required_fields:
                if field not in result:
                    return False
            
            if result['status'] not in ['PASSED', 'FAILED', 'SKIPPED']:
                return False
        
        return True


class DatabaseConnectionTester:
    """Database connection tester"""
    
    def __init__(self):
        """Initialize connection tester"""
        self.connection_manager = DatabaseConnectionManager()
    
    def test_basic_connectivity(self) -> Dict[str, Any]:
        """Test basic connectivity"""
        try:
            success = self.connection_manager.connect()
            return {
                'status': 'PASSED' if success else 'FAILED',
                'connected': success,
                'engine_available': self.connection_manager.engine is not None
            }
        except Exception as e:
            return {
                'status': 'FAILED',
                'error': str(e),
                'connected': False
            }
    
    def test_connection_pool(self, pool_size: int = 5) -> Dict[str, Any]:
        """Test connection pool"""
        try:
            if not self.connection_manager.is_connected():
                self.connection_manager.connect()
            
            # Create multiple sessions to test connection pool
            sessions = []
            for i in range(pool_size):
                session = self.connection_manager.session_factory()
                sessions.append(session)
            
            # Close all sessions
            for session in sessions:
                session.close()
            
            return {
                'status': 'PASSED',
                'pool_size_tested': pool_size,
                'sessions_created': len(sessions)
            }
        
        except Exception as e:
            return {
                'status': 'FAILED',
                'error': str(e)
            }
    
    def test_transaction_handling(self) -> Dict[str, Any]:
        """Test transaction handling"""
        try:
            if not self.connection_manager.is_connected():
                self.connection_manager.connect()
            
            # Test normal transaction
            with self.connection_manager.get_session() as session:
                from sqlalchemy import text
                result = session.execute(text("SELECT 1"))
                assert result.scalar() == 1
            
            # Test transaction rollback
            try:
                with self.connection_manager.get_session() as session:
                    session.execute(text("SELECT 1"))
                    raise Exception("测试异常")
            except Exception:
                pass  # Expected exception
            
            return {
                'status': 'PASSED',
                'transaction_commit': True,
                'transaction_rollback': True
            }
        
        except Exception as e:
            return {
                'status': 'FAILED',
                'error': str(e)
            }


def measure_execution_time(func: Callable) -> Callable:
    """Decorator: measure function execution time"""
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        
        execution_time = end_time - start_time
        
        # If the result is a dict, add execution time
        if isinstance(result, dict):
            result['execution_time'] = execution_time
        
        return result
    
    return wrapper


def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """Decorator: retry on failure"""
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries:
                        logging.warning(f"函数 {func.__name__} 第 {attempt + 1} 次尝试失败: {e}")
                        time.sleep(delay * (2 ** attempt))  # 指数退避
                    else:
                        logging.error(f"函数 {func.__name__} 在 {max_retries + 1} 次尝试后仍然失败")
            
            raise last_exception
        
        return wrapper
    return decorator


# Helper functions
def setup_test_environment():
    """Set up test environment"""
    # Set environment variables
    os.environ['DB_ENABLED'] = 'true'
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def cleanup_test_environment():
    """Clean up test environment"""
    helper = DatabaseTestHelper()
    return helper.clean_test_data()


if __name__ == "__main__":
    # Example usage
    setup_test_environment()
    
    # Test database connectivity
    conn_tester = DatabaseConnectionTester()
    result = conn_tester.test_basic_connectivity()
    print(f"连接测试结果: {result}")
    
    # Performance monitoring example
    monitor = PerformanceMonitor()
    monitor.start_monitoring()
    
    # Simulate some work
    time.sleep(2)
    
    perf_summary = monitor.stop_monitoring()
    print(f"性能摘要: {perf_summary}")
    
    # Benchmark example
    timer = BenchmarkTimer("示例测试")
    with timer.measure():
        time.sleep(0.1)
    
    stats = timer.get_statistics()
    print(f"基准测试统计: {stats}")
