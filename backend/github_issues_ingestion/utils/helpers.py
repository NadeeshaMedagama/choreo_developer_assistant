"""
Helper utilities for GitHub Issues Ingestion.
"""

from datetime import datetime
from typing import Optional, Tuple
import re


def format_timestamp(dt: Optional[datetime] = None, iso_format: bool = True) -> str:
    """
    Format a datetime object as a string.

    Args:
        dt: Datetime object (defaults to current UTC time)
        iso_format: Whether to use ISO format

    Returns:
        Formatted timestamp string
    """
    if dt is None:
        dt = datetime.utcnow()
    
    if iso_format:
        return dt.isoformat()
    else:
        return dt.strftime("%Y-%m-%d %H:%M:%S")


def validate_repo_format(repo_string: str) -> Tuple[str, str]:
    """
    Validate and parse repository string in format 'owner/repo'.

    Args:
        repo_string: Repository string

    Returns:
        Tuple of (owner, repo)

    Raises:
        ValueError: If format is invalid
    """
    if not repo_string or "/" not in repo_string:
        raise ValueError("Repository must be in format 'owner/repo'")
    
    parts = repo_string.split("/")
    if len(parts) != 2:
        raise ValueError("Repository must be in format 'owner/repo'")
    
    owner, repo = parts
    
    if not owner or not repo:
        raise ValueError("Owner and repo cannot be empty")
    
    # Validate GitHub naming rules
    if not re.match(r"^[a-zA-Z0-9-]+$", owner):
        raise ValueError("Invalid owner name")
    
    if not re.match(r"^[a-zA-Z0-9._-]+$", repo):
        raise ValueError("Invalid repository name")
    
    return owner, repo


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to a maximum length.

    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated

    Returns:
        Truncated text
    """
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename by removing invalid characters.

    Args:
        filename: Original filename

    Returns:
        Sanitized filename
    """
    # Remove invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove leading/trailing spaces and dots
    sanitized = sanitized.strip('. ')
    
    return sanitized or "unnamed"


def calculate_progress_percentage(current: int, total: int) -> float:
    """
    Calculate progress percentage.

    Args:
        current: Current progress
        total: Total items

    Returns:
        Percentage (0-100)
    """
    if total == 0:
        return 0.0
    
    return min(100.0, (current / total) * 100.0)


def estimate_time_remaining(
    current: int,
    total: int,
    elapsed_seconds: float
) -> Optional[float]:
    """
    Estimate remaining time based on current progress.

    Args:
        current: Current progress
        total: Total items
        elapsed_seconds: Elapsed time in seconds

    Returns:
        Estimated remaining seconds, or None if cannot estimate
    """
    if current == 0 or total == 0:
        return None
    
    rate = current / elapsed_seconds
    remaining_items = total - current
    
    if rate == 0:
        return None
    
    return remaining_items / rate

