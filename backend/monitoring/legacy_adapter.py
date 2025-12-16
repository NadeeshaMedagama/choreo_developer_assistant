"""
Legacy Adapter - Adapter Pattern
Provides backward compatibility with old monitoring API.
"""
from .services.monitoring_service import get_monitoring_service
from .middleware.metrics_middleware import MetricsMiddleware


# Get the global monitoring service
_monitoring = get_monitoring_service()


def metrics_middleware():
    """Return the metrics middleware class (legacy API)."""
    return MetricsMiddleware


def record_ai_inference(model: str, endpoint: str, duration: float, status: str = "success",
                       input_tokens: int = 0, output_tokens: int = 0,
                       request_size: int = 0, response_size: int = 0):
    """Record AI inference metrics (legacy API)."""
    success = (status == "success")
    _monitoring.record_ai_inference(duration, success, input_tokens, output_tokens)
    _monitoring.log_info(
        f"AI inference completed",
        logger_type='ai',
        model=model,
        endpoint=endpoint,
        duration=f"{duration:.3f}s",
        status=status
    )


def record_vector_search(operation: str, duration: float, status: str = "success", results_count: int = 0):
    """Record vector database search metrics (legacy API)."""
    _monitoring.record_vector_search(duration, results_count)
    _monitoring.log_info(
        f"Vector search completed",
        logger_type='app',
        operation=operation,
        duration=f"{duration:.3f}s",
        results=results_count
    )


def record_github_ingestion(repo: str, duration: float, status: str = "success", files_processed: dict = None):
    """Record GitHub ingestion metrics (legacy API)."""
    _monitoring.log_info(
        f"GitHub ingestion completed",
        logger_type='ingestion',
        repo=repo,
        duration=f"{duration:.3f}s",
        status=status,
        files_processed=files_processed or {}
    )


def record_error(error_type: str, endpoint: str):
    """Record an error occurrence (legacy API)."""
    _monitoring.record_error()
    _monitoring.log_error(
        f"Error occurred: {error_type}",
        logger_type='app',
        error_type=error_type,
        endpoint=endpoint
    )


def record_health_status(component: str, is_healthy: bool):
    """Record health check status for a component (legacy API)."""
    status = "healthy" if is_healthy else "unhealthy"
    _monitoring.log_info(
        f"Health check: {component} is {status}",
        logger_type='app',
        component=component,
        status=status
    )

