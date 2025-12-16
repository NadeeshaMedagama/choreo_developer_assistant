"""
Metrics Collector Interface - Single Responsibility Principle
Each collector is responsible for one type of metrics.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any


class IMetricsCollector(ABC):
    """Interface for metrics collection."""

    @abstractmethod
    def collect(self) -> Dict[str, Any]:
        """Collect metrics and return as dictionary."""
        pass

    @abstractmethod
    def get_metric_names(self) -> list:
        """Get list of metric names this collector provides."""
        pass


class IMetricsExporter(ABC):
    """Interface for exporting metrics to monitoring systems."""

    @abstractmethod
    def export(self, metrics: Dict[str, Any]) -> str:
        """Export metrics in the appropriate format."""
        pass

    @abstractmethod
    def register_collector(self, collector: IMetricsCollector) -> None:
        """Register a metrics collector."""
        pass

