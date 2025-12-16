"""
Monitoring Service - Facade Pattern
Provides a unified interface to the monitoring subsystem.
"""
from typing import Dict, Any, List, Optional
from ..interfaces.metrics_interface import IMetricsCollector, IMetricsExporter
from ..interfaces.logging_interface import ILogger
from ..collectors.system_metrics_collector import SystemMetricsCollector
from ..collectors.application_metrics_collector import ApplicationMetricsCollector
from ..collectors.ai_metrics_collector import AIMetricsCollector
from ..collectors.scraping_metrics_collector import ScrapingMetricsCollector
from ..collectors.rule_evaluation_metrics_collector import RuleEvaluationMetricsCollector
from ..exporters.prometheus_exporter import PrometheusExporter
from ..loggers.structured_logger import StructuredLogger
from ..health.health_checker import HealthChecker


class MonitoringService:
    """
    Centralized monitoring service following Facade pattern.
    Provides simple interface to complex monitoring subsystem.
    """

    def __init__(self, enable_json_logging: bool = False):
        """
        Initialize monitoring service.

        Args:
            enable_json_logging: Whether to enable JSON logging format
        """
        # Initialize collectors
        self._system_collector = SystemMetricsCollector()
        self._app_collector = ApplicationMetricsCollector()
        self._ai_collector = AIMetricsCollector()
        self._scraping_collector = ScrapingMetricsCollector()
        self._rule_evaluation_collector = RuleEvaluationMetricsCollector()

        # Initialize exporter
        self._exporter = PrometheusExporter()
        self._exporter.register_collector(self._system_collector)
        self._exporter.register_collector(self._app_collector)
        self._exporter.register_collector(self._ai_collector)
        self._exporter.register_collector(self._scraping_collector)
        self._exporter.register_collector(self._rule_evaluation_collector)

        # Initialize loggers
        self._app_logger = StructuredLogger('app', enable_json_logging)
        self._ai_logger = StructuredLogger('ai', enable_json_logging)
        self._ingestion_logger = StructuredLogger('ingestion', enable_json_logging)

        # Initialize health checker
        self._health_checker = HealthChecker()

    # Metrics methods
    def get_metrics(self) -> str:
        """Get all metrics in Prometheus format."""
        return self._exporter.export()

    def record_request(self) -> None:
        """Record an HTTP request."""
        self._app_collector.increment_requests()

    def record_error(self) -> None:
        """Record an error."""
        self._app_collector.increment_errors()

    def increment_active_requests(self) -> None:
        """Increment active requests counter."""
        self._app_collector.increment_active_requests()

    def decrement_active_requests(self) -> None:
        """Decrement active requests counter."""
        self._app_collector.decrement_active_requests()

    def record_ai_inference(self, duration: float, success: bool = True,
                           input_tokens: int = 0, output_tokens: int = 0) -> None:
        """Record an AI inference event."""
        self._ai_collector.record_inference(duration, success, input_tokens, output_tokens)

    def record_vector_search(self, duration: float, results_count: int = 0) -> None:
        """Record a vector search event."""
        self._ai_collector.record_vector_search(duration, results_count)

    # Scraping/Ingestion metrics methods
    def record_missed_iteration(self, count: int = 1) -> None:
        """Record one or more missed scraping iterations."""
        self._scraping_collector.increment_missed_iterations(count)
        metric = self._exporter.get_metric('scraping_missed_iterations')
        if metric:
            metric.inc(count)

    def record_skipped_iteration(self, count: int = 1) -> None:
        """Record one or more skipped scraping iterations."""
        self._scraping_collector.increment_skipped_iterations(count)
        metric = self._exporter.get_metric('scraping_skipped_iterations')
        if metric:
            metric.inc(count)

    def record_tardy_scrape(self, count: int = 1) -> None:
        """Record one or more tardy scrapes (started late)."""
        self._scraping_collector.increment_tardy_scrapes(count)
        metric = self._exporter.get_metric('scraping_tardy_scrapes')
        if metric:
            metric.inc(count)

    def record_reload_failure(self, count: int = 1) -> None:
        """Record one or more configuration reload failures."""
        self._scraping_collector.increment_reload_failures(count)
        metric = self._exporter.get_metric('scraping_reload_failures')
        if metric:
            metric.inc(count)

    def record_skipped_scrape(self, count: int = 1) -> None:
        """Record one or more skipped individual scrapes."""
        self._scraping_collector.increment_skipped_scrapes(count)
        metric = self._exporter.get_metric('scraping_skipped_scrapes')
        if metric:
            metric.inc(count)

    def record_iteration_start(self) -> None:
        """Record the start of a scraping iteration."""
        self._scraping_collector.record_iteration_start()
        metric = self._exporter.get_metric('scraping_iterations_total')
        if metric:
            metric.inc()

    def record_scrape_complete(self, duration_seconds: float, success: bool = True) -> None:
        """Record completion of a scrape operation."""
        self._scraping_collector.record_scrape_complete(duration_seconds, success)
        if success:
            metric = self._exporter.get_metric('scraping_successful_scrapes')
            if metric:
                metric.inc()

    def set_scraping_interval(self, seconds: int) -> None:
        """Set the expected interval between scraping iterations."""
        self._scraping_collector.set_expected_interval(seconds)

    def get_scraping_health(self) -> Dict[str, Any]:
        """Get current health status of scraping operations."""
        return self._scraping_collector.get_health_status()

    # Rule Evaluation and System Status metrics methods
    def record_rule_evaluation(self, duration_seconds: float) -> None:
        """Record a rule evaluation duration."""
        self._rule_evaluation_collector.record_rule_evaluation(duration_seconds)

    def record_http_request_duration(self, duration_seconds: float) -> None:
        """Record an HTTP request duration."""
        self._rule_evaluation_collector.record_http_request_duration(duration_seconds)

    def record_rule_evaluator_iteration(self, duration_seconds: float = None) -> None:
        """Record a rule evaluator iteration."""
        if duration_seconds:
            self._rule_evaluation_collector.record_rule_evaluator_iteration(duration_seconds)
        else:
            self._rule_evaluation_collector.increment_rule_evaluator_iteration()
        metric = self._exporter.get_metric('rule_evaluator_iterations')
        if metric:
            metric.inc()

    def set_system_down(self, is_down: bool = True) -> None:
        """Set system down status."""
        self._rule_evaluation_collector.set_system_down(is_down)

    def set_system_up(self) -> None:
        """Mark system as up/healthy."""
        self._rule_evaluation_collector.set_system_up()

    def is_system_down(self) -> bool:
        """Check if system is currently down."""
        return self._rule_evaluation_collector.is_system_down()

    def get_rule_evaluation_health(self) -> Dict[str, Any]:
        """Get current health status of rule evaluation system."""
        return self._rule_evaluation_collector.get_health_status()

    # Logging methods
    def log_info(self, message: str, logger_type: str = 'app', **kwargs) -> None:
        """Log info message."""
        logger = self._get_logger(logger_type)
        logger.info(message, **kwargs)

    def log_error(self, message: str, logger_type: str = 'app', exc_info: bool = False, **kwargs) -> None:
        """Log error message."""
        logger = self._get_logger(logger_type)
        logger.error(message, exc_info=exc_info, **kwargs)

    def log_warning(self, message: str, logger_type: str = 'app', **kwargs) -> None:
        """Log warning message."""
        logger = self._get_logger(logger_type)
        logger.warning(message, **kwargs)

    # Health check methods
    def check_health(self) -> Dict[str, Any]:
        """Check health of all components."""
        return self._health_checker.check_all()

    def register_health_checker(self, checker) -> None:
        """Register a health checker."""
        self._health_checker.register_checker(checker)

    # Helper methods
    def _get_logger(self, logger_type: str) -> ILogger:
        """Get logger by type."""
        loggers = {
            'app': self._app_logger,
            'ai': self._ai_logger,
            'ingestion': self._ingestion_logger,
        }
        return loggers.get(logger_type, self._app_logger)

    # Getters for direct access
    @property
    def system_collector(self) -> SystemMetricsCollector:
        """Get system metrics collector."""
        return self._system_collector

    @property
    def app_collector(self) -> ApplicationMetricsCollector:
        """Get application metrics collector."""
        return self._app_collector

    @property
    def ai_collector(self) -> AIMetricsCollector:
        """Get AI metrics collector."""
        return self._ai_collector

    @property
    def scraping_collector(self) -> ScrapingMetricsCollector:
        """Get scraping metrics collector."""
        return self._scraping_collector

    @property
    def rule_evaluation_collector(self) -> RuleEvaluationMetricsCollector:
        """Get rule evaluation metrics collector."""
        return self._rule_evaluation_collector

    @property
    def exporter(self) -> PrometheusExporter:
        """Get metrics exporter."""
        return self._exporter

    @property
    def app_logger(self) -> ILogger:
        """Get application logger."""
        return self._app_logger

    @property
    def ai_logger(self) -> ILogger:
        """Get AI logger."""
        return self._ai_logger

    @property
    def ingestion_logger(self) -> ILogger:
        """Get ingestion logger."""
        return self._ingestion_logger


# Global singleton instance
_monitoring_service: Optional[MonitoringService] = None


def get_monitoring_service() -> MonitoringService:
    """Get the global monitoring service instance."""
    global _monitoring_service
    if _monitoring_service is None:
        _monitoring_service = MonitoringService()
    return _monitoring_service
