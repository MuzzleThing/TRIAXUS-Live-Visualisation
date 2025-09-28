#!/usr/bin/env python3
"""
TRIAXUS Test Suite - Modern Test Runner

This module provides a modern, pytest-based test runner for the TRIAXUS system.
It organizes tests into logical categories and provides flexible execution options.

Test Categories:
- unit: Individual component tests (core, data, database, plotters, utils)
- integration: Cross-component tests (workflows, visualization, database)
- e2e: End-to-end system tests (full_system, performance)

Usage:
    python -m pytest tests/                    # Run all tests
    python -m pytest tests/unit/               # Run unit tests only
    python -m pytest tests/integration/        # Run integration tests only
    python -m pytest tests/e2e/               # Run end-to-end tests only
    python -m pytest tests/ -v                # Verbose output
    python -m pytest tests/ -k "database"    # Run tests matching "database"
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
from typing import List, Optional

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class ModernTestRunner:
    """Modern pytest-based test runner for TRIAXUS system"""
    
    def __init__(self):
        self.project_root = project_root
        self.tests_dir = self.project_root / "tests"
        
    def setup_environment(self):
        """Setup test environment"""
        print("Setting up test environment...")
        
        # Set test environment variables
        os.environ['TESTING'] = 'true'
        os.environ['DB_ENABLED'] = 'true'
        os.environ['DATABASE_URL'] = 'postgresql://steven@localhost:5432/triaxus_test_db'
        
        # Ensure output directory exists
        output_dir = self.tests_dir / "output"
        output_dir.mkdir(exist_ok=True)
        
        print("Environment setup complete")
    
    def run_tests(self, 
                  category: Optional[str] = None,
                  verbose: bool = False,
                  parallel: bool = False,
                  coverage: bool = False,
                  pattern: Optional[str] = None) -> int:
        """Run tests with specified options"""
        
        self.setup_environment()
        
        # Build pytest command
        cmd = ["python", "-m", "pytest"]
        
        # Add test directory or specific category
        if category:
            test_path = self.tests_dir / category
            if not test_path.exists():
                print(f"Test category '{category}' not found")
                return 1
            cmd.append(str(test_path))
        else:
            cmd.append(str(self.tests_dir))
        
        # Add options
        if verbose:
            cmd.append("-v")
        
        if parallel:
            cmd.extend(["-n", "auto"])  # Requires pytest-xdist
        
        if coverage:
            cmd.extend(["--cov=triaxus", "--cov-report=html", "--cov-report=term"])
        
        if pattern:
            cmd.extend(["-k", pattern])
        
        # Add configuration
        cmd.extend([
            "--tb=short",
            "--strict-markers",
            "--disable-warnings"
        ])
        
        print(f"Running tests: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(cmd, cwd=self.project_root)
            return result.returncode
        except KeyboardInterrupt:
            print("\nTests interrupted by user")
            return 1
        except Exception as e:
            print(f"Error running tests: {e}")
            return 1
    
    def run_unit_tests(self, verbose: bool = False) -> int:
        """Run unit tests only"""
        print("Running unit tests...")
        return self.run_tests(category="unit", verbose=verbose)
    
    def run_integration_tests(self, verbose: bool = False) -> int:
        """Run integration tests only"""
        print("Running integration tests...")
        return self.run_tests(category="integration", verbose=verbose)
    
    def run_e2e_tests(self, verbose: bool = False) -> int:
        """Run end-to-end tests only"""
        print("Running end-to-end tests...")
        return self.run_tests(category="e2e", verbose=verbose)
    
    def run_performance_tests(self, verbose: bool = False) -> int:
        """Run performance tests only"""
        print("Running performance tests...")
        return self.run_tests(category="e2e/performance", verbose=verbose)
    
    def run_database_tests(self, verbose: bool = False) -> int:
        """Run database-related tests only"""
        print("Running database tests...")
        return self.run_tests(pattern="database", verbose=verbose)
    
    def run_visualization_tests(self, verbose: bool = False) -> int:
        """Run visualization-related tests only"""
        print("Running visualization tests...")
        return self.run_tests(pattern="plot", verbose=verbose)
    
    def show_test_structure(self):
        """Show the test directory structure"""
        print("Test Directory Structure:")
        print("=" * 50)
        
        def print_tree(path: Path, prefix: str = "", max_depth: int = 3, current_depth: int = 0):
            if current_depth >= max_depth:
                return
            
            items = sorted(path.iterdir())
            for i, item in enumerate(items):
                if item.name.startswith('.') or item.name == '__pycache__':
                    continue
                
                is_last = i == len(items) - 1
                current_prefix = "└── " if is_last else "├── "
                print(f"{prefix}{current_prefix}{item.name}")
                
                if item.is_dir() and current_depth < max_depth - 1:
                    next_prefix = prefix + ("    " if is_last else "│   ")
                    print_tree(item, next_prefix, max_depth, current_depth + 1)
        
        print_tree(self.tests_dir)
        print("=" * 50)

def main():
    """Main entry point for the test runner"""
    parser = argparse.ArgumentParser(description="TRIAXUS Test Runner")
    parser.add_argument("--category", choices=["unit", "integration", "e2e"], 
                       help="Run tests for specific category")
    parser.add_argument("--type", choices=["unit", "integration", "e2e", "performance", "database", "visualization"],
                       help="Run specific type of tests")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("-p", "--parallel", action="store_true", help="Run tests in parallel")
    parser.add_argument("-c", "--coverage", action="store_true", help="Generate coverage report")
    parser.add_argument("-k", "--pattern", help="Run tests matching pattern")
    parser.add_argument("--structure", action="store_true", help="Show test directory structure")
    
    args = parser.parse_args()
    
    runner = ModernTestRunner()
    
    if args.structure:
        runner.show_test_structure()
        return 0
    
    # Run specific test type
    if args.type:
        if args.type == "unit":
            return runner.run_unit_tests(args.verbose)
        elif args.type == "integration":
            return runner.run_integration_tests(args.verbose)
        elif args.type == "e2e":
            return runner.run_e2e_tests(args.verbose)
        elif args.type == "performance":
            return runner.run_performance_tests(args.verbose)
        elif args.type == "database":
            return runner.run_database_tests(args.verbose)
        elif args.type == "visualization":
            return runner.run_visualization_tests(args.verbose)
    
    # Run tests with specified options
    return runner.run_tests(
        category=args.category,
        verbose=args.verbose,
        parallel=args.parallel,
        coverage=args.coverage,
        pattern=args.pattern
    )

if __name__ == "__main__":
    sys.exit(main())
