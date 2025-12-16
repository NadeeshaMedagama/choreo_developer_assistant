"""
Interface for vector storage operations.
Following Interface Segregation Principle.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from ..models.chunk import TextChunk


class IVectorStore(ABC):
    """Interface for storing and querying vector embeddings."""

    @abstractmethod
    def store_chunk(self, chunk: TextChunk, vector: List[float]) -> str:
        """
        Store a single chunk with its vector.

        Args:
            chunk: TextChunk object
            vector: Embedding vector

        Returns:
            ID of the stored chunk
        """
        pass

    @abstractmethod
    def store_chunks_batch(self, chunks: List[TextChunk], vectors: List[List[float]]) -> List[str]:
        """
        Store multiple chunks with their vectors in batch.

        Args:
            chunks: List of TextChunk objects
            vectors: List of embedding vectors

        Returns:
            List of IDs for stored chunks
        """
        pass

    @abstractmethod
    def query_similar(
        self,
        query_vector: List[float],
        top_k: int = 5,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Query for similar vectors.

        Args:
            query_vector: Query embedding vector
            top_k: Number of results to return
            filter_dict: Optional metadata filters

        Returns:
            List of matches with metadata and scores
        """
        pass

    @abstractmethod
    def delete_by_metadata(self, filter_dict: Dict[str, Any]) -> int:
        """
        Delete vectors by metadata filter.

        Args:
            filter_dict: Metadata filters

        Returns:
            Number of vectors deleted
        """
        pass

