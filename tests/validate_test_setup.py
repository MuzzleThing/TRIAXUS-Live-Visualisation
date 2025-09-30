#!/usr/bin/env python3
"""
Validate database test setup
Check that all test files and configurations are correctly created
"""

import os
import sys
from pathlib import Path

def check_file_exists(file_path: str, description: str) -> bool:
    """Check if a file exists"""
    if Path(file_path).exists():
        print(f"✅ {description}: {file_path}")
        return True
    else:
        print(f"❌ {description}: {file_path} (文件不存在)")
        return False

def check_directory_exists(dir_path: str, description: str) -> bool:
    """Check if a directory exists"""
    if Path(dir_path).is_dir():
        print(f"✅ {description}: {dir_path}")
        return True
    else:
        print(f"❌ {description}: {dir_path} (目录不存在)")
        return False

def validate_python_syntax(file_path: str) -> bool:
    """Validate Python file syntax"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            compile(f.read(), file_path, 'exec')
        return True
    except SyntaxError as e:
        print(f"❌ 语法错误 {file_path}: {e}")
        return False
    except Exception as e:
        print(f"❌ 文件读取错误 {file_path}: {e}")
        return False

def main():
    """Main validation function"""
    print("TRIAXUS 数据库测试设置验证")
    print("=" * 50)
    
    all_checks_passed = True
    
    # Check main documentation files
    print("\n📋 检查文档文件:")
    doc_files = [
        ("tests/DATABASE_TESTING_PLAN.md", "数据库测试方案文档"),
        ("tests/README_DATABASE_TESTING.md", "数据库测试使用指南"),
        ("tests/database_test_config.yaml", "数据库测试配置文件")
    ]
    
    for file_path, description in doc_files:
        if not check_file_exists(file_path, description):
            all_checks_passed = False
    
    # Check main Python scripts
    print("\n🐍 检查 Python 脚本:")
    python_files = [
        ("tests/run_database_tests.py", "快速测试执行脚本"),
        ("tests/advanced_database_test_runner.py", "高级测试执行器"),
        ("tests/fixtures/test_data_generator.py", "测试数据生成器"),
        ("tests/utils/test_utilities.py", "测试工具函数")
    ]
    
    for file_path, description in python_files:
        if check_file_exists(file_path, description):
            if not validate_python_syntax(file_path):
                all_checks_passed = False
        else:
            all_checks_passed = False
    
    # Check directory structure
    print("\n📁 检查目录结构:")
    directories = [
        ("tests/fixtures", "测试数据目录"),
        ("tests/utils", "测试工具目录"),
        ("tests/unit/database", "单元测试目录")
    ]
    
    for dir_path, description in directories:
        if not check_directory_exists(dir_path, description):
            all_checks_passed = False
    
    # Check existing test files
    print("\n🧪 检查现有测试文件:")
    existing_test_files = [
        ("tests/test_database.py", "原有数据库测试脚本"),
        ("tests/unit/database/test_connectivity.py", "连接性测试"),
        ("tests/unit/database/test_schema.py", "模式测试"),
        ("tests/unit/database/test_mapping.py", "数据映射测试"),
        ("tests/unit/database/test_operations.py", "操作测试")
    ]
    
    for file_path, description in existing_test_files:
        if not check_file_exists(file_path, description):
            print(f"⚠️  {description}: {file_path} (可能需要检查)")
    
    # Check file permissions
    print("\n🔐 检查文件权限:")
    executable_files = [
        "tests/run_database_tests.py",
        "tests/advanced_database_test_runner.py"
    ]
    
    for file_path in executable_files:
        if Path(file_path).exists():
            if os.access(file_path, os.X_OK):
                print(f"✅ 可执行权限: {file_path}")
            else:
                print(f"⚠️  缺少执行权限: {file_path}")
                print(f"   运行: chmod +x {file_path}")
    
    # Check Python imports
    print("\n📦 检查 Python 导入:")
    try:
        import yaml
        print("✅ PyYAML 已安装")
    except ImportError:
        print("❌ PyYAML 未安装 - 运行: pip install pyyaml")
        all_checks_passed = False
    
    try:
        import psutil
        print("✅ psutil 已安装")
    except ImportError:
        print("❌ psutil 未安装 - 运行: pip install psutil")
        all_checks_passed = False
    
    # Summary
    print("\n" + "=" * 50)
    if all_checks_passed:
        print("🎉 所有检查通过！数据库测试设置完成。")
        print("\n下一步:")
        print("1. 设置环境变量:")
        print("   export DB_ENABLED=true")
        print("   export DATABASE_URL=postgresql://username:password@localhost:5432/triaxus_test")
        print("\n2. 运行测试:")
        print("   python tests/run_database_tests.py --check-env")
        print("   python tests/run_database_tests.py --quick")
        return True
    else:
        print("❌ 部分检查失败，请检查上述错误。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
