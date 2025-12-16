"""
Monitoring module following SOLID principles.
Provides interfaces and dependency injection for metrics, logging, and alerting.
"""

# Core interfaces
from .interfaces.metrics_interface import IMetricsCollector, IMetricsExporter
from .interfaces.logging_interface import ILogger
from .interfaces.health_interface import IHealthChecker

# Implementations
from .collectors.system_metrics_collector import SystemMetricsCollector
from .collectors.application_metrics_collector import ApplicationMetricsCollector
from .collectors.ai_metrics_collector import AIMetricsCollector
from .collectors.scraping_metrics_collector import ScrapingMetricsCollector
from .collectors.rule_evaluation_metrics_collector import RuleEvaluationMetricsCollector
from .exporters.prometheus_exporter import PrometheusExporter
from .loggers.structured_logger import StructuredLogger
from .health.health_checker import HealthChecker

# Services
from .services.monitoring_service import MonitoringService, get_monitoring_service
from .middleware.metrics_middleware import MetricsMiddleware

# Backward compatibility
from .legacy_adapter import (
    metrics_middleware,
    record_ai_inference,
    record_vector_search,
    record_github_ingestion,
    record_error,
)

__all__ = [
    # Interfaces
    'IMetricsCollector',
    'IMetricsExporter',
    'ILogger',
    'IHealthChecker',

    # Implementations
    'SystemMetricsCollector',
    'ApplicationMetricsCollector',
    'AIMetricsCollector',
    'ScrapingMetricsCollector',
    'RuleEvaluationMetricsCollector',
    'PrometheusExporter',
    'StructuredLogger',
    'HealthChecker',

    # Services
    'MonitoringService',
    'get_monitoring_service',
    'MetricsMiddleware',

    # Legacy API
    'metrics_middleware',
    'record_ai_inference',
    'record_vector_search',
    'record_github_ingestion',
    'record_error',
]

