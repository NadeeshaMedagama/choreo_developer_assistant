"""
Scraping Metrics Collector - Single Responsibility
Collects ingestion and scraping-specific metrics for monitoring data collection health.
"""
from typing import Dict, Any
from datetime import datetime, timedelta
from ..interfaces.metrics_interface import IMetricsCollector


class ScrapingMetricsCollector(IMetricsCollector):
    """Collects scraping/ingestion performance and health metrics."""
    
    def __init__(self):
        """Initialize scraping metrics collector."""
        self._metric_names = [
            'scraping_missed_iterations_total',
            'scraping_skipped_iterations_total',
            'scraping_tardy_scrapes_total',
            'scraping_reload_failures_total',
            'scraping_skipped_scrapes_total',
            'scraping_iterations_total',
            'scraping_successful_scrapes_total',
            'scraping_last_scrape_timestamp',
            'scraping_last_scrape_duration_seconds',
            'scraping_iteration_delay_seconds'
        ]
        
        # Counter metrics
        self._missed_iterations = 0
        self._skipped_iterations = 0
        self._tardy_scrapes = 0
        self._reload_failures = 0
        self._skipped_scrapes = 0
        self._total_iterations = 0
        self._successful_scrapes = 0
        
        # Timing metrics
        self._last_scrape_timestamp = None
        self._last_scrape_duration = 0.0
        self._expected_interval_seconds = 3600  # Default 1 hour
        self._last_iteration_timestamp = None
    
    def collect(self) -> Dict[str, Any]:
        """
        Collect scraping metrics.
        
        Returns:
            Dictionary of metric names and values
        """
        metrics = {
            'scraping_missed_iterations_total': self._missed_iterations,
            'scraping_skipped_iterations_total': self._skipped_iterations,
            'scraping_tardy_scrapes_total': self._tardy_scrapes,
            'scraping_reload_failures_total': self._reload_failures,
            'scraping_skipped_scrapes_total': self._skipped_scrapes,
            'scraping_iterations_total': self._total_iterations,
            'scraping_successful_scrapes_total': self._successful_scrapes,
            'scraping_last_scrape_duration_seconds': self._last_scrape_duration,
        }
        
        # Add timestamp if available
        if self._last_scrape_timestamp:
            metrics['scraping_last_scrape_timestamp'] = self._last_scrape_timestamp.timestamp()
        
        # Calculate iteration delay if we have timing info
        if self._last_iteration_timestamp:
            delay = (datetime.now() - self._last_iteration_timestamp).total_seconds()
            metrics['scraping_iteration_delay_seconds'] = delay
        
        return metrics
    
    def get_metric_names(self) -> list:
        """Get list of metric names."""
        return self._metric_names.copy()
    
    # Increment methods for tracking events
    
    def increment_missed_iterations(self, count: int = 1) -> None:
        """
        Increment missed iterations counter.
        A missed iteration occurs when a scheduled scrape doesn't start on time.
        
        Args:
            count: Number of iterations to add (default 1)
        """
        self._missed_iterations += count
    
    def increment_skipped_iterations(self, count: int = 1) -> None:
        """
        Increment skipped iterations counter.
        A skipped iteration occurs when a scheduled scrape is intentionally skipped.
        
        Args:
            count: Number of iterations to add (default 1)
        """
        self._skipped_iterations += count
    
    def increment_tardy_scrapes(self, count: int = 1) -> None:
        """
        Increment tardy scrapes counter.
        A tardy scrape is one that starts later than expected.
        
        Args:
            count: Number of tardy scrapes to add (default 1)
        """
        self._tardy_scrapes += count
    
    def increment_reload_failures(self, count: int = 1) -> None:
        """
        Increment reload failures counter.
        A reload failure occurs when the system fails to reload configuration or data.
        
        Args:
            count: Number of failures to add (default 1)
        """
        self._reload_failures += count
    
    def increment_skipped_scrapes(self, count: int = 1) -> None:
        """
        Increment skipped scrapes counter.
        A skipped scrape occurs when individual scraping operations are skipped.
        
        Args:
            count: Number of skipped scrapes to add (default 1)
        """
        self._skipped_scrapes += count
    
    def record_iteration_start(self) -> None:
        """
        Record the start of a scraping iteration.
        Automatically detects if this iteration is late.
        """
        now = datetime.now()
        
        # Check if this iteration is tardy
        if self._last_iteration_timestamp:
            expected_time = self._last_iteration_timestamp + timedelta(seconds=self._expected_interval_seconds)
            if now > expected_time + timedelta(seconds=60):  # Grace period of 60 seconds
                self.increment_tardy_scrapes()
        
        self._total_iterations += 1
        self._last_iteration_timestamp = now
    
    def record_scrape_complete(self, duration_seconds: float, success: bool = True) -> None:
        """
        Record completion of a scrape operation.
        
        Args:
            duration_seconds: How long the scrape took
            success: Whether the scrape was successful
        """
        self._last_scrape_timestamp = datetime.now()
        self._last_scrape_duration = duration_seconds
        
        if success:
            self._successful_scrapes += 1
    
    def record_scrape_failed(self) -> None:
        """Record a failed scrape attempt."""
        # Failed scrapes are tracked as the difference between iterations and successful scrapes
        pass
    
    def set_expected_interval(self, seconds: int) -> None:
        """
        Set the expected interval between scraping iterations.
        
        Args:
            seconds: Expected interval in seconds
        """
        self._expected_interval_seconds = seconds
    
    def get_health_status(self) -> Dict[str, Any]:
        """
        Get current health status of scraping operations.
        
        Returns:
            Dictionary with health metrics and status
        """
        total_failures = (
            self._missed_iterations + 
            self._skipped_iterations + 
            self._tardy_scrapes + 
            self._reload_failures + 
            self._skipped_scrapes
        )
        
        success_rate = 0.0
        if self._total_iterations > 0:
            success_rate = (self._successful_scrapes / self._total_iterations) * 100
        
        is_healthy = (
            success_rate >= 90.0 and  # At least 90% success rate
            self._reload_failures == 0 and  # No reload failures
            self._missed_iterations < 5  # Fewer than 5 missed iterations
        )
        
        return {
            'healthy': is_healthy,
            'success_rate_percent': success_rate,
            'total_failures': total_failures,
            'last_scrape': self._last_scrape_timestamp.isoformat() if self._last_scrape_timestamp else None,
            'metrics': {
                'missed_iterations': self._missed_iterations,
                'skipped_iterations': self._skipped_iterations,
                'tardy_scrapes': self._tardy_scrapes,
                'reload_failures': self._reload_failures,
                'skipped_scrapes': self._skipped_scrapes,
            }
        }
    
    def reset_counters(self) -> None:
        """Reset all counters (useful for testing or periodic resets)."""
        self._missed_iterations = 0
        self._skipped_iterations = 0
        self._tardy_scrapes = 0
        self._reload_failures = 0
        self._skipped_scrapes = 0
        self._total_iterations = 0
        self._successful_scrapes = 0
        self._last_scrape_timestamp = None
        self._last_scrape_duration = 0.0
        self._last_iteration_timestamp = None

