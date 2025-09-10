"""
File hashing utilities for data integrity verification.
"""
import hashlib
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

class HashUtils:
    """Utilities for file hashing and integrity verification."""
    
    @staticmethod
    def calculate_file_hash(file_path: str, algorithm: str = 'sha256', chunk_size: int = 8192) -> str:
        """Calculate hash of a file using specified algorithm."""
        try:
            path_obj = Path(file_path)
            if not path_obj.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            # Get hash algorithm
            hash_algo = hashlib.new(algorithm)
            
            # Read file in chunks to handle large files
            with open(file_path, 'rb') as f:
                while chunk := f.read(chunk_size):
                    hash_algo.update(chunk)  # type: ignore[arg-type]
            
            return hash_algo.hexdigest()
            
        except Exception as e:
            logger.error(f"Error calculating hash for {file_path}: {str(e)}")
            raise
    
    @staticmethod
    def calculate_string_hash(text: str, algorithm: str = 'sha256') -> str:
        """Calculate hash of a string."""
        try:
            hash_algo = hashlib.new(algorithm)
            hash_algo.update(text.encode('utf-8'))  # type: ignore[arg-type]
            return hash_algo.hexdigest()
        except Exception as e:
            logger.error(f"Error calculating string hash: {str(e)}")
            raise
    
    @staticmethod
    def verify_file_integrity(file_path: str, expected_hash: str, algorithm: str = 'sha256') -> bool:
        """Verify file integrity against expected hash."""
        try:
            actual_hash = HashUtils.calculate_file_hash(file_path, algorithm)
            return actual_hash.lower() == expected_hash.lower()
        except Exception as e:
            logger.error(f"Error verifying file integrity: {str(e)}")
            return False
    
    @staticmethod
    def calculate_partial_hash(file_path: str, start_byte: int = 0, num_bytes: Optional[int] = None, 
                             algorithm: str = 'sha256') -> str:
        """Calculate hash of a portion of a file."""
        try:
            path_obj = Path(file_path)
            if not path_obj.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            hash_algo = hashlib.new(algorithm)
            
            with open(file_path, 'rb') as f:
                f.seek(start_byte)
                
                if num_bytes is None:
                    # Read from start_byte to end of file
                    while chunk := f.read(8192):
                        hash_algo.update(chunk)  # type: ignore[arg-type]
                else:
                    # Read only specified number of bytes
                    bytes_read = 0
                    while bytes_read < num_bytes:
                        chunk_size = min(8192, num_bytes - bytes_read)
                        chunk = f.read(chunk_size)
                        if not chunk:
                            break
                        hash_algo.update(chunk)  # type: ignore[arg-type]
                        bytes_read += len(chunk)
            
            return hash_algo.hexdigest()
            
        except Exception as e:
            logger.error(f"Error calculating partial hash for {file_path}: {str(e)}")
            raise