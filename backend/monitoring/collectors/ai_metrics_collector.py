"""
AI Metrics Collector - Single Responsibility
Collects only AI/ML-specific metrics.
"""
from typing import Dict, Any, List
from ..interfaces.metrics_interface import IMetricsCollector


class AIMetricsCollector(IMetricsCollector):
    """Collects AI/ML model performance metrics."""
    
    def __init__(self):
        """Initialize AI metrics collector."""
        self._metric_names = [
            'ai_inference_duration_seconds',
            'ai_requests_total',
            'ai_tokens_total',
            'ai_payload_size_bytes',
            'vector_search_duration_seconds',
            'vector_searches_total'
        ]
        self._inference_count = 0
        self._inference_errors = 0
        self._total_tokens_input = 0
        self._total_tokens_output = 0
        self._vector_search_count = 0
    
    def collect(self) -> Dict[str, Any]:
        """
        Collect AI metrics.
        
        Returns:
            Dictionary of metric names and values
        """
        return {
            'ai_requests_total': self._inference_count,
            'ai_requests_errors': self._inference_errors,
            'ai_tokens_input': self._total_tokens_input,
            'ai_tokens_output': self._total_tokens_output,
            'vector_searches_total': self._vector_search_count,
        }
    
    def get_metric_names(self) -> list:
        """Get list of metric names."""
        return self._metric_names.copy()
    
    def record_inference(self, duration: float, success: bool = True, 
                        input_tokens: int = 0, output_tokens: int = 0) -> None:
        """Record an AI inference event."""
        self._inference_count += 1
        if not success:
            self._inference_errors += 1
        self._total_tokens_input += input_tokens
        self._total_tokens_output += output_tokens
    
    def record_vector_search(self, duration: float, results_count: int = 0) -> None:
        """Record a vector search event."""
        self._vector_search_count += 1

