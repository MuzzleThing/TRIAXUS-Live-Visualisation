#!/usr/bin/env python3
"""
CNV Batch Processor

This module provides functionality to process CNV files in batch mode.
It handles reading, processing, and archiving CNV files from a specified directory.
"""

import sys
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

from .cnv_reader import CNVFileReader
from .archiver import DataArchiver
from .processor import DataProcessor
from ..core.config import ConfigManager


class CNVBatchProcessor:
    """
    Batch CNV file processor for processing multiple files at once
    """
    
    def __init__(self, config_manager: Optional[ConfigManager] = None, custom_config_path: Optional[str] = None):
        """
        Initialize CNV batch processor
        
        Args:
            config_manager: Configuration manager instance
            custom_config_path: Path to custom configuration file
        """
        if config_manager is None:
            if custom_config_path:
                self.config_manager = ConfigManager(custom_config_path=custom_config_path)
            else:
                self.config_manager = ConfigManager()
        else:
            self.config_manager = config_manager
            
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.cnv_reader = CNVFileReader()
        self.data_processor = DataProcessor(self.config_manager)
        self.data_archiver = DataArchiver(self.config_manager, self.data_processor)
        
        # Get CNV processing configuration
        self.cnv_config = self.config_manager.settings.get("cnv_processing", {})
    
    def get_source_directory(self) -> Path:
        """
        Get the configured source directory for CNV files
        
        Returns:
            Path to the source directory
        """
        source_dir = self.cnv_config.get("source_directory", "testdataQC")
        return Path(source_dir)
    
    def process_directory(self, directory_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Process all CNV files in the specified directory
        
        Args:
            directory_path: Path to directory containing CNV files
            
        Returns:
            Dictionary with processing results
        """
        if directory_path is None:
            directory_path = str(self.get_source_directory())
        
        self.logger.info(f"Processing CNV files from directory: {directory_path}")
        
        results = {
            'start_time': datetime.now(),
            'processed_files': [],
            'failed_files': [],
            'total_records': 0,
            'database_stored': 0,
            'processing_time': None
        }
        
        try:
            # Read all CNV files
            cnv_data = self.cnv_reader.read_directory(directory_path)
            
            if not cnv_data:
                self.logger.warning(f"No CNV files found in {directory_path}")
                return results
            
            # Process each file
            for filename, (df, metadata) in cnv_data.items():
                try:
                    file_result = self.process_single_file(df, metadata, filename)
                    results['processed_files'].append(file_result)
                    results['total_records'] += file_result['records']
                    if file_result['database_stored']:
                        results['database_stored'] += file_result['records']
                        
                except Exception as e:
                    self.logger.error(f"Failed to process {filename}: {e}")
                    results['failed_files'].append({
                        'filename': filename,
                        'error': str(e)
                    })
            
            # Calculate processing time
            results['processing_time'] = datetime.now() - results['start_time']
            
            self.logger.info(f"Processing complete: {len(results['processed_files'])} files processed, "
                            f"{len(results['failed_files'])} failed")
            
        except Exception as e:
            self.logger.error(f"Error processing directory {directory_path}: {e}")
            raise
        
        return results
    
    def process_single_file(self, df, metadata: Dict[str, Any], filename: str) -> Dict[str, Any]:
        """
        Process a single CNV file through the complete pipeline
        
        Args:
            df: DataFrame with CNV data
            metadata: File metadata
            filename: Source filename
            
        Returns:
            Dictionary with processing results for this file
        """
        self.logger.info(f"Processing {filename}...")
        
        # Archive data (includes processing and database storage)
        archive_result = self.data_archiver.archive(
            data=df,
            source_name=filename,
            metadata={
                'filename': filename,
                'file_type': 'CNV',
                'total_records': len(df),
                'cruise': metadata.get('metadata', {}).get('Cruise', 'unknown'),
                'ship': metadata.get('metadata', {}).get('Ship', 'unknown'),
                'station': metadata.get('metadata', {}).get('Station', 'unknown'),
                'operator': metadata.get('metadata', {}).get('Operator', 'unknown'),
                'start_time': metadata.get('start_time'),
                'variables': len(metadata.get('variables', []))
            }
        )
        
        result = {
            'filename': filename,
            'records': archive_result['row_count'],
            'database_stored': archive_result['database_stored'],
            'archive_files': archive_result['archive'],
            'quality_report': archive_result.get('quality_report')
        }
        
        self.logger.info(f"Successfully processed {filename}: {archive_result['row_count']} records")
        return result
    
    def test_reader(self, directory_path: Optional[str] = None) -> bool:
        """
        Test CNV reader functionality
        
        Args:
            directory_path: Path to directory containing CNV files
            
        Returns:
            True if test successful, False otherwise
        """
        if directory_path is None:
            directory_path = str(self.get_source_directory())
        
        self.logger.info(f"Testing CNV reader with directory: {directory_path}")
        
        try:
            # Test reading a single CNV file
            cnv_files = list(Path(directory_path).glob("*.cnv"))
            
            if not cnv_files:
                self.logger.warning(f"No CNV files found in {directory_path} for testing")
                return False
            
            # Test with first CNV file
            test_file = cnv_files[0]
            self.logger.info(f"Testing CNV reader with {test_file.name}")
            
            df, metadata = self.cnv_reader.read_cnv_file(str(test_file))
            
            self.logger.info(f"Successfully read {test_file.name}")
            self.logger.info(f"Data shape: {df.shape}")
            self.logger.info(f"Columns: {list(df.columns)}")
            self.logger.info(f"Data types: {df.dtypes.to_dict()}")
            
            if len(df) > 0:
                self.logger.info(f"First few rows:")
                self.logger.info(f"{df.head()}")
            
            self.logger.info(f"Metadata keys: {list(metadata.keys())}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error testing CNV reader: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return False


def setup_logging():
    """Setup logging configuration"""
    # Ensure logs directory exists
    logs_dir = Path('logs')
    logs_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(logs_dir / 'cnv_batch_processing.log')
        ]
    )


def show_help():
    """Show help information"""
    print("""
CNV Batch Processor

Usage:
    python -m triaxus.data.cnv_batch_processor [options]

Options:
    --help, -h          Show this help message
    --config, -c        Show current configuration
    --test, -t          Test CNV reader functionality
    <no args>           Process all CNV files in configured directory

Configuration:
    The source directory is configured in configs/default.yaml under:
    cnv_processing.source_directory

Examples:
    python -m triaxus.data.cnv_batch_processor
    python -m triaxus.data.cnv_batch_processor --test
    python -m triaxus.data.cnv_batch_processor --config
    """)


def show_config():
    """Show current configuration"""
    try:
        processor = CNVBatchProcessor()
        source_dir = processor.get_source_directory()
        
        print(f"\nCNV Batch Processing Configuration:")
        print(f"Source directory: {source_dir}")
        print(f"Directory exists: {source_dir.exists()}")
        
        if source_dir.exists():
            cnv_files = list(source_dir.glob("*.cnv"))
            print(f"\nCNV files found: {len(cnv_files)}")
            for cnv_file in cnv_files:
                print(f"  {cnv_file.name}")
        else:
            print(f"\nDirectory does not exist. Please check your configuration.")
            print("Configuration file: configs/default.yaml")
            print("Section: cnv_processing.source_directory")
        
    except Exception as e:
        print(f"Error reading configuration: {e}")


def main():
    """Main batch processing function"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Initialize processor
    processor = CNVBatchProcessor()
    source_path = str(processor.get_source_directory())
    
    # Find CNV files
    cnv_files = list(Path(source_path).glob("*.cnv"))
    logger.info(f"Found {len(cnv_files)} CNV files to process")
    
    if not cnv_files:
        logger.warning(f"No CNV files found in {source_path} directory")
        return 0
    
    try:
        # Process all CNV files
        logger.info(f"Starting processing of CNV files from {source_path}...")
        results = processor.process_directory()
        
        # Print results
        logger.info("=" * 60)
        logger.info("PROCESSING RESULTS")
        logger.info("=" * 60)
        logger.info(f"Files processed successfully: {len(results['processed_files'])}")
        logger.info(f"Files failed: {len(results['failed_files'])}")
        logger.info(f"Total records processed: {results['total_records']:,}")
        logger.info(f"Records stored in database: {results['database_stored']:,}")
        
        if results['processing_time']:
            logger.info(f"Processing time: {results['processing_time']}")
        
        if results['processed_files']:
            logger.info("\nSuccessfully processed files:")
            for file_result in results['processed_files']:
                logger.info(f"  {file_result['filename']}: {file_result['records']:,} records")
                if file_result['database_stored']:
                    logger.info(f"    Stored in database")
                else:
                    logger.info(f"    Database storage failed")
        
        if results['failed_files']:
            logger.info("\nFailed files:")
            for file_result in results['failed_files']:
                logger.error(f"  {file_result['filename']}: {file_result['error']}")
        
        logger.info("=" * 60)
        logger.info("Processing complete!")
        
        return 0
        
    except Exception as e:
        logger.error(f"Error during processing: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return 1


def get_cnv_source_directory():
    """Get the configured CNV source directory"""
    processor = CNVBatchProcessor()
    return str(processor.get_source_directory())


def test_cnv_reader():
    """Test CNV reader functionality"""
    setup_logging()
    processor = CNVBatchProcessor()
    return processor.test_reader()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "--help" or command == "-h":
            show_help()
        elif command == "--config" or command == "-c":
            show_config()
        elif command == "--test" or command == "-t":
            success = test_cnv_reader()
            sys.exit(0 if success else 1)
        else:
            print(f"Unknown command: {command}")
            print("Use --help for usage information")
            sys.exit(1)
    else:
        # Default: process CNV files
        exit_code = main()
        sys.exit(exit_code)
