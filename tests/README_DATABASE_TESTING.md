# TRIAXUS 数据库测试使用指南

## 概述

本指南介绍如何使用 TRIAXUS 数据库测试套件。该测试套件提供了全面的数据库功能测试，包括连接性、模式验证、数据映射、CRUD 操作、性能测试等。

## 快速开始

### 1. 环境准备

```bash
# 设置必需的环境变量
export DB_ENABLED=true
export DATABASE_URL=postgresql://username:password@localhost:5432/triaxus_test

# 安装依赖（如果需要）
pip install psutil pyyaml
```

### 2. 检查环境

```bash
# 检查测试环境是否正确配置
python tests/run_database_tests.py --check-env
```

### 3. 运行快速测试

```bash
# 运行基础连接测试
python tests/run_database_tests.py --quick
```

### 4. 运行完整测试

```bash
# 运行所有测试类别
python tests/run_database_tests.py --full

# 运行特定测试类别
python tests/run_database_tests.py --full --categories connectivity schema
```

## 测试文件结构

```
tests/
├── DATABASE_TESTING_PLAN.md           # 详细测试方案文档
├── database_test_config.yaml          # 测试配置文件
├── run_database_tests.py              # 快速测试执行脚本
├── advanced_database_test_runner.py   # 高级测试执行器
├── test_database.py                   # 原有的数据库测试脚本
├── fixtures/
│   └── test_data_generator.py         # 测试数据生成器
├── utils/
│   └── test_utilities.py              # 测试工具函数
└── unit/database/
    ├── test_connectivity.py           # 连接性测试
    ├── test_schema.py                  # 模式测试
    ├── test_mapping.py                 # 数据映射测试
    └── test_operations.py              # 操作测试
```

## 测试类别说明

### 1. 连接性测试 (Connectivity)
- 基础数据库连接
- 会话管理
- 连接池功能
- 并发连接处理

### 2. 模式测试 (Schema)
- 表结构验证
- 列定义检查
- 索引存在性验证
- 约束验证

### 3. 数据映射测试 (Mapping)
- DataFrame 到模型转换
- 模型到 DataFrame 转换
- 字段映射准确性
- 数据类型转换

### 4. 操作测试 (Operations)
- CRUD 操作
- 批量操作
- 仓储模式功能
- 性能测试

## 使用方法

### 基础用法

```bash
# 1. 生成示例配置文件
python tests/run_database_tests.py --generate-config

# 2. 检查环境
python tests/run_database_tests.py --check-env

# 3. 运行快速测试
python tests/run_database_tests.py --quick

# 4. 运行完整测试
python tests/run_database_tests.py --full

# 5. 清理测试数据
python tests/run_database_tests.py --cleanup
```

### 高级用法

```bash
# 使用自定义配置文件
python tests/run_database_tests.py --full --config my_config.yaml

# 指定测试环境
python tests/run_database_tests.py --full --environment production

# 运行特定测试类别
python tests/run_database_tests.py --full --categories connectivity operations

# 详细输出
python tests/run_database_tests.py --full --verbose
```

### 使用高级测试执行器

```bash
# 直接使用高级执行器
python tests/advanced_database_test_runner.py --environment development

# 指定配置文件和测试类别
python tests/advanced_database_test_runner.py \
    --config tests/database_test_config.yaml \
    --environment integration \
    --categories connectivity schema mapping operations
```

## 配置文件

### 基础配置

```yaml
# tests/database_test_config.yaml
test_environments:
  development:
    database_url: "postgresql://user:pass@localhost:5432/triaxus_test"
    pool_size: 5
    max_overflow: 10

test_cases:
  connectivity:
    enabled: true
  schema:
    enabled: true
  mapping:
    enabled: true
  operations:
    enabled: true

reporting:
  output_formats: ["html", "json"]
  output_directory: "test_results"
```

### 性能测试配置

```yaml
performance_benchmarks:
  insertion:
    target_rate: 1000        # 目标插入速率 (records/sec)
  query:
    simple_query_time: 2     # 简单查询最大时间 (ms)
    complex_query_time: 20   # 复杂查询最大时间 (ms)

test_data:
  performance_test_size: 10000   # 性能测试数据量
  stress_test_size: 100000       # 压力测试数据量
```

## 测试数据生成

### 使用测试数据生成器

```python
from tests.fixtures.test_data_generator import TestDataManager

# 创建数据管理器
manager = TestDataManager()

# 生成基础测试数据
basic_data = manager.get_test_dataset('basic', count=100)

# 生成现实的海洋剖面数据
profile_data = manager.get_test_dataset('realistic_profile', count=1000)

# 生成边界测试数据
boundary_data = manager.get_test_dataset('boundary')

# 生成性能测试数据
perf_data = manager.get_test_dataset('performance', count=10000)
```

### 数据类型

- `basic`: 基础随机数据
- `realistic_profile`: 现实的海洋剖面数据
- `boundary`: 边界值测试数据
- `invalid`: 无效数据（用于约束测试）
- `performance`: 性能测试数据
- `stress`: 压力测试数据

## 测试报告

测试完成后，报告将生成在 `test_results/` 目录中：

- `database_test_report_YYYYMMDD_HHMMSS.html` - HTML 格式报告
- `database_test_report_YYYYMMDD_HHMMSS.json` - JSON 格式报告
- `database_test_report_YYYYMMDD_HHMMSS.xml` - XML 格式报告（JUnit 兼容）

### 报告内容

- 测试执行摘要
- 详细测试结果
- 性能指标
- 失败分析
- 系统资源使用情况

## 性能监控

测试执行期间会自动监控系统性能：

- CPU 使用率
- 内存使用率
- 磁盘 I/O
- 网络 I/O
- 数据库连接数

## 故障排除

### 常见问题

#### 1. 数据库连接失败

```
错误: FATAL: password authentication failed
解决方案:
- 检查 DATABASE_URL 环境变量
- 验证数据库用户名和密码
- 确认数据库服务正在运行
```

#### 2. 表不存在

```
错误: relation "oceanographic_data" does not exist
解决方案:
- 运行数据库初始化脚本
- 检查数据库模式
```

#### 3. 权限错误

```
错误: permission denied for table
解决方案:
- 检查数据库用户权限
- 确认用户有创建/删除表的权限
```

### 调试技巧

1. **启用详细日志**:
   ```bash
   python tests/run_database_tests.py --full --verbose
   ```

2. **检查数据库日志**:
   ```bash
   tail -f /var/log/postgresql/postgresql-13-main.log
   ```

3. **使用 SQL 调试**:
   ```yaml
   # 在配置文件中启用 SQL 回显
   test_environments:
     development:
       echo: true
   ```

## 持续集成

### GitHub Actions 示例

```yaml
name: Database Tests
on: [push, pull_request]

jobs:
  database-tests:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: triaxus_test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install psutil pyyaml
    
    - name: Run database tests
      env:
        DB_ENABLED: true
        DATABASE_URL: postgresql://postgres:postgres@localhost:5432/triaxus_test
      run: |
        python tests/run_database_tests.py --full
    
    - name: Upload test reports
      uses: actions/upload-artifact@v2
      if: always()
      with:
        name: test-reports
        path: test_results/
```

## 最佳实践

1. **测试前清理**: 始终在测试前清理旧数据
2. **环境隔离**: 使用专用的测试数据库
3. **数据备份**: 在生产环境测试前备份数据
4. **监控资源**: 关注测试期间的系统资源使用
5. **定期运行**: 将测试集成到 CI/CD 流程中

## 扩展测试

### 添加自定义测试

1. 在 `tests/unit/database/` 中创建新的测试模块
2. 实现测试类，遵循现有模式
3. 在配置文件中启用新测试
4. 更新测试执行器以包含新测试

### 自定义数据生成器

```python
from tests.fixtures.test_data_generator import OceanographicTestDataGenerator

class CustomDataGenerator(OceanographicTestDataGenerator):
    def generate_custom_data(self, count: int):
        # 实现自定义数据生成逻辑
        pass
```

## 支持和贡献

如有问题或建议，请：

1. 查看详细的测试方案文档：`tests/DATABASE_TESTING_PLAN.md`
2. 检查现有的测试用例实现
3. 提交 Issue 或 Pull Request

---

**版本**: 1.0  
**最后更新**: 2024-01-15  
**维护者**: TRIAXUS 开发团队
