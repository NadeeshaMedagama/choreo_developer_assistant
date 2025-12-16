"""
Structured Logger - Liskov Substitution Principle
Can be used anywhere ILogger is expected.
"""
import logging
import json
from datetime import datetime
from typing import Dict, Any
from ..interfaces.logging_interface import IStructuredLogger


class StructuredLogger(IStructuredLogger):
    """Structured logging implementation."""
    
    def __init__(self, name: str, enable_json: bool = False):
        """
        Initialize structured logger.
        
        Args:
            name: Logger name
            enable_json: Whether to output in JSON format
        """
        self._logger = logging.getLogger(name)
        self._enable_json = enable_json
    
    def debug(self, message: str, **kwargs) -> None:
        """Log debug message."""
        self._log('DEBUG', message, **kwargs)
    
    def info(self, message: str, **kwargs) -> None:
        """Log info message."""
        self._log('INFO', message, **kwargs)
    
    def warning(self, message: str, **kwargs) -> None:
        """Log warning message."""
        self._log('WARNING', message, **kwargs)
    
    def error(self, message: str, exc_info: bool = False, **kwargs) -> None:
        """Log error message."""
        self._log('ERROR', message, exc_info=exc_info, **kwargs)
    
    def critical(self, message: str, exc_info: bool = False, **kwargs) -> None:
        """Log critical message."""
        self._log('CRITICAL', message, exc_info=exc_info, **kwargs)
    
    def log_with_context(self, level: str, message: str, context: Dict[str, Any]) -> None:
        """Log with structured context."""
        self._log(level, message, **context)
    
    def _log(self, level: str, message: str, exc_info: bool = False, **kwargs) -> None:
        """Internal logging method."""
        log_method = getattr(self._logger, level.lower())
        
        if self._enable_json:
            log_data = {
                'timestamp': datetime.utcnow().isoformat(),
                'level': level,
                'message': message,
                **kwargs
            }
            log_method(json.dumps(log_data), exc_info=exc_info)
        else:
            extra_info = ' '.join(f'{k}={v}' for k, v in kwargs.items()) if kwargs else ''
            full_message = f"{message} {extra_info}".strip()
            log_method(full_message, exc_info=exc_info)

