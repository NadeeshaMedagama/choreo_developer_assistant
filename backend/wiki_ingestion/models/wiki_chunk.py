"""
WikiChunk Model.
Represents a chunk of wiki content ready for embedding.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from datetime import datetime
import uuid


@dataclass
class WikiChunk:
    """Model representing a chunk of wiki content."""

    chunk_id: str
    text: str
    chunk_index: int
    
    # Source information
    source_url: str
    source_title: str
    source_type: str = "wiki_page"  # wiki_page, linked_content, etc.
    
    # Repository info
    repository: Optional[str] = None
    owner: Optional[str] = None
    
    # Chunk metadata
    chunk_size: int = 0
    total_chunks: int = 0
    
    # Content metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        """Calculate chunk size if not provided."""
        if self.chunk_size == 0:
            self.chunk_size = len(self.text)
    
    @staticmethod
    def generate_id() -> str:
        """Generate a unique chunk ID."""
        return str(uuid.uuid4())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for vector storage."""
        return {
            "chunk_id": self.chunk_id,
            "text": self.text,
            "chunk_index": self.chunk_index,
            "source_url": self.source_url,
            "source_title": self.source_title,
            "source_type": self.source_type,
            "repository": self.repository,
            "owner": self.owner,
            "chunk_size": self.chunk_size,
            "total_chunks": self.total_chunks,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
    
    def to_vector_metadata(self) -> Dict[str, Any]:
        """
        Convert to metadata format for Pinecone.
        Only includes fields that should be stored as metadata (not the text itself).
        """
        return {
            "chunk_id": self.chunk_id,
            "chunk_index": self.chunk_index,
            "source_url": self.source_url,
            "source_title": self.source_title,
            "source_type": self.source_type,
            "repository": self.repository or "",
            "owner": self.owner or "",
            "chunk_size": self.chunk_size,
            "total_chunks": self.total_chunks,
            **self.metadata,  # Include additional metadata
        }
    
    def __str__(self) -> str:
        """String representation."""
        return f"WikiChunk(id={self.chunk_id[:8]}..., index={self.chunk_index}, url={self.source_url})"
    
    def __repr__(self) -> str:
        """Detailed representation."""
        return (
            f"WikiChunk(chunk_id={self.chunk_id!r}, "
            f"chunk_index={self.chunk_index}, "
            f"source_url={self.source_url!r}, "
            f"chunk_size={self.chunk_size})"
        )

