import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
import atexit
import os

# Create .logs directory in the project root
LOG_DIR = Path(__file__).parent.parent.parent / ".logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "backend.log"

# Track created loggers to ensure cleanup
_loggers = []


def _flush_and_fsync_handler(handler):
    """Force flush and fsync a handler to disk."""
    try:
        handler.flush()
    except Exception:
        pass
    stream = getattr(handler, "stream", None)
    if stream and hasattr(stream, "fileno"):
        try:
            os.fsync(stream.fileno())
        except Exception:
            pass


def _cleanup_all_loggers():
    """Flush and close all handlers on exit."""
    for logger in _loggers:
        for handler in list(logger.handlers):
            try:
                _flush_and_fsync_handler(handler)
                handler.close()
            except Exception:
                pass


# Register cleanup on exit
atexit.register(_cleanup_all_loggers)


def get_logger(name: str, level=logging.DEBUG) -> logging.Logger:
    """Get a configured logger instance with file and console output."""
    logger = logging.getLogger(name)

    # Avoid adding duplicate handlers
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # File handler with rotation (append mode ensures persistence)
    file_handler = RotatingFileHandler(
        str(LOG_FILE),
        mode='a',  # Append mode - logs never deleted
        maxBytes=20 * 1024 * 1024,  # 20 MB per file
        backupCount=10,  # Keep up to 10 backup files
        encoding='utf-8',
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Track logger for cleanup
    _loggers.append(logger)

    return logger
