"""
Interfaces for Wiki Ingestion Module.
Following Interface Segregation Principle.
"""

from .web_crawler import IWebCrawler
from .content_extractor import IContentExtractor
from .url_fetcher import IUrlFetcher

__all__ = [
    'IWebCrawler',
    'IContentExtractor',
    'IUrlFetcher',
]

