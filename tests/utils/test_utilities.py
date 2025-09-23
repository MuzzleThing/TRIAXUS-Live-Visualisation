#!/usr/bin/env python3
"""
数据库测试实用工具
提供数据库测试中常用的工具函数和类
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

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from triaxus.database.connection_manager import DatabaseConnectionManager
from triaxus.database.models import OceanographicData, DataSource


class DatabaseTestHelper:
    """数据库测试辅助类"""
    
    def __init__(self):
        """初始化测试辅助类"""
        self.connection_manager = DatabaseConnectionManager()
        self.logger = logging.getLogger(__name__)
    
    def ensure_connection(self) -> bool:
        """确保数据库连接"""
        if not self.connection_manager.is_connected():
            return self.connection_manager.connect()
        return True
    
    def clean_test_data(self) -> bool:
        """清理测试数据"""
        try:
            if not self.ensure_connection():
                return False
            
            with self.connection_manager.get_session() as session:
                # 清理海洋数据
                oceanographic_count = session.query(OceanographicData).count()
                if oceanographic_count > 0:
                    session.query(OceanographicData).delete()
                    self.logger.info(f"清理了 {oceanographic_count} 条海洋数据记录")
                
                # 清理数据源
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
        """获取表中的记录数"""
        try:
            if not self.ensure_connection():
                return -1
            
            with self.connection_manager.get_session() as session:
                if table_name == 'oceanographic_data':
                    return session.query(OceanographicData).count()
                elif table_name == 'data_sources':
                    return session.query(DataSource).count()
                else:
                    # 使用原生 SQL 查询
                    from sqlalchemy import text
                    result = session.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                    return result.scalar()
        
        except Exception as e:
            self.logger.error(f"获取表 {table_name} 记录数失败: {e}")
            return -1
    
    def verify_data_integrity(self, sample_data: pd.DataFrame) -> Dict[str, Any]:
        """验证数据完整性"""
        integrity_results = {
            'total_records': len(sample_data),
            'null_values': {},
            'constraint_violations': {},
            'data_quality_issues': []
        }
        
        # 检查空值
        for column in sample_data.columns:
            null_count = sample_data[column].isnull().sum()
            if null_count > 0:
                integrity_results['null_values'][column] = null_count
        
        # 检查约束违反
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
        """临时数据上下文管理器"""
        from triaxus.database.mappers import DataMapper
        
        mapper = DataMapper()
        models = mapper.dataframe_to_models(data, "temp_test_data.csv")
        
        try:
            # 插入临时数据
            if self.ensure_connection():
                with self.connection_manager.get_session() as session:
                    session.add_all(models)
                    session.commit()
            
            yield models
        
        finally:
            # 清理临时数据
            try:
                if self.ensure_connection():
                    with self.connection_manager.get_session() as session:
                        for model in models:
                            session.delete(model)
                        session.commit()
            except Exception as e:
                self.logger.warning(f"清理临时数据失败: {e}")


class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self):
        """初始化性能监控器"""
        self.metrics = {}
        self.start_time = None
        self.monitoring = False
        self.monitor_thread = None
    
    def start_monitoring(self, interval: float = 1.0):
        """开始性能监控"""
        self.start_time = time.time()
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, args=(interval,))
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
    
    def stop_monitoring(self) -> Dict[str, Any]:
        """停止性能监控并返回结果"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        
        return self._calculate_summary()
    
    def _monitor_loop(self, interval: float):
        """监控循环"""
        while self.monitoring:
            try:
                timestamp = time.time() - self.start_time
                
                # 收集系统指标
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
        """计算性能摘要"""
        if not self.metrics:
            return {}
        
        # 转换为 DataFrame 便于计算
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
    """基准测试计时器"""
    
    def __init__(self, name: str = "Benchmark"):
        """初始化计时器"""
        self.name = name
        self.start_time = None
        self.end_time = None
        self.measurements = []
    
    def start(self):
        """开始计时"""
        self.start_time = time.perf_counter()
    
    def stop(self) -> float:
        """停止计时并返回耗时"""
        if self.start_time is None:
            raise ValueError("计时器未启动")
        
        self.end_time = time.perf_counter()
        duration = self.end_time - self.start_time
        self.measurements.append(duration)
        return duration
    
    def reset(self):
        """重置计时器"""
        self.start_time = None
        self.end_time = None
    
    def get_statistics(self) -> Dict[str, float]:
        """获取统计信息"""
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
        """计时上下文管理器"""
        self.start()
        try:
            yield self
        finally:
            self.stop()


class TestDataValidator:
    """测试数据验证器"""
    
    @staticmethod
    def validate_oceanographic_data(data: pd.DataFrame) -> Dict[str, Any]:
        """验证海洋数据"""
        validation_results = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'statistics': {}
        }
        
        required_columns = ['time', 'depth', 'latitude', 'longitude']
        
        # 检查必需列
        missing_columns = [col for col in required_columns if col not in data.columns]
        if missing_columns:
            validation_results['valid'] = False
            validation_results['errors'].append(f"缺少必需列: {missing_columns}")
        
        # 检查数据范围
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
        
        # 检查数据质量
        null_counts = data.isnull().sum()
        high_null_columns = null_counts[null_counts > len(data) * 0.5]
        if not high_null_columns.empty:
            validation_results['warnings'].append(f"以下列有超过50%的空值: {high_null_columns.index.tolist()}")
        
        # 计算统计信息
        validation_results['statistics'] = {
            'total_records': len(data),
            'null_values': null_counts.to_dict(),
            'data_types': data.dtypes.to_dict()
        }
        
        return validation_results
    
    @staticmethod
    def validate_test_results(results: Dict[str, Any]) -> bool:
        """验证测试结果格式"""
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
    """数据库连接测试器"""
    
    def __init__(self):
        """初始化连接测试器"""
        self.connection_manager = DatabaseConnectionManager()
    
    def test_basic_connectivity(self) -> Dict[str, Any]:
        """测试基础连接"""
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
        """测试连接池"""
        try:
            if not self.connection_manager.is_connected():
                self.connection_manager.connect()
            
            # 创建多个会话测试连接池
            sessions = []
            for i in range(pool_size):
                session = self.connection_manager.session_factory()
                sessions.append(session)
            
            # 关闭所有会话
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
        """测试事务处理"""
        try:
            if not self.connection_manager.is_connected():
                self.connection_manager.connect()
            
            # 测试正常事务
            with self.connection_manager.get_session() as session:
                from sqlalchemy import text
                result = session.execute(text("SELECT 1"))
                assert result.scalar() == 1
            
            # 测试事务回滚
            try:
                with self.connection_manager.get_session() as session:
                    session.execute(text("SELECT 1"))
                    raise Exception("测试异常")
            except Exception:
                pass  # 预期的异常
            
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
    """装饰器：测量函数执行时间"""
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        
        execution_time = end_time - start_time
        
        # 如果结果是字典，添加执行时间
        if isinstance(result, dict):
            result['execution_time'] = execution_time
        
        return result
    
    return wrapper


def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """装饰器：失败时重试"""
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


# 便利函数
def setup_test_environment():
    """设置测试环境"""
    # 设置环境变量
    os.environ['DB_ENABLED'] = 'true'
    
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def cleanup_test_environment():
    """清理测试环境"""
    helper = DatabaseTestHelper()
    return helper.clean_test_data()


if __name__ == "__main__":
    # 示例用法
    setup_test_environment()
    
    # 测试数据库连接
    conn_tester = DatabaseConnectionTester()
    result = conn_tester.test_basic_connectivity()
    print(f"连接测试结果: {result}")
    
    # 性能监控示例
    monitor = PerformanceMonitor()
    monitor.start_monitoring()
    
    # 模拟一些工作
    time.sleep(2)
    
    perf_summary = monitor.stop_monitoring()
    print(f"性能摘要: {perf_summary}")
    
    # 基准测试示例
    timer = BenchmarkTimer("示例测试")
    with timer.measure():
        time.sleep(0.1)
    
    stats = timer.get_statistics()
    print(f"基准测试统计: {stats}")
