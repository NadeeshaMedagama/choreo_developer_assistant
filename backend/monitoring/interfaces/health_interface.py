"""
Health Checker Interface - Dependency Inversion Principle
Depend on abstractions, not concretions.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any
from enum import Enum


class HealthStatus(Enum):
    """Health status enumeration."""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"


class IHealthChecker(ABC):
    """Interface for health checking components."""
    
    @abstractmethod
    def check_health(self) -> Dict[str, Any]:
        """
        Check health of the component.
        
        Returns:
            Dict with keys: status, message, details
        """
        pass
    
    @abstractmethod
    def get_component_name(self) -> str:
        """Get the name of the component being checked."""
        pass

