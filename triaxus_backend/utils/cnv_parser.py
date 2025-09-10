"""
CNV file parser for SeaBird CTD data files.
"""
import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

class CNVParser:
    """Parser for SeaBird CNV (converted) data files."""
    
    def __init__(self):
        self.header_patterns = {
            'cruise_name': re.compile(r'\* cruise_name:\s*(.+)', re.IGNORECASE),
            'vessel_name': re.compile(r'\* vessel_name:\s*(.+)', re.IGNORECASE),
            'start_time': re.compile(r'\* start_time = (.+)', re.IGNORECASE),
            'latitude': re.compile(r'\* latitude:\s*([\-\d\.]+)', re.IGNORECASE),
            'longitude': re.compile(r'\* longitude:\s*([\-\d\.]+)', re.IGNORECASE),
            'cast_number': re.compile(r'\* cast:\s*(\d+)', re.IGNORECASE),
            'water_depth': re.compile(r'\* water_depth:\s*([\d\.]+)', re.IGNORECASE),
            'instrument_type': re.compile(r'\* instrument_type:\s*(.+)', re.IGNORECASE),
            'serial_number': re.compile(r'\* serial_number:\s*(.+)', re.IGNORECASE),
        }
        
        # Column name mapping from common CNV names to standard names
        self.column_mapping = {
            'prDM': 'pressure',
            'depSM': 'depth', 
            't090C': 'temperature',
            't190C': 'temperature2',
            'c0S/m': 'conductivity',
            'c1S/m': 'conductivity2',
            'sal00': 'salinity',
            'sal11': 'salinity2',
            'oxML/L': 'oxygen',
            'flECO-AFL': 'fluorescence',
            'turbWETbb0': 'turbidity',
            'par': 'par',
            'latitude': 'latitude',
            'longitude': 'longitude',
            'timeS': 'time_seconds',
            'scan': 'scan_number'
        }
    
    def parse_file(self, file_path: str) -> Dict[str, Any]:
        """Parse complete CNV file and return header and data."""
        try:
            path_obj = Path(file_path)
            if not path_obj.exists():
                raise FileNotFoundError(f"CNV file not found: {file_path}")
            
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Split header and data sections
            header_section, data_section = self._split_header_data(content)
            
            # Parse header
            header_info = self._parse_header(header_section)
            
            # Parse column definitions
            column_info = self._parse_column_definitions(header_section)
            
            # Parse data
            data_records = self._parse_data_section(data_section, column_info)
            
            return {
                'file_path': str(path_obj),
                'file_name': path_obj.name,
                'header_info': header_info,
                'column_info': column_info,
                'data_records': data_records,
                'record_count': len(data_records),
                'parsed_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error parsing CNV file {file_path}: {str(e)}")
            raise
    
    def parse_header_only(self, file_path: str) -> Dict[str, Any]:
        """Parse only the header section of a CNV file."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                header_lines = []
                for line in f:
                    if line.startswith('*END*'):
                        break
                    header_lines.append(line)
                
                header_section = ''.join(header_lines)
            
            header_info = self._parse_header(header_section)
            column_info = self._parse_column_definitions(header_section)
            
            return {
                'header_info': header_info,
                'column_info': column_info,
                'parsed_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error parsing CNV header {file_path}: {str(e)}")
            raise
    
    def parse_data_line(self, line: str, column_info: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        """Parse a single data line from CNV file."""
        try:
            line = line.strip()
            if not line or line.startswith('*') or line.startswith('#'):
                return None
            
            # Split line into values
            values = line.split()
            if not values:
                return None
            
            parsed_data = {}
            
            # If we have column information, map values to columns
            if column_info and 'columns' in column_info:
                columns = column_info['columns']
                for i, value in enumerate(values):
                    if i < len(columns):
                        column_name = columns[i]['standard_name']
                        try:
                            # Convert to appropriate type
                            if column_name in ['scan_number']:
                                parsed_data[column_name] = int(float(value))
                            else:
                                parsed_data[column_name] = float(value)
                        except (ValueError, TypeError):
                            parsed_data[column_name] = value
            else:
                # Generic parsing without column mapping
                for i, value in enumerate(values):
                    try:
                        parsed_data[f'column_{i}'] = float(value)
                    except (ValueError, TypeError):
                        parsed_data[f'column_{i}'] = value
            
            return parsed_data
            
        except Exception as e:
            logger.debug(f"Error parsing data line: {line[:50]}... - {str(e)}")
            return None
    
    def _split_header_data(self, content: str) -> Tuple[str, str]:
        """Split CNV content into header and data sections."""
        lines = content.split('\n')
        header_lines = []
        data_lines = []
        
        in_data_section = False
        
        for line in lines:
            if line.strip() == '*END*':
                in_data_section = True
                continue
            
            if in_data_section:
                data_lines.append(line)
            else:
                header_lines.append(line)
        
        return '\n'.join(header_lines), '\n'.join(data_lines)
    
    def _parse_header(self, header_section: str) -> Dict[str, Any]:
        """Parse header information from CNV file."""
        header_info = {}
        
        for key, pattern in self.header_patterns.items():
            match = pattern.search(header_section)
            if match:
                value = match.group(1).strip()
                
                # Special handling for certain fields
                if key == 'start_time':
                    try:
                        # Try to parse common SeaBird time formats
                        for fmt in ['%b %d %Y %H:%M:%S', '%m/%d/%Y %H:%M:%S', '%Y-%m-%d %H:%M:%S']:
                            try:
                                header_info[key] = datetime.strptime(value, fmt)
                                break
                            except ValueError:
                                continue
                        else:
                            header_info[key] = value  # Keep as string if parsing fails
                    except Exception:
                        header_info[key] = value
                elif key in ['latitude', 'longitude', 'water_depth']:
                    try:
                        header_info[key] = float(value)
                    except ValueError:
                        header_info[key] = value
                elif key == 'cast_number':
                    try:
                        header_info[key] = int(value)
                    except ValueError:
                        header_info[key] = value
                else:
                    header_info[key] = value
        
        # Extract additional configuration information
        config_lines = [line for line in header_section.split('\n') if line.startswith('#')]
        if config_lines:
            header_info['configuration'] = config_lines
        
        return header_info
    
    def _parse_column_definitions(self, header_section: str) -> Dict[str, Any]:
        """Parse column definitions from CNV header."""
        column_info = {'columns': [], 'units': {}}
        
        # Look for column definition lines (usually start with # name)
        name_pattern = re.compile(r'# name (\d+) = (.+): (.+)')
        
        for line in header_section.split('\n'):
            name_match = name_pattern.search(line)
            if name_match:
                col_index = int(name_match.group(1))
                col_name = name_match.group(2).strip()
                col_description = name_match.group(3).strip()
                
                # Map to standard name
                standard_name = self.column_mapping.get(col_name, col_name)
                
                column_info['columns'].append({
                    'index': col_index,
                    'original_name': col_name,
                    'standard_name': standard_name,
                    'description': col_description
                })
        
        # Sort columns by index
        column_info['columns'].sort(key=lambda x: x['index'])
        
        return column_info
    
    def _parse_data_section(self, data_section: str, column_info: Dict) -> List[Dict[str, Any]]:
        """Parse data section of CNV file."""
        data_records = []
        
        for line_num, line in enumerate(data_section.split('\n'), 1):
            parsed_line = self.parse_data_line(line, column_info)
            if parsed_line:
                parsed_line['line_number'] = line_num
                data_records.append(parsed_line)
        
        return data_records
    
    def validate_cnv_format(self, file_path: str) -> bool:
        """Validate if file is a proper CNV format."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                # Read first few lines
                first_lines = [f.readline() for _ in range(10)]
            
            # Check for CNV format indicators
            has_header = any(line.startswith('*') for line in first_lines)
            has_end_marker = any('*END*' in line for line in first_lines)
            
            return has_header or has_end_marker
            
        except Exception:
            return False