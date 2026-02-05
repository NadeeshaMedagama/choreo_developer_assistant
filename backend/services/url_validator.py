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

# Import the URL Grounding Service
try:
    from .url_grounding_service import get_grounding_service
    GROUNDING_AVAILABLE = True
except ImportError:
    GROUNDING_AVAILABLE = False
    logger.warning("URL Grounding Service not available")


class URLValidator:
    """Service to validate URLs and filter out broken/inaccessible ones."""
    
    # Trusted domains that should bypass validation (only for non-GitHub URLs)
    # GitHub URLs should ALWAYS be validated to ensure repos actually exist
    # NOTE: wso2.com/choreo/docs paths are validated, but main wso2.com/choreo is trusted
    TRUSTED_DOMAINS = [
        'console.choreo.dev',          # Choreo console
        'docs.choreo.dev',             # Choreo docs (alternative domain)
        'wso2.com/choreo',             # Choreo main platform page (valid)
    ]

    # Known INVALID documentation URL patterns that LLMs often hallucinate
    # These URL patterns don't exist and should be removed from responses
    KNOWN_INVALID_URL_PATTERNS = [
        # Invalid Choreo doc URL paths - these are hallucinated by LLMs
        'wso2.com/choreo/docs/ballerina',           # Ballerina docs are separate at ballerina.io
        'wso2.com/choreo/docs/developer-tools',     # Wrong path structure
        'wso2.com/choreo/docs/tutorials',           # Wrong path - should be specific tutorial paths
        'wso2.com/choreo/docs/guides',              # Wrong path structure
        'wso2.com/choreo/docs/quick-start',         # Wrong - should be 'quick-start-guides'
        'wso2.com/choreo/docs/api-reference',       # Wrong path structure
        'wso2.com/choreo/docs/samples',             # Wrong path structure
        'wso2.com/choreo/docs/examples',            # Wrong path structure
        'wso2.com/choreo/docs/getting-started/ballerina',  # Wrong combined path
        'wso2.com/choreo/docs/deploy/ballerina',    # Wrong combined path
        'wso2.com/choreo/docs/build/ballerina',     # Wrong combined path
        'wso2.com/choreo/docs/test/ballerina',      # Wrong combined path
        'wso2.com/choreo/docs/observability/ballerina',  # Wrong combined path
        'wso2.com/choreo/docs/components/ballerina',     # Wrong combined path
        # Invalid API Management paths - use internal docs instead
        'wso2.com/choreo/docs/api-management',      # Wrong - use Choreo APIM Setup Guide doc
        # Invalid Security paths - use internal docs instead
        'wso2.com/choreo/docs/security',            # Wrong - use Choreo Light-Weight STS doc
        # Invalid Environment Management paths - use correct Choreo docs path
        'wso2.com/choreo/docs/environment-management',  # Wrong - use devops-and-ci-cd/manage-environments
        # Invalid Components Configuration paths - use correct Choreo docs path
        'wso2.com/choreo/docs/components/configuration',  # Wrong - use develop-components/use-configuration-form
        # Invalid Observability paths - do not exist
        'wso2.com/choreo/docs/observability',            # Does not exist
        # Invalid Alert Management paths - do not exist
        'wso2.com/choreo/docs/alert-management',         # Does not exist
        # Invalid Logging paths - do not exist
        'wso2.com/choreo/docs/logging',                  # Does not exist
        # Invalid/hallucinated GitHub repository paths - these repos don't exist
        'github.com/wso2-enterprise/choreo-alert-configuration-service',
        'github.com/wso2-enterprise/choreo-alerts-service',
        'github.com/wso2-enterprise/choreo-notification-service',
        'github.com/wso2-enterprise/choreo-config-service',
        'github.com/wso2-enterprise/choreo-settings-service',
    ]

    # Complete URL patterns that are known to be completely wrong
    KNOWN_INVALID_URLS = [
        'https://wso2.com/choreo/docs/ballerina/',
        'https://wso2.com/choreo/docs/ballerina',
        'https://wso2.com/choreo/docs/developer-tools/',
        'https://wso2.com/choreo/docs/developer-tools',
        'https://wso2.com/choreo/docs/tutorials/',
        'https://wso2.com/choreo/docs/tutorials',
        'https://wso2.com/choreo/docs/guides/',
        'https://wso2.com/choreo/docs/guides',
        'https://wso2.com/choreo/docs/api-reference/',
        'https://wso2.com/choreo/docs/api-reference',
        # Invalid API Management URLs - use internal Choreo APIM Setup Guide
        'https://wso2.com/choreo/docs/api-management/',
        'https://wso2.com/choreo/docs/api-management',
        # Invalid Security URLs - use internal Choreo Light-Weight STS doc
        'https://wso2.com/choreo/docs/security/',
        'https://wso2.com/choreo/docs/security',
        'https://wso2.com/choreo/docs/security/service-authentication/',
        'https://wso2.com/choreo/docs/security/service-authentication',
        'https://wso2.com/choreo/docs/api-management/security/',
        'https://wso2.com/choreo/docs/api-management/security',
        # Invalid Environment Management URLs - correct is devops-and-ci-cd/manage-environments
        'https://wso2.com/choreo/docs/environment-management/',
        'https://wso2.com/choreo/docs/environment-management',
        # Invalid Components Configuration URLs - correct is develop-components/use-configuration-form
        'https://wso2.com/choreo/docs/components/configuration/',
        'https://wso2.com/choreo/docs/components/configuration',
        # Invalid Observability URLs - do not exist
        'https://wso2.com/choreo/docs/observability/',
        'https://wso2.com/choreo/docs/observability',
        # Invalid Alert Management URLs - do not exist
        'https://wso2.com/choreo/docs/alert-management/',
        'https://wso2.com/choreo/docs/alert-management',
        # Invalid Logging URLs - do not exist
        'https://wso2.com/choreo/docs/logging/',
        'https://wso2.com/choreo/docs/logging',
        # Invalid GitHub repos - do not exist
        'https://github.com/wso2-enterprise/choreo-observability',
        'https://github.com/wso2/choreo-observability',
        # Invalid/hallucinated Choreo service repos - these don't exist
        'https://github.com/wso2-enterprise/choreo-alert-configuration-service',
        'https://github.com/wso2-enterprise/choreo-alerts-service',
        'https://github.com/wso2-enterprise/choreo-notification-service',
        'https://github.com/wso2-enterprise/choreo-config-service',
        'https://github.com/wso2-enterprise/choreo-settings-service',
    ]

    # URL Correction Mapping: Maps invalid URL patterns to correct internal documentation URLs
    # When these invalid URLs are detected, they should be replaced with the correct ones
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
    }

    # GitHub URLs that need special handling (authenticated access)
    # These will be validated but with special logic
    GITHUB_ENTERPRISE_DOMAINS = [
        'github.com/wso2-enterprise',  # WSO2 Enterprise GitHub (private repos)
        'github.com/wso2',             # WSO2 public GitHub
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

        # Initialize URL Grounding Service
        self.grounding_service = get_grounding_service() if GROUNDING_AVAILABLE else None
        if self.grounding_service:
            logger.info("URL Grounding Service integrated with URL validator")

    def is_known_invalid_url(self, url: str) -> bool:
        """
        Check if URL matches known invalid URL patterns that LLMs commonly hallucinate.
        These URLs look valid but don't actually exist.

        Args:
            url: URL to check

        Returns:
            True if URL is known to be invalid, False otherwise
        """
        url_lower = url.lower()

        # Check exact matches first
        for invalid_url in self.KNOWN_INVALID_URLS:
            if url_lower == invalid_url.lower() or url_lower.rstrip('/') == invalid_url.lower().rstrip('/'):
                logger.warning(f"URL matches known invalid URL: {url}")
                return True

        # Check pattern matches
        for pattern in self.KNOWN_INVALID_URL_PATTERNS:
            if pattern.lower() in url_lower:
                logger.warning(f"URL matches known invalid pattern '{pattern}': {url}")
                return True

        return False

    def is_trusted_url(self, url: str) -> bool:
        """
        Check if URL is from a trusted domain (non-GitHub).
        GitHub URLs are NOT automatically trusted - they must be validated.
        Known invalid URLs are NEVER trusted even if from trusted domains.

        Args:
            url: URL to check

        Returns:
            True if URL is from a trusted domain, False otherwise
        """
        # First check if this is a known invalid URL - never trust these
        if self.is_known_invalid_url(url):
            return False

        # GitHub URLs should always be validated, not trusted
        if 'github.com' in url:
            return False

        for domain in self.trusted_domains:
            if domain in url:
                return True
        return False

    def is_github_url(self, url: str) -> bool:
        """Check if URL is a GitHub URL."""
        return 'github.com' in url.lower()

    async def validate_github_repo(self, url: str, session: ClientSession) -> bool:
        """
        Validate if a GitHub repository exists and is accessible.
        Uses GitHub API for better reliability than HTTP HEAD requests.

        Args:
            url: GitHub repository URL
            session: aiohttp ClientSession

        Returns:
            True if repository exists and is accessible, False otherwise
        """
        # Extract owner and repo from URL
        # Pattern: github.com/{owner}/{repo}
        pattern = r'github\.com/([^/]+)/([^/]+?)(?:/|$|\?|#)'
        match = re.search(pattern, url)

        if not match:
            logger.warning(f"Invalid GitHub URL format: {url}")
            return False

        owner, repo = match.groups()

        # SPECIAL HANDLING: Trust all wso2-enterprise repositories
        # These are private repos used by Choreo developers internally
        if owner.lower() == 'wso2-enterprise':
            logger.info(f"✓ Trusting wso2-enterprise repository (internal): {owner}/{repo}")
            return True

        # Use GitHub API to check if repo exists
        api_url = f"https://api.github.com/repos/{owner}/{repo}"

        try:
            # GitHub API is more reliable than checking the web URL
            headers = {}
            # If GITHUB_TOKEN is available in environment, use it for private repos
            import os
            github_token = os.getenv('GITHUB_TOKEN')
            if github_token:
                headers['Authorization'] = f'token {github_token}'

            async with session.get(api_url, headers=headers, timeout=self.timeout) as response:
                if response.status == 200:
                    logger.info(f"✓ GitHub repo exists: {owner}/{repo}")
                    return True
                elif response.status == 404:
                    logger.warning(f"✗ GitHub repo NOT FOUND (404): {owner}/{repo}")
                    return False
                elif response.status == 403:
                    # Rate limited or private repo without access
                    logger.warning(f"⚠ GitHub repo access forbidden (403): {owner}/{repo} - may be private")
                    # For private repos, assume they exist if they're in our registry
                    if self.choreo_registry:
                        validation = self.choreo_registry.validate_github_url(url)
                        if validation and validation.get("is_valid"):
                            logger.info(f"✓ Private repo in registry, assuming valid: {owner}/{repo}")
                            return True
                    # Also trust wso2 organization repos (Choreo-related)
                    if owner.lower() == 'wso2':
                        logger.info(f"✓ Trusting wso2 organization repository: {owner}/{repo}")
                        return True
                    return False
                else:
                    logger.warning(f"GitHub API returned status {response.status} for {owner}/{repo}")
                    return False

        except asyncio.TimeoutError:
            logger.warning(f"GitHub API timeout for: {owner}/{repo}")
            return False
        except Exception as e:
            logger.error(f"GitHub API error for {owner}/{repo}: {str(e)}")
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

    def get_correct_url_for_invalid(self, invalid_url: str) -> Optional[str]:
        """
        Get the correct URL replacement for a known invalid URL.

        Args:
            invalid_url: The invalid URL to find a correction for

        Returns:
            The correct URL if a correction exists, None otherwise
        """
        invalid_url_lower = invalid_url.lower()

        for pattern, correct_url in self.URL_CORRECTIONS.items():
            if pattern.lower() in invalid_url_lower:
                logger.info(f"Found URL correction: {invalid_url} -> {correct_url}")
                return correct_url

        return None

    def remove_known_invalid_urls(self, text: str) -> str:
        """
        Remove or replace known invalid URLs from text proactively.
        When a correct URL is available, replaces the invalid URL with the correct one.
        This catches hallucinated URLs before validation.

        Args:
            text: Text potentially containing invalid URLs

        Returns:
            Text with known invalid URLs replaced with correct ones or removed
        """
        filtered_text = text

        # First, try to replace invalid URLs with correct ones
        for pattern, correct_url in self.URL_CORRECTIONS.items():
            # Build regex to match URLs containing this pattern
            url_pattern = r'https?://[^\s\)\]\"\'\,\>\}]*' + re.escape(pattern) + r'[^\s\)\]\"\'\,\>\}]*'
            matches = re.findall(url_pattern, filtered_text, re.IGNORECASE)
            for match in matches:
                logger.info(f"Replacing invalid URL '{match}' with correct URL: {correct_url}")
                filtered_text = filtered_text.replace(match, correct_url)
                # Also handle markdown format - replace the URL in the link
                markdown_pattern = r'(\[[^\]]+\]\()' + re.escape(match) + r'(\))'
                filtered_text = re.sub(markdown_pattern, r'\1' + correct_url + r'\2', filtered_text)

        # Remove exact invalid URLs that don't have corrections
        for invalid_url in self.KNOWN_INVALID_URLS:
            # Skip if this URL has a correction (already handled above)
            has_correction = any(pattern in invalid_url.lower() for pattern in self.URL_CORRECTIONS.keys())
            if has_correction:
                continue

            if invalid_url in filtered_text:
                logger.warning(f"Removing known invalid URL from text: {invalid_url}")
                filtered_text = re.sub(re.escape(invalid_url), "[removed invalid URL]", filtered_text)
                # Also handle markdown format
                markdown_pattern = r'\[([^\]]+)\]\(' + re.escape(invalid_url) + r'\)'
                filtered_text = re.sub(markdown_pattern, r'\1', filtered_text)

        # Remove URLs matching invalid patterns that don't have corrections
        for pattern in self.KNOWN_INVALID_URL_PATTERNS:
            # Skip if this pattern has a correction (already handled above)
            if pattern in self.URL_CORRECTIONS:
                continue

            # Build regex to match URLs containing this pattern
            url_pattern = r'https?://[^\s\)\]\"\'\,\>\}]*' + re.escape(pattern) + r'[^\s\)\]\"\'\,\>\}]*'
            matches = re.findall(url_pattern, filtered_text, re.IGNORECASE)
            for match in matches:
                logger.warning(f"Removing URL matching invalid pattern '{pattern}': {match}")
                filtered_text = filtered_text.replace(match, "[removed invalid URL]")
                # Also handle markdown format
                markdown_pattern = r'\[([^\]]+)\]\(' + re.escape(match) + r'\)'
                filtered_text = re.sub(markdown_pattern, r'\1', filtered_text)

        return filtered_text

    def auto_fix_all_choreo_urls(self, text: str) -> str:
        """
        Aggressively fix ALL wso2 public org URLs to wso2-enterprise in text.
        Also removes known invalid URLs.
        This catches any URLs the LLM generates before validation.

        Args:
            text: Text potentially containing incorrect Choreo URLs

        Returns:
            Text with all wso2 public org URLs fixed to wso2-enterprise and invalid URLs removed
        """
        # FIRST: Remove known invalid URLs
        text = self.remove_known_invalid_urls(text)

        if not self.choreo_registry:
            return text

        # Pattern to match github.com/wso2/choreo-* URLs (but not wso2-enterprise)
        # This will match: github.com/wso2/choreo-console but not github.com/wso2-enterprise/choreo-console
        pattern = r'github\.com/wso2/choreo-([a-zA-Z0-9\-]+)'

        def replace_func(match):
            component = f"choreo-{match.group(1)}"
            # Check if this is a valid Choreo component
            if self.choreo_registry.is_valid_choreo_component(component):
                original_url = match.group(0)
                fixed_url = f"github.com/wso2-enterprise/{component}"
                logger.info(f"Auto-fixed URL in text: {original_url} -> {fixed_url}")
                return fixed_url
            return match.group(0)

        fixed_text = re.sub(pattern, replace_func, text)

        # Also fix full URLs with https://
        pattern_full = r'https://github\.com/wso2/choreo-([a-zA-Z0-9\-]+)'

        def replace_func_full(match):
            component = f"choreo-{match.group(1)}"
            if self.choreo_registry.is_valid_choreo_component(component):
                original_url = match.group(0)
                fixed_url = f"https://github.com/wso2-enterprise/{component}"
                logger.info(f"Auto-fixed full URL in text: {original_url} -> {fixed_url}")
                return fixed_url
            return match.group(0)

        fixed_text = re.sub(pattern_full, replace_func_full, fixed_text)

        return fixed_text

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
        For GitHub URLs, uses GitHub API to verify repository existence.
        For other URLs, uses HTTP HEAD/GET requests.

        Args:
            url: URL to validate
            session: aiohttp ClientSession
            
        Returns:
            True if URL is accessible, False otherwise
        """
        # Check cache first
        if url in self._cache:
            logger.debug(f"URL validation cache hit: {url}")
            return self._cache[url]

        # GitHub URLs get special validation via API
        if self.is_github_url(url):
            async with self._semaphore:
                is_valid = await self.validate_github_repo(url, session)
                self._cache[url] = is_valid
                return is_valid

        # Non-GitHub trusted domains bypass validation
        if self.is_trusted_url(url):
            logger.debug(f"URL is from trusted domain, marking as valid: {url}")
            self._cache[url] = True
            return True

        # Standard HTTP validation for other URLs
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
        
        IMPORTANT: Choreo documentation URLs (wso2.com/choreo/docs/*) are generally kept,
        EXCEPT for known invalid URL patterns that LLMs commonly hallucinate.

        Args:
            text: Text containing URLs
            validation_map: Dictionary mapping URLs to their validation status
            
        Returns:
            Text with invalid URLs removed (except valid Choreo docs URLs which are always kept)
        """
        if not validation_map:
            return text
        
        filtered_text = text
        
        for url, is_valid in validation_map.items():
            if not is_valid:
                # FIRST: Check if this is a known invalid URL - ALWAYS remove these
                if self.is_known_invalid_url(url):
                    logger.warning(f"Removing known invalid URL: {url}")
                    # Remove invalid URLs from text
                    filtered_text = re.sub(re.escape(url), "[URL removed - invalid documentation path]", filtered_text)
                    # Also remove markdown links containing this URL
                    markdown_pattern = r'\[([^\]]+)\]\(' + re.escape(url) + r'\)'
                    filtered_text = re.sub(markdown_pattern, r'\1 [link removed - invalid path]', filtered_text)
                    continue

                # Keep valid Choreo documentation URLs
                # These are trusted URLs from the knowledge base
                if 'wso2.com/choreo/docs' in url or 'docs.choreo.dev' in url:
                    logger.info(f"Keeping Choreo docs URL even though validation failed: {url}")
                    continue  # Skip removal for Choreo docs

                # CRITICAL: NEVER remove wso2-enterprise repository URLs
                # These are internal private repos
                if 'github.com/wso2-enterprise' in url:
                    logger.info(f"Keeping wso2-enterprise repo URL even though validation failed: {url}")
                    continue  # Skip removal for wso2-enterprise repos

                # Only remove non-Choreo URLs that failed validation
                logger.warning(f"Removing invalid non-Choreo URL: {url}")

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
    
    async def validate_answer_urls(self, answer: str, llm_service=None, context: str = "") -> tuple[str, Dict[str, bool]]:
        """
        Validate URLs in the answer text using BOTH LLM intelligence AND accessibility checks.

        This method:
        1. Uses LLM to verify URLs are correct and relevant (if llm_service provided)
        2. Fixes GitHub organization URLs (wso2 -> wso2-enterprise for Choreo repos)
        3. Validates URLs for accessibility (404, timeout, network errors)
        4. Removes URLs that are wrong or inaccessible

        The LLM validates URLs are correct BEFORE checking if they're accessible.

        Args:
            answer: Answer text potentially containing URLs
            llm_service: LLM service instance for intelligent URL validation (optional)
            context: The knowledge base context used to generate the answer

        Returns:
            Tuple of (filtered_answer, validation_map)
        """
        # If validation is disabled, still apply GitHub org URL fixes
        if not self.enable_validation:
            if self.choreo_registry:
                auto_fixed_answer = self.auto_fix_all_choreo_urls(answer)
                return auto_fixed_answer, {}
            return answer, {}

        # Fix all wso2 public org URLs to wso2-enterprise
        auto_fixed_answer = self.auto_fix_all_choreo_urls(answer)

        # STEP 0: Apply URL Grounding - correct known invalid URLs before validation
        if self.grounding_service:
            logger.info("Applying URL grounding to correct known invalid URLs")
            auto_fixed_answer = await self.grounding_service.ground_text(auto_fixed_answer)

        # Extract URLs from the answer
        urls = self.extract_urls_from_text(auto_fixed_answer)

        if not urls:
            return auto_fixed_answer, {}

        # STEP 1: LLM-based URL validation (if LLM service is available)
        llm_validated_urls = {}
        if llm_service:
            logger.info(f"Using LLM to validate {len(urls)} URLs for correctness and relevance")
            llm_validated_urls = await self._validate_urls_with_llm(urls, llm_service, context, answer)
        else:
            # If no LLM service, assume all URLs need HTTP validation
            llm_validated_urls = {url: True for url in urls}

        # STEP 2: Fix any incorrect Choreo URLs
        url_fixes = {}
        for url in urls:
            if llm_validated_urls.get(url, False):  # Only fix URLs that LLM validated
                fixed_url, is_choreo = self.validate_and_fix_choreo_url(url)
                if fixed_url != url:
                    url_fixes[url] = fixed_url

        # Apply fixes to the answer text
        fixed_answer = auto_fixed_answer
        for old_url, new_url in url_fixes.items():
            fixed_answer = fixed_answer.replace(old_url, new_url)
            logger.info(f"Replaced URL in answer: {old_url} -> {new_url}")

        # Get the updated list of URLs after fixes
        updated_urls = self.extract_urls_from_text(fixed_answer)

        # Filter to only URLs that passed LLM validation
        urls_to_validate = [url for url in updated_urls if llm_validated_urls.get(url, True)]

        # STEP 3: HTTP validation for accessibility (404 check)
        validation_map = await self.validate_urls(urls_to_validate)

        # Combine LLM validation results with HTTP validation
        final_validation = {}
        for url in updated_urls:
            llm_valid = llm_validated_urls.get(url, True)
            http_valid = validation_map.get(url, False)
            final_validation[url] = llm_valid and http_valid

            if not llm_valid:
                logger.warning(f"URL failed LLM validation (incorrect/irrelevant): {url}")
            elif not http_valid:
                logger.warning(f"URL failed HTTP validation (404/timeout): {url}")

        # STEP 4: Filter out invalid URLs
        filtered_answer = self.filter_valid_urls_from_text(fixed_answer, final_validation)

        return filtered_answer, final_validation

    async def _validate_urls_with_llm(self, urls: List[str], llm_service, context: str, answer: str) -> Dict[str, bool]:
        """
        Use LLM to validate if URLs are correct and relevant.

        IMPORTANT: Choreo documentation URLs and wso2-enterprise repo URLs are AUTOMATICALLY APPROVED
        without LLM validation. We trust these URLs from the knowledge base.

        Args:
            urls: List of URLs to validate
            llm_service: LLM service instance
            context: The knowledge base context
            answer: The answer containing the URLs

        Returns:
            Dictionary mapping URL to LLM validation result (True/False)
        """
        if not urls:
            return {}

        # Pre-validate: Automatically approve Choreo docs and wso2-enterprise URLs
        validation_results = {}
        urls_to_validate = []

        for url in urls:
            # FIRST: Check if this is a known invalid URL - NEVER approve these
            if self.is_known_invalid_url(url):
                validation_results[url] = False
                logger.warning(f"❌ Rejected known invalid URL: {url}")
            # ALWAYS approve Choreo documentation URLs (after checking known invalid patterns)
            elif 'wso2.com/choreo/docs' in url or 'docs.choreo.dev' in url:
                validation_results[url] = True
                logger.info(f"✅ Auto-approved Choreo docs URL (trusted): {url}")
            # ALWAYS approve wso2-enterprise repository URLs
            elif 'github.com/wso2-enterprise' in url:
                validation_results[url] = True
                logger.info(f"✅ Auto-approved wso2-enterprise repo URL (trusted): {url}")
            # ALWAYS approve docs-choreo-dev repo
            elif 'github.com/wso2/docs-choreo-dev' in url:
                validation_results[url] = True
                logger.info(f"✅ Auto-approved docs-choreo-dev URL (trusted): {url}")
            else:
                # Other URLs need LLM validation
                urls_to_validate.append(url)

        # If all URLs are trusted, return immediately
        if not urls_to_validate:
            logger.info("All URLs are trusted Choreo/wso2-enterprise URLs, skipping LLM validation")
            return validation_results

        # Create a prompt for the LLM to validate remaining URLs
        url_list = "\n".join([f"{i+1}. {url}" for i, url in enumerate(urls_to_validate)])

        validation_prompt = f"""You are a URL validation expert for Choreo documentation and repositories.

TASK: Validate if the following URLs are CORRECT and RELEVANT to the answer.

KNOWLEDGE BASE CONTEXT:
{context[:2000] if context else "No context available"}

ANSWER PROVIDED:
{answer[:1000]}

URLS TO VALIDATE:
{url_list}

VALIDATION CRITERIA:
1. Is the URL structure correct for Choreo documentation?
   - Correct: https://wso2.com/choreo/docs/choreo-cli/get-started-with-the-choreo-cli/
   - Correct: https://wso2.com/choreo/docs/references/faq/#choreo-cli
   - Wrong: https://wso2.com/choreo/docs/developer-tools/choreo-cli/
   
2. Is the URL relevant to the answer content?
3. Does the URL path make logical sense?
4. For repository URLs: Is it wso2-enterprise organization?

RESPOND WITH ONLY:
For each URL, write either "VALID" or "INVALID" followed by the URL number.
Example:
VALID: 1
INVALID: 2
VALID: 3

Be lenient - mark as VALID unless the URL is clearly wrong."""

        try:
            # Get LLM response
            llm_response = llm_service.get_response(validation_prompt, max_tokens=500)

            logger.info(f"LLM URL validation response: {llm_response}")

            # Parse the LLM response for non-trusted URLs
            for url_idx, url in enumerate(urls_to_validate, 1):
                # Check if LLM marked this URL as valid
                if f"VALID: {url_idx}" in llm_response or f"VALID:{url_idx}" in llm_response:
                    validation_results[url] = True
                    logger.info(f"✅ LLM validated URL {url_idx}: {url}")
                elif f"INVALID: {url_idx}" in llm_response or f"INVALID:{url_idx}" in llm_response:
                    validation_results[url] = False
                    logger.warning(f"❌ LLM rejected URL {url_idx}: {url}")
                else:
                    # Default to True if LLM didn't explicitly reject
                    validation_results[url] = True
                    logger.info(f"⚠️ LLM unclear on URL {url_idx}, defaulting to valid: {url}")

            return validation_results

        except Exception as e:
            logger.error(f"LLM URL validation failed: {e}")
            # If LLM validation fails, default all remaining URLs to valid
            for url in urls_to_validate:
                validation_results[url] = True
            return validation_results

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

