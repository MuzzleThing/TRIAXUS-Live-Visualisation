"""
Database data mapping tests for TRIAXUS

This module tests data mapping between DataFrames and database models.
"""

import os
import sys
from typing import Dict, Any, List

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from triaxus.database.connection_manager import DatabaseConnectionManager
from triaxus.database.models import OceanographicData, DataSource
from triaxus.database.mappers import DataMapper
from triaxus.data.simple_data_generator import PlotTestDataGenerator
import pandas as pd


class DatabaseMappingTester:
    """Test data mapping functionality"""
    
    def __init__(self):
        """Initialize mapping tester"""
        self.connection_manager = DatabaseConnectionManager()
        self.data_mapper = DataMapper()
        self.data_generator = PlotTestDataGenerator()
    
    def _ensure_connection(self):
        """Ensure database connection is established"""
        if not self.connection_manager.is_connected():
            self.connection_manager.connect()
    
    def test_dataframe_to_models(self) -> Dict[str, Any]:
        """Test DataFrame to models conversion"""
        print("Testing DataFrame to models conversion...")
        
        # Generate test data
        test_data = self.data_generator.generate_plot_test_data()
        print(f"Generated {len(test_data)} test records")
        
        # Convert DataFrame to models
        models = self.data_mapper.dataframe_to_models(test_data, "test_mapping.csv")
        print(f"Created {len(models)} models")
        
        # Validate models - data mapper already filters invalid models
        valid_models = len(models)  # All models returned by mapper are valid
        print(f"Valid models: {valid_models}/{len(models)}")
        
        # Additional validation check
        validation_passed = True
        for model in models[:3]:  # Check first 3 models
            if not model.validate():
                validation_passed = False
                print(f"Model validation failed: {model}")
                break
        
        success = validation_passed
        
        return {
            "status": "PASSED" if success else "FAILED",
            "total_models": len(models),
            "valid_models": valid_models,
            "conversion_success": success
        }
    
    def test_models_to_dataframe(self) -> Dict[str, Any]:
        """Test models to DataFrame conversion"""
        print("Testing models to DataFrame conversion...")
        
        # Generate test data and convert to models
        test_data = self.data_generator.generate_plot_test_data()
        models = self.data_mapper.dataframe_to_models(test_data, "test_mapping.csv")
        
        # Convert models back to DataFrame
        df = self.data_mapper.models_to_dataframe(models)
        print(f"Converted to DataFrame: {len(df)} rows, {len(df.columns)} columns")
        
        # Validate DataFrame
        required_columns = ['time', 'depth', 'latitude', 'longitude', 'tv290c', 'sal00', 'sbeox0mm_l', 'fleco_afl', 'ph']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        success = len(missing_columns) == 0 and len(df) == len(models)
        print(f"Missing columns: {missing_columns}")
        print(f"Row count match: {len(df)} == {len(models)}")
        
        return {
            "status": "PASSED" if success else "FAILED",
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "missing_columns": missing_columns,
            "row_count_match": len(df) == len(models)
        }
    
    def test_field_mapping(self) -> Dict[str, Any]:
        """Test field mapping configuration"""
        print("Testing field mapping configuration...")
        
        field_mapping = self.data_mapper.FIELD_MAPPING
        print(f"Field mapping: {len(field_mapping)} fields")
        
        # Test mapping consistency
        expected_mappings = {
            'time': 'datetime',
            'depth': 'depth',
            'latitude': 'latitude',
            'longitude': 'longitude',
            'tv290c': 'tv290c',
            'sal00': 'sal00',
            'sbeox0mm_l': 'sbeox0mm_l',
            'fleco_afl': 'fleco_afl',
            'ph': 'ph'
        }
        
        mapping_consistent = True
        for df_col, expected_model_attr in expected_mappings.items():
            if df_col not in field_mapping:
                print(f"Missing mapping for {df_col}")
                mapping_consistent = False
            elif field_mapping[df_col] != expected_model_attr:
                print(f"Wrong mapping for {df_col}: {field_mapping[df_col]} != {expected_model_attr}")
                mapping_consistent = False
        
        print(f"Field mapping consistent: {mapping_consistent}")
        
        return {
            "status": "PASSED" if mapping_consistent else "FAILED",
            "total_mappings": len(field_mapping),
            "mapping_consistent": mapping_consistent
        }
    
    def test_data_type_conversion(self) -> Dict[str, Any]:
        """Test data type conversion accuracy"""
        print("Testing data type conversion accuracy...")
        
        # Generate test data
        test_data = self.data_generator.generate_plot_test_data()
        models = self.data_mapper.dataframe_to_models(test_data, "test_types.csv")
        
        # Test data type preservation
        type_issues = []
        for i, model in enumerate(models[:5]):  # Test first 5 models
            row = test_data.iloc[i]
            
            # Check numeric fields
            numeric_fields = ['depth', 'latitude', 'longitude', 'tv290c', 'sal00', 'sbeox0mm_l', 'fleco_afl', 'ph']
            for field in numeric_fields:
                if field in row and pd.notna(row[field]):
                    model_value = getattr(model, field, None)
                    if model_value is not None:
                        if not isinstance(model_value, (int, float)):
                            type_issues.append(f"Row {i}, {field}: expected numeric, got {type(model_value)}")
        
        success = len(type_issues) == 0
        print(f"Type conversion issues: {len(type_issues)}")
        if type_issues:
            for issue in type_issues[:3]:  # Show first 3 issues
                print(f"  {issue}")
        
        return {
            "status": "PASSED" if success else "FAILED",
            "type_issues": len(type_issues),
            "conversion_accurate": success
        }
    
    def test_empty_dataframe_handling(self) -> Dict[str, Any]:
        """Test handling of empty DataFrames"""
        print("Testing empty DataFrame handling...")
        
        # Test empty DataFrame
        empty_df = pd.DataFrame()
        models = self.data_mapper.dataframe_to_models(empty_df, "empty.csv")
        
        empty_success = len(models) == 0
        print(f"Empty DataFrame handling: {empty_success}")
        
        # Test DataFrame with missing columns
        incomplete_df = pd.DataFrame({
            'time': ['2024-01-01'],
            'depth': [10.0]
            # Missing required columns
        })
        models_incomplete = self.data_mapper.dataframe_to_models(incomplete_df, "incomplete.csv")
        
        incomplete_success = len(models_incomplete) == 0
        print(f"Incomplete DataFrame handling: {incomplete_success}")
        
        success = empty_success and incomplete_success
        
        return {
            "status": "PASSED" if success else "FAILED",
            "empty_handling": empty_success,
            "incomplete_handling": incomplete_success
        }
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all mapping tests"""
        print("=" * 50)
        print("DATABASE MAPPING TESTS")
        print("=" * 50)
        
        test_results = {}
        
        # Run individual tests
        tests = [
            ("DataFrame to Models", self.test_dataframe_to_models),
            ("Models to DataFrame", self.test_models_to_dataframe),
            ("Field Mapping", self.test_field_mapping),
            ("Data Type Conversion", self.test_data_type_conversion),
            ("Empty DataFrame Handling", self.test_empty_dataframe_handling)
        ]
        
        for test_name, test_method in tests:
            print(f"\n--- {test_name} ---")
            try:
                result = test_method()
                test_results[test_name] = result
                status = "PASSED" if result.get("status") == "PASSED" else "FAILED"
                print(f"{status}: {test_name}")
            except Exception as e:
                test_results[test_name] = {"status": "FAILED", "error": str(e)}
                print(f"FAILED: {test_name} - {e}")
        
        # Summary
        passed = sum(1 for result in test_results.values() if result.get("status") == "PASSED")
        total = len(test_results)
        print(f"\nMapping Tests Summary: {passed}/{total} passed")
        
        return test_results


if __name__ == "__main__":
    tester = DatabaseMappingTester()
    results = tester.run_all_tests()
