#!/usr/bin/env python3
"""
CNV Real-time Processor

This module provides functionality to process CNV files in real-time mode.
It monitors a directory for new CNV files and processes them as they appear.
"""

import sys
import time
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

# Add project root to path for absolute imports
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from triaxus.data.cnv_reader import CNVFileReader
from triaxus.data.archiver import DataArchiver
from triaxus.data.processor import DataProcessor
from triaxus.core.config import ConfigManager
from triaxus.visualizer import TriaxusVisualizer
from triaxus.data.database_source import DatabaseDataSource


class CNVRealtimeProcessor:
    """
    Real-time CNV file processor for monitoring and processing new files
    """
    
    def __init__(self, config_manager: Optional[ConfigManager] = None, custom_config_path: Optional[str] = None):
        """
        Initialize CNV real-time processor
        
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
        # Use YAML config for better control over list merging
        if hasattr(self.config_manager, '_yaml_config') and self.config_manager._yaml_config:
            self.cnv_config = self.config_manager._yaml_config.get("cnv_processing", {})
        else:
            self.cnv_config = self.config_manager.settings.get("cnv_processing", {})
    
    def get_source_directory(self) -> Path:
        """
        Get the configured source directory for CNV files
        
        Returns:
            Path to the source directory
        """
        source_dir = self.cnv_config.get("source_directory", "testdataQC")
        return Path(source_dir)
    
    def process_file_by_path(self, file_path: str) -> Dict[str, Any]:
        """
        Process a single CNV file by path through the complete pipeline
        
        Args:
            file_path: Path to the CNV file
            
        Returns:
            Dictionary with processing results for this file
        """
        try:
            # Read the CNV file
            df, metadata = self.cnv_reader.read_cnv_file(file_path)
            filename = Path(file_path).name
            
            # Process the data
            return self.process_single_file(df, metadata, filename)
        except Exception as e:
            self.logger.error(f"Failed to process file {file_path}: {e}")
            raise
    
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
    
    def watch_for_new_files(self, patterns: Optional[list] = None, 
                           interval: int = 30, min_age: float = 0.5,
                           plot_after: bool = True, output_dir: Optional[Path] = None,
                           state_file: Optional[Path] = None):
        """
        Watch for new CNV files and process them in real-time
        
        Args:
            patterns: File patterns to watch for (default: ["live_*.cnv"])
            interval: Polling interval in seconds
            min_age: Minimum file age in seconds before processing
            plot_after: Whether to generate plots after processing
            output_dir: Directory for output plots
            state_file: Path to state file for tracking processed files
        """
        if patterns is None:
            patterns = ["live_*.cnv"]
        
        if output_dir is None:
            output_dir = Path("tests/output/realtime_plots")
        
        if state_file is None:
            state_file = Path(".runtime/cnv_seen_realtime.json")
        
        source_dir = self.get_source_directory()
        output_dir.mkdir(parents=True, exist_ok=True)
        state_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Load previous state
        seen = set()
        if state_file.exists():
            try:
                prev = json.loads(state_file.read_text(encoding="utf-8"))
                if isinstance(prev, list):
                    for item in prev:
                        if isinstance(item, str):
                            seen.add(item)
            except Exception:
                pass
        
        self.logger.info(f"Starting realtime watch: {source_dir} every {interval}s")
        self.logger.info(f"File patterns: {patterns}")
        self.logger.info(f"Previously seen files: {len(seen)}")
        
        try:
            last_plot_time = 0  # Track when we last generated plots
            
            while True:
                # Find matching files
                matched = []
                for pat in patterns:
                    matched.extend(source_dir.glob(pat))
                
                # Check for new files
                now = time.time()
                candidate_files = []
                for p in matched:
                    try:
                        st = p.stat()
                        age_ok = (now - st.st_mtime) >= min_age
                        # For real-time files, use file path + size as key to detect size changes
                        # This allows detection of appended data even if mtime doesn't change
                        key = f"{str(p.resolve())}:{st.st_size}"
                        if age_ok:
                            candidate_files.append((p, key))
                    except FileNotFoundError:
                        continue
                
                new_files = [p for (p, key) in candidate_files if key not in seen]
                
                # Check if it's time to update plots (respect interval for plotting)
                should_update_plots = plot_after and (now - last_plot_time) >= interval
                
                if new_files:
                    self.logger.info(f"Detected {len(new_files)} new CNV file(s)")
                    
                    # Process only new files
                    for file_path in new_files:
                        try:
                            self.logger.info(f"Processing new file: {file_path}")
                            result = self.process_file_by_path(str(file_path))
                            self.logger.info(f"Successfully processed {file_path.name}: {result['records']} records")
                        except Exception as e:
                            self.logger.error(f"Failed to process {file_path}: {e}")
                    
                    # Mark files as seen
                    for (p, key) in candidate_files:
                        if key not in seen:
                            seen.add(key)
                    
                    # Save state
                    try:
                        state_file.write_text(json.dumps(list(seen)), encoding="utf-8")
                    except Exception:
                        pass
                
                # Generate plots when interval has passed OR when new files are processed
                if should_update_plots or (plot_after and new_files):
                    try:
                        db = DatabaseDataSource()
                        if db.is_available():
                            # Load recent data (last 2 hours) for real-time visualization
                            from datetime import datetime, timedelta
                            import pandas as pd
                            
                            # Get data from the last 2 hours to show real-time changes
                            cutoff_time = datetime.now() - timedelta(hours=2)
                            data = db.load_data(limit=1000)  # Increase limit to get more data
                            
                            # Filter to recent data if we have timestamps
                            if len(data) > 0 and 'time' in data.columns:
                                # Convert time column to datetime if it's not already
                                if not pd.api.types.is_datetime64_any_dtype(data['time']):
                                    data['time'] = pd.to_datetime(data['time'])
                                
                                # Make cutoff_time timezone-aware to match data
                                if data['time'].dt.tz is not None:
                                    cutoff_time = cutoff_time.replace(tzinfo=data['time'].dt.tz)
                                
                                # Filter to last 2 hours
                                recent_data = data[data['time'] >= cutoff_time]
                                if len(recent_data) > 0:
                                    data = recent_data
                                else:
                                    # If no recent data, use the latest 200 records
                                    data = data.tail(200)
                            
                            if len(data) > 0:
                                viz = TriaxusVisualizer()
                                
                                # Generate multiple plot types
                                plots_generated = []
                                
                                # 1. Time series plot
                                out_ts = output_dir / "realtime_timeseries_latest.html"
                                viz.create_time_series_plot(data, variables=["tv290c", "sal00"], output_file=str(out_ts))
                                plots_generated.append("time_series")
                                
                                # 2. Depth profile plot
                                out_dp = output_dir / "realtime_depth_profile_latest.html"
                                viz.create_depth_profile_plot(data, variables=["tv290c", "sal00"], output_file=str(out_dp))
                                plots_generated.append("depth_profile")
                                
                                # 3. Contour plot (temperature)
                                out_contour = output_dir / "realtime_contour_latest.html"
                                viz.create_contour_plot(data, variable="tv290c", output_file=str(out_contour))
                                plots_generated.append("contour")
                                
                                # 4. Map plot (if location data available)
                                if 'latitude' in data.columns and 'longitude' in data.columns:
                                    out_map = output_dir / "realtime_map_latest.html"
                                    viz.create_map_plot(data, output_file=str(out_map))
                                    plots_generated.append("map")
                                
                                self.logger.info(f"Realtime plots updated: {', '.join(plots_generated)} with {len(data)} records")
                                last_plot_time = now  # Update the last plot time
                            else:
                                self.logger.info("No data loaded for plotting")
                        else:
                            self.logger.info("Database not available; skipping plotting")
                    except Exception as plot_exc:
                        self.logger.warning(f"Plotting failed: {plot_exc}")
                elif new_files:
                    self.logger.debug(f"Files processed but plot update skipped (next update in {interval - (now - last_plot_time):.1f}s)")
                else:
                    self.logger.debug("No new files detected")
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            self.logger.info("Realtime processor interrupted; exiting")
            sys.exit(0)


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
            logging.FileHandler(logs_dir / 'cnv_realtime_processing.log')
        ]
    )


def show_help():
    """Show help information"""
    print("""
CNV Real-time Processor

Usage:
    python -m triaxus.data.cnv_realtime_processor [options]

Options:
    --help, -h          Show this help message
    --config, -c        Show current configuration
    --watch             Start real-time monitoring mode

Configuration:
    Real-time settings are configured in configs/default.yaml under:
    cnv_processing.realtime

Examples:
    python -m triaxus.data.cnv_realtime_processor --watch
    python -m triaxus.data.cnv_realtime_processor --config
    """)


def show_config():
    """Show current configuration"""
    try:
        processor = CNVRealtimeProcessor()
        source_dir = processor.get_source_directory()
        realtime_cfg = processor.cnv_config.get("realtime", {})
        
        print(f"\nCNV Real-time Processing Configuration:")
        print(f"Source directory: {source_dir}")
        print(f"Directory exists: {source_dir.exists()}")
        print(f"Realtime enabled: {realtime_cfg.get('enabled', False)}")
        print(f"Interval: {realtime_cfg.get('interval_seconds', 30)} seconds")
        print(f"File patterns: {realtime_cfg.get('file_patterns', ['*.cnv'])}")
        print(f"Min age: {realtime_cfg.get('min_age_seconds', 5)} seconds")
        print(f"Plot after ingest: {realtime_cfg.get('plot_after_ingest', True)}")
        print(f"Output directory: {realtime_cfg.get('plot_output_dir', 'tests/output/realtime_plots')}")
        print(f"State file: {realtime_cfg.get('state_file', '.runtime/cnv_seen_realtime.json')}")
        
    except Exception as e:
        print(f"Error reading configuration: {e}")


def main():
    """Main real-time processing function"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Check for custom config file
    custom_config = None
    if len(sys.argv) > 2:
        for i, arg in enumerate(sys.argv):
            if arg == "--config" and i + 1 < len(sys.argv):
                custom_config = sys.argv[i + 1]
                break
    
    # Initialize processor with custom config if provided
    processor = CNVRealtimeProcessor(custom_config_path=custom_config)
    realtime_cfg = processor.cnv_config.get("realtime", {})
    
    # Configuration
    patterns = realtime_cfg.get("file_patterns", ["live_*.cnv"])
    interval = int(realtime_cfg.get("interval_seconds", 30))
    min_age = float(realtime_cfg.get("min_age_seconds", 0.5))
    plot_after = bool(realtime_cfg.get("plot_after_ingest", True))
    output_dir = Path(realtime_cfg.get("plot_output_dir", "tests/output/realtime_plots"))
    state_file = Path(realtime_cfg.get("state_file", ".runtime/cnv_seen_realtime.json"))
    
    logger.info(f"Starting realtime CNV processor with config:")
    logger.info(f"  Patterns: {patterns}")
    logger.info(f"  Interval: {interval}s")
    logger.info(f"  Min age: {min_age}s")
    logger.info(f"  Plot after: {plot_after}")
    logger.info(f"  Output dir: {output_dir}")
    logger.info(f"  State file: {state_file}")
    
    # Start watching
    processor.watch_for_new_files(
        patterns=patterns,
        interval=interval,
        min_age=min_age,
        plot_after=plot_after,
        output_dir=output_dir,
        state_file=state_file
    )


if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "--help" or command == "-h":
            show_help()
        elif command == "--config" or command == "-c":
            show_config()
        elif command == "--watch":
            main()
        else:
            print(f"Unknown command: {command}")
            print("Use --help for usage information")
            sys.exit(1)
    else:
        # Default: start real-time monitoring
        main()

