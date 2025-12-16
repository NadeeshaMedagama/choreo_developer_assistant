"""
System Metrics Collector - Single Responsibility
Collects only system-level metrics (CPU, memory, disk).
"""
import psutil
from typing import Dict, Any
from ..interfaces.metrics_interface import IMetricsCollector


class SystemMetricsCollector(IMetricsCollector):
    """Collects system infrastructure metrics."""
    
    def __init__(self):
        """Initialize system metrics collector."""
        self._metric_names = [
            'cpu_usage_percent',
            'memory_usage_bytes',
            'memory_usage_percent',
            'disk_usage_bytes',
            'disk_usage_percent',
            'process_count'
        ]
    
    def collect(self) -> Dict[str, Any]:
        """
        Collect system metrics.
        
        Returns:
            Dictionary of metric names and values
        """
        try:
            metrics = {}
            
            # CPU metrics
            metrics['cpu_usage_percent'] = psutil.cpu_percent(interval=0.1)
            
            # Memory metrics
            memory = psutil.virtual_memory()
            metrics['memory_usage_bytes'] = memory.used
            metrics['memory_usage_percent'] = memory.percent
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            metrics['disk_usage_bytes'] = disk.used
            metrics['disk_usage_percent'] = disk.percent
            
            # Process metrics
            metrics['process_count'] = len(psutil.pids())
            
            return metrics
            
        except Exception as e:
            print(f"Error collecting system metrics: {e}")
            return {}
    
    def get_metric_names(self) -> list:
        """Get list of metric names."""
        return self._metric_names.copy()

