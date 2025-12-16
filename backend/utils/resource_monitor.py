"""
Resource monitoring utilities for preventing memory overload during processing.
"""
import time
import os
from typing import Optional

from .logger import get_logger

logger = get_logger(__name__)

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    logger.warning("psutil not installed. Install with: pip install psutil")


def get_memory_usage_percent() -> float:
    """
    Get current system memory usage as a percentage.

    Returns:
        Memory usage percentage (0-100)

    Raises:
        RuntimeError if psutil is not available
    """
    if not PSUTIL_AVAILABLE:
        raise RuntimeError("psutil required for memory monitoring. Install with: pip install psutil")

    return psutil.virtual_memory().percent


def get_memory_usage_mb() -> float:
    """
    Get current process memory usage in MB.

    Returns:
        Memory usage in megabytes
    """
    if not PSUTIL_AVAILABLE:
        return 0.0

    try:
        process = psutil.Process(os.getpid())
        mem_info = process.memory_info()
        return mem_info.rss / 1024 / 1024
    except Exception as e:
        logger.warning(f"Could not get process memory: {e}")
        return 0.0


def check_memory_available(threshold_percent: float = 85.0) -> bool:
    """
    Check if memory usage is below the threshold.

    Args:
        threshold_percent: Maximum acceptable memory usage (0-100)

    Returns:
        True if memory usage is below threshold, False otherwise
    """
    if not PSUTIL_AVAILABLE:
        logger.warning("psutil not available, skipping memory check")
        return True

    try:
        current_usage = get_memory_usage_percent()
        return current_usage < threshold_percent
    except Exception as e:
        logger.warning(f"Memory check failed: {e}")
        return True  # Continue processing if check fails


def wait_for_memory(
    threshold_percent: float = 85.0,
    check_interval: float = 2.0,
    timeout: Optional[float] = 60.0,
    raise_on_timeout: bool = False
) -> bool:
    """
    Wait until memory usage drops below threshold or timeout expires.

    Args:
        threshold_percent: Maximum acceptable memory usage (0-100)
        check_interval: Seconds to wait between checks
        timeout: Maximum seconds to wait (None = wait forever)
        raise_on_timeout: If True, raise RuntimeError on timeout; if False, return False

    Returns:
        True if memory is available, False if timeout expired (when raise_on_timeout=False)

    Raises:
        RuntimeError if timeout expires and raise_on_timeout=True
    """
    if not PSUTIL_AVAILABLE:
        logger.warning("psutil not available, skipping memory wait")
        return True

    start_time = time.time()

    while not check_memory_available(threshold_percent):
        current_usage = get_memory_usage_percent()
        elapsed = time.time() - start_time

        logger.warning(
            f"⚠️  Memory usage high: {current_usage:.1f}% "
            f"(threshold: {threshold_percent}%) - waiting... [{elapsed:.1f}s elapsed]"
        )

        # Check timeout
        if timeout is not None and elapsed > timeout:
            error_msg = (
                f"Memory usage above {threshold_percent}% for more than {timeout} seconds. "
                f"Current usage: {current_usage:.1f}%"
            )

            if raise_on_timeout:
                raise RuntimeError(error_msg)
            else:
                logger.error(error_msg)
                return False

        # Wait before checking again
        time.sleep(check_interval)

    return True


def force_garbage_collection():
    """
    Force garbage collection and log memory before/after.
    """
    import gc

    if PSUTIL_AVAILABLE:
        before = get_memory_usage_mb()
        gc.collect()
        after = get_memory_usage_mb()
        freed = before - after

        if freed > 0:
            logger.info(f"🧹 Garbage collection freed {freed:.1f}MB (was {before:.1f}MB, now {after:.1f}MB)")
        else:
            logger.debug(f"Garbage collection completed ({after:.1f}MB)")
    else:
        gc.collect()
        logger.debug("Garbage collection completed")


class MemoryMonitor:
    """
    Context manager for monitoring memory during operations.
    """

    def __init__(
        self,
        operation_name: str = "operation",
        threshold_percent: float = 85.0,
        check_interval: float = 2.0,
        auto_gc: bool = True
    ):
        """
        Initialize memory monitor.

        Args:
            operation_name: Name of operation being monitored (for logging)
            threshold_percent: Memory threshold to warn/wait at
            check_interval: Seconds between memory checks
            auto_gc: If True, run garbage collection on exit
        """
        self.operation_name = operation_name
        self.threshold_percent = threshold_percent
        self.check_interval = check_interval
        self.auto_gc = auto_gc
        self.start_memory = None
        self.start_time = None

    def __enter__(self):
        """Start monitoring."""
        self.start_time = time.time()

        if PSUTIL_AVAILABLE:
            self.start_memory = get_memory_usage_mb()
            memory_percent = get_memory_usage_percent()
            logger.info(
                f"▶️  Starting {self.operation_name} "
                f"[Memory: {self.start_memory:.1f}MB / {memory_percent:.1f}%]"
            )
        else:
            logger.info(f"▶️  Starting {self.operation_name}")

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop monitoring and report."""
        elapsed = time.time() - self.start_time

        if PSUTIL_AVAILABLE:
            end_memory = get_memory_usage_mb()
            memory_percent = get_memory_usage_percent()
            memory_delta = end_memory - (self.start_memory or 0)

            logger.info(
                f"⏹️  Completed {self.operation_name} in {elapsed:.1f}s "
                f"[Memory: {end_memory:.1f}MB / {memory_percent:.1f}% "
                f"(Δ{memory_delta:+.1f}MB)]"
            )
        else:
            logger.info(f"⏹️  Completed {self.operation_name} in {elapsed:.1f}s")

        if self.auto_gc:
            force_garbage_collection()

    def check_and_wait(self, timeout: Optional[float] = 30.0) -> bool:
        """
        Check memory and wait if needed.

        Args:
            timeout: Maximum seconds to wait

        Returns:
            True if memory is available, False if timeout
        """
        return wait_for_memory(
            threshold_percent=self.threshold_percent,
            check_interval=self.check_interval,
            timeout=timeout,
            raise_on_timeout=False
        )

