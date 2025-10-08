"""
CNV File Reader for TRIAXUS visualization system

This module provides functionality to read and parse Sea-Bird CNV files
and convert them to pandas DataFrames for processing.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timezone
import logging
import re
from pathlib import Path

logger = logging.getLogger(__name__)


class CNVFileReader:
    """
    Reader for Sea-Bird CNV files
    
    CNV files contain oceanographic data with:
    - Header information (lines starting with * or #)
    - Variable definitions and spans
    - Data rows with measurements
    """
    
    def __init__(self):
        """Initialize CNV file reader"""
        self.logger = logging.getLogger(__name__)
        
        # Standard CNV variable mapping to our internal format
        self.VARIABLE_MAPPING = {
            't090C': 'tv290c',           # Temperature [ITS-90, deg C]
            'c0S/m': 'conductivity',     # Conductivity [S/m]
            'prDM': 'depth',             # Pressure, Digiquartz [db] -> depth
            't190C': 'tv290c_2',         # Temperature, 2 [ITS-90, deg C]
            'c1S/m': 'conductivity_2',   # Conductivity, 2 [S/m]
            'sbeox0Mm/L': 'sbeox0mm_l',  # Oxygen, SBE 43 [umol/l]
            'sbeox1Mm/L': 'sbeox1mm_l',  # Oxygen, SBE 43, 2 [umol/l]
            'par': 'par',                # PAR/Irradiance [umol photons/m^2/sec]
            'CStarTr0': 'cstar_tr0',     # Beam Transmission [%]
            'sal00': 'sal00',            # Salinity, Practical [PSU]
            'sal11': 'sal11',            # Salinity, Practical, 2 [PSU]
            'fleco_afl': 'fleco_afl',    # Fluorescence [mg/m³]
            'ph': 'ph',                  # pH
            'scan': 'scan',              # Scan Count
            'timeS': 'time_elapsed',        # Time, Elapsed [seconds] -> time_elapsed
            'pumps': 'pumps',            # Pump Status
            'latitude': 'latitude',      # Latitude [deg]
            'longitude': 'longitude',    # Longitude [deg]
            'flag': 'flag'               # Flag
        }
    
    def read_cnv_file(self, file_path: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Read a CNV file and convert to DataFrame
        
        Args:
            file_path: Path to the CNV file
            
        Returns:
            Tuple of (DataFrame, metadata)
        """
        try:
            self.logger.info(f"Reading CNV file: {file_path}")
            
            # Parse header and extract metadata
            header_info = self._parse_cnv_header(file_path)
            
            # Parse data rows
            data_rows = self._parse_cnv_data(file_path, header_info)
            
            # Convert to DataFrame
            df = pd.DataFrame(data_rows)
            
            # Standardize column names
            df = self._standardize_columns(df)
            
            # Add time column if not present
            if 'time' not in df.columns and 'time_elapsed' in df.columns:
                df = self._add_time_column(df, header_info)
            
            self.logger.info(f"Successfully read {len(df)} records from {file_path}")
            
            return df, header_info
            
        except Exception as e:
            self.logger.error(f"Error reading CNV file {file_path}: {e}")
            raise
    
    def _parse_cnv_header(self, file_path: str) -> Dict[str, Any]:
        """
        Parse CNV file header to extract metadata
        
        Args:
            file_path: Path to the CNV file
            
        Returns:
            Dictionary with header information
        """
        header_info = {
            'filename': Path(file_path).name,
            'file_path': file_path,
            'variables': [],
            'spans': {},
            'metadata': {},
            'start_time': None,
            'n_values': None
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    
                    # Stop at data section (non-header lines)
                    if line and not line.startswith('*') and not line.startswith('#'):
                        break
                    
                    # Parse variable definitions
                    if line.startswith('# name '):
                        var_info = self._parse_variable_definition(line)
                        if var_info:
                            header_info['variables'].append(var_info)
                    
                    # Parse spans
                    elif line.startswith('# span '):
                        span_info = self._parse_span_definition(line)
                        if span_info:
                            header_info['spans'].update(span_info)
                    
                    # Parse metadata
                    elif line.startswith('*'):
                        meta_info = self._parse_metadata_line(line)
                        if meta_info:
                            header_info['metadata'].update(meta_info)
                    
                    # Parse nvalues
                    elif line.startswith('# nvalues ='):
                        try:
                            header_info['n_values'] = int(line.split('=')[1].strip())
                        except:
                            pass
                    
                    # Parse start time
                    elif 'System UTC' in line or 'NMEA UTC' in line or 'start_time' in line:
                        time_str = self._extract_time_from_line(line)
                        if time_str:
                            header_info['start_time'] = time_str
            
            self.logger.info(f"Parsed header with {len(header_info['variables'])} variables")
            
        except Exception as e:
            self.logger.error(f"Error parsing CNV header: {e}")
            raise
        
        return header_info
    
    def _parse_cnv_data(self, file_path: str, header_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Parse CNV file data rows
        
        Args:
            file_path: Path to the CNV file
            header_info: Header information from _parse_cnv_header
            
        Returns:
            List of dictionaries with data rows
        """
        data_rows = []
        variable_names = [var['name'] for var in header_info['variables']]
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                in_data_section = False
                
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    
                    # Skip empty lines
                    if not line:
                        continue
                    
                    # Check if we're in data section
                    if not line.startswith('*') and not line.startswith('#'):
                        in_data_section = True
                    
                    # Parse data rows
                    if in_data_section and line:
                        try:
                            # Split line into values
                            values = line.split()
                            
                            # Convert to appropriate types
                            row_data = {}
                            for i, value in enumerate(values):
                                if i < len(variable_names):
                                    var_name = variable_names[i]
                                    
                                    # Convert to float, handling scientific notation
                                    try:
                                        float_value = float(value)
                                        row_data[var_name] = float_value
                                    except ValueError:
                                        # Keep as string if conversion fails
                                        row_data[var_name] = value
                            
                            data_rows.append(row_data)
                            
                        except Exception as e:
                            self.logger.warning(f"Error parsing data line {line_num}: {e}")
                            continue
            
            self.logger.info(f"Parsed {len(data_rows)} data rows")
            
        except Exception as e:
            self.logger.error(f"Error parsing CNV data: {e}")
            raise
        
        return data_rows
    
    def _parse_variable_definition(self, line: str) -> Optional[Dict[str, str]]:
        """Parse variable definition line"""
        try:
            # Format: # name 0 = t090C: Temperature [ITS-90, deg C]
            match = re.match(r'# name \d+ = ([^:]+):\s*(.+)', line)
            if match:
                return {
                    'name': match.group(1).strip(),
                    'description': match.group(2).strip()
                }
        except Exception:
            pass
        return None
    
    def _parse_span_definition(self, line: str) -> Optional[Dict[str, Tuple[float, float]]]:
        """Parse span definition line"""
        try:
            # Format: # span 0 =    12.3276,    21.6890
            match = re.match(r'# span \d+ = \s*([\d.-]+),\s*([\d.-]+)', line)
            if match:
                var_index = int(re.search(r'# span (\d+)', line).group(1))
                min_val = float(match.group(1))
                max_val = float(match.group(2))
                return {f'span_{var_index}': (min_val, max_val)}
        except Exception:
            pass
        return None
    
    def _parse_metadata_line(self, line: str) -> Optional[Dict[str, str]]:
        """Parse metadata line"""
        try:
            # Format: * FileName = D:\triaxus\in2023_v06\in2023_v06_07\in2023_v06_07_002.hex
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip('* ').strip()
                value = value.strip()
                return {key: value}
        except Exception:
            pass
        return None
    
    def _extract_time_from_line(self, line: str) -> Optional[str]:
        """Extract time from metadata line"""
        try:
            # Look for time patterns like "Oct 15 2023 13:40:44" or "Oct 15 2023  13:40:44" (with extra spaces)
            time_match = re.search(r'(\w{3} \d{1,2} \d{4}\s+\d{2}:\d{2}:\d{2})', line)
            if time_match:
                # Normalize spaces in the extracted time string
                time_str = time_match.group(1)
                time_str = re.sub(r'\s+', ' ', time_str)  # Replace multiple spaces with single space
                return time_str
        except Exception:
            pass
        return None
    
    def _standardize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Standardize column names to match our internal format
        
        Args:
            df: DataFrame with CNV column names
            
        Returns:
            DataFrame with standardized column names
        """
        # Create mapping for columns that exist in the DataFrame
        column_mapping = {}
        for cnv_name, std_name in self.VARIABLE_MAPPING.items():
            if cnv_name in df.columns:
                column_mapping[cnv_name] = std_name
        
        # Rename columns
        df = df.rename(columns=column_mapping)
        
        # Ensure required columns exist (except 'time' which will be added later)
        required_columns = ['depth', 'latitude', 'longitude']
        for col in required_columns:
            if col not in df.columns:
                self.logger.warning(f"Required column '{col}' not found in data")
        
        return df
    
    def _add_time_column(self, df: pd.DataFrame, header_info: Dict[str, Any]) -> pd.DataFrame:
        """
        Add time column based on elapsed time and start time
        
        Args:
            df: DataFrame with time_elapsed column
            header_info: Header information with start_time
            
        Returns:
            DataFrame with time column added
        """
        if 'time_elapsed' not in df.columns:
            return df
        
        try:
            # Parse start time
            start_time_str = header_info.get('start_time')
            if start_time_str:
                # Parse time format like "Oct 15 2023 13:40:44" as UTC
                start_time = datetime.strptime(start_time_str, "%b %d %Y %H:%M:%S")
                # Mark as UTC since CNV files store time as UTC
                start_time = start_time.replace(tzinfo=timezone.utc)
                
                # Add elapsed time to start time
                df['time'] = start_time + pd.to_timedelta(df['time_elapsed'], unit='s')
            else:
                # Fallback: use elapsed time as relative time
                df['time'] = pd.to_datetime(df['time_elapsed'], unit='s')
                
        except Exception as e:
            self.logger.warning(f"Error adding time column: {e}")
            # Fallback: use elapsed time as relative time
            df['time'] = pd.to_datetime(df['time_elapsed'], unit='s')
        
        return df
    
    def read_testdataQC_directory(self, directory_path: str) -> Dict[str, Tuple[pd.DataFrame, Dict[str, Any]]]:
        """
        Read all CNV files from testdataQC directory
        
        Args:
            directory_path: Path to testdataQC directory
            
        Returns:
            Dictionary mapping filename to (DataFrame, metadata) tuples
        """
        results = {}
        directory = Path(directory_path)
        
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory_path}")
        
        # Find all CNV files
        cnv_files = list(directory.glob("*.cnv"))
        
        if not cnv_files:
            self.logger.warning(f"No CNV files found in {directory_path}")
            return results
        
        self.logger.info(f"Found {len(cnv_files)} CNV files in {directory_path}")
        
        for cnv_file in cnv_files:
            try:
                df, metadata = self.read_cnv_file(str(cnv_file))
                results[cnv_file.name] = (df, metadata)
                self.logger.info(f"Successfully processed {cnv_file.name}: {len(df)} records")
            except Exception as e:
                self.logger.error(f"Failed to process {cnv_file.name}: {e}")
                continue
        
        return results


# This function has been moved to cnv_processor.py for better organization


if __name__ == "__main__":
    # Example usage
    import logging
    logging.basicConfig(level=logging.INFO)
    
    # Test reading a single CNV file
    reader = CNVFileReader()
    test_file = "testdataQC/in2023_v06_07_002.cnv"
    
    try:
        df, metadata = reader.read_cnv_file(test_file)
        print(f"Successfully read {test_file}")
        print(f"Data shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")
        print(f"Time range: {df['time'].min()} to {df['time'].max()}")
    except Exception as e:
        print(f"Error reading file: {e}")
