"""
Web Crawler Service Implementation.
Crawls websites and extracts pages with their content and links.
"""

import re
from typing import List, Set, Dict, Optional
from urllib.parse import urljoin, urlparse, urlunparse
from bs4 import BeautifulSoup
from collections import deque

from ..interfaces.web_crawler import IWebCrawler
from ..interfaces.url_fetcher import IUrlFetcher
from ..interfaces.content_extractor import IContentExtractor
from ..models.wiki_page import WikiPage


class WebCrawlerService(IWebCrawler):
    """Service for crawling websites and extracting content."""

    def __init__(
        self,
        url_fetcher: IUrlFetcher,
        content_extractor: IContentExtractor,
        max_pages: int = 100,
        respect_robots: bool = True
    ):
        """
        Initialize web crawler.

        Args:
            url_fetcher: Service for fetching URLs
            content_extractor: Service for extracting content
            max_pages: Maximum number of pages to crawl
            respect_robots: Whether to respect robots.txt (future implementation)
        """
        self.url_fetcher = url_fetcher
        self.content_extractor = content_extractor
        self.max_pages = max_pages
        self.respect_robots = respect_robots
        
        # Tracking
        self.visited_urls: Set[str] = set()
        self.pages: List[WikiPage] = []
    
    def crawl(self, start_url: str, max_depth: int = 3) -> List[WikiPage]:
        """
        Crawl a website starting from the given URL.

        Args:
            start_url: Starting URL to begin crawling
            max_depth: Maximum depth to crawl (0 = only start page, 1 = start + linked pages, etc.)

        Returns:
            List of WikiPage objects containing page data
        """
        print(f"\n{'='*80}")
        print(f"🕷️  Starting crawl from: {start_url}")
        print(f"📊 Max depth: {max_depth}, Max pages: {self.max_pages}")
        print(f"{'='*80}\n")
        
        # Reset state
        self.visited_urls.clear()
        self.pages.clear()
        
        # BFS queue: (url, depth, parent_url)
        queue = deque([(start_url, 0, None)])
        
        # Extract base domain for filtering
        base_domain = self._extract_domain(start_url)
        base_path = self._extract_base_path(start_url)
        
        while queue and len(self.pages) < self.max_pages:
            url, depth, parent_url = queue.popleft()
            
            # Normalize URL
            url = self._normalize_url(url)
            
            # Skip if already visited
            if url in self.visited_urls:
                continue
            
            # Skip if exceeds max depth
            if depth > max_depth:
                continue
            
            # Skip if not valid
            if not self.is_valid_url(url, base_domain):
                continue
            
            # Mark as visited
            self.visited_urls.add(url)
            
            # Extract page
            print(f"📄 [{len(self.pages) + 1}/{self.max_pages}] Crawling (depth {depth}): {url}")
            page = self.extract_page(url)
            
            if page:
                page.depth = depth
                page.parent_url = parent_url
                self.pages.append(page)
                
                # Extract links and add to queue for next level
                if depth < max_depth:
                    links = self._extract_internal_links(page, base_domain, base_path)
                    for link in links:
                        if link not in self.visited_urls:
                            queue.append((link, depth + 1, url))
                    
                    print(f"   ✓ Found {len(links)} internal links")
            else:
                print(f"   ✗ Failed to extract page")
        
        print(f"\n{'='*80}")
        print(f"✅ Crawl complete! Extracted {len(self.pages)} pages")
        print(f"{'='*80}\n")
        
        return self.pages
    
    def extract_page(self, url: str) -> Optional[WikiPage]:
        """
        Extract a single page's content.

        Args:
            url: URL of the page to extract

        Returns:
            WikiPage object with extracted content
        """
        # Fetch HTML
        html = self.url_fetcher.fetch(url)
        if not html:
            return None
        
        try:
            # Extract content
            extracted = self.content_extractor.extract_content(html, url)
            
            # Extract all links
            internal_links, external_links = self._extract_all_links(html, url)
            
            # Parse repository info from URL
            repo_info = self._parse_github_url(url)
            
            # Create WikiPage
            page = WikiPage(
                url=url,
                title=extracted['title'],
                content=extracted['content'],
                raw_html=html,
                markdown=extracted['markdown'],
                internal_urls=internal_links,
                external_urls=external_links,
                repository=repo_info.get('repository'),
                owner=repo_info.get('owner'),
                wiki_name=repo_info.get('wiki_name'),
                page_path=repo_info.get('page_path'),
                metadata=extracted['metadata'],
            )
            
            return page
            
        except Exception as e:
            print(f"❌ Error extracting page {url}: {e}")
            return None
    
    def extract_links(self, content: str, base_url: str) -> Set[str]:
        """
        Extract all links from HTML/markdown content.

        Args:
            content: HTML or markdown content
            base_url: Base URL for resolving relative links

        Returns:
            Set of absolute URLs found in the content
        """
        soup = BeautifulSoup(content, 'html.parser')
        links = set()
        
        # Extract from <a> tags
        for link in soup.find_all('a', href=True):
            href = link['href']
            absolute_url = urljoin(base_url, href)
            links.add(absolute_url)
        
        return links
    
    def is_valid_url(self, url: str, base_domain: str) -> bool:
        """
        Check if a URL is valid and should be crawled.

        Args:
            url: URL to validate
            base_domain: Base domain to restrict crawling to

        Returns:
            True if URL should be crawled, False otherwise
        """
        try:
            parsed = urlparse(url)
            
            # Must have scheme and netloc
            if not parsed.scheme or not parsed.netloc:
                return False
            
            # Must be HTTP(S)
            if parsed.scheme not in ['http', 'https']:
                return False
            
            # Must be same domain (for wiki crawling)
            url_domain = f"{parsed.netloc}{parsed.path.split('/wiki/')[0]}" if '/wiki/' in parsed.path else parsed.netloc
            if base_domain not in url_domain:
                return False
            
            # Skip common non-content URLs
            skip_patterns = [
                r'/wiki/_',  # Special wiki pages
                r'\.pdf$',
                r'\.zip$',
                r'\.tar\.gz$',
                r'/edit$',
                r'/history$',
                r'/compare',
                r'#',  # Fragment-only URLs (handled separately)
            ]
            
            for pattern in skip_patterns:
                if re.search(pattern, url):
                    return False
            
            return True
            
        except Exception:
            return False
    
    def _extract_all_links(self, html: str, base_url: str) -> tuple[Set[str], Set[str]]:
        """Extract and categorize all links from HTML."""
        soup = BeautifulSoup(html, 'html.parser')
        internal_links = set()
        external_links = set()
        
        base_domain = self._extract_domain(base_url)
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            
            # Skip anchors and special URLs
            if href.startswith('#') or href.startswith('javascript:') or href.startswith('mailto:'):
                continue
            
            # Make absolute
            absolute_url = urljoin(base_url, href)
            
            # Remove fragments
            absolute_url = absolute_url.split('#')[0]
            
            # Categorize
            if base_domain in absolute_url:
                internal_links.add(absolute_url)
            else:
                external_links.add(absolute_url)
        
        return internal_links, external_links
    
    def _extract_internal_links(self, page: WikiPage, base_domain: str, base_path: str) -> Set[str]:
        """Extract only wiki-internal links for crawling."""
        internal = set()
        
        for url in page.internal_urls:
            # Only include wiki pages from the same wiki
            if '/wiki/' in url and base_path in url:
                internal.add(url)
        
        return internal
    
    def _normalize_url(self, url: str) -> str:
        """Normalize URL for comparison."""
        parsed = urlparse(url)
        
        # Remove fragment
        normalized = urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            parsed.query,
            ''  # Remove fragment
        ))
        
        # Remove trailing slash
        if normalized.endswith('/'):
            normalized = normalized[:-1]
        
        return normalized
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        parsed = urlparse(url)
        return parsed.netloc
    
    def _extract_base_path(self, url: str) -> str:
        """Extract base wiki path from URL."""
        # For GitHub wikis: https://github.com/owner/repo/wiki
        parsed = urlparse(url)
        path_parts = parsed.path.split('/wiki/')
        if len(path_parts) > 0:
            return path_parts[0] + '/wiki/'
        return parsed.path
    
    def _parse_github_url(self, url: str) -> Dict[str, Optional[str]]:
        """Parse GitHub wiki URL to extract repository info."""
        parsed = urlparse(url)
        
        # Pattern: github.com/owner/repo/wiki/Page-Name
        match = re.match(r'/([^/]+)/([^/]+)/wiki/?(.*)$', parsed.path)
        
        if match:
            owner, repo, page_path = match.groups()
            return {
                'owner': owner,
                'repository': f"{owner}/{repo}",
                'wiki_name': repo,
                'page_path': page_path or 'Home',
            }
        
        return {
            'owner': None,
            'repository': None,
            'wiki_name': None,
            'page_path': None,
        }

