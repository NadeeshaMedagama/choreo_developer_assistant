"""
URL Validation Service

This service validates URLs to ensure they are accessible before including them in responses.
It checks for 404 errors and other accessibility issues.
It also integrates with the Choreo Repository Registry to validate and fix Choreo component URLs.
"""

import re
import asyncio
from typing import List, Dict, Optional, Set
import aiohttp
from aiohttp import ClientTimeout, ClientSession
import logging

logger = logging.getLogger(__name__)

# Import the Choreo Repository Registry
try:
    from .choreo_repo_registry import get_choreo_registry
    REGISTRY_AVAILABLE = True
except ImportError:
    REGISTRY_AVAILABLE = False
    logger.warning("Choreo Repository Registry not available")


class URLValidator:
    """Service to validate URLs and filter out broken/inaccessible ones."""
    
    # Trusted domains that should bypass validation (e.g., private repos, internal sites)
    TRUSTED_DOMAINS = [
        'github.com/wso2-enterprise',  # WSO2 Enterprise GitHub (private repos)
        'github.com/wso2',             # WSO2 public GitHub
        'wso2.com',                    # WSO2 official site
        'console.choreo.dev',          # Choreo console
        'docs.choreo.dev',             # Choreo docs
    ]

    def __init__(
        self,
        timeout: int = 5,
        max_concurrent: int = 10,
        cache_ttl: int = 3600,
        enable_validation: bool = True,
        trusted_domains: Optional[List[str]] = None
    ):
        """
        Initialize URL validator.
        
        Args:
            timeout: Request timeout in seconds
            max_concurrent: Maximum concurrent validation requests
            cache_ttl: Cache time-to-live in seconds
            enable_validation: Enable/disable URL validation (for performance testing)
            trusted_domains: Additional trusted domains to bypass validation
        """
        self.timeout = ClientTimeout(total=timeout)
        self.max_concurrent = max_concurrent
        self.cache_ttl = cache_ttl
        self.enable_validation = enable_validation
        self._cache: Dict[str, bool] = {}  # Simple in-memory cache
        self._semaphore = asyncio.Semaphore(max_concurrent)
        
        # Merge default trusted domains with any additional ones
        self.trusted_domains = list(self.TRUSTED_DOMAINS)
        if trusted_domains:
            self.trusted_domains.extend(trusted_domains)

        # Initialize Choreo Registry
        self.choreo_registry = get_choreo_registry() if REGISTRY_AVAILABLE else None
        if self.choreo_registry:
            logger.info("Choreo Repository Registry integrated with URL validator")

    def is_trusted_url(self, url: str) -> bool:
        """
        Check if URL is from a trusted domain.

        Args:
            url: URL to check

        Returns:
            True if URL is from a trusted domain, False otherwise
        """
        for domain in self.trusted_domains:
            if domain in url:
                return True
        return False

    def validate_and_fix_choreo_url(self, url: str) -> tuple[str, bool]:
        """
        Validate and potentially fix a Choreo component GitHub URL.
        Fixes URLs that use wrong organizations (e.g., wso2 public instead of wso2-enterprise).

        Args:
            url: URL to validate and fix

        Returns:
            Tuple of (fixed_url, is_valid)
        """
        if not self.choreo_registry or "github.com" not in url:
            return url, True  # Return as-is if not a GitHub URL

        # Check if this is a Choreo component URL
        validation = self.choreo_registry.validate_github_url(url)

        if validation and validation.get("is_valid"):
            correct_url = validation.get("correct_url")
            if correct_url and correct_url != url:
                logger.info(f"Fixed Choreo URL (wrong organization): {url} -> {correct_url}")
                return correct_url, True
            return url, True

        # If it's a wso2 or wso2-enterprise GitHub URL but not recognized, try to fix it
        if "github.com/wso2" in url.lower() or "github.com/wso2-enterprise" in url.lower():
            fixed_url = self.choreo_registry.fix_github_url(url)
            if fixed_url:
                logger.info(f"Fixed incorrect Choreo URL: {url} -> {fixed_url}")
                return fixed_url, True

        return url, False

    def extract_urls_from_text(self, text: str) -> List[str]:
        """
        Extract URLs from text using regex.
        
        Args:
            text: Text containing URLs
            
        Returns:
            List of extracted URLs
        """
        # Enhanced regex to match URLs in markdown format too
        url_pattern = r'https?://[^\s\)\]\"\'\,\>\}]+'
        markdown_pattern = r'\[([^\]]+)\]\((https?://[^\)]+)\)'
        
        # Extract plain URLs
        plain_urls = re.findall(url_pattern, text)
        
        # Extract URLs from markdown links
        markdown_urls = re.findall(markdown_pattern, text)
        markdown_urls = [url for _, url in markdown_urls]
        
        # Combine and deduplicate
        all_urls = list(set(plain_urls + markdown_urls))
        
        return all_urls
    
    async def validate_url(self, url: str, session: ClientSession) -> bool:
        """
        Validate a single URL by checking if it's accessible.
        Trusted domains (e.g., wso2-enterprise GitHub) are automatically marked as valid.

        Args:
            url: URL to validate
            session: aiohttp ClientSession
            
        Returns:
            True if URL is accessible, False otherwise
        """
        # Trusted domains bypass validation (e.g., private repos, internal sites)
        if self.is_trusted_url(url):
            logger.debug(f"URL is from trusted domain, marking as valid: {url}")
            self._cache[url] = True
            return True

        # Check cache first
        if url in self._cache:
            logger.debug(f"URL validation cache hit: {url}")
            return self._cache[url]
        
        async with self._semaphore:
            try:
                # Use HEAD request for efficiency (doesn't download full content)
                async with session.head(url, timeout=self.timeout, allow_redirects=True) as response:
                    is_valid = response.status < 400
                    
                    # If HEAD fails, try GET (some servers don't support HEAD)
                    if not is_valid:
                        async with session.get(url, timeout=self.timeout, allow_redirects=True) as get_response:
                            is_valid = get_response.status < 400
                    
                    # Cache result
                    self._cache[url] = is_valid
                    
                    if not is_valid:
                        logger.warning(f"URL validation failed (status {response.status}): {url}")
                    else:
                        logger.debug(f"URL validation successful: {url}")
                    
                    return is_valid
                    
            except asyncio.TimeoutError:
                logger.warning(f"URL validation timeout: {url}")
                self._cache[url] = False
                return False
                
            except aiohttp.ClientError as e:
                logger.warning(f"URL validation client error: {url} - {str(e)}")
                self._cache[url] = False
                return False
                
            except Exception as e:
                logger.error(f"URL validation unexpected error: {url} - {str(e)}")
                self._cache[url] = False
                return False
    
    async def validate_urls(self, urls: List[str]) -> Dict[str, bool]:
        """
        Validate multiple URLs concurrently.
        
        Args:
            urls: List of URLs to validate
            
        Returns:
            Dictionary mapping URL to validation status (True/False)
        """
        if not self.enable_validation:
            logger.info("URL validation disabled, marking all URLs as valid")
            return {url: True for url in urls}
        
        if not urls:
            return {}
        
        logger.info(f"Validating {len(urls)} URLs")
        
        async with aiohttp.ClientSession() as session:
            tasks = [self.validate_url(url, session) for url in urls]
            results = await asyncio.gather(*tasks)
            
        validation_map = dict(zip(urls, results))
        
        valid_count = sum(1 for v in results if v)
        invalid_count = len(results) - valid_count
        
        logger.info(f"URL validation complete: {valid_count} valid, {invalid_count} invalid")
        
        return validation_map
    
    def filter_valid_urls_from_text(self, text: str, validation_map: Dict[str, bool]) -> str:
        """
        Remove invalid URLs from text.
        
        Args:
            text: Text containing URLs
            validation_map: Dictionary mapping URLs to their validation status
            
        Returns:
            Text with invalid URLs removed
        """
        if not validation_map:
            return text
        
        filtered_text = text
        
        for url, is_valid in validation_map.items():
            if not is_valid:
                # Remove invalid URLs from text
                # Handle both plain URLs and markdown format
                filtered_text = re.sub(re.escape(url), "[URL removed - not accessible]", filtered_text)
                
                # Also remove markdown links containing this URL
                markdown_pattern = r'\[([^\]]+)\]\(' + re.escape(url) + r'\)'
                filtered_text = re.sub(markdown_pattern, r'\1 [link removed - not accessible]', filtered_text)
        
        return filtered_text
    
    async def validate_and_filter_sources(self, sources: List[Dict]) -> List[Dict]:
        """
        Validate URLs in source documents, fix incorrect Choreo URLs, and filter out sources with invalid URLs.

        Args:
            sources: List of source dictionaries
            
        Returns:
            List of sources with validated and fixed URLs
        """
        if not self.enable_validation:
            return sources
        
        # First pass: Fix incorrect Choreo URLs
        for source in sources:
            if "url" in source:
                original_url = source["url"]
                fixed_url, _ = self.validate_and_fix_choreo_url(original_url)
                if fixed_url != original_url:
                    source["url"] = fixed_url
                    logger.info(f"Fixed source URL: {original_url} -> {fixed_url}")

        # Extract all URLs from sources
        all_urls: Set[str] = set()
        for source in sources:
            if "url" in source:
                all_urls.add(source["url"])
        
        # Validate URLs
        validation_map = await self.validate_urls(list(all_urls))
        
        # Filter sources
        filtered_sources = []
        for source in sources:
            source_url = source.get("url")
            
            # Keep sources without URLs
            if not source_url:
                filtered_sources.append(source)
                continue
            
            # Keep sources with valid URLs
            if validation_map.get(source_url, False):
                filtered_sources.append(source)
            else:
                logger.info(f"Filtering out source with invalid URL: {source_url}")
        
        return filtered_sources
    
    async def validate_answer_urls(self, answer: str) -> tuple[str, Dict[str, bool]]:
        """
        Validate URLs in the answer text, fix incorrect Choreo URLs, and return filtered answer.

        Args:
            answer: Answer text potentially containing URLs
            
        Returns:
            Tuple of (filtered_answer, validation_map)
        """
        if not self.enable_validation:
            return answer, {}
        
        # Extract URLs from answer
        urls = self.extract_urls_from_text(answer)
        
        if not urls:
            return answer, {}
        
        # First, fix any incorrect Choreo URLs
        url_fixes = {}
        for url in urls:
            fixed_url, is_choreo = self.validate_and_fix_choreo_url(url)
            if fixed_url != url:
                url_fixes[url] = fixed_url

        # Apply fixes to the answer text
        fixed_answer = answer
        for old_url, new_url in url_fixes.items():
            fixed_answer = fixed_answer.replace(old_url, new_url)
            logger.info(f"Replaced URL in answer: {old_url} -> {new_url}")

        # Get the updated list of URLs after fixes
        updated_urls = self.extract_urls_from_text(fixed_answer)

        # Validate URLs
        validation_map = await self.validate_urls(updated_urls)

        # Filter answer
        filtered_answer = self.filter_valid_urls_from_text(fixed_answer, validation_map)

        return filtered_answer, validation_map
    
    def clear_cache(self):
        """Clear the validation cache."""
        self._cache.clear()
        logger.info("URL validation cache cleared")


# Singleton instance
_url_validator_instance: Optional[URLValidator] = None


def get_url_validator(
    timeout: int = 5,
    max_concurrent: int = 10,
    enable_validation: bool = True,
    trusted_domains: Optional[List[str]] = None
) -> URLValidator:
    """
    Get or create the URL validator singleton instance.
    
    Args:
        timeout: Request timeout in seconds
        max_concurrent: Maximum concurrent validation requests
        enable_validation: Enable/disable URL validation
        trusted_domains: Additional trusted domains to bypass validation

    Returns:
        URLValidator instance
    """
    global _url_validator_instance
    
    if _url_validator_instance is None:
        _url_validator_instance = URLValidator(
            timeout=timeout,
            max_concurrent=max_concurrent,
            enable_validation=enable_validation,
            trusted_domains=trusted_domains
        )
    
    return _url_validator_instance

