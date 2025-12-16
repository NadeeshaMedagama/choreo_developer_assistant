"""
Chunking Service.
Implements IChunker interface.
"""

from typing import List, Dict, Any
from ..interfaces.chunker import IChunker
from ..models.chunk import TextChunk


class ChunkingService(IChunker):
    """Service for chunking text into smaller parts with overlap."""

    def __init__(self, chunk_size: int = 1000, overlap: int = 200):
        """
        Initialize Chunking Service.

        Args:
            chunk_size: Size of each chunk in characters
            overlap: Number of overlapping characters between chunks
        """
        if chunk_size <= 0:
            raise ValueError("Chunk size must be positive")
        
        if overlap < 0:
            raise ValueError("Overlap cannot be negative")
        
        if overlap >= chunk_size:
            raise ValueError("Overlap must be less than chunk size")

        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_text(self, text: str, metadata: dict = None) -> List[TextChunk]:
        """
        Chunk text into smaller parts with overlap.

        Args:
            text: Text to chunk
            metadata: Additional metadata to attach to each chunk

        Returns:
            List of TextChunk objects
        """
        if not text or not text.strip():
            return []

        # Clean the text
        text = text.strip()
        
        # If text is smaller than chunk size, return as single chunk
        if len(text) <= self.chunk_size:
            return [
                TextChunk(
                    content=text,
                    chunk_index=0,
                    total_chunks=1,
                    metadata=metadata or {},
                )
            ]

        chunks = []
        start = 0
        chunk_index = 0

        # Calculate total number of chunks
        step = self.chunk_size - self.overlap
        total_chunks = max(1, (len(text) - self.overlap + step - 1) // step)

        while start < len(text):
            end = start + self.chunk_size
            
            # Get the chunk
            chunk_text = text[start:end]
            
            # Try to break at sentence boundary if possible
            if end < len(text):
                # Look for sentence endings near the end of chunk
                sentence_endings = ['. ', '.\n', '! ', '!\n', '? ', '?\n']
                best_break = -1
                
                # Search backwards from end for a good break point
                search_start = max(0, len(chunk_text) - 100)
                for ending in sentence_endings:
                    pos = chunk_text.rfind(ending, search_start)
                    if pos > best_break:
                        best_break = pos + len(ending)
                
                # Use sentence break if found
                if best_break > 0:
                    chunk_text = chunk_text[:best_break]

            # Create chunk
            chunk = TextChunk(
                content=chunk_text.strip(),
                chunk_index=chunk_index,
                total_chunks=total_chunks,
                metadata=metadata or {},
            )
            chunks.append(chunk)

            # Move to next chunk
            if end >= len(text):
                break
            
            start += self.chunk_size - self.overlap
            chunk_index += 1

        # Update total chunks count (in case it changed)
        actual_total = len(chunks)
        for chunk in chunks:
            chunk.total_chunks = actual_total

        return chunks

    def chunk_by_tokens(
        self,
        text: str,
        metadata: dict = None,
        max_tokens: int = 500,
        overlap_tokens: int = 50
    ) -> List[TextChunk]:
        """
        Chunk text by token count (approximate using words).

        Args:
            text: Text to chunk
            metadata: Additional metadata to attach to each chunk
            max_tokens: Maximum tokens per chunk (approximated by words)
            overlap_tokens: Overlap in tokens

        Returns:
            List of TextChunk objects
        """
        if not text or not text.strip():
            return []

        # Split into words (rough token approximation)
        words = text.split()
        
        if len(words) <= max_tokens:
            return [
                TextChunk(
                    content=text,
                    chunk_index=0,
                    total_chunks=1,
                    metadata=metadata or {},
                )
            ]

        chunks = []
        start = 0
        chunk_index = 0
        step = max_tokens - overlap_tokens

        # Calculate total chunks
        total_chunks = max(1, (len(words) - overlap_tokens + step - 1) // step)

        while start < len(words):
            end = min(start + max_tokens, len(words))
            chunk_words = words[start:end]
            chunk_text = ' '.join(chunk_words)

            chunk = TextChunk(
                content=chunk_text.strip(),
                chunk_index=chunk_index,
                total_chunks=total_chunks,
                metadata=metadata or {},
            )
            chunks.append(chunk)

            if end >= len(words):
                break

            start += step
            chunk_index += 1

        # Update total chunks count
        actual_total = len(chunks)
        for chunk in chunks:
            chunk.total_chunks = actual_total

        return chunks

    def get_chunk_size(self) -> int:
        """Get the configured chunk size."""
        return self.chunk_size

    def get_overlap(self) -> int:
        """Get the configured overlap size."""
        return self.overlap

    def set_chunk_size(self, chunk_size: int):
        """Set a new chunk size."""
        if chunk_size <= 0:
            raise ValueError("Chunk size must be positive")
        if self.overlap >= chunk_size:
            raise ValueError("Overlap must be less than chunk size")
        self.chunk_size = chunk_size

    def set_overlap(self, overlap: int):
        """Set a new overlap size."""
        if overlap < 0:
            raise ValueError("Overlap cannot be negative")
        if overlap >= self.chunk_size:
            raise ValueError("Overlap must be less than chunk size")
        self.overlap = overlap

