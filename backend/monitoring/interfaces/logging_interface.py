"""
Logging Interface - Interface Segregation Principle
Separate interfaces for different logging concerns.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class ILogger(ABC):
    """Base logging interface."""
    
    @abstractmethod
    def debug(self, message: str, **kwargs) -> None:
        """Log debug message."""
        pass
    
    @abstractmethod
    def info(self, message: str, **kwargs) -> None:
        """Log info message."""
        pass
    
    @abstractmethod
    def warning(self, message: str, **kwargs) -> None:
        """Log warning message."""
        pass
    
    @abstractmethod
    def error(self, message: str, exc_info: bool = False, **kwargs) -> None:
        """Log error message."""
        pass
    
    @abstractmethod
    def critical(self, message: str, exc_info: bool = False, **kwargs) -> None:
        """Log critical message."""
        pass


class IStructuredLogger(ILogger):
    """Extended interface for structured logging."""
    
    @abstractmethod
    def log_with_context(self, level: str, message: str, context: Dict[str, Any]) -> None:
        """Log with structured context."""
        pass

