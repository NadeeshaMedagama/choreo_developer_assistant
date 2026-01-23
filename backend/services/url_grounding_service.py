"""
URL Grounding Service

This service provides real-time URL validation and correction by grounding LLM-generated URLs
against verified documentation sources. It can optionally use Google Search API for real-time
URL discovery when configured.

The grounding process:
1. Detect potentially invalid URLs in LLM response
2. Look up corrections from the URL correction mapping
3. Optionally validate URLs against live web (Google Search or HTTP HEAD requests)
4. Replace invalid URLs with correct ones

Supports both LOCAL and CLOUD (Choreo) deployments.
"""

import re
import asyncio
import aiohttp
from typing import Optional, Dict, Tuple
from aiohttp import ClientTimeout
import logging
import os

logger = logging.getLogger(__name__)

# Check for Google Search API availability
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_SEARCH_ENGINE_ID = os.getenv("GOOGLE_SEARCH_ENGINE_ID")
GOOGLE_SEARCH_ENABLED = bool(GOOGLE_API_KEY and GOOGLE_SEARCH_ENGINE_ID)

if GOOGLE_SEARCH_ENABLED:
    logger.info("🔍 Google Search Grounding ENABLED")
else:
    logger.info("⚠️ Google Search Grounding disabled - using static URL correction mappings")


class URLGroundingService:
    """
    Service to ground and validate URLs in LLM responses.

    Grounding Process (when Google Search is enabled):
    1. Trigger: Detect URLs in LLM response that may be invalid
    2. Retrieval: Perform Google Search for the correct documentation URL
    3. Extraction: Extract the verified URL from search results
    4. Citation: Replace the invalid URL with the verified one

    When Google Search is not available:
    - Uses static URL correction mappings
    - Performs HTTP HEAD validation for reachability
    """

    # Static URL corrections - Maps invalid URL patterns to correct URLs
    # These are known LLM hallucination patterns and their corrections
    URL_CORRECTIONS = {
        # Choreo APIM Setup Guide For Development
        'wso2.com/choreo/docs/api-management': 'https://docs.google.com/document/d/1qkonR2EG7ppgn5jhrNyd8aMhBjxlgzHtZ_1Wb1hrs1c/edit?tab=t.0#heading=h.44xczcdf40wf',

        # Choreo Light-Weight Security Token Service
        'wso2.com/choreo/docs/security': 'https://docs.google.com/document/d/19NUdAdhpO-AqpCBdd8v7EegAZLrLPfREY-0PozXv3g0/edit?tab=t.0',
        'wso2.com/choreo/docs/security/service-authentication': 'https://docs.google.com/document/d/19NUdAdhpO-AqpCBdd8v7EegAZLrLPfREY-0PozXv3g0/edit?tab=t.0',
        'wso2.com/choreo/docs/api-management/security': 'https://docs.google.com/document/d/19NUdAdhpO-AqpCBdd8v7EegAZLrLPfREY-0PozXv3g0/edit?tab=t.0',

        # Environment Management - correct Choreo docs path
        'wso2.com/choreo/docs/environment-management': 'https://wso2.com/choreo/docs/devops-and-ci-cd/manage-environments/',

        # Components Configuration - correct Choreo docs path
        'wso2.com/choreo/docs/components/configuration': 'https://wso2.com/choreo/docs/develop-components/use-configuration-form/',

        # Ballerina docs are at ballerina.io, not wso2.com
        'wso2.com/choreo/docs/ballerina': 'https://ballerina.io/learn/',

        # Choreo CLI Documentation - correct path
        'wso2.com/choreo/docs/cli': 'https://wso2.com/choreo/docs/choreo-cli/choreo-cli-overview/',
        'wso2.com/choreo/docs/develop-components/cli': 'https://wso2.com/choreo/docs/choreo-cli/choreo-cli-overview/',
        'wso2.com/choreo/docs/reference/cli': 'https://wso2.com/choreo/docs/choreo-cli/choreo-cli-overview/',
        'wso2.com/choreo/docs/reference/faq/#choreo-cli': 'https://wso2.com/choreo/docs/choreo-cli/choreo-cli-overview/',
        'wso2.com/choreo/docs/references/faq/#choreo-cli': 'https://wso2.com/choreo/docs/choreo-cli/choreo-cli-overview/',
        'wso2.com/choreo/docs/getting-started/cli': 'https://wso2.com/choreo/docs/choreo-cli/choreo-cli-overview/',
    }

    # Known invalid URL patterns that should be removed or corrected
    INVALID_URL_PATTERNS = [
        'wso2.com/choreo/docs/ballerina',
        'wso2.com/choreo/docs/developer-tools',
        'wso2.com/choreo/docs/tutorials',
        'wso2.com/choreo/docs/guides',
        'wso2.com/choreo/docs/quick-start',
        'wso2.com/choreo/docs/api-reference',
        'wso2.com/choreo/docs/samples',
        'wso2.com/choreo/docs/examples',
        'wso2.com/choreo/docs/api-management',
        'wso2.com/choreo/docs/security',
        'wso2.com/choreo/docs/environment-management',
        'wso2.com/choreo/docs/components/configuration',
        'wso2.com/choreo/docs/cli',
        'wso2.com/choreo/docs/develop-components/cli',
        'wso2.com/choreo/docs/reference/cli',
        'wso2.com/choreo/docs/reference/faq/#choreo-cli',
        'wso2.com/choreo/docs/references/faq/#choreo-cli',
        'wso2.com/choreo/docs/getting-started/cli',
    ]

    # Topic to search query mapping for Google Search grounding
    TOPIC_SEARCH_QUERIES = {
        'environment-management': 'site:wso2.com choreo manage environments documentation',
        'configuration': 'site:wso2.com choreo component configuration form documentation',
        'api-management': 'site:wso2.com choreo API management setup documentation',
        'security': 'site:wso2.com choreo security token service STS documentation',
        'ballerina': 'site:ballerina.io learn documentation',
    }

    def __init__(self, timeout: int = 5, enable_google_search: bool = True):
        """
        Initialize URL Grounding Service.

        Args:
            timeout: HTTP request timeout in seconds
            enable_google_search: Enable Google Search grounding if API is available
        """
        self.timeout = ClientTimeout(total=timeout)
        self.enable_google_search = enable_google_search and GOOGLE_SEARCH_ENABLED
        self._url_cache: Dict[str, str] = {}  # Cache for validated URLs

        if self.enable_google_search:
            logger.info("Google Search grounding is enabled for URL validation")
        else:
            logger.info("Using static URL correction mappings (Google Search not configured)")

    def is_invalid_url(self, url: str) -> bool:
        """
        Check if a URL matches known invalid patterns.

        Args:
            url: URL to check

        Returns:
            True if URL is known to be invalid
        """
        url_lower = url.lower()
        for pattern in self.INVALID_URL_PATTERNS:
            if pattern.lower() in url_lower:
                return True
        return False

    def get_static_correction(self, url: str) -> Optional[str]:
        """
        Get static URL correction from the mapping.

        Args:
            url: Invalid URL to find correction for

        Returns:
            Correct URL if found, None otherwise
        """
        url_lower = url.lower()

        # Regex-based corrections for common patterns
        # This catches ALL CLI-related invalid URLs regardless of exact path
        cli_pattern = re.compile(r'wso2\.com/choreo/docs/.*cli', re.IGNORECASE)
        if cli_pattern.search(url_lower):
            correct_url = "https://wso2.com/choreo/docs/choreo-cli/choreo-cli-overview/"
            logger.info(f"Found CLI URL correction (regex): {url} -> {correct_url}")
            return correct_url

        # Static pattern matching for other URLs
        for pattern, correct_url in self.URL_CORRECTIONS.items():
            if pattern.lower() in url_lower:
                logger.info(f"Found static URL correction: {url} -> {correct_url}")
                return correct_url
        return None

    async def search_correct_url_google(self, topic: str) -> Optional[str]:
        """
        Use Google Custom Search API to find the correct URL for a topic.

        This implements the Grounding with Google Search process:
        1. Trigger: Topic needs URL verification
        2. Retrieval: Google Search is performed
        3. Extraction: URL is extracted from search results
        4. Citation: Returns the verified URL

        Args:
            topic: Topic to search for (e.g., 'environment-management')

        Returns:
            Verified URL from Google Search, or None if not found
        """
        if not self.enable_google_search:
            logger.debug("Google Search not enabled, skipping search")
            return None

        # Check cache first
        cache_key = f"google_search:{topic}"
        if cache_key in self._url_cache:
            return self._url_cache[cache_key]

        # Get search query for topic
        search_query = self.TOPIC_SEARCH_QUERIES.get(
            topic,
            f'site:wso2.com choreo {topic} documentation'
        )

        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                url = "https://www.googleapis.com/customsearch/v1"
                params = {
                    'key': GOOGLE_API_KEY,
                    'cx': GOOGLE_SEARCH_ENGINE_ID,
                    'q': search_query,
                    'num': 3  # Get top 3 results
                }

                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        items = data.get('items', [])

                        if items:
                            # Return the first result URL
                            result_url = items[0].get('link')
                            if result_url:
                                logger.info(f"Google Search found URL for '{topic}': {result_url}")
                                self._url_cache[cache_key] = result_url
                                return result_url
                    else:
                        logger.warning(f"Google Search API returned status {response.status}")

        except Exception as e:
            logger.error(f"Google Search API error: {e}")

        return None

    async def validate_url_reachable(self, url: str) -> bool:
        """
        Validate if a URL is reachable via HTTP HEAD request.

        Args:
            url: URL to validate

        Returns:
            True if URL is reachable (not 404)
        """
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.head(url, allow_redirects=True) as response:
                    return response.status < 400
        except Exception as e:
            logger.debug(f"URL validation failed for {url}: {e}")
            return False

    async def ground_url(self, url: str) -> Tuple[str, bool]:
        """
        Ground a URL - validate and correct if necessary.

        Args:
            url: URL to ground

        Returns:
            Tuple of (corrected_url, was_corrected)
        """
        # Check if URL is known invalid
        if not self.is_invalid_url(url):
            return url, False

        # Try static correction first
        correction = self.get_static_correction(url)
        if correction:
            return correction, True

        # Try Google Search grounding if enabled
        if self.enable_google_search:
            # Extract topic from URL
            topic = self._extract_topic_from_url(url)
            if topic:
                searched_url = await self.search_correct_url_google(topic)
                if searched_url:
                    return searched_url, True

        # No correction found - return original
        return url, False

    def _extract_topic_from_url(self, url: str) -> Optional[str]:
        """Extract topic/keyword from URL for search purposes."""
        # Match common patterns like /docs/environment-management/
        match = re.search(r'/docs/([^/]+)', url)
        if match:
            return match.group(1)
        return None

    async def ground_text(self, text: str) -> str:
        """
        Ground all URLs in a text - validate and correct invalid ones.

        Args:
            text: Text containing URLs

        Returns:
            Text with corrected URLs
        """
        # Find all URLs in text
        url_pattern = r'https?://[^\s\)\]\>\"\']+(?=[)\]\s\>\"\'<]|$)'
        urls = re.findall(url_pattern, text)

        if not urls:
            return text

        # Ground each URL
        corrections = {}
        for url in set(urls):  # Process unique URLs only
            corrected, was_corrected = await self.ground_url(url)
            if was_corrected:
                corrections[url] = corrected

        # Apply corrections to text
        result = text
        for original, corrected in corrections.items():
            result = result.replace(original, corrected)
            logger.info(f"Grounded URL: {original} -> {corrected}")

        return result

    def ground_text_sync(self, text: str) -> str:
        """
        Synchronous wrapper for ground_text.

        Args:
            text: Text containing URLs

        Returns:
            Text with corrected URLs
        """
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        return loop.run_until_complete(self.ground_text(text))


# Singleton instance
_grounding_service: Optional[URLGroundingService] = None


def get_grounding_service() -> URLGroundingService:
    """Get or create the singleton URLGroundingService instance."""
    global _grounding_service
    if _grounding_service is None:
        _grounding_service = URLGroundingService()
    return _grounding_service


def ground_response_urls(response_text: str) -> str:
    """
    Convenience function to ground all URLs in an LLM response.

    This should be called after receiving an LLM response to validate
    and correct any hallucinated URLs.

    Args:
        response_text: LLM response text containing URLs

    Returns:
        Response with corrected URLs
    """
    service = get_grounding_service()
    return service.ground_text_sync(response_text)
