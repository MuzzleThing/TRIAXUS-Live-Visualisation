"""
Real-time data processing service for continuous CNV file monitoring.
"""
import time
import logging
from typing import Optional, Dict, Any, List
from pathlib import Path
from datetime import datetime
from sqlalchemy.orm import Session
from uuid import UUID

from ..config.settings import settings
from ..config.database import get_db_context
from ..repositories.file_repository import FileRepository
from ..repositories.realtime_repository import RealtimeRepository
from ..repositories.sensor_data_repository import SensorDataRepository
from ..utils.cnv_parser import CNVParser
from ..utils.hash_utils import HashUtils
from .cast_detection_service import CastDetectionService
from .qc_service import QualityControlService

logger = logging.getLogger(__name__)

class RealtimeService:
    """Service for real-time data processing and monitoring."""
    
    def __init__(self):
        self.file_repository = FileRepository()
        self.realtime_repository = RealtimeRepository()
        self.sensor_data_repository = SensorDataRepository()
        self.cnv_parser = CNVParser()
        self.hash_utils = HashUtils()
        self.cast_detection_service = CastDetectionService()
        self.qc_service = QualityControlService()
        self.file_positions: Dict[UUID, int] = {}  # Track file read positions
        self.is_running = False
    
    def start_monitoring(self, file_path: str, cruise_id: UUID) -> UUID:
        """Start monitoring a CNV file for real-time data."""
        with get_db_context() as db:
            # Register or get existing file
            file_record = self._register_file(db, file_path, cruise_id)
            
            # Initialize file position tracking
            self.file_positions[file_record.file_id] = 0
            
            logger.info(f"Started monitoring file: {file_path}")
            return file_record.file_id
    
    def process_file_updates(self, file_id: UUID) -> int:
        """Process new data from a monitored file."""
        with get_db_context() as db:
            file_record = self.file_repository.get_by_id(db, file_id)
            if not file_record:
                raise ValueError(f"File not found: {file_id}")
            
            file_path = Path(file_record.file_path)
            if not file_path.exists():
                logger.warning(f"File does not exist: {file_path}")
                return 0
            
            # Read new lines from file
            new_lines = self._read_new_lines(file_path, file_id)
            if not new_lines:
                return 0
            
            # Process new lines
            processed_count = 0
            for line_number, line_content in new_lines:
                try:
                    # Store in realtime buffer
                    buffer_record = self.realtime_repository.create_buffer_entry(
                        db, file_id, line_content, line_number
                    )
                    
                    # Try to parse and process the line
                    parsed_data = self.cnv_parser.parse_data_line(line_content)
                    if parsed_data:
                        # Update buffer with parsed data
                        self.realtime_repository.update_buffer_parsed_data(
                            db, buffer_record.buffer_id, parsed_data
                        )
                        
                        # Create sensor data record
                        sensor_record = self._create_sensor_data_record(
                            db, file_id, parsed_data
                        )
                        
                        # Perform QC checks
                        qc_results = self.qc_service.perform_realtime_qc(
                            db, sensor_record
                        )
                        
                        # Check for cast transitions
                        self.cast_detection_service.check_cast_transition(
                            db, file_id, sensor_record
                        )
                        
                        processed_count += 1
                    
                    # Mark buffer as processed
                    self.realtime_repository.mark_buffer_processed(
                        db, buffer_record.buffer_id
                    )
                    
                except Exception as e:
                    logger.error(f"Error processing line {line_number}: {str(e)}")
                    # Mark buffer as failed
                    self.realtime_repository.mark_buffer_failed(
                        db, buffer_record.buffer_id
                    )
            
            logger.info(f"Processed {processed_count} new data points from {file_path}")
            return processed_count
    
    def run_monitoring_loop(self, file_ids: List[UUID]):
        """Run continuous monitoring loop for multiple files."""
        self.is_running = True
        logger.info(f"Starting monitoring loop for {len(file_ids)} files")
        
        while self.is_running:
            try:
                total_processed = 0
                for file_id in file_ids:
                    processed = self.process_file_updates(file_id)
                    total_processed += processed
                
                if total_processed > 0:
                    logger.info(f"Processing cycle completed: {total_processed} records")
                
                # Sleep based on configured interval
                time.sleep(settings.FILE_WATCH_INTERVAL)
                
            except KeyboardInterrupt:
                logger.info("Monitoring interrupted by user")
                self.stop_monitoring()
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {str(e)}")
                time.sleep(5)  # Wait before retrying
    
    def stop_monitoring(self):
        """Stop the monitoring loop."""
        self.is_running = False
        logger.info("Monitoring stopped")
    
    def get_realtime_status(self, file_id: UUID) -> Dict[str, Any]:
        """Get real-time processing status for a file."""
        with get_db_context() as db:
            # Get buffer statistics
            buffer_stats = self.realtime_repository.get_buffer_stats(db, file_id)
            
            # Get recent data count
            recent_data_count = len(
                self.sensor_data_repository.get_recent_data(db, 5, file_id=file_id)
            )
            
            # Get file position
            current_position = self.file_positions.get(file_id, 0)
            
            return {
                'file_id': str(file_id),
                'is_monitoring': self.is_running,
                'current_position': current_position,
                'buffer_stats': buffer_stats,
                'recent_data_count': recent_data_count,
                'last_update': datetime.utcnow().isoformat()
            }
    
    def _register_file(self, db: Session, file_path: str, cruise_id: UUID):
        """Register a file for monitoring."""
        path_obj = Path(file_path)
        file_hash = self.hash_utils.calculate_file_hash(file_path)
        
        # Check if file already exists
        existing_file = self.file_repository.find_one_by(
            db, 
            file_name=path_obj.name,
            file_hash=file_hash
        )
        
        if existing_file:
            return existing_file
        
        # Create new file record
        return self.file_repository.create(
            db,
            cruise_id=cruise_id,
            file_name=path_obj.name,
            file_path=str(path_obj.absolute()),
            file_type='CNV',
            file_size=path_obj.stat().st_size,
            file_hash=file_hash,
            processing_status='monitoring'
        )
    
    def _read_new_lines(self, file_path: Path, file_id: UUID) -> List[tuple]:
        """Read new lines from file since last position."""
        current_position = self.file_positions.get(file_id, 0)
        new_lines = []
        
        try:
            with open(file_path, 'r', encoding=settings.CNV_ENCODING) as f:
                f.seek(current_position)
                line_number = current_position
                
                for line in f:
                    line_number += 1
                    if line.strip():  # Skip empty lines
                        new_lines.append((line_number, line.strip()))
                
                # Update position
                self.file_positions[file_id] = f.tell()
                
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {str(e)}")
        
        return new_lines
    
    def _create_sensor_data_record(
        self, 
        db: Session, 
        file_id: UUID, 
        parsed_data: Dict[str, Any]
    ):
        """Create a sensor data record from parsed data."""
        # Convert parsed data to sensor data format
        sensor_data = {
            'file_id': file_id,
            'scan_number': parsed_data.get('scan_number'),
            'timestamp': parsed_data.get('timestamp') or datetime.utcnow(),
            'pressure': parsed_data.get('pressure'),
            'temperature': parsed_data.get('temperature'),
            'conductivity': parsed_data.get('conductivity'),
            'salinity': parsed_data.get('salinity'),
            'depth': parsed_data.get('depth'),
            'oxygen': parsed_data.get('oxygen'),
            'fluorescence': parsed_data.get('fluorescence'),
            'turbidity': parsed_data.get('turbidity'),
            'par': parsed_data.get('par'),
            'latitude': parsed_data.get('latitude'),
            'longitude': parsed_data.get('longitude'),
            'additional_channels': parsed_data.get('additional_channels')
        }
        
        return self.sensor_data_repository.create(db, **sensor_data)