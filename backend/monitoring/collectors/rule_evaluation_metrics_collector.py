"""
Rule Evaluation Metrics Collector - Single Responsibility
Collects rule evaluation and system status metrics.
"""
from typing import Dict, Any
from datetime import datetime
from ..interfaces.metrics_interface import IMetricsCollector


class RuleEvaluationMetricsCollector(IMetricsCollector):
    """Collects rule evaluation performance and system status metrics."""
    
    def __init__(self):
        """Initialize rule evaluation metrics collector."""
        self._metric_names = [
            'rule_evaluation_duration_seconds',
            'rule_evaluation_duration_avg_seconds',
            'http_request_duration_seconds',
            'http_request_duration_avg_seconds',
            'rule_evaluator_iterations_total',
            'system_currently_down',
        ]
        
        # Rule evaluation metrics
        self._rule_eval_durations = []
        self._max_duration_samples = 100  # Keep last 100 samples
        self._last_rule_eval_duration = 0.0
        
        # HTTP request metrics
        self._http_request_durations = []
        self._last_http_duration = 0.0
        
        # Rule evaluator iterations
        self._rule_evaluator_iterations = 0
        
        # System status
        self._system_down = False
        self._downtime_start = None
        self._total_downtime_seconds = 0.0
    
    def collect(self) -> Dict[str, Any]:
        """
        Collect rule evaluation and status metrics.
        
        Returns:
            Dictionary of metric names and values
        """
        # Calculate average rule evaluation duration
        avg_rule_duration = 0.0
        if self._rule_eval_durations:
            avg_rule_duration = sum(self._rule_eval_durations) / len(self._rule_eval_durations)
        
        # Calculate average HTTP request duration
        avg_http_duration = 0.0
        if self._http_request_durations:
            avg_http_duration = sum(self._http_request_durations) / len(self._http_request_durations)
        
        return {
            'rule_evaluation_duration_seconds': self._last_rule_eval_duration,
            'rule_evaluation_duration_avg_seconds': avg_rule_duration,
            'http_request_duration_seconds': self._last_http_duration,
            'http_request_duration_avg_seconds': avg_http_duration,
            'rule_evaluator_iterations_total': self._rule_evaluator_iterations,
            'system_currently_down': 1.0 if self._system_down else 0.0,
        }
    
    def get_metric_names(self) -> list:
        """Get list of metric names."""
        return self._metric_names.copy()
    
    # Rule evaluation methods
    
    def record_rule_evaluation(self, duration_seconds: float) -> None:
        """
        Record a rule evaluation duration.
        
        Args:
            duration_seconds: Time taken to evaluate rules in seconds
        """
        self._last_rule_eval_duration = duration_seconds
        self._rule_eval_durations.append(duration_seconds)
        
        # Keep only last N samples to prevent unbounded growth
        if len(self._rule_eval_durations) > self._max_duration_samples:
            self._rule_eval_durations.pop(0)
    
    def get_avg_rule_evaluation_duration(self) -> float:
        """
        Get average rule evaluation duration.
        
        Returns:
            Average duration in seconds
        """
        if not self._rule_eval_durations:
            return 0.0
        return sum(self._rule_eval_durations) / len(self._rule_eval_durations)
    
    # HTTP request duration methods
    
    def record_http_request_duration(self, duration_seconds: float) -> None:
        """
        Record an HTTP request duration.
        
        Args:
            duration_seconds: Time taken for HTTP request in seconds
        """
        self._last_http_duration = duration_seconds
        self._http_request_durations.append(duration_seconds)
        
        # Keep only last N samples
        if len(self._http_request_durations) > self._max_duration_samples:
            self._http_request_durations.pop(0)
    
    def get_avg_http_request_duration(self) -> float:
        """
        Get average HTTP request duration.
        
        Returns:
            Average duration in seconds
        """
        if not self._http_request_durations:
            return 0.0
        return sum(self._http_request_durations) / len(self._http_request_durations)
    
    # Rule evaluator iteration methods
    
    def increment_rule_evaluator_iteration(self, count: int = 1) -> None:
        """
        Increment rule evaluator iteration counter.
        
        Args:
            count: Number of iterations to add (default 1)
        """
        self._rule_evaluator_iterations += count
    
    def record_rule_evaluator_iteration(self, duration_seconds: float) -> None:
        """
        Record a complete rule evaluator iteration.
        
        Args:
            duration_seconds: Duration of the iteration
        """
        self.increment_rule_evaluator_iteration()
        self.record_rule_evaluation(duration_seconds)
    
    # System status methods
    
    def set_system_down(self, is_down: bool = True) -> None:
        """
        Set system down status.
        
        Args:
            is_down: True if system is down, False if up
        """
        if is_down and not self._system_down:
            # System just went down
            self._system_down = True
            self._downtime_start = datetime.now()
        elif not is_down and self._system_down:
            # System came back up
            self._system_down = False
            if self._downtime_start:
                downtime = (datetime.now() - self._downtime_start).total_seconds()
                self._total_downtime_seconds += downtime
                self._downtime_start = None
    
    def set_system_up(self) -> None:
        """Mark system as up/healthy."""
        self.set_system_down(False)
    
    def is_system_down(self) -> bool:
        """
        Check if system is currently down.
        
        Returns:
            True if system is down, False otherwise
        """
        return self._system_down
    
    def get_total_downtime(self) -> float:
        """
        Get total downtime in seconds.
        
        Returns:
            Total downtime in seconds
        """
        total = self._total_downtime_seconds
        
        # Add current downtime if system is down
        if self._system_down and self._downtime_start:
            total += (datetime.now() - self._downtime_start).total_seconds()
        
        return total
    
    def get_health_status(self) -> Dict[str, Any]:
        """
        Get current health status of rule evaluation system.
        
        Returns:
            Dictionary with health metrics and status
        """
        avg_rule_duration = self.get_avg_rule_evaluation_duration()
        avg_http_duration = self.get_avg_http_request_duration()
        
        # Consider system unhealthy if:
        # - Average rule evaluation > 5 seconds
        # - Average HTTP request > 3 seconds
        # - System is currently down
        is_healthy = (
            avg_rule_duration < 5.0 and
            avg_http_duration < 3.0 and
            not self._system_down
        )
        
        return {
            'healthy': is_healthy,
            'avg_rule_evaluation_duration': avg_rule_duration,
            'avg_http_request_duration': avg_http_duration,
            'total_iterations': self._rule_evaluator_iterations,
            'system_down': self._system_down,
            'total_downtime_seconds': self.get_total_downtime(),
            'metrics': {
                'last_rule_eval_duration': self._last_rule_eval_duration,
                'last_http_duration': self._last_http_duration,
                'rule_eval_samples': len(self._rule_eval_durations),
                'http_samples': len(self._http_request_durations),
            }
        }
    
    def reset_counters(self) -> None:
        """Reset all counters (useful for testing or periodic resets)."""
        self._rule_eval_durations.clear()
        self._http_request_durations.clear()
        self._last_rule_eval_duration = 0.0
        self._last_http_duration = 0.0
        self._rule_evaluator_iterations = 0
        self._system_down = False
        self._downtime_start = None
        self._total_downtime_seconds = 0.0

