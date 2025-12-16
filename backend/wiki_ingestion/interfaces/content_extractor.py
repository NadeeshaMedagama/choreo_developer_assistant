"""
Interface for content extraction from web pages.
Following Interface Segregation Principle.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from ..models.wiki_page import WikiPage


class IContentExtractor(ABC):
    """Interface for extracting and processing content from web pages."""

    @abstractmethod
    def extract_content(self, html: str, url: str) -> Dict[str, Any]:
        """
        Extract meaningful content from HTML.

        Args:
            html: Raw HTML content
            url: Source URL

        Returns:
            Dictionary with extracted content (title, body, metadata)
        """
        pass

    @abstractmethod
    def extract_markdown(self, html: str) -> str:
        """
        Convert HTML to markdown format.

        Args:
            html: Raw HTML content

        Returns:
            Markdown formatted text
        """
        pass

    @abstractmethod
    def clean_content(self, content: str) -> str:
        """
        Clean and normalize content.

        Args:
            content: Raw content text

        Returns:
            Cleaned content
        """
        pass

    @abstractmethod
    def extract_metadata(self, html: str, url: str) -> Dict[str, Any]:
        """
        Extract metadata from HTML (title, description, keywords, etc.).

        Args:
            html: Raw HTML content
            url: Source URL

        Returns:
            Dictionary of metadata
        """
        pass

