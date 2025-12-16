"""
Interface for web crawling.
Following Interface Segregation Principle - single responsibility for crawling.
"""

from abc import ABC, abstractmethod
from typing import List, Set
from ..models.wiki_page import WikiPage


class IWebCrawler(ABC):
    """Interface for crawling web pages."""

    @abstractmethod
    def crawl(self, start_url: str, max_depth: int = 3) -> List[WikiPage]:
        """
        Crawl a website starting from the given URL.

        Args:
            start_url: Starting URL to begin crawling
            max_depth: Maximum depth to crawl (0 = only start page, 1 = start + linked pages, etc.)

        Returns:
            List of WikiPage objects containing page data
        """
        pass

    @abstractmethod
    def extract_page(self, url: str) -> WikiPage:
        """
        Extract a single page's content.

        Args:
            url: URL of the page to extract

        Returns:
            WikiPage object with extracted content
        """
        pass

    @abstractmethod
    def extract_links(self, content: str, base_url: str) -> Set[str]:
        """
        Extract all links from HTML/markdown content.

        Args:
            content: HTML or markdown content
            base_url: Base URL for resolving relative links

        Returns:
            Set of absolute URLs found in the content
        """
        pass

    @abstractmethod
    def is_valid_url(self, url: str, base_domain: str) -> bool:
        """
        Check if a URL is valid and should be crawled.

        Args:
            url: URL to validate
            base_domain: Base domain to restrict crawling to

        Returns:
            True if URL should be crawled, False otherwise
        """
        pass

