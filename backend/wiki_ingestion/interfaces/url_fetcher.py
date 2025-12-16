"""
Interface for fetching content from URLs.
Following Interface Segregation Principle.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict


class IUrlFetcher(ABC):
    """Interface for fetching content from URLs."""

    @abstractmethod
    def fetch(self, url: str, timeout: int = 30) -> Optional[str]:
        """
        Fetch content from a URL.

        Args:
            url: URL to fetch
            timeout: Request timeout in seconds

        Returns:
            HTML content as string, or None if fetch failed
        """
        pass

    @abstractmethod
    def fetch_with_retry(self, url: str, max_retries: int = 3) -> Optional[str]:
        """
        Fetch content with automatic retry on failure.

        Args:
            url: URL to fetch
            max_retries: Maximum number of retry attempts

        Returns:
            HTML content as string, or None if all attempts failed
        """
        pass

    @abstractmethod
    def get_headers(self) -> Dict[str, str]:
        """
        Get HTTP headers used for requests.

        Returns:
            Dictionary of HTTP headers
        """
        pass

    @abstractmethod
    def set_headers(self, headers: Dict[str, str]) -> None:
        """
        Set custom HTTP headers for requests.

        Args:
            headers: Dictionary of HTTP headers
        """
        pass

