"""
Azure OpenAI Embedding Service.
Implements IEmbeddingService interface.
"""

from typing import List
import gc
from openai import AzureOpenAI

from ..interfaces.embedding_service import IEmbeddingService


class AzureEmbeddingService(IEmbeddingService):
    """Service for generating embeddings using Azure OpenAI."""

    def __init__(
        self,
        api_key: str,
        endpoint: str,
        deployment: str,
        api_version: str = "2024-02-01"
    ):
        """
        Initialize Azure Embedding Service.

        Args:
            api_key: Azure OpenAI API key
            endpoint: Azure OpenAI endpoint URL
            deployment: Embeddings deployment name
            api_version: API version
        """
        self.api_key = api_key
        self.endpoint = endpoint
        self.deployment = deployment
        self.api_version = api_version
        
        # Initialize Azure OpenAI client
        self.client = AzureOpenAI(
            api_key=api_key,
            api_version=api_version,
            azure_endpoint=endpoint
        )
        
        # Embedding dimension for text-embedding-ada-002 and text-embedding-3-small
        # For text-embedding-3-large, use 3072
        self.embedding_dimension = 1536
        
        print(f"Initialized Azure OpenAI Embedding Service with deployment: {deployment}")

    def create_embedding(self, text: str) -> List[float]:
        """
        Create embedding for a single text.

        Args:
            text: Text to embed

        Returns:
            Embedding vector

        Raises:
            Exception: If embedding creation fails
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")

        try:
            response = self.client.embeddings.create(
                input=text,
                model=self.deployment
            )
            
            embedding = response.data[0].embedding
            
            # Clean up
            del response
            
            return embedding
        
        except Exception as e:
            print(f"Error creating embedding: {e}")
            raise

    def create_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Create embeddings for multiple texts in batches.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors

        Raises:
            Exception: If embedding creation fails
        """
        if not texts:
            return []

        # Filter out empty texts
        valid_texts = [t for t in texts if t and t.strip()]
        
        if not valid_texts:
            raise ValueError("No valid texts to embed")

        embeddings = []
        
        # Process in small batches to prevent memory issues
        batch_size = 10
        
        for i in range(0, len(valid_texts), batch_size):
            batch = valid_texts[i:i + batch_size]
            
            try:
                response = self.client.embeddings.create(
                    input=batch,
                    model=self.deployment
                )
                
                # Extract embeddings
                batch_embeddings = [item.embedding for item in response.data]
                embeddings.extend(batch_embeddings)
                
                # Clean up
                del response, batch_embeddings
                gc.collect()
                
                # Progress logging
                if (i + batch_size) % 50 == 0:
                    print(f"Created embeddings for {i + batch_size}/{len(valid_texts)} texts")
            
            except Exception as e:
                print(f"Error creating embeddings for batch {i//batch_size}: {e}")
                raise

        print(f"Successfully created {len(embeddings)} embeddings")
        return embeddings

    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of the embeddings.

        Returns:
            Embedding dimension
        """
        return self.embedding_dimension

    def set_embedding_dimension(self, dimension: int):
        """
        Set the embedding dimension.
        
        Args:
            dimension: Embedding dimension (1536 or 3072)
        """
        if dimension not in [1536, 3072]:
            raise ValueError("Embedding dimension must be 1536 or 3072")
        self.embedding_dimension = dimension

