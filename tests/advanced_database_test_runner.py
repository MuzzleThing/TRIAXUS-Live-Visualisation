#!/usr/bin/env python3
"""
高级数据库测试执行器
TRIAXUS 数据库测试的高级执行脚本，支持配置文件、报告生成、监控等功能
"""

import os
import sys
import yaml
import json
import time
import logging
import argparse
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入测试模块
from tests.unit.database.test_connectivity import DatabaseConnectivityTester
from tests.unit.database.test_schema import DatabaseSchemaTester
from tests.unit.database.test_mapping import DatabaseMappingTester
from tests.unit.database.test_operations import DatabaseOperationsTester


@dataclass
class TestResult:
    """测试结果数据类"""
    name: str
    status: str
    duration: float
    details: Dict[str, Any]
    error: Optional[str] = None


class TestConfiguration:
    """测试配置管理器"""
    
    def __init__(self, config_path: str = "tests/database_test_config.yaml"):
        """初始化配置管理器"""
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logging.warning(f"配置文件 {self.config_path} 未找到，使用默认配置")
            return self._get_default_config()
        except yaml.YAMLError as e:
            logging.error(f"配置文件解析错误: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            'test_environments': {
                'development': {
                    'database_url': 'postgresql://triaxus_user:password@localhost:5432/triaxus_test',
                    'pool_size': 5,
                    'max_overflow': 10,
                    'echo': False
                }
            },
            'test_cases': {
                'connectivity': {'enabled': True},
                'schema': {'enabled': True},
                'mapping': {'enabled': True},
                'operations': {'enabled': True}
            },
            'performance_benchmarks': {
                'insertion': {'target_rate': 1000},
                'query': {'simple_query_time': 2}
            },
            'reporting': {
                'output_formats': ['html', 'json'],
                'output_directory': 'test_results'
            }
        }
    
    def get_environment_config(self, env_name: str) -> Dict[str, Any]:
        """获取环境配置"""
        return self.config.get('test_environments', {}).get(env_name, {})
    
    def get_test_config(self, test_category: str) -> Dict[str, Any]:
        """获取测试配置"""
        return self.config.get('test_cases', {}).get(test_category, {})
    
    def is_test_enabled(self, test_category: str) -> bool:
        """检查测试是否启用"""
        return self.get_test_config(test_category).get('enabled', True)


class TestMonitor:
    """测试监控器"""
    
    def __init__(self):
        """初始化监控器"""
        self.start_time = None
        self.metrics = {}
        self.monitoring_active = False
        self.monitor_thread = None
    
    def start_monitoring(self):
        """开始监控"""
        self.start_time = time.time()
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        logging.info("测试监控已启动")
    
    def stop_monitoring(self):
        """停止监控"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logging.info("测试监控已停止")
    
    def _monitor_loop(self):
        """监控循环"""
        while self.monitoring_active:
            try:
                # 收集系统指标
                self._collect_system_metrics()
                time.sleep(5)  # 每5秒收集一次指标
            except Exception as e:
                logging.error(f"监控错误: {e}")
    
    def _collect_system_metrics(self):
        """收集系统指标"""
        try:
            import psutil
            
            # CPU 使用率
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # 内存使用率
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # 磁盘 I/O
            disk_io = psutil.disk_io_counters()
            
            timestamp = time.time()
            self.metrics[timestamp] = {
                'cpu_percent': cpu_percent,
                'memory_percent': memory_percent,
                'disk_read_bytes': disk_io.read_bytes if disk_io else 0,
                'disk_write_bytes': disk_io.write_bytes if disk_io else 0
            }
            
        except ImportError:
            # psutil 未安装，跳过系统监控
            pass
        except Exception as e:
            logging.error(f"收集系统指标失败: {e}")


class TestReporter:
    """测试报告生成器"""
    
    def __init__(self, config: TestConfiguration):
        """初始化报告生成器"""
        self.config = config
        self.results = []
        self.start_time = None
        self.end_time = None
    
    def add_result(self, result: TestResult):
        """添加测试结果"""
        self.results.append(result)
    
    def generate_reports(self):
        """生成所有格式的报告"""
        output_dir = Path(self.config.config.get('reporting', {}).get('output_directory', 'test_results'))
        output_dir.mkdir(exist_ok=True)
        
        formats = self.config.config.get('reporting', {}).get('output_formats', ['html', 'json'])
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if 'html' in formats:
            html_path = output_dir / f"database_test_report_{timestamp}.html"
            self._generate_html_report(html_path)
        
        if 'json' in formats:
            json_path = output_dir / f"database_test_report_{timestamp}.json"
            self._generate_json_report(json_path)
        
        if 'xml' in formats:
            xml_path = output_dir / f"database_test_report_{timestamp}.xml"
            self._generate_xml_report(xml_path)
    
    def _generate_html_report(self, output_path: Path):
        """生成 HTML 报告"""
        # 计算统计信息
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.status == 'PASSED')
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        # HTML 模板
        html_content = f"""
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>TRIAXUS 数据库测试报告</title>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
                .container {{ max-width: 1200px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .header {{ text-align: center; margin-bottom: 30px; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 10px; }}
                .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }}
                .summary-card {{ background-color: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; border-left: 4px solid #007bff; }}
                .summary-card.success {{ border-left-color: #28a745; }}
                .summary-card.danger {{ border-left-color: #dc3545; }}
                .summary-card h3 {{ margin: 0 0 10px 0; color: #333; }}
                .summary-card .value {{ font-size: 2em; font-weight: bold; color: #007bff; }}
                .test-results {{ margin-top: 30px; }}
                .test-category {{ margin-bottom: 30px; }}
                .test-category h3 {{ color: #333; border-bottom: 2px solid #007bff; padding-bottom: 10px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
                th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
                th {{ background-color: #f8f9fa; font-weight: 600; }}
                .status-passed {{ color: #28a745; font-weight: bold; }}
                .status-failed {{ color: #dc3545; font-weight: bold; }}
                .duration {{ color: #6c757d; }}
                .footer {{ margin-top: 40px; text-align: center; color: #6c757d; border-top: 1px solid #ddd; padding-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>TRIAXUS 数据库测试报告</h1>
                    <p>生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
                
                <div class="summary">
                    <div class="summary-card">
                        <h3>总测试数</h3>
                        <div class="value">{total_tests}</div>
                    </div>
                    <div class="summary-card success">
                        <h3>通过测试</h3>
                        <div class="value" style="color: #28a745;">{passed_tests}</div>
                    </div>
                    <div class="summary-card danger">
                        <h3>失败测试</h3>
                        <div class="value" style="color: #dc3545;">{failed_tests}</div>
                    </div>
                    <div class="summary-card">
                        <h3>成功率</h3>
                        <div class="value">{success_rate:.1f}%</div>
                    </div>
                </div>
                
                <div class="test-results">
                    <h2>详细测试结果</h2>
                    {self._generate_test_results_html()}
                </div>
                
                <div class="footer">
                    <p>TRIAXUS 数据库测试系统 | 版本 1.0</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logging.info(f"HTML 报告已生成: {output_path}")
    
    def _generate_test_results_html(self) -> str:
        """生成测试结果的 HTML"""
        # 按类别分组测试结果
        categories = {}
        for result in self.results:
            category = result.name.split('_')[0] if '_' in result.name else 'Other'
            if category not in categories:
                categories[category] = []
            categories[category].append(result)
        
        html_parts = []
        for category, results in categories.items():
            html_parts.append(f'<div class="test-category">')
            html_parts.append(f'<h3>{category.title()} 测试</h3>')
            html_parts.append('<table>')
            html_parts.append('<tr><th>测试名称</th><th>状态</th><th>执行时间</th><th>详细信息</th></tr>')
            
            for result in results:
                status_class = 'status-passed' if result.status == 'PASSED' else 'status-failed'
                details = json.dumps(result.details, ensure_ascii=False, indent=2) if result.details else ''
                
                html_parts.append(f'''
                <tr>
                    <td>{result.name}</td>
                    <td class="{status_class}">{result.status}</td>
                    <td class="duration">{result.duration:.2f}s</td>
                    <td><pre style="font-size: 0.8em; max-height: 100px; overflow-y: auto;">{details}</pre></td>
                </tr>
                ''')
            
            html_parts.append('</table>')
            html_parts.append('</div>')
        
        return ''.join(html_parts)
    
    def _generate_json_report(self, output_path: Path):
        """生成 JSON 报告"""
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_tests': len(self.results),
                'passed_tests': sum(1 for r in self.results if r.status == 'PASSED'),
                'failed_tests': sum(1 for r in self.results if r.status == 'FAILED'),
                'success_rate': (sum(1 for r in self.results if r.status == 'PASSED') / len(self.results) * 100) if self.results else 0
            },
            'results': [
                {
                    'name': r.name,
                    'status': r.status,
                    'duration': r.duration,
                    'details': r.details,
                    'error': r.error
                }
                for r in self.results
            ]
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        logging.info(f"JSON 报告已生成: {output_path}")
    
    def _generate_xml_report(self, output_path: Path):
        """生成 XML 报告（JUnit 格式）"""
        import xml.etree.ElementTree as ET
        
        # 创建根元素
        testsuites = ET.Element('testsuites')
        testsuite = ET.SubElement(testsuites, 'testsuite')
        testsuite.set('name', 'TRIAXUS Database Tests')
        testsuite.set('tests', str(len(self.results)))
        testsuite.set('failures', str(sum(1 for r in self.results if r.status == 'FAILED')))
        testsuite.set('time', str(sum(r.duration for r in self.results)))
        
        # 添加测试用例
        for result in self.results:
            testcase = ET.SubElement(testsuite, 'testcase')
            testcase.set('name', result.name)
            testcase.set('time', str(result.duration))
            
            if result.status == 'FAILED':
                failure = ET.SubElement(testcase, 'failure')
                failure.set('message', result.error or 'Test failed')
                failure.text = json.dumps(result.details, ensure_ascii=False, indent=2)
        
        # 写入文件
        tree = ET.ElementTree(testsuites)
        tree.write(output_path, encoding='utf-8', xml_declaration=True)
        
        logging.info(f"XML 报告已生成: {output_path}")


class AdvancedDatabaseTestRunner:
    """高级数据库测试执行器"""
    
    def __init__(self, config_path: str = "tests/database_test_config.yaml"):
        """初始化测试执行器"""
        self.config = TestConfiguration(config_path)
        self.monitor = TestMonitor()
        self.reporter = TestReporter(self.config)
        self.setup_logging()
    
    def setup_logging(self):
        """设置日志"""
        log_config = self.config.config.get('logging', {})
        log_level = getattr(logging, log_config.get('level', 'INFO'))
        log_format = log_config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        # 创建日志目录
        log_file = log_config.get('file', 'test_logs/database_tests.log')
        log_dir = Path(log_file).parent
        log_dir.mkdir(exist_ok=True)
        
        # 配置日志
        logging.basicConfig(
            level=log_level,
            format=log_format,
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
    
    def run_tests(self, environment: str = 'development', categories: List[str] = None):
        """运行测试"""
        logging.info(f"开始运行数据库测试 - 环境: {environment}")
        
        # 设置环境变量
        self._setup_environment(environment)
        
        # 开始监控
        if self.config.config.get('monitoring', {}).get('enabled', False):
            self.monitor.start_monitoring()
        
        try:
            # 运行测试类别
            if categories is None:
                categories = ['connectivity', 'schema', 'mapping', 'operations']
            
            for category in categories:
                if self.config.is_test_enabled(category):
                    self._run_test_category(category)
                else:
                    logging.info(f"跳过已禁用的测试类别: {category}")
            
        finally:
            # 停止监控
            if self.config.config.get('monitoring', {}).get('enabled', False):
                self.monitor.stop_monitoring()
            
            # 生成报告
            self.reporter.generate_reports()
        
        logging.info("数据库测试完成")
    
    def _setup_environment(self, environment: str):
        """设置测试环境"""
        env_config = self.config.get_environment_config(environment)
        if env_config:
            os.environ['DATABASE_URL'] = env_config.get('database_url', '')
            os.environ['DB_ENABLED'] = 'true'
            logging.info(f"环境配置已设置: {environment}")
    
    def _run_test_category(self, category: str):
        """运行测试类别"""
        logging.info(f"运行 {category} 测试")
        
        start_time = time.time()
        
        try:
            if category == 'connectivity':
                tester = DatabaseConnectivityTester()
                results = tester.run_all_tests()
            elif category == 'schema':
                tester = DatabaseSchemaTester()
                results = tester.run_all_tests()
            elif category == 'mapping':
                tester = DatabaseMappingTester()
                results = tester.run_all_tests()
            elif category == 'operations':
                tester = DatabaseOperationsTester()
                results = tester.run_all_tests()
            else:
                logging.warning(f"未知的测试类别: {category}")
                return
            
            # 处理结果
            for test_name, result in results.items():
                duration = time.time() - start_time
                test_result = TestResult(
                    name=f"{category}_{test_name}",
                    status=result.get('status', 'UNKNOWN'),
                    duration=duration,
                    details=result,
                    error=result.get('error')
                )
                self.reporter.add_result(test_result)
        
        except Exception as e:
            logging.error(f"测试类别 {category} 执行失败: {e}")
            duration = time.time() - start_time
            test_result = TestResult(
                name=f"{category}_error",
                status='FAILED',
                duration=duration,
                details={},
                error=str(e)
            )
            self.reporter.add_result(test_result)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="TRIAXUS 高级数据库测试执行器")
    parser.add_argument('--config', default='tests/database_test_config.yaml', help='配置文件路径')
    parser.add_argument('--environment', default='development', help='测试环境')
    parser.add_argument('--categories', nargs='+', help='要运行的测试类别')
    parser.add_argument('--verbose', action='store_true', help='详细输出')
    
    args = parser.parse_args()
    
    # 创建测试执行器
    runner = AdvancedDatabaseTestRunner(args.config)
    
    # 运行测试
    runner.run_tests(
        environment=args.environment,
        categories=args.categories
    )


if __name__ == "__main__":
    main()
