#!/usr/bin/env python3
"""
Quick database testing runner
Provides a simple CLI to run various database tests
"""

import os
import sys
import argparse
import logging
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.advanced_database_test_runner import AdvancedDatabaseTestRunner
from tests.utils.test_utilities import setup_test_environment, cleanup_test_environment


def setup_logging(verbose: bool = False):
    """Configure logging"""
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


def check_environment():
    """Check test environment"""
    print("检查测试环境...")
    
    # Check required environment variables
    required_env_vars = ['DB_ENABLED']
    missing_vars = []
    
    for var in required_env_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ 缺少必需的环境变量: {', '.join(missing_vars)}")
        print("请设置以下环境变量:")
        print("export DB_ENABLED=true")
        print("export DATABASE_URL=postgresql://username:password@localhost:5432/triaxus_test")
        return False
    
    # Check database connection
    try:
        from triaxus.database.connection_manager import DatabaseConnectionManager
        conn_manager = DatabaseConnectionManager()
        if conn_manager.connect():
            print("✅ 数据库连接正常")
            return True
        else:
            print("❌ 数据库连接失败")
            return False
    except Exception as e:
        print(f"❌ 数据库连接检查失败: {e}")
        return False


def run_quick_tests():
    """Run quick tests"""
    print("\n" + "="*60)
    print("运行快速数据库测试")
    print("="*60)
    
    from tests.unit.database.test_connectivity import DatabaseConnectivityTester
    
    # Only run connectivity tests
    tester = DatabaseConnectivityTester()
    results = tester.run_all_tests()
    
    # Display results
    passed = sum(1 for result in results.values() if result.get('status') == 'PASSED')
    total = len(results)
    
    print(f"\n快速测试完成: {passed}/{total} 测试通过")
    
    if passed == total:
        print("✅ 所有快速测试通过")
        return True
    else:
        print("❌ 部分测试失败")
        return False


def run_full_tests(config_path: str, environment: str, categories: list):
    """Run full test suite"""
    print("\n" + "="*60)
    print("运行完整数据库测试套件")
    print("="*60)
    
    try:
        runner = AdvancedDatabaseTestRunner(config_path)
        runner.run_tests(environment=environment, categories=categories)
        print("✅ 完整测试执行完成")
        return True
    except Exception as e:
        print(f"❌ 完整测试执行失败: {e}")
        return False


def generate_sample_config():
    """Generate a sample configuration file"""
    config_path = Path("tests/database_test_config.yaml")
    
    if config_path.exists():
        print(f"配置文件已存在: {config_path}")
        return
    
    sample_config = """# TRIAXUS 数据库测试配置文件示例
test_environments:
  development:
    database_url: "postgresql://triaxus_user:password@localhost:5432/triaxus_test"
    pool_size: 5
    max_overflow: 10
    echo: false

test_cases:
  connectivity:
    enabled: true
  schema:
    enabled: true
  mapping:
    enabled: true
  operations:
    enabled: true

performance_benchmarks:
  insertion:
    target_rate: 1000
  query:
    simple_query_time: 2

reporting:
  output_formats:
    - html
    - json
  output_directory: "test_results"

logging:
  level: INFO
  file: "test_logs/database_tests.log"
"""
    
    # Create directory
    config_path.parent.mkdir(exist_ok=True)
    
    # Write configuration file
    with open(config_path, 'w', encoding='utf-8') as f:
        f.write(sample_config)
    
    print(f"✅ 示例配置文件已生成: {config_path}")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="TRIAXUS 数据库测试执行器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 检查环境
  python run_database_tests.py --check-env
  
  # 运行快速测试
  python run_database_tests.py --quick
  
  # 运行完整测试
  python run_database_tests.py --full
  
  # 运行特定类别的测试
  python run_database_tests.py --full --categories connectivity schema
  
  # 生成示例配置文件
  python run_database_tests.py --generate-config
  
  # 清理测试数据
  python run_database_tests.py --cleanup
        """
    )
    
    parser.add_argument('--check-env', action='store_true', help='检查测试环境')
    parser.add_argument('--quick', action='store_true', help='运行快速测试')
    parser.add_argument('--full', action='store_true', help='运行完整测试')
    parser.add_argument('--cleanup', action='store_true', help='清理测试数据')
    parser.add_argument('--generate-config', action='store_true', help='生成示例配置文件')
    
    parser.add_argument('--config', default='tests/database_test_config.yaml', help='配置文件路径')
    parser.add_argument('--environment', default='development', help='测试环境')
    parser.add_argument('--categories', nargs='+', 
                       choices=['connectivity', 'schema', 'mapping', 'operations'],
                       help='要运行的测试类别')
    parser.add_argument('--verbose', action='store_true', help='详细输出')
    
    args = parser.parse_args()
    
    # Configure logging
    setup_logging(args.verbose)
    
    # Show help if no action specified
    if not any([args.check_env, args.quick, args.full, args.cleanup, args.generate_config]):
        parser.print_help()
        return
    
    # Generate configuration file
    if args.generate_config:
        generate_sample_config()
        return
    
    # Set up test environment
    setup_test_environment()
    
    # Check environment
    if args.check_env:
        if check_environment():
            print("✅ 环境检查通过")
        else:
            print("❌ 环境检查失败")
            sys.exit(1)
        return
    
    # Clean up test data
    if args.cleanup:
        print("清理测试数据...")
        if cleanup_test_environment():
            print("✅ 测试数据清理完成")
        else:
            print("❌ 测试数据清理失败")
        return
    
    # Check environment (before running tests)
    if not check_environment():
        print("❌ 环境检查失败，无法运行测试")
        sys.exit(1)
    
    # Run tests
    success = True
    
    if args.quick:
        success = run_quick_tests()
    
    if args.full:
        success = run_full_tests(args.config, args.environment, args.categories)
    
    # Exit status
    if success:
        print("\n🎉 所有测试执行成功!")
        sys.exit(0)
    else:
        print("\n💥 测试执行失败!")
        sys.exit(1)


if __name__ == "__main__":
    main()
