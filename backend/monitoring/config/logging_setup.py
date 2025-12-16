"""
Logging Configuration Setup
Initializes logging for the application.
"""
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler


def setup_logging(log_level: str = "INFO", enable_json: bool = False):
    """
    Set up logging configuration for the application.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        enable_json: Whether to use JSON formatting for logs
    """
    # Create logs directory
    logs_dir = Path(__file__).parent.parent.parent / "logs"
    logs_dir.mkdir(exist_ok=True)
    
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # File handler for all logs
    all_logs_handler = RotatingFileHandler(
        logs_dir / "app.log",
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5
    )
    all_logs_handler.setLevel(logging.DEBUG)
    all_logs_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    all_logs_handler.setFormatter(all_logs_formatter)
    root_logger.addHandler(all_logs_handler)
    
    # File handler for errors only
    error_handler = RotatingFileHandler(
        logs_dir / "error.log",
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(all_logs_formatter)
    root_logger.addHandler(error_handler)
    
    logging.info(f"Logging initialized at {log_level} level")


# Initialize logging on import
setup_logging()

