"""
Application Metrics Collector - Single Responsibility
Collects only application-level metrics (requests, errors).
"""
from typing import Dict, Any
from ..interfaces.metrics_interface import IMetricsCollector


class ApplicationMetricsCollector(IMetricsCollector):
    """Collects application performance metrics."""
    
    def __init__(self):
        """Initialize application metrics collector."""
        self._metric_names = [
            'http_requests_total',
            'http_request_duration_seconds',
            'http_requests_active',
            'errors_total'
        ]
        self._request_count = 0
        self._error_count = 0
        self._active_requests = 0
    
    def collect(self) -> Dict[str, Any]:
        """
        Collect application metrics.
        
        Returns:
            Dictionary of metric names and values
        """
        return {
            'http_requests_total': self._request_count,
            'http_requests_active': self._active_requests,
            'errors_total': self._error_count,
        }
    
    def get_metric_names(self) -> list:
        """Get list of metric names."""
        return self._metric_names.copy()
    
    def increment_requests(self) -> None:
        """Increment request counter."""
        self._request_count += 1
    
    def increment_errors(self) -> None:
        """Increment error counter."""
        self._error_count += 1
    
    def increment_active_requests(self) -> None:
        """Increment active requests."""
        self._active_requests += 1
    
    def decrement_active_requests(self) -> None:
        """Decrement active requests."""
        self._active_requests = max(0, self._active_requests - 1)

