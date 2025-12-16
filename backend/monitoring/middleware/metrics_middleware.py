"""
Metrics Middleware - Dependency Injection
Uses MonitoringService for loose coupling.
"""
import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from ..services.monitoring_service import get_monitoring_service


class MetricsMiddleware(BaseHTTPMiddleware):
    """
    Middleware to track HTTP request metrics.
    Follows Dependency Inversion - depends on MonitoringService abstraction.
    """

    def __init__(self, app, monitoring_service=None):
        """
        Initialize metrics middleware.

        Args:
            app: FastAPI application
            monitoring_service: Optional monitoring service (injected dependency)
        """
        super().__init__(app)
        self._monitoring = monitoring_service or get_monitoring_service()

    async def dispatch(self, request: Request, call_next):
        """Process request and track metrics."""
        # Skip metrics endpoint itself
        if request.url.path == "/metrics":
            return await call_next(request)

        # Track active requests
        self._monitoring.increment_active_requests()

        # Track request timing
        start_time = time.time()

        try:
            response = await call_next(request)

            # Calculate latency
            latency = time.time() - start_time

            # Record metrics
            self._monitoring.record_request()

            # Log request
            self._monitoring.log_info(
                f"Request processed",
                logger_type='app',
                method=request.method,
                path=request.url.path,
                status=response.status_code,
                duration=f"{latency:.3f}s"
            )

            return response

        except Exception as e:
            # Record error
            self._monitoring.record_error()
            self._monitoring.log_error(
                f"Request failed: {str(e)}",
                logger_type='app',
                exc_info=True,
                method=request.method,
                path=request.url.path
            )
            raise
        finally:
            self._monitoring.decrement_active_requests()

