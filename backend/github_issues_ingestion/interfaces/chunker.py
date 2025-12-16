"""
Interface for chunking text.
Following Interface Segregation Principle.
"""

from abc import ABC, abstractmethod
from typing import List
from ..models.chunk import TextChunk


class IChunker(ABC):
    """Interface for chunking text into smaller parts."""

    @abstractmethod
    def chunk_text(self, text: str, metadata: dict = None) -> List[TextChunk]:
        """
        Chunk text into smaller parts with overlap.

        Args:
            text: Text to chunk
            metadata: Additional metadata to attach to each chunk

        Returns:
            List of TextChunk objects
        """
        pass

    @abstractmethod
    def get_chunk_size(self) -> int:
        """Get the configured chunk size."""
        pass

    @abstractmethod
    def get_overlap(self) -> int:
        """Get the configured overlap size."""
        pass

