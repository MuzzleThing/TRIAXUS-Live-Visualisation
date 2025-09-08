"""
Error Handler for TRIAXUS visualization system

This module provides centralized error handling and user-friendly error messages.
"""

import logging
from typing import Dict, Any, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class ErrorType(Enum):
    """Error types for categorization"""
    DATA_VALIDATION = "data_validation"
    CONFIGURATION = "configuration"
    PLOT_GENERATION = "plot_generation"
    HTML_GENERATION = "html_generation"
    FILE_OPERATION = "file_operation"
    NETWORK = "network"
    UNKNOWN = "unknown"


class ErrorHandler:
    """Centralized error handler"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Error message templates
        self.error_messages = {
            ErrorType.DATA_VALIDATION: {
                'missing_columns': "Missing required columns: {columns}",
                'invalid_data_type': "Invalid data type for column '{column}': expected {expected_type}",
                'empty_data': "Data is empty or contains no valid rows",
                'out_of_range': "Values in column '{column}' are outside valid range [{min_val}, {max_val}]"
            },
            ErrorType.CONFIGURATION: {
                'invalid_config': "Invalid configuration: {message}",
                'missing_config': "Missing required configuration: {key}",
                'invalid_theme': "Invalid theme: {theme}. Available themes: {available_themes}"
            },
            ErrorType.PLOT_GENERATION: {
                'plot_failed': "Failed to generate {plot_type} plot: {message}",
                'insufficient_data': "Insufficient data for {plot_type} plot: {message}",
                'invalid_parameters': "Invalid parameters for {plot_type} plot: {message}"
            },
            ErrorType.HTML_GENERATION: {
                'html_failed': "Failed to generate HTML: {message}",
                'plotly_error': "Plotly error: {message}"
            },
            ErrorType.FILE_OPERATION: {
                'file_not_found': "File not found: {file_path}",
                'permission_denied': "Permission denied: {file_path}",
                'invalid_format': "Invalid file format: {file_path}"
            },
            ErrorType.NETWORK: {
                'connection_failed': "Network connection failed: {message}",
                'timeout': "Request timeout: {message}"
            }
        }
    
    def handle_plot_error(self, error: Exception, plot_type: str, context: str = "") -> str:
        """
        Handle plot generation errors
        
        Args:
            error: The exception that occurred
            plot_type: Type of plot being generated
            context: Additional context information
            
        Returns:
            User-friendly error message
        """
        error_type = self._classify_error(error)
        message = self._format_error_message(error_type, error, plot_type, context)
        
        # Log the error
        self.logger.error(f"Plot error in {plot_type}: {str(error)}", exc_info=True)
        
        return message
    
    def handle_data_error(self, error: Exception, context: str = "") -> str:
        """
        Handle data validation errors
        
        Args:
            error: The exception that occurred
            context: Additional context information
            
        Returns:
            User-friendly error message
        """
        error_type = self._classify_error(error)
        message = self._format_error_message(error_type, error, context=context)
        
        # Log the error
        self.logger.error(f"Data error: {str(error)}", exc_info=True)
        
        return message
    
    def handle_config_error(self, error: Exception, context: str = "") -> str:
        """
        Handle configuration errors
        
        Args:
            error: The exception that occurred
            context: Additional context information
            
        Returns:
            User-friendly error message
        """
        error_type = self._classify_error(error)
        message = self._format_error_message(error_type, error, context=context)
        
        # Log the error
        self.logger.error(f"Configuration error: {str(error)}", exc_info=True)
        
        return message
    
    def _classify_error(self, error: Exception) -> ErrorType:
        """Classify error type based on exception"""
        error_str = str(error).lower()
        
        if 'missing' in error_str or 'required' in error_str:
            return ErrorType.DATA_VALIDATION
        elif 'config' in error_str or 'theme' in error_str:
            return ErrorType.CONFIGURATION
        elif 'plot' in error_str or 'figure' in error_str:
            return ErrorType.PLOT_GENERATION
        elif 'html' in error_str or 'plotly' in error_str:
            return ErrorType.HTML_GENERATION
        elif 'file' in error_str or 'path' in error_str:
            return ErrorType.FILE_OPERATION
        elif 'network' in error_str or 'connection' in error_str:
            return ErrorType.NETWORK
        else:
            return ErrorType.UNKNOWN
    
    def _format_error_message(self, error_type: ErrorType, error: Exception, 
                            plot_type: str = "", context: str = "") -> str:
        """Format error message based on type"""
        error_str = str(error)
        
        # Get base message
        if error_type in self.error_messages:
            messages = self.error_messages[error_type]
            
            # Try to match specific error patterns
            if 'missing required columns' in error_str.lower():
                return messages.get('missing_columns', error_str).format(columns=error_str)
            elif 'invalid data type' in error_str.lower():
                return messages.get('invalid_data_type', error_str).format(
                    column="unknown", expected_type="unknown"
                )
            elif 'empty' in error_str.lower():
                return messages.get('empty_data', error_str)
            elif plot_type:
                return messages.get('plot_failed', error_str).format(
                    plot_type=plot_type, message=error_str
                )
            else:
                # Use first available message template
                first_key = list(messages.keys())[0]
                return messages[first_key].format(message=error_str)
        
        # Fallback to generic message
        if plot_type:
            return f"Error generating {plot_type} plot: {error_str}"
        else:
            return f"Error: {error_str}"
    
    def create_error_response(self, error: Exception, plot_type: str = "", 
                            context: str = "") -> Dict[str, Any]:
        """
        Create structured error response
        
        Args:
            error: The exception that occurred
            plot_type: Type of plot being generated
            context: Additional context information
            
        Returns:
            Structured error response
        """
        error_type = self._classify_error(error)
        message = self._format_error_message(error_type, error, plot_type, context)
        
        return {
            'success': False,
            'error_type': error_type.value,
            'message': message,
            'plot_type': plot_type,
            'context': context,
            'details': str(error)
        }
    
    def log_error(self, error: Exception, level: str = "ERROR", context: str = ""):
        """Log error with appropriate level"""
        log_func = getattr(self.logger, level.lower(), self.logger.error)
        
        if context:
            log_func(f"{context}: {str(error)}", exc_info=True)
        else:
            log_func(str(error), exc_info=True)
    
    def get_suggestions(self, error_type: ErrorType, context: str = "") -> list:
        """Get suggestions for fixing errors"""
        suggestions = {
            ErrorType.DATA_VALIDATION: [
                "Check that your data contains all required columns",
                "Ensure data types are correct (numeric for values, datetime for time)",
                "Remove rows with missing required data",
                "Check data ranges are within expected limits"
            ],
            ErrorType.CONFIGURATION: [
                "Verify configuration file format (JSON or YAML)",
                "Check that all required configuration keys are present",
                "Validate configuration values are correct types",
                "Use a valid theme name"
            ],
            ErrorType.PLOT_GENERATION: [
                "Ensure data contains sufficient points for plotting",
                "Check that variables exist in the data",
                "Verify plot parameters are valid",
                "Try with a smaller dataset to isolate the issue"
            ],
            ErrorType.HTML_GENERATION: [
                "Check Plotly installation and version",
                "Verify HTML generation configuration",
                "Ensure figure object is valid",
                "Check for JavaScript errors in browser console"
            ]
        }
        
        return suggestions.get(error_type, ["Please check the error details and try again"])
