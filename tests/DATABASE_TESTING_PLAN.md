# TRIAXUS 数据库测试方案

## 概述

本文档详细描述了 TRIAXUS 海洋数据可视化系统的数据库测试方案。该方案涵盖了从基础连接测试到复杂性能测试的完整测试体系，确保数据库系统的可靠性、性能和数据完整性。

## 目录

1. [测试架构](#测试架构)
2. [测试环境配置](#测试环境配置)
3. [测试分类](#测试分类)
4. [测试用例详细说明](#测试用例详细说明)
5. [性能测试](#性能测试)
6. [数据完整性测试](#数据完整性测试)
7. [安全性测试](#安全性测试)
8. [测试执行流程](#测试执行流程)
9. [测试报告](#测试报告)
10. [故障排除](#故障排除)

## 测试架构

### 系统架构概览

```
TRIAXUS Database Testing Architecture
├── 数据库层 (PostgreSQL)
│   ├── 主要表: oceanographic_data
│   ├── 元数据表: data_sources
│   ├── 索引和约束
│   └── 视图和存储过程
├── ORM层 (SQLAlchemy)
│   ├── 模型定义 (models.py)
│   ├── 数据映射 (mappers.py)
│   └── 仓储模式 (repositories.py)
├── 连接管理层
│   ├── 连接池管理
│   ├── 会话管理
│   └── 配置管理
└── 测试层
    ├── 单元测试
    ├── 集成测试
    ├── 性能测试
    └── 端到端测试
```

### 核心组件

- **DatabaseConnectionManager**: 数据库连接和会话管理
- **OceanographicData Model**: 海洋数据主模型
- **DataSource Model**: 数据源元数据模型
- **DataMapper**: 数据框架与模型间的映射
- **OceanographicDataRepository**: 数据访问仓储

## 测试环境配置

### 环境变量设置

```bash
# 必需的环境变量
export DB_ENABLED=true
export DATABASE_URL=postgresql://username:password@localhost:5432/triaxus_db

# 可选的配置变量
export DB_POOL_SIZE=5
export DB_MAX_OVERFLOW=10
export DB_POOL_TIMEOUT=30
export DB_ECHO=false
```

### 数据库配置

```yaml
database:
  enabled: true
  url: postgresql://username:password@localhost:5432/triaxus_db
  pool_size: 5
  max_overflow: 10
  pool_timeout: 30
  pool_recycle: 3600
  echo: false
```

### 测试数据库设置

1. **开发测试数据库**: `triaxus_test_dev`
2. **集成测试数据库**: `triaxus_test_integration`
3. **性能测试数据库**: `triaxus_test_performance`

## 测试分类

### 1. 连接性测试 (Connectivity Tests)

**目标**: 验证数据库连接、会话管理和连接池功能

**测试模块**: `tests/unit/database/test_connectivity.py`

**测试用例**:
- 基础数据库连接测试
- 会话创建和管理测试
- 连接池功能测试
- 连接超时和重连测试
- 并发连接测试

### 2. 模式测试 (Schema Tests)

**目标**: 验证数据库表结构、列定义、索引和约束

**测试模块**: `tests/unit/database/test_schema.py`

**测试用例**:
- 表存在性验证
- 列定义和数据类型验证
- 主键和外键约束验证
- 索引存在性和性能验证
- 数据库视图验证

### 3. 数据映射测试 (Mapping Tests)

**目标**: 验证 DataFrame 与数据库模型间的数据转换

**测试模块**: `tests/unit/database/test_mapping.py`

**测试用例**:
- DataFrame 到模型的转换测试
- 模型到 DataFrame 的转换测试
- 字段映射正确性测试
- 数据类型转换测试
- 空值和异常数据处理测试

### 4. 操作测试 (Operations Tests)

**目标**: 验证 CRUD 操作、仓储模式和业务逻辑

**测试模块**: `tests/unit/database/test_operations.py`

**测试用例**:
- 数据插入操作测试
- 数据查询操作测试
- 数据更新操作测试
- 数据删除操作测试
- 批量操作测试
- 仓储模式功能测试

## 测试用例详细说明

### 连接性测试详细用例

#### TC-CONN-001: 基础连接测试
```python
def test_basic_connection():
    """测试基础数据库连接功能"""
    # 预期结果: 成功建立连接
    # 验证点: connection_manager.is_connected() == True
```

#### TC-CONN-002: 会话管理测试
```python
def test_session_management():
    """测试会话创建、提交和回滚"""
    # 预期结果: 会话正常创建和管理
    # 验证点: 会话上下文管理器正常工作
```

#### TC-CONN-003: 连接池测试
```python
def test_connection_pool():
    """测试连接池的并发处理能力"""
    # 预期结果: 多个并发连接正常处理
    # 验证点: 连接池配置参数生效
```

### 模式测试详细用例

#### TC-SCHEMA-001: 表结构验证
```python
def test_table_structure():
    """验证核心表的存在和结构"""
    # 验证表: oceanographic_data, data_sources
    # 预期结果: 所有必需表存在且结构正确
```

#### TC-SCHEMA-002: 列定义验证
```python
def test_column_definitions():
    """验证表列的数据类型和约束"""
    # 验证列: id, datetime, depth, latitude, longitude, etc.
    # 预期结果: 列类型和约束符合设计要求
```

#### TC-SCHEMA-003: 索引性能验证
```python
def test_index_performance():
    """验证关键索引的存在和性能"""
    # 验证索引: datetime, depth, latitude, longitude
    # 预期结果: 索引存在且查询性能符合要求
```

### 数据映射测试详细用例

#### TC-MAPPING-001: DataFrame 转模型测试
```python
def test_dataframe_to_model_conversion():
    """测试 DataFrame 到 OceanographicData 模型的转换"""
    # 输入: 标准海洋数据 DataFrame
    # 预期结果: 正确转换为模型对象列表
```

#### TC-MAPPING-002: 模型转 DataFrame 测试
```python
def test_model_to_dataframe_conversion():
    """测试模型对象到 DataFrame 的转换"""
    # 输入: OceanographicData 模型对象列表
    # 预期结果: 正确转换为 DataFrame
```

#### TC-MAPPING-003: 字段映射测试
```python
def test_field_mapping_accuracy():
    """测试字段映射的准确性"""
    # 验证映射: time->datetime, tv290c->tv290c, etc.
    # 预期结果: 所有字段正确映射
```

### 操作测试详细用例

#### TC-OPS-001: 数据插入测试
```python
def test_data_insertion():
    """测试海洋数据的插入操作"""
    # 操作: 插入测试数据
    # 预期结果: 数据成功插入且可查询
```

#### TC-OPS-002: 批量操作测试
```python
def test_bulk_operations():
    """测试批量数据操作的性能和正确性"""
    # 操作: 批量插入大量数据
    # 预期结果: 操作成功且性能符合要求
```

#### TC-OPS-003: 仓储模式测试
```python
def test_repository_pattern():
    """测试仓储模式的各种查询方法"""
    # 操作: 使用仓储方法进行各种查询
    # 预期结果: 查询结果正确且性能良好
```

## 性能测试

### 性能测试指标

| 操作类型 | 目标性能 | 测试数据量 | 验收标准 |
|---------|---------|-----------|----------|
| 单条插入 | > 100 ops/sec | 1,000 条记录 | 平均响应时间 < 10ms |
| 批量插入 | > 1,000 records/sec | 10,000 条记录 | 总时间 < 10s |
| 简单查询 | > 500 ops/sec | 100,000 条记录 | 平均响应时间 < 2ms |
| 复杂查询 | > 50 ops/sec | 100,000 条记录 | 平均响应时间 < 20ms |
| 聚合查询 | > 10 ops/sec | 1,000,000 条记录 | 平均响应时间 < 100ms |

### 性能测试用例

#### TC-PERF-001: 插入性能测试
```python
def test_insertion_performance():
    """测试数据插入操作的性能"""
    # 测试场景: 插入 10,000 条海洋数据记录
    # 性能目标: > 1,000 records/sec
    # 监控指标: 插入速率、内存使用、CPU 使用率
```

#### TC-PERF-002: 查询性能测试
```python
def test_query_performance():
    """测试各种查询操作的性能"""
    # 测试场景: 在 100,000 条记录中进行各种查询
    # 性能目标: 简单查询 < 2ms, 复杂查询 < 20ms
    # 监控指标: 查询响应时间、索引使用情况
```

#### TC-PERF-003: 并发性能测试
```python
def test_concurrent_performance():
    """测试并发操作的性能和稳定性"""
    # 测试场景: 10 个并发连接同时进行读写操作
    # 性能目标: 无死锁、无连接泄漏
    # 监控指标: 连接池使用率、事务成功率
```

## 数据完整性测试

### 数据完整性验证

#### TC-INTEGRITY-001: 约束验证测试
```python
def test_constraint_validation():
    """测试数据库约束的有效性"""
    # 测试场景: 插入违反约束的数据
    # 预期结果: 约束生效，操作被拒绝
    # 验证约束: 深度 >= 0, 纬度范围, 经度范围
```

#### TC-INTEGRITY-002: 数据一致性测试
```python
def test_data_consistency():
    """测试数据的一致性和完整性"""
    # 测试场景: 复杂的数据操作序列
    # 预期结果: 数据保持一致性
    # 验证点: 外键关系、事务完整性
```

#### TC-INTEGRITY-003: 数据恢复测试
```python
def test_data_recovery():
    """测试数据恢复和回滚机制"""
    # 测试场景: 模拟操作失败和回滚
    # 预期结果: 数据正确回滚到之前状态
```

## 安全性测试

### 安全测试用例

#### TC-SECURITY-001: 连接安全测试
```python
def test_connection_security():
    """测试数据库连接的安全性"""
    # 验证点: SSL 连接、密码加密、连接超时
```

#### TC-SECURITY-002: SQL 注入防护测试
```python
def test_sql_injection_protection():
    """测试 SQL 注入攻击的防护"""
    # 测试场景: 尝试各种 SQL 注入攻击
    # 预期结果: 攻击被有效阻止
```

#### TC-SECURITY-003: 权限控制测试
```python
def test_access_control():
    """测试数据库访问权限控制"""
    # 验证点: 用户权限、表级权限、列级权限
```

## 测试执行流程

### 自动化测试执行

```bash
# 执行完整数据库测试套件
python tests/test_database.py

# 执行特定类别的测试
python tests/test_database.py --category connectivity
python tests/test_database.py --category schema
python tests/test_database.py --category mapping
python tests/test_database.py --category operations

# 清理数据库后执行测试
python tests/test_database.py --clean-db
```

### 测试执行顺序

1. **环境准备**: 设置环境变量和数据库连接
2. **连接性测试**: 验证基础连接功能
3. **模式测试**: 验证数据库结构
4. **映射测试**: 验证数据转换功能
5. **操作测试**: 验证 CRUD 操作
6. **性能测试**: 验证系统性能
7. **完整性测试**: 验证数据完整性
8. **安全性测试**: 验证安全机制
9. **清理**: 清理测试数据和连接

### 持续集成集成

```yaml
# CI/CD 管道配置示例
database_tests:
  stage: test
  script:
    - export DB_ENABLED=true
    - export DATABASE_URL=$TEST_DATABASE_URL
    - python tests/test_database.py --clean-db
  artifacts:
    reports:
      junit: test-results.xml
    paths:
      - test-results/
```

## 测试报告

### 报告格式

测试报告包含以下部分：

1. **执行摘要**: 总体测试结果和统计
2. **详细结果**: 每个测试用例的详细结果
3. **性能指标**: 关键性能指标和趋势
4. **失败分析**: 失败用例的详细分析
5. **建议**: 改进建议和后续行动

### 报告示例

```
=============================================================
TRIAXUS DATABASE TESTING REPORT
=============================================================
执行时间: 2024-01-15 14:30:00
测试环境: PostgreSQL 13.x on localhost
数据库: triaxus_test_db

总体结果:
- 总测试数: 45
- 通过: 43
- 失败: 2
- 成功率: 95.6%
- 总执行时间: 125.3 秒

分类结果:
- 连接性测试: 12/12 通过
- 模式测试: 8/8 通过
- 映射测试: 10/10 通过
- 操作测试: 13/15 通过 (2 个失败)

性能指标:
- 插入速率: 1,250 records/sec
- 查询速率: 850 queries/sec
- 平均响应时间: 3.2ms

失败用例分析:
1. TC-OPS-014: 大批量插入超时
   - 原因: 连接池配置不足
   - 建议: 增加 max_overflow 参数

2. TC-OPS-015: 并发更新死锁
   - 原因: 事务隔离级别设置
   - 建议: 调整事务隔离级别
```

## 故障排除

### 常见问题和解决方案

#### 问题 1: 数据库连接失败
```
错误: FATAL: password authentication failed for user "username"
解决方案:
1. 检查数据库用户名和密码
2. 验证数据库服务是否运行
3. 检查网络连接和防火墙设置
```

#### 问题 2: 表不存在错误
```
错误: relation "oceanographic_data" does not exist
解决方案:
1. 运行数据库初始化脚本
2. 检查数据库模式是否正确创建
3. 验证用户权限
```

#### 问题 3: 性能测试失败
```
错误: 插入性能低于预期 (500 records/sec < 1000 records/sec)
解决方案:
1. 检查数据库配置和硬件资源
2. 优化索引策略
3. 调整连接池参数
```

### 调试工具和技巧

1. **日志分析**: 启用 SQLAlchemy 日志记录
2. **性能分析**: 使用 PostgreSQL 的 EXPLAIN ANALYZE
3. **连接监控**: 监控连接池状态和使用情况
4. **资源监控**: 监控 CPU、内存和磁盘 I/O

### 测试数据管理

1. **测试数据生成**: 使用 `PlotTestDataGenerator` 生成测试数据
2. **数据清理**: 每次测试前清理旧数据
3. **数据备份**: 保留重要测试数据的备份
4. **数据隔离**: 使用独立的测试数据库

## 测试实施指南

### 测试环境搭建

#### 1. 开发环境设置

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 设置环境变量
export DB_ENABLED=true
export DATABASE_URL=postgresql://triaxus_user:password@localhost:5432/triaxus_test

# 3. 初始化测试数据库
python -c "
from triaxus.database.initializer import DatabaseInitializer
initializer = DatabaseInitializer()
initializer.initialize_database()
"

# 4. 验证安装
python tests/test_database.py --category connectivity
```

#### 2. Docker 测试环境

```dockerfile
# Dockerfile.test
FROM postgres:13
ENV POSTGRES_DB=triaxus_test
ENV POSTGRES_USER=triaxus_user
ENV POSTGRES_PASSWORD=test_password
COPY database/sql/init_database.sql /docker-entrypoint-initdb.d/
```

```yaml
# docker-compose.test.yml
version: '3.8'
services:
  test-db:
    build:
      context: .
      dockerfile: Dockerfile.test
    ports:
      - "5433:5432"
    environment:
      POSTGRES_DB: triaxus_test
      POSTGRES_USER: triaxus_user
      POSTGRES_PASSWORD: test_password
    volumes:
      - test_db_data:/var/lib/postgresql/data

volumes:
  test_db_data:
```

### 测试数据管理策略

#### 测试数据分类

1. **基础测试数据**: 最小化的有效数据集
2. **边界测试数据**: 边界值和极端情况数据
3. **性能测试数据**: 大量数据用于性能测试
4. **异常测试数据**: 无效和异常数据

#### 测试数据生成器

```python
# tests/fixtures/data_generator.py
class TestDataGenerator:
    """测试数据生成器"""

    @staticmethod
    def generate_basic_oceanographic_data(count=100):
        """生成基础海洋数据"""
        return pd.DataFrame({
            'time': pd.date_range('2024-01-01', periods=count, freq='1H'),
            'depth': np.random.uniform(0, 1000, count),
            'latitude': np.random.uniform(-90, 90, count),
            'longitude': np.random.uniform(-180, 180, count),
            'tv290c': np.random.uniform(0, 30, count),
            'sal00': np.random.uniform(30, 40, count)
        })

    @staticmethod
    def generate_boundary_test_data():
        """生成边界测试数据"""
        return pd.DataFrame({
            'time': [datetime.min, datetime.max],
            'depth': [0, 11000],  # 最深海沟
            'latitude': [-90, 90],
            'longitude': [-180, 180],
            'tv290c': [-2, 40],  # 海水温度范围
            'sal00': [0, 50]     # 盐度范围
        })

    @staticmethod
    def generate_invalid_test_data():
        """生成无效测试数据"""
        return pd.DataFrame({
            'time': [None, 'invalid_date'],
            'depth': [-100, float('inf')],  # 负深度和无穷大
            'latitude': [-100, 100],        # 超出范围
            'longitude': [-200, 200],       # 超出范围
            'tv290c': [None, float('nan')],
            'sal00': [-10, 100]             # 异常盐度值
        })
```

### 高级测试场景

#### 并发测试场景

```python
# tests/advanced/test_concurrency.py
import threading
import time
from concurrent.futures import ThreadPoolExecutor

class ConcurrencyTester:
    """并发测试器"""

    def test_concurrent_insertions(self):
        """测试并发插入操作"""
        def insert_worker(worker_id, record_count):
            """工作线程函数"""
            connection_manager = DatabaseConnectionManager()
            connection_manager.connect()

            test_data = TestDataGenerator.generate_basic_oceanographic_data(record_count)
            mapper = DataMapper()
            models = mapper.dataframe_to_models(test_data, f"worker_{worker_id}.csv")

            with connection_manager.get_session() as session:
                session.add_all(models)
                session.commit()

            return len(models)

        # 启动多个并发工作线程
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            for i in range(10):
                future = executor.submit(insert_worker, i, 1000)
                futures.append(future)

            # 收集结果
            total_inserted = sum(future.result() for future in futures)

        # 验证结果
        assert total_inserted == 10000

    def test_read_write_concurrency(self):
        """测试读写并发操作"""
        # 实现读写并发测试逻辑
        pass
```

#### 故障恢复测试

```python
# tests/advanced/test_fault_tolerance.py
class FaultToleranceTester:
    """故障容错测试器"""

    def test_connection_recovery(self):
        """测试连接恢复能力"""
        connection_manager = DatabaseConnectionManager()
        connection_manager.connect()

        # 模拟连接中断
        connection_manager.disconnect()

        # 尝试重新连接
        recovery_success = connection_manager.connect()
        assert recovery_success

    def test_transaction_rollback(self):
        """测试事务回滚机制"""
        connection_manager = DatabaseConnectionManager()
        connection_manager.connect()

        try:
            with connection_manager.get_session() as session:
                # 插入有效数据
                valid_data = OceanographicData(
                    datetime=datetime.now(),
                    depth=100.0,
                    latitude=45.0,
                    longitude=-120.0
                )
                session.add(valid_data)

                # 插入无效数据（触发异常）
                invalid_data = OceanographicData(
                    datetime=datetime.now(),
                    depth=-100.0,  # 违反约束
                    latitude=45.0,
                    longitude=-120.0
                )
                session.add(invalid_data)
                session.commit()
        except Exception:
            # 验证回滚后数据库状态
            with connection_manager.get_session() as session:
                count = session.query(OceanographicData).count()
                # 应该没有数据被插入
                assert count == 0
```

### 性能基准测试

#### 基准测试套件

```python
# tests/benchmarks/performance_benchmarks.py
import time
import statistics
from typing import List, Dict

class PerformanceBenchmark:
    """性能基准测试"""

    def __init__(self):
        self.results = {}

    def benchmark_insertion_performance(self, record_counts: List[int]):
        """基准测试插入性能"""
        results = {}

        for count in record_counts:
            times = []
            for run in range(5):  # 运行5次取平均值
                test_data = TestDataGenerator.generate_basic_oceanographic_data(count)
                mapper = DataMapper()
                models = mapper.dataframe_to_models(test_data)

                start_time = time.time()

                connection_manager = DatabaseConnectionManager()
                connection_manager.connect()
                with connection_manager.get_session() as session:
                    session.add_all(models)
                    session.commit()

                end_time = time.time()
                times.append(end_time - start_time)

            avg_time = statistics.mean(times)
            records_per_sec = count / avg_time

            results[count] = {
                'avg_time': avg_time,
                'records_per_sec': records_per_sec,
                'std_dev': statistics.stdev(times)
            }

        return results

    def benchmark_query_performance(self):
        """基准测试查询性能"""
        # 实现查询性能基准测试
        pass
```

### 测试报告生成

#### 自动化报告生成器

```python
# tests/reporting/test_reporter.py
import json
from datetime import datetime
from typing import Dict, Any

class TestReporter:
    """测试报告生成器"""

    def __init__(self):
        self.report_data = {
            'timestamp': datetime.now().isoformat(),
            'environment': self._get_environment_info(),
            'results': {}
        }

    def add_test_results(self, category: str, results: Dict[str, Any]):
        """添加测试结果"""
        self.report_data['results'][category] = results

    def generate_html_report(self, output_path: str):
        """生成 HTML 格式报告"""
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>TRIAXUS Database Test Report</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .header { background-color: #f0f0f0; padding: 20px; }
                .summary { background-color: #e8f5e8; padding: 15px; margin: 10px 0; }
                .failed { background-color: #ffe8e8; }
                .test-category { margin: 20px 0; }
                table { border-collapse: collapse; width: 100%; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #f2f2f2; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>TRIAXUS Database Test Report</h1>
                <p>Generated: {timestamp}</p>
            </div>

            <div class="summary">
                <h2>Test Summary</h2>
                <p>Total Tests: {total_tests}</p>
                <p>Passed: {passed_tests}</p>
                <p>Failed: {failed_tests}</p>
                <p>Success Rate: {success_rate}%</p>
            </div>

            {detailed_results}
        </body>
        </html>
        """

        # 生成详细结果HTML
        detailed_html = self._generate_detailed_results_html()

        # 计算汇总统计
        stats = self._calculate_summary_stats()

        # 填充模板
        html_content = html_template.format(
            timestamp=self.report_data['timestamp'],
            total_tests=stats['total'],
            passed_tests=stats['passed'],
            failed_tests=stats['failed'],
            success_rate=stats['success_rate'],
            detailed_results=detailed_html
        )

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

    def generate_json_report(self, output_path: str):
        """生成 JSON 格式报告"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.report_data, f, indent=2, ensure_ascii=False)

    def _get_environment_info(self) -> Dict[str, str]:
        """获取环境信息"""
        import platform
        import os

        return {
            'python_version': platform.python_version(),
            'platform': platform.platform(),
            'database_url': os.getenv('DATABASE_URL', 'Not set'),
            'db_enabled': os.getenv('DB_ENABLED', 'false')
        }

    def _calculate_summary_stats(self) -> Dict[str, Any]:
        """计算汇总统计"""
        total = 0
        passed = 0

        for category_results in self.report_data['results'].values():
            if isinstance(category_results, dict):
                for result in category_results.values():
                    if isinstance(result, dict) and 'status' in result:
                        total += 1
                        if result['status'] == 'PASSED':
                            passed += 1

        failed = total - passed
        success_rate = (passed / total * 100) if total > 0 else 0

        return {
            'total': total,
            'passed': passed,
            'failed': failed,
            'success_rate': round(success_rate, 1)
        }
```

---

**文档版本**: 1.0
**最后更新**: 2024-01-15
**维护者**: TRIAXUS 开发团队
**审核者**: 数据库架构师
