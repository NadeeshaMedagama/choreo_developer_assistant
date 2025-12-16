"""
Content Extractor Service Implementation.
Extracts and processes content from HTML pages.
"""

import re
from typing import Dict, Any
from bs4 import BeautifulSoup
import html2text

from ..interfaces.content_extractor import IContentExtractor


class ContentExtractorService(IContentExtractor):
    """Service for extracting and cleaning content from HTML."""

    def __init__(self):
        """Initialize content extractor."""
        # Configure html2text
        self.html_converter = html2text.HTML2Text()
        self.html_converter.ignore_links = False
        self.html_converter.ignore_images = False
        self.html_converter.ignore_emphasis = False
        self.html_converter.body_width = 0  # Don't wrap lines
        self.html_converter.single_line_break = False
    
    def extract_content(self, html: str, url: str) -> Dict[str, Any]:
        """
        Extract meaningful content from HTML.

        Args:
            html: Raw HTML content
            url: Source URL

        Returns:
            Dictionary with extracted content (title, body, metadata)
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
            element.decompose()
        
        # Extract title
        title = self._extract_title(soup)
        
        # Extract main content
        main_content = self._extract_main_content(soup)
        
        # Extract text
        text = main_content.get_text(separator='\n', strip=True)
        
        # Convert to markdown
        markdown = self.extract_markdown(str(main_content))
        
        # Extract metadata
        metadata = self.extract_metadata(html, url)
        
        return {
            "title": title,
            "content": text,
            "markdown": markdown,
            "html": str(main_content),
            "metadata": metadata,
        }
    
    def extract_markdown(self, html: str) -> str:
        """
        Convert HTML to markdown format.

        Args:
            html: Raw HTML content

        Returns:
            Markdown formatted text
        """
        try:
            markdown = self.html_converter.handle(html)
            return self.clean_content(markdown)
        except Exception as e:
            print(f"⚠️  Error converting to markdown: {e}")
            # Fallback to plain text
            soup = BeautifulSoup(html, 'html.parser')
            return soup.get_text(separator='\n', strip=True)
    
    def clean_content(self, content: str) -> str:
        """
        Clean and normalize content.

        Args:
            content: Raw content text

        Returns:
            Cleaned content
        """
        # Remove excessive whitespace
        content = re.sub(r'\n{3,}', '\n\n', content)
        content = re.sub(r' {2,}', ' ', content)
        
        # Remove leading/trailing whitespace from lines
        lines = [line.rstrip() for line in content.split('\n')]
        content = '\n'.join(lines)
        
        # Remove common wiki artifacts
        content = re.sub(r'\[edit\]', '', content)  # Remove [edit] links
        content = re.sub(r'\^\s*\[\d+\]', '', content)  # Remove citation markers
        
        return content.strip()
    
    def extract_metadata(self, html: str, url: str) -> Dict[str, Any]:
        """
        Extract metadata from HTML (title, description, keywords, etc.).

        Args:
            html: Raw HTML content
            url: Source URL

        Returns:
            Dictionary of metadata
        """
        soup = BeautifulSoup(html, 'html.parser')
        metadata = {}
        
        # Extract meta tags
        for meta in soup.find_all('meta'):
            name = meta.get('name', '').lower()
            property_attr = meta.get('property', '').lower()
            content = meta.get('content', '')
            
            if name in ['description', 'keywords', 'author']:
                metadata[name] = content
            elif property_attr.startswith('og:'):
                metadata[property_attr] = content
        
        # Extract canonical URL
        canonical = soup.find('link', rel='canonical')
        if canonical and canonical.get('href'):
            metadata['canonical_url'] = canonical['href']
        
        # Extract language
        html_tag = soup.find('html')
        if html_tag and html_tag.get('lang'):
            metadata['language'] = html_tag['lang']
        
        return metadata
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title from various sources."""
        # Try different title sources in order of preference
        
        # 1. h1 tag
        h1 = soup.find('h1')
        if h1:
            return h1.get_text(strip=True)
        
        # 2. title tag
        title_tag = soup.find('title')
        if title_tag:
            title = title_tag.get_text(strip=True)
            # Remove common suffixes
            title = re.sub(r'\s*[-|·]\s*.*$', '', title)
            return title
        
        # 3. First header
        for header in ['h2', 'h3', 'h4']:
            header_tag = soup.find(header)
            if header_tag:
                return header_tag.get_text(strip=True)
        
        return "Untitled"
    
    def _extract_main_content(self, soup: BeautifulSoup) -> BeautifulSoup:
        """Extract the main content area from the page."""
        # Try to find main content container
        # GitHub wiki uses specific classes
        main_content = (
            soup.find('div', class_='markdown-body') or
            soup.find('article') or
            soup.find('main') or
            soup.find('div', id='wiki-body') or
            soup.find('div', class_='wiki-body') or
            soup.find('div', role='main') or
            soup.find('body')
        )
        
        return main_content or soup

