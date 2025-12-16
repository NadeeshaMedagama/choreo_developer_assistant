"""
Scraping Metrics Integration Helper

This module provides easy-to-use decorators and context managers
for tracking scraping metrics in your ingestion workflows.

Usage Examples:

1. Track entire scraping iteration:
    ```python
    from monitoring.helpers.scraping_metrics import track_scraping_iteration
    
    @track_scraping_iteration(monitoring_service)
    def run_scraping_job():
        # Your scraping logic here
        pass
    ```

2. Use context manager for granular control:
    ```python
    from monitoring.helpers.scraping_metrics import ScrapingIterationTracker
    
    with ScrapingIterationTracker(monitoring_service) as tracker:
        try:
            # Your scraping logic
            do_scraping()
            tracker.mark_success(duration=123.45)
        except Exception as e:
            tracker.mark_failure()
            raise
    ```

3. Track individual scrape operations:
    ```python
    from monitoring.helpers.scraping_metrics import track_scrape
    
    @track_scrape(monitoring_service)
    def scrape_single_repo(repo_url):
        # Scrape logic
        pass
    ```
"""

import time
from typing import Optional, Callable, Any
from functools import wraps
from contextlib import contextmanager


class ScrapingIterationTracker:
    """Context manager for tracking scraping iterations."""
    
    def __init__(self, monitoring_service):
        """
        Initialize iteration tracker.
        
        Args:
            monitoring_service: MonitoringService instance
        """
        self.monitoring = monitoring_service
        self.start_time = None
        self.success = False
    
    def __enter__(self):
        """Start tracking an iteration."""
        self.start_time = time.time()
        self.monitoring.record_iteration_start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Complete tracking, record results."""
        duration = time.time() - self.start_time
        
        if exc_type is None and self.success:
            # Successful completion
            self.monitoring.record_scrape_complete(duration, success=True)
        else:
            # Failed or not marked as success
            self.monitoring.record_scrape_complete(duration, success=False)
        
        return False  # Don't suppress exceptions
    
    def mark_success(self, duration: Optional[float] = None):
        """Mark this iteration as successful."""
        self.success = True
        if duration is not None:
            self.monitoring.record_scrape_complete(duration, success=True)
    
    def mark_failure(self):
        """Mark this iteration as failed."""
        self.success = False
    
    def record_missed(self, count: int = 1):
        """Record missed iteration(s)."""
        self.monitoring.record_missed_iteration(count)
    
    def record_skipped(self, count: int = 1):
        """Record skipped iteration(s)."""
        self.monitoring.record_skipped_iteration(count)
    
    def record_tardy(self, count: int = 1):
        """Record tardy scrape(s)."""
        self.monitoring.record_tardy_scrape(count)
    
    def record_reload_failure(self, count: int = 1):
        """Record reload failure(s)."""
        self.monitoring.record_reload_failure(count)
    
    def record_skipped_scrape(self, count: int = 1):
        """Record skipped scrape(s)."""
        self.monitoring.record_skipped_scrape(count)


def track_scraping_iteration(monitoring_service):
    """
    Decorator to automatically track a scraping iteration.
    
    Args:
        monitoring_service: MonitoringService instance
    
    Usage:
        @track_scraping_iteration(monitoring)
        def run_scraping_job():
            # Your scraping logic
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            with ScrapingIterationTracker(monitoring_service) as tracker:
                try:
                    result = func(*args, **kwargs)
                    tracker.mark_success()
                    return result
                except Exception as e:
                    tracker.mark_failure()
                    raise
        return wrapper
    return decorator


def track_scrape(monitoring_service):
    """
    Decorator to track individual scrape operations.
    
    Args:
        monitoring_service: MonitoringService instance
    
    Usage:
        @track_scrape(monitoring)
        def scrape_repository(repo_url):
            # Scraping logic
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                monitoring_service.record_scrape_complete(duration, success=True)
                return result
            except Exception as e:
                duration = time.time() - start_time
                monitoring_service.record_scrape_complete(duration, success=False)
                monitoring_service.record_skipped_scrape()
                raise
        return wrapper
    return decorator


@contextmanager
def track_reload_operation(monitoring_service):
    """
    Context manager for tracking configuration reload operations.
    
    Usage:
        with track_reload_operation(monitoring):
            reload_configuration()
    """
    try:
        yield
    except Exception as e:
        monitoring_service.record_reload_failure()
        raise


class ScrapingMetricsHelper:
    """
    Helper class providing convenient methods for recording scraping metrics.
    """
    
    def __init__(self, monitoring_service):
        """
        Initialize helper.
        
        Args:
            monitoring_service: MonitoringService instance
        """
        self.monitoring = monitoring_service
    
    def iteration(self) -> ScrapingIterationTracker:
        """
        Get a new iteration tracker.
        
        Returns:
            ScrapingIterationTracker context manager
        """
        return ScrapingIterationTracker(self.monitoring)
    
    def missed(self, count: int = 1):
        """Record missed iteration(s)."""
        self.monitoring.record_missed_iteration(count)
    
    def skipped(self, count: int = 1):
        """Record skipped iteration(s)."""
        self.monitoring.record_skipped_iteration(count)
    
    def tardy(self, count: int = 1):
        """Record tardy scrape(s)."""
        self.monitoring.record_tardy_scrape(count)
    
    def reload_failed(self, count: int = 1):
        """Record reload failure(s)."""
        self.monitoring.record_reload_failure(count)
    
    def skipped_scrape(self, count: int = 1):
        """Record skipped scrape(s)."""
        self.monitoring.record_skipped_scrape(count)
    
    def set_interval(self, seconds: int):
        """Set expected scraping interval."""
        self.monitoring.set_scraping_interval(seconds)
    
    def health(self) -> dict:
        """Get scraping health status."""
        return self.monitoring.get_scraping_health()

