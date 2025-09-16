"""
Database operations tests for TRIAXUS

This module tests CRUD operations, data validation, and repository functionality.
"""

import os
import sys
import time
from typing import Dict, Any, List
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from triaxus.database.connection_manager import DatabaseConnectionManager
from triaxus.database.models import OceanographicData, DataSource
from triaxus.database.mappers import DataMapper
from triaxus.database.repositories import OceanographicDataRepository
from triaxus.data.simple_data_generator import PlotTestDataGenerator


class DatabaseOperationsTester:
    """Test database operations and CRUD functionality"""
    
    def __init__(self):
        """Initialize operations tester"""
        self.connection_manager = DatabaseConnectionManager()
        self.data_mapper = DataMapper()
        self.repository = OceanographicDataRepository()
        self.data_generator = PlotTestDataGenerator()
    
    def _ensure_connection(self):
        """Ensure database connection is established"""
        if not self.connection_manager.is_connected():
            self.connection_manager.connect()
    
    def test_data_insertion(self) -> Dict[str, Any]:
        """Test data insertion operations"""
        print("Testing data insertion...")
        
        self._ensure_connection()
        
        # Generate test data
        test_data = self.data_generator.generate_plot_test_data()
        models = self.data_mapper.dataframe_to_models(test_data, "test_insert.csv")
        
        print(f"Generated {len(models)} test records")
        
        with self.connection_manager.get_session() as session:
            # Insert data
            session.add_all(models)
            session.commit()
            
            # Verify insertion
            inserted_count = session.query(OceanographicData).count()
            print(f"Inserted {len(models)} records, total in DB: {inserted_count}")
            
            success = inserted_count >= len(models)
            
            return {
                "status": "PASSED" if success else "FAILED",
                "inserted": len(models),
                "total_in_db": inserted_count,
                "insertion_success": success
            }
    
    def test_data_retrieval(self) -> Dict[str, Any]:
        """Test data retrieval operations"""
        print("Testing data retrieval...")
        
        self._ensure_connection()
        
        with self.connection_manager.get_session() as session:
            # Test basic retrieval
            total_records = session.query(OceanographicData).count()
            print(f"Total records: {total_records}")
            
            # Test filtered retrieval
            recent_records = session.query(OceanographicData).filter(
                OceanographicData.datetime >= datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            ).count()
            print(f"Recent records: {recent_records}")
            
            # Test specific field retrieval
            temp_records = session.query(OceanographicData).filter(
                OceanographicData.tv290c.isnot(None)
            ).count()
            print(f"Records with temperature: {temp_records}")
            
            success = total_records > 0
            
            return {
                "status": "PASSED" if success else "FAILED",
                "total_records": total_records,
                "recent_records": recent_records,
                "temp_records": temp_records,
                "retrieval_success": success
            }
    
    def test_data_update(self) -> Dict[str, Any]:
        """Test data update operations"""
        print("Testing data update...")
        
        self._ensure_connection()
        
        with self.connection_manager.get_session() as session:
            # Find a record to update
            record = session.query(OceanographicData).filter(
                OceanographicData.tv290c.isnot(None)
            ).first()
            
            if not record:
                print("No records available for update test")
                return {
                    "status": "FAILED",
                    "error": "No records available for update"
                }
            
            # Store original value
            original_temp = record.tv290c
            new_temp = original_temp + 1.0
            
            # Update record
            record.tv290c = new_temp
            session.commit()
            
            # Verify update
            updated_record = session.query(OceanographicData).filter_by(id=record.id).first()
            update_success = updated_record.tv290c == new_temp
            
            # Restore original value
            updated_record.tv290c = original_temp
            session.commit()
            
            print(f"Update test: {update_success}")
            
            return {
                "status": "PASSED" if update_success else "FAILED",
                "update_success": update_success,
                "original_value": original_temp,
                "new_value": new_temp
            }
    
    def test_data_deletion(self) -> Dict[str, Any]:
        """Test data deletion operations"""
        print("Testing data deletion...")
        
        self._ensure_connection()
        
        with self.connection_manager.get_session() as session:
            # Find records to delete
            records_to_delete = session.query(OceanographicData).filter(
                OceanographicData.tv290c.isnot(None)
            ).limit(3).all()
            
            if not records_to_delete:
                print("No records available for deletion test")
                return {
                    "status": "FAILED",
                    "error": "No records available for deletion"
                }
            
            delete_count = len(records_to_delete)
            record_ids = [record.id for record in records_to_delete]
            
            # Delete records
            for record in records_to_delete:
                session.delete(record)
            session.commit()
            
            # Verify deletion
            remaining_count = session.query(OceanographicData).filter(
                OceanographicData.id.in_(record_ids)
            ).count()
            
            deletion_success = remaining_count == 0
            print(f"Deleted {delete_count} records, remaining: {remaining_count}")
            
            return {
                "status": "PASSED" if deletion_success else "FAILED",
                "deleted_count": delete_count,
                "remaining_count": remaining_count,
                "deletion_success": deletion_success
            }
    
    def test_repository_operations(self) -> Dict[str, Any]:
        """Test repository pattern operations"""
        print("Testing repository operations...")
        
        self._ensure_connection()
        
        try:
            # Test get_latest_records
            latest_records = self.repository.get_latest_records(limit=10)
            print(f"Latest records: {len(latest_records)}")
            
            # Test get_by_depth_range
            depth_records = self.repository.get_by_depth_range(0, 50)
            print(f"Records in depth range 0-50m: {len(depth_records)}")
            
            # Test get_by_time_range
            end_time = datetime.now()
            start_time = datetime(end_time.year, end_time.month, end_time.day)
            time_records = self.repository.get_by_time_range(start_time, end_time)
            print(f"Records in time range: {len(time_records)}")
            
            success = True  # If we get here without exception, it's successful
            
            return {
                "status": "PASSED",
                "latest_records": len(latest_records),
                "depth_records": len(depth_records),
                "time_records": len(time_records),
                "repository_success": success
            }
        except Exception as e:
            print(f"Repository operations failed: {e}")
            return {
                "status": "FAILED",
                "error": str(e)
            }
    
    def test_performance(self) -> Dict[str, Any]:
        """Test database performance"""
        print("Testing database performance...")
        
        self._ensure_connection()
        
        # Test bulk insert performance
        start_time = time.time()
        test_data = self.data_generator.generate_plot_test_data()
        models = self.data_mapper.dataframe_to_models(test_data, "performance_test.csv")
        
        with self.connection_manager.get_session() as session:
            session.add_all(models)
            session.commit()
        
        insert_time = time.time() - start_time
        print(f"Bulk insert {len(models)} records: {insert_time:.3f}s")
        
        # Test query performance
        start_time = time.time()
        with self.connection_manager.get_session() as session:
            records = session.query(OceanographicData).limit(1000).all()
        query_time = time.time() - start_time
        print(f"Query {len(records)} records: {query_time:.3f}s")
        
        # Test update performance
        start_time = time.time()
        with self.connection_manager.get_session() as session:
            records_to_update = session.query(OceanographicData).limit(50).all()
            for record in records_to_update:
                if record.tv290c is not None:
                    record.tv290c += 0.1
            session.commit()
        update_time = time.time() - start_time
        print(f"Update {len(records_to_update)} records: {update_time:.3f}s")
        
        # Calculate rates
        insert_rate = len(models) / insert_time if insert_time > 0 else 0
        query_rate = len(records) / query_time if query_time > 0 else 0
        
        return {
            "status": "PASSED",
            "insert_time": insert_time,
            "query_time": query_time,
            "update_time": update_time,
            "insert_rate": insert_rate,
            "query_rate": query_rate,
            "records_inserted": len(models),
            "records_queried": len(records),
            "records_updated": len(records_to_update)
        }
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all operations tests"""
        print("=" * 50)
        print("DATABASE OPERATIONS TESTS")
        print("=" * 50)
        
        test_results = {}
        
        # Run individual tests
        tests = [
            ("Data Insertion", self.test_data_insertion),
            ("Data Retrieval", self.test_data_retrieval),
            ("Data Update", self.test_data_update),
            ("Data Deletion", self.test_data_deletion),
            ("Repository Operations", self.test_repository_operations),
            ("Performance", self.test_performance)
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
        print(f"\nOperations Tests Summary: {passed}/{total} passed")
        
        return test_results


if __name__ == "__main__":
    tester = DatabaseOperationsTester()
    results = tester.run_all_tests()
