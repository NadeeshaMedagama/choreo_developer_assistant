"""
TextChunk model representing a chunk of text with metadata.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from datetime import datetime


@dataclass
class TextChunk:
    """Represents a chunk of text with associated metadata."""

    content: str
    chunk_index: int
    total_chunks: int
    metadata: Dict[str, Any] = field(default_factory=dict)
    chunk_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        """Validate chunk data after initialization."""
        if not self.content or not self.content.strip():
            raise ValueError("Chunk content cannot be empty")
        
        if self.chunk_index < 0:
            raise ValueError("Chunk index must be non-negative")
        
        if self.total_chunks <= 0:
            raise ValueError("Total chunks must be positive")
        
        if self.chunk_index >= self.total_chunks:
            raise ValueError("Chunk index must be less than total chunks")

    def to_dict(self) -> Dict[str, Any]:
        """Convert chunk to dictionary for storage."""
        return {
            "content": self.content,
            "chunk_index": self.chunk_index,
            "total_chunks": self.total_chunks,
            "metadata": self.metadata,
            "chunk_id": self.chunk_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TextChunk":
        """Create chunk from dictionary."""
        created_at = data.get("created_at")
        if created_at and isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        
        return cls(
            content=data["content"],
            chunk_index=data["chunk_index"],
            total_chunks=data["total_chunks"],
            metadata=data.get("metadata", {}),
            chunk_id=data.get("chunk_id"),
            created_at=created_at or datetime.utcnow(),
        )

    def __repr__(self) -> str:
        """String representation of chunk."""
        content_preview = self.content[:50] + "..." if len(self.content) > 50 else self.content
        return f"TextChunk(index={self.chunk_index}/{self.total_chunks}, content='{content_preview}')"

