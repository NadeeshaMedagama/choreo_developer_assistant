"""
URL Fetcher Service Implementation.
Handles HTTP requests to fetch web page content.
"""

import time
from typing import Optional, Dict
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from ..interfaces.url_fetcher import IUrlFetcher


class UrlFetcherService(IUrlFetcher):
    """Service for fetching content from URLs with retry logic."""

    def __init__(
        self,
        timeout: int = 30,
        max_retries: int = 3,
        backoff_factor: float = 0.5,
        user_agent: Optional[str] = None,
        github_token: Optional[str] = None
    ):
        """
        Initialize URL fetcher.

        Args:
            timeout: Default timeout for requests in seconds
            max_retries: Maximum number of retry attempts
            backoff_factor: Backoff factor for retries
            user_agent: Custom user agent string
            github_token: GitHub personal access token for private repositories
        """
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor

        # Default headers
        self._headers = {
            "User-Agent": user_agent or "WikiCrawler/1.0 (GitHub Wiki Ingestion Bot)",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
        }

        # Add GitHub authentication if token provided
        if github_token:
            self._headers["Authorization"] = f"token {github_token}"
            print(f"🔐 GitHub authentication enabled")

        # Create session with retry logic
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
        """Create a requests session with retry configuration."""
        session = requests.Session()

        # Configure retry strategy
        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=self.backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "HEAD"],
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        return session

    def fetch(self, url: str, timeout: int = 30) -> Optional[str]:
        """
        Fetch content from a URL.

        Args:
            url: URL to fetch
            timeout: Request timeout in seconds

        Returns:
            HTML content as string, or None if fetch failed
        """
        try:
            response = self.session.get(
                url,
                headers=self._headers,
                timeout=timeout or self.timeout,
                allow_redirects=True
            )
            response.raise_for_status()

            # Check content type
            content_type = response.headers.get('Content-Type', '').lower()
            if 'text/html' not in content_type and 'text/plain' not in content_type:
                print(f"⚠️  Skipping non-HTML content: {url} (type: {content_type})")
                return None

            return response.text

        except requests.exceptions.Timeout:
            print(f"❌ Timeout fetching {url}")
            return None
        except requests.exceptions.HTTPError as e:
            print(f"❌ HTTP error fetching {url}: {e}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching {url}: {e}")
            return None
        except Exception as e:
            print(f"❌ Unexpected error fetching {url}: {e}")
            return None

    def fetch_with_retry(self, url: str, max_retries: int = 3) -> Optional[str]:
        """
        Fetch content with automatic retry on failure.

        Args:
            url: URL to fetch
            max_retries: Maximum number of retry attempts

        Returns:
            HTML content as string, or None if all attempts failed
        """
        for attempt in range(max_retries):
            result = self.fetch(url)
            if result is not None:
                return result

            if attempt < max_retries - 1:
                wait_time = self.backoff_factor * (2 ** attempt)
                print(f"⏳ Retrying in {wait_time}s... (attempt {attempt + 1}/{max_retries})")
                time.sleep(wait_time)

        print(f"❌ Failed to fetch {url} after {max_retries} attempts")
        return None

    def get_headers(self) -> Dict[str, str]:
        """
        Get HTTP headers used for requests.

        Returns:
            Dictionary of HTTP headers
        """
        return self._headers.copy()

    def set_headers(self, headers: Dict[str, str]) -> None:
        """
        Set custom HTTP headers for requests.

        Args:
            headers: Dictionary of HTTP headers
        """
        self._headers.update(headers)

    def close(self):
        """Close the session."""
        if self.session:
            self.session.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

