"""
Health Checker - Dependency Inversion
Depends on IHealthChecker abstraction.
"""
from typing import Dict, Any, List
from ..interfaces.health_interface import IHealthChecker, HealthStatus


class HealthChecker:
    """Aggregates health checks from multiple components."""
    
    def __init__(self):
        """Initialize health checker."""
        self._checkers: List[IHealthChecker] = []
    
    def register_checker(self, checker: IHealthChecker) -> None:
        """Register a health checker."""
        self._checkers.append(checker)
    
    def check_all(self) -> Dict[str, Any]:
        """
        Check health of all registered components.
        
        Returns:
            Dict with overall status and component statuses
        """
        component_statuses = {}
        overall_healthy = True
        
        for checker in self._checkers:
            result = checker.check_health()
            component_name = checker.get_component_name()
            component_statuses[component_name] = result
            
            if result.get('status') != HealthStatus.HEALTHY.value:
                overall_healthy = False
        
        return {
            'status': HealthStatus.HEALTHY.value if overall_healthy else HealthStatus.UNHEALTHY.value,
            'components': component_statuses,
            'timestamp': self._get_timestamp()
        }
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.utcnow().isoformat()


class MilvusHealthChecker(IHealthChecker):
    """Health checker for Milvus vector database."""

    def __init__(self, vector_client):
        """Initialize with vector client."""
        self._vector_client = vector_client
    
    def check_health(self) -> Dict[str, Any]:
        """Check Milvus health."""
        try:
            is_connected = self._vector_client.test_connection()
            return {
                'status': HealthStatus.HEALTHY.value if is_connected else HealthStatus.UNHEALTHY.value,
                'message': 'Milvus connected' if is_connected else 'Milvus disconnected',
                'details': {}
            }
        except Exception as e:
            return {
                'status': HealthStatus.UNHEALTHY.value,
                'message': f'Milvus check failed: {str(e)}',
                'details': {'error': str(e)}
            }
    
    def get_component_name(self) -> str:
        """Get component name."""
        return 'milvus'


class ApplicationHealthChecker(IHealthChecker):
    """Health checker for application."""
    
    def check_health(self) -> Dict[str, Any]:
        """Check application health."""
        return {
            'status': HealthStatus.HEALTHY.value,
            'message': 'Application running',
            'details': {}
        }
    
    def get_component_name(self) -> str:
        """Get component name."""
        return 'application'

