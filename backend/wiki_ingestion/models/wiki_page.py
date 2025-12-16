"""
WikiPage Model.
Represents a single wiki page with its content and metadata.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Set
from datetime import datetime


@dataclass
class WikiPage:
    """Model representing a wiki page."""

    url: str
    title: str
    content: str
    raw_html: Optional[str] = None
    markdown: Optional[str] = None
    
    # URLs found within the content
    internal_urls: Set[str] = field(default_factory=set)
    external_urls: Set[str] = field(default_factory=set)
    
    # Metadata
    repository: Optional[str] = None
    owner: Optional[str] = None
    wiki_name: Optional[str] = None
    page_path: Optional[str] = None
    
    # Timestamps
    fetched_at: datetime = field(default_factory=datetime.utcnow)
    last_modified: Optional[datetime] = None
    
    # Additional metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Processing info
    depth: int = 0
    parent_url: Optional[str] = None
    
    def __post_init__(self):
        """Ensure sets are mutable."""
        if not isinstance(self.internal_urls, set):
            self.internal_urls = set(self.internal_urls) if self.internal_urls else set()
        if not isinstance(self.external_urls, set):
            self.external_urls = set(self.external_urls) if self.external_urls else set()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "url": self.url,
            "title": self.title,
            "content": self.content,
            "raw_html": self.raw_html,
            "markdown": self.markdown,
            "internal_urls": list(self.internal_urls),
            "external_urls": list(self.external_urls),
            "repository": self.repository,
            "owner": self.owner,
            "wiki_name": self.wiki_name,
            "page_path": self.page_path,
            "fetched_at": self.fetched_at.isoformat() if self.fetched_at else None,
            "last_modified": self.last_modified.isoformat() if self.last_modified else None,
            "metadata": self.metadata,
            "depth": self.depth,
            "parent_url": self.parent_url,
        }
    
    def get_all_urls(self) -> Set[str]:
        """Get all URLs (internal + external)."""
        return self.internal_urls.union(self.external_urls)
    
    def __str__(self) -> str:
        """String representation."""
        return f"WikiPage(url={self.url}, title={self.title}, depth={self.depth})"
    
    def __repr__(self) -> str:
        """Detailed representation."""
        return (
            f"WikiPage(url={self.url!r}, title={self.title!r}, "
            f"internal_urls={len(self.internal_urls)}, "
            f"external_urls={len(self.external_urls)}, "
            f"depth={self.depth})"
        )

