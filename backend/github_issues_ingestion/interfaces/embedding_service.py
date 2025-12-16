"""
Interface for embedding services.
Following Interface Segregation Principle.
"""

from abc import ABC, abstractmethod
from typing import List


class IEmbeddingService(ABC):
    """Interface for generating embeddings from text."""

    @abstractmethod
    def create_embedding(self, text: str) -> List[float]:
        """
        Create embedding for a single text.

        Args:
            text: Text to embed

        Returns:
            Embedding vector
        """
        pass

    @abstractmethod
    def create_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Create embeddings for multiple texts.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        pass

    @abstractmethod
    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of the embeddings.

        Returns:
            Embedding dimension
        """
        pass

