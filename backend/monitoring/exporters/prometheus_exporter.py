"""
Prometheus Exporter - Open/Closed Principle
Export metrics to Prometheus format without modifying collectors.
"""
from prometheus_client import Counter, Histogram, Gauge, generate_latest, REGISTRY
from typing import Dict, Any, List
from ..interfaces.metrics_interface import IMetricsExporter, IMetricsCollector


class PrometheusExporter(IMetricsExporter):
    """Exports metrics in Prometheus format."""
    
    def __init__(self):
        """Initialize Prometheus exporter."""
        self._collectors: List[IMetricsCollector] = []
        self._prometheus_metrics = self._initialize_prometheus_metrics()
    
    def _initialize_prometheus_metrics(self) -> Dict[str, Any]:
        """Initialize Prometheus metric objects."""
        return {
            # System metrics
            'cpu_usage': Gauge('cpu_usage_percent', 'CPU usage percentage'),
            'memory_usage': Gauge('memory_usage_bytes', 'Memory usage in bytes'),
            'memory_usage_percent': Gauge('memory_usage_percent', 'Memory usage percentage'),
            'disk_usage': Gauge('disk_usage_bytes', 'Disk usage in bytes'),
            'disk_usage_percent': Gauge('disk_usage_percent', 'Disk usage percentage'),
            'process_count': Gauge('process_count', 'Number of running processes'),
            
            # Application metrics
            'request_count': Counter('http_requests_total', 'Total HTTP requests', 
                                    ['method', 'endpoint', 'status']),
            'request_latency': Histogram('http_request_duration_seconds', 'HTTP request latency',
                                        ['method', 'endpoint']),
            'active_requests': Gauge('http_requests_active', 'Number of active HTTP requests'),
            'error_count': Counter('errors_total', 'Total errors', ['type', 'endpoint']),
            
            # AI metrics
            'ai_inference_time': Histogram('ai_inference_duration_seconds', 'AI model inference time',
                                          ['model', 'endpoint']),
            'ai_request_count': Counter('ai_requests_total', 'Total AI inference requests',
                                       ['model', 'endpoint', 'status']),
            'ai_token_count': Counter('ai_tokens_total', 'Total tokens processed', ['type']),
            
            # Vector DB metrics
            'vector_search_time': Histogram('vector_search_duration_seconds', 'Vector search query time',
                                           ['operation']),
            'vector_search_count': Counter('vector_searches_total', 'Total vector searches',
                                          ['operation', 'status']),
            
            # Health metrics
            'health_status': Gauge('health_check_status', 'Health check status (1=healthy, 0=unhealthy)',
                                  ['component']),

            # Scraping/Ingestion metrics
            'scraping_missed_iterations': Counter('scraping_missed_iterations_total',
                                                 'Total number of missed scraping iterations'),
            'scraping_skipped_iterations': Counter('scraping_skipped_iterations_total',
                                                  'Total number of skipped scraping iterations'),
            'scraping_tardy_scrapes': Counter('scraping_tardy_scrapes_total',
                                             'Total number of tardy scrapes (started late)'),
            'scraping_reload_failures': Counter('scraping_reload_failures_total',
                                               'Total number of configuration reload failures'),
            'scraping_skipped_scrapes': Counter('scraping_skipped_scrapes_total',
                                               'Total number of skipped individual scrapes'),
            'scraping_iterations_total': Counter('scraping_iterations_total',
                                                'Total number of scraping iterations'),
            'scraping_successful_scrapes': Counter('scraping_successful_scrapes_total',
                                                  'Total number of successful scrapes'),
            'scraping_last_scrape_timestamp': Gauge('scraping_last_scrape_timestamp',
                                                   'Timestamp of last scrape (Unix time)'),
            'scraping_last_scrape_duration': Gauge('scraping_last_scrape_duration_seconds',
                                                  'Duration of last scrape in seconds'),
            'scraping_iteration_delay': Gauge('scraping_iteration_delay_seconds',
                                             'Time since last iteration in seconds'),

            # Rule Evaluation and System Status metrics (NEW)
            'rule_evaluation_duration': Gauge('rule_evaluation_duration_seconds',
                                              'Last rule evaluation duration in seconds'),
            'rule_evaluation_duration_avg': Gauge('rule_evaluation_duration_avg_seconds',
                                                  'Average rule evaluation duration in seconds'),
            # Note: Histogram for HTTP request duration already defined above as 'request_latency'
            # We add gauges for last and average durations for convenience
            'http_request_duration_gauge': Gauge('http_request_duration_last_seconds',
                                                 'Last HTTP request duration in seconds'),
            'http_request_duration_avg': Gauge('http_request_duration_avg_seconds',
                                               'Average HTTP request duration in seconds'),
            'rule_evaluator_iterations': Counter('rule_evaluator_iterations_total',
                                                 'Total number of rule evaluator iterations'),
            'system_currently_down': Gauge('system_currently_down',
                                           'System down status (1=down, 0=up)'),
        }
    
    def register_collector(self, collector: IMetricsCollector) -> None:
        """Register a metrics collector."""
        self._collectors.append(collector)
    
    def export(self, metrics: Dict[str, Any] = None) -> str:
        """
        Export all collected metrics in Prometheus format.
        
        Args:
            metrics: Optional dict of metrics to export. If None, collects from all registered collectors.
        
        Returns:
            Prometheus-formatted metrics string
        """
        # If no metrics provided, collect from all registered collectors
        if metrics is None:
            metrics = {}
            for collector in self._collectors:
                metrics.update(collector.collect())
        
        # Update Prometheus metrics
        self._update_prometheus_metrics(metrics)
        
        # Generate Prometheus format
        return generate_latest(REGISTRY).decode('utf-8')
    
    def _update_prometheus_metrics(self, metrics: Dict[str, Any]) -> None:
        """Update Prometheus metric values."""
        # System metrics
        if 'cpu_usage_percent' in metrics:
            self._prometheus_metrics['cpu_usage'].set(metrics['cpu_usage_percent'])
        if 'memory_usage_bytes' in metrics:
            self._prometheus_metrics['memory_usage'].set(metrics['memory_usage_bytes'])
        if 'memory_usage_percent' in metrics:
            self._prometheus_metrics['memory_usage_percent'].set(metrics['memory_usage_percent'])
        if 'disk_usage_bytes' in metrics:
            self._prometheus_metrics['disk_usage'].set(metrics['disk_usage_bytes'])
        if 'disk_usage_percent' in metrics:
            self._prometheus_metrics['disk_usage_percent'].set(metrics['disk_usage_percent'])
        if 'process_count' in metrics:
            self._prometheus_metrics['process_count'].set(metrics['process_count'])
        
        # Application metrics
        if 'http_requests_active' in metrics:
            self._prometheus_metrics['active_requests'].set(metrics['http_requests_active'])

        # Scraping metrics
        if 'scraping_missed_iterations_total' in metrics:
            # Note: Counters can't be set, they need to be incremented
            # We track the delta and increment accordingly
            pass  # These are incremented directly via the collector methods

        if 'scraping_last_scrape_timestamp' in metrics:
            self._prometheus_metrics['scraping_last_scrape_timestamp'].set(metrics['scraping_last_scrape_timestamp'])

        if 'scraping_last_scrape_duration_seconds' in metrics:
            self._prometheus_metrics['scraping_last_scrape_duration'].set(metrics['scraping_last_scrape_duration_seconds'])

        if 'scraping_iteration_delay_seconds' in metrics:
            self._prometheus_metrics['scraping_iteration_delay'].set(metrics['scraping_iteration_delay_seconds'])

        # Rule Evaluation and System Status metrics
        if 'rule_evaluation_duration_seconds' in metrics:
            m = self._prometheus_metrics.get('rule_evaluation_duration')
            if m is not None:
                m.set(metrics['rule_evaluation_duration_seconds'])

        if 'rule_evaluation_duration_avg_seconds' in metrics:
            m = self._prometheus_metrics.get('rule_evaluation_duration_avg')
            if m is not None:
                m.set(metrics['rule_evaluation_duration_avg_seconds'])

        if 'http_request_duration_seconds' in metrics:
            m = self._prometheus_metrics.get('http_request_duration_gauge')
            if m is not None:
                m.set(metrics['http_request_duration_seconds'])

        if 'http_request_duration_avg_seconds' in metrics:
            m = self._prometheus_metrics.get('http_request_duration_avg')
            if m is not None:
                m.set(metrics['http_request_duration_avg_seconds'])

        if 'rule_evaluator_iterations_total' in metrics:
            # Counter value incremented via recording methods; nothing to set here.
            pass

        if 'system_currently_down' in metrics:
            m = self._prometheus_metrics.get('system_currently_down')
            if m is not None:
                m.set(metrics['system_currently_down'])

    def get_metric(self, name: str):
        """Get a Prometheus metric object by name."""
        return self._prometheus_metrics.get(name)
