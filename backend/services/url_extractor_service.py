"""
URL Extractor Service

This service extracts all URLs from document content including:
- Official Choreo documentation URLs (https://wso2.com/choreo/docs/...)
- GitHub repository URLs
- Wiki URLs
- External reference links
- Google Docs links
- Ballerina documentation links

The extracted URLs are categorized and returned alongside the main source.
"""

import re
from typing import List, Dict, Any, Set, Optional
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class URLCategory(Enum):
    """Categories of URLs that can be extracted."""
    CHOREO_DOCS = "choreo_documentation"
    GITHUB_REPO = "github_repository"
    GITHUB_WIKI = "github_wiki"
    GOOGLE_DOCS = "google_docs"
    BALLERINA_DOCS = "ballerina_documentation"
    WSO2_DOCS = "wso2_documentation"
    EXTERNAL = "external_reference"
    UNKNOWN = "unknown"


@dataclass
class ExtractedURL:
    """Represents an extracted URL with its metadata."""
    url: str
    category: URLCategory
    title: Optional[str] = None
    context: Optional[str] = None  # Surrounding text that mentions this URL

    def to_dict(self) -> Dict[str, Any]:
        return {
            "url": self.url,
            "category": self.category.value,
            "title": self.title,
            "context": self.context
        }


class URLExtractorService:
    """
    Service to extract all URLs from document content and categorize them.

    This helps provide users with all relevant reference links, not just
    the source repository URL.
    """

    # Known INVALID repository URLs that should NEVER be returned
    # These are hallucinated/incorrect URLs that don't exist (404 errors)
    INVALID_REPO_URLS = {
        # Known hallucinated repos - add more as discovered
        "https://github.com/wso2-enterprise/choreo-alert-configuration-service",
        "https://github.com/wso2-enterprise/choreo-alerts-service",
        "https://github.com/wso2-enterprise/choreo-notification-service",
        "https://github.com/wso2-enterprise/choreo-config-service",
        "https://github.com/wso2-enterprise/choreo-settings-service",
        "https://github.com/wso2-enterprise/choreo-observability",
        # Invalid dataplane repos - 404 errors
        "https://github.com/wso2-enterprise/choreodp-auth-module",
        "https://github.com/wso2-enterprise/choreodp-cicd",
        "https://github.com/wso2-enterprise/choreodp-secret-manager",
        "https://github.com/wso2-enterprise/choreodp-mizzen",
        "https://github.com/wso2-enterprise/choreodp-project-manager",
        "https://github.com/wso2-enterprise/choreodp-cloud-manager",
        "https://github.com/wso2-enterprise/choreodp-garbage-collector",
        "https://github.com/wso2-enterprise/choreodp-kv-resolver",
        "https://github.com/wso2-enterprise/choreodp-git-runners",
        # Other invalid repos - 404 errors
        "https://github.com/wso2-enterprise/product-microgateway",
        "https://github.com/wso2-enterprise/growth-hacking",
    }

    # Patterns for invalid/hallucinated repo names
    INVALID_REPO_PATTERNS = [
        r'choreo-alert-configuration-service',
        r'choreo-alerts-service',
        r'choreo-notification-service',
        r'choreo-config-service',
        r'choreo-settings-service',
        r'choreo-observability',
        # Invalid dataplane repos
        r'choreodp-auth-module',
        r'choreodp-cicd',
        r'choreodp-secret-manager',
        r'choreodp-mizzen',
        r'choreodp-project-manager',
        r'choreodp-cloud-manager',
        r'choreodp-garbage-collector',
        r'choreodp-kv-resolver',
        r'choreodp-git-runners',
        # Other invalid repos
        r'product-microgateway',
        r'growth-hacking',
    ]

    # URL patterns for different categories
    URL_PATTERNS = {
        URLCategory.CHOREO_DOCS: [
            r'https?://(?:www\.)?wso2\.com/choreo/docs[^\s\)\]\"\'\>]*',
        ],
        URLCategory.GITHUB_REPO: [
            r'https?://github\.com/wso2-enterprise/[^\s\)\]\"\'\>]+',
            r'https?://github\.com/wso2/[^\s\)\]\"\'\>]+',
            r'https?://github\.com/ballerina-platform/[^\s\)\]\"\'\>]+',
        ],
        URLCategory.GITHUB_WIKI: [
            r'https?://github\.com/[^/]+/[^/]+/wiki[^\s\)\]\"\'\>]*',
        ],
        URLCategory.GOOGLE_DOCS: [
            r'https?://docs\.google\.com/document/d/[^\s\)\]\"\'\>]+',
            r'https?://docs\.google\.com/spreadsheets/d/[^\s\)\]\"\'\>]+',
        ],
        URLCategory.BALLERINA_DOCS: [
            r'https?://(?:www\.)?ballerina\.io/[^\s\)\]\"\'\>]+',
        ],
        URLCategory.WSO2_DOCS: [
            r'https?://(?:www\.)?wso2\.com/(?!choreo/docs)[^\s\)\]\"\'\>]+',
            r'https?://apim\.docs\.wso2\.com/[^\s\)\]\"\'\>]+',
            r'https?://is\.docs\.wso2\.com/[^\s\)\]\"\'\>]+',
            r'https?://mi\.docs\.wso2\.com/[^\s\)\]\"\'\>]+',
        ],
    }

    # General URL pattern for catching any URL
    GENERAL_URL_PATTERN = r'https?://[^\s\)\]\"\'\>\<]+'

    # Markdown link pattern: [text](url)
    MARKDOWN_LINK_PATTERN = r'\[([^\]]+)\]\(([^\)]+)\)'

    def __init__(self):
        """Initialize the URL Extractor Service."""
        self._compiled_patterns = {}
        self._compile_patterns()

    def _compile_patterns(self):
        """Pre-compile regex patterns for efficiency."""
        for category, patterns in self.URL_PATTERNS.items():
            self._compiled_patterns[category] = [
                re.compile(pattern, re.IGNORECASE)
                for pattern in patterns
            ]
        self._general_pattern = re.compile(self.GENERAL_URL_PATTERN, re.IGNORECASE)
        self._markdown_pattern = re.compile(self.MARKDOWN_LINK_PATTERN)

    def _categorize_url(self, url: str) -> URLCategory:
        """Determine the category of a URL."""
        for category, patterns in self._compiled_patterns.items():
            for pattern in patterns:
                if pattern.match(url):
                    return category
        return URLCategory.EXTERNAL

    def _is_valid_url(self, url: str) -> bool:
        """
        Check if a URL is valid (not a known hallucinated/invalid URL).

        Args:
            url: URL to validate

        Returns:
            True if URL is valid, False if it's a known invalid URL
        """
        # Check against exact invalid URLs
        if url in self.INVALID_REPO_URLS:
            logger.warning(f"Filtered out known invalid URL: {url}")
            return False

        # Check against invalid URL patterns
        url_lower = url.lower()
        for pattern in self.INVALID_REPO_PATTERNS:
            if re.search(pattern, url_lower):
                logger.warning(f"Filtered out URL matching invalid pattern '{pattern}': {url}")
                return False

        return True

    def _clean_url(self, url: str) -> str:
        """Clean up URL by removing trailing punctuation and fragments."""
        # Remove trailing punctuation that might have been captured
        url = url.rstrip('.,;:!?')
        # Remove trailing parentheses/brackets that aren't part of URL
        while url.endswith(')') or url.endswith(']') or url.endswith('>'):
            url = url[:-1]
        return url

    def _extract_context(self, content: str, url: str, context_chars: int = 100) -> Optional[str]:
        """Extract surrounding context for a URL."""
        try:
            idx = content.find(url)
            if idx == -1:
                return None

            start = max(0, idx - context_chars)
            end = min(len(content), idx + len(url) + context_chars)
            context = content[start:end].strip()

            # Clean up context
            context = ' '.join(context.split())  # Normalize whitespace
            if start > 0:
                context = '...' + context
            if end < len(content):
                context = context + '...'

            return context
        except Exception:
            return None

    def extract_urls_from_content(
        self,
        content: str,
        include_context: bool = True,
        deduplicate: bool = True
    ) -> List[ExtractedURL]:
        """
        Extract all URLs from content.

        Args:
            content: The text content to extract URLs from
            include_context: Whether to include surrounding context
            deduplicate: Whether to remove duplicate URLs

        Returns:
            List of ExtractedURL objects
        """
        if not content:
            return []

        extracted_urls: List[ExtractedURL] = []
        seen_urls: Set[str] = set()

        # First, extract markdown links to get titles
        markdown_links: Dict[str, str] = {}  # url -> title
        for match in self._markdown_pattern.finditer(content):
            title, url = match.groups()
            url = self._clean_url(url)
            if url.startswith('http'):
                markdown_links[url] = title

        # Extract all URLs using general pattern
        for match in self._general_pattern.finditer(content):
            url = self._clean_url(match.group())

            # Skip if already seen and deduplication is enabled
            if deduplicate and url in seen_urls:
                continue
            seen_urls.add(url)

            # Skip if URL is known to be invalid/hallucinated
            if not self._is_valid_url(url):
                continue

            # Categorize the URL
            category = self._categorize_url(url)

            # Get title from markdown links if available
            title = markdown_links.get(url)

            # Get context if requested
            context = None
            if include_context:
                context = self._extract_context(content, url)

            extracted_urls.append(ExtractedURL(
                url=url,
                category=category,
                title=title,
                context=context
            ))

        return extracted_urls

    def extract_urls_from_sources(
        self,
        sources: List[Dict[str, Any]],
        include_content_urls: bool = True
    ) -> List[ExtractedURL]:
        """
        Extract URLs from source documents including their content.

        Args:
            sources: List of source documents with content and metadata
            include_content_urls: Whether to also extract URLs from content

        Returns:
            List of all extracted URLs
        """
        all_urls: List[ExtractedURL] = []
        seen_urls: Set[str] = set()

        for source in sources:
            # Extract URL from metadata
            if source.get("url"):
                url = source["url"]
                if url not in seen_urls and self._is_valid_url(url):
                    seen_urls.add(url)
                    category = self._categorize_url(url)
                    all_urls.append(ExtractedURL(
                        url=url,
                        category=category,
                        title=source.get("title") or source.get("file_path"),
                        context=f"Source document from {source.get('repository', 'unknown repository')}"
                    ))

            # Extract URLs from content if enabled
            if include_content_urls and source.get("content"):
                content_urls = self.extract_urls_from_content(
                    source["content"],
                    include_context=True,
                    deduplicate=True
                )
                for extracted in content_urls:
                    if extracted.url not in seen_urls:
                        seen_urls.add(extracted.url)
                        all_urls.append(extracted)

        return all_urls

    def categorize_urls(
        self,
        urls: List[ExtractedURL]
    ) -> Dict[str, List[ExtractedURL]]:
        """
        Group URLs by category.

        Args:
            urls: List of extracted URLs

        Returns:
            Dictionary with category names as keys and lists of URLs as values
        """
        categorized: Dict[str, List[ExtractedURL]] = {}

        for url in urls:
            category_name = url.category.value
            if category_name not in categorized:
                categorized[category_name] = []
            categorized[category_name].append(url)

        return categorized

    def get_documentation_urls(
        self,
        urls: List[ExtractedURL]
    ) -> List[ExtractedURL]:
        """
        Filter to get only documentation URLs (Choreo docs, Ballerina docs, WSO2 docs).

        Args:
            urls: List of extracted URLs

        Returns:
            List of documentation URLs only
        """
        doc_categories = {
            URLCategory.CHOREO_DOCS,
            URLCategory.BALLERINA_DOCS,
            URLCategory.WSO2_DOCS,
            URLCategory.GOOGLE_DOCS,
        }
        return [url for url in urls if url.category in doc_categories]

    def get_repository_urls(
        self,
        urls: List[ExtractedURL]
    ) -> List[ExtractedURL]:
        """
        Filter to get only repository URLs.

        Args:
            urls: List of extracted URLs

        Returns:
            List of repository URLs only
        """
        repo_categories = {
            URLCategory.GITHUB_REPO,
            URLCategory.GITHUB_WIKI,
        }
        return [url for url in urls if url.category in repo_categories]

    def format_urls_for_response(
        self,
        urls: List[ExtractedURL],
        max_per_category: int = 5
    ) -> Dict[str, Any]:
        """
        Format extracted URLs for API response.

        Args:
            urls: List of extracted URLs
            max_per_category: Maximum URLs to include per category

        Returns:
            Formatted dictionary for API response
        """
        categorized = self.categorize_urls(urls)

        formatted = {
            "total_urls": len(urls),
            "categories": {}
        }

        for category, category_urls in categorized.items():
            formatted["categories"][category] = {
                "count": len(category_urls),
                "urls": [
                    url.to_dict()
                    for url in category_urls[:max_per_category]
                ]
            }

        return formatted


# Singleton instance
_url_extractor_instance: Optional[URLExtractorService] = None


def get_url_extractor() -> URLExtractorService:
    """Get the singleton URL extractor instance."""
    global _url_extractor_instance
    if _url_extractor_instance is None:
        _url_extractor_instance = URLExtractorService()
    return _url_extractor_instance
