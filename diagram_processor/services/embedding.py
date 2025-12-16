"""
Embedding Service

Responsible for generating embeddings from text chunks and storing them.
"""

from typing import List, Dict, Any, Optional
import hashlib
import time

from ..models import TextChunk, EmbeddingRecord
from ..utils.logger import get_logger

logger = get_logger(__name__)


class EmbeddingService:
    """Service for generating and managing embeddings."""

    def __init__(self, openai_api_key: str, embedding_model: str = "text-embedding-3-small",
                 azure_endpoint: Optional[str] = None, azure_api_version: Optional[str] = None,
                 azure_deployment: Optional[str] = None):
        """
        Initialize embedding service.

        Args:
            openai_api_key: OpenAI or Azure OpenAI API key
            embedding_model: Model to use for embeddings (or Azure deployment name)
            azure_endpoint: Azure OpenAI endpoint (if using Azure)
            azure_api_version: Azure OpenAI API version (if using Azure)
            azure_deployment: Azure OpenAI embeddings deployment name (if using Azure)
        """
        self.api_key = openai_api_key
        self.embedding_model = embedding_model
        self.is_azure = azure_endpoint is not None

        try:
            if self.is_azure:
                # Use Azure OpenAI
                from openai import AzureOpenAI
                self.client = AzureOpenAI(
                    api_key=openai_api_key,
                    api_version=azure_api_version or "2024-02-01",
                    azure_endpoint=azure_endpoint
                )
                self.embedding_model = azure_deployment or embedding_model
                logger.info(f"✓ Azure OpenAI embedding client initialized with deployment: {self.embedding_model}")
            else:
                # Use standard OpenAI
                from openai import OpenAI
                self.client = OpenAI(api_key=openai_api_key)
                logger.info(f"✓ OpenAI embedding client initialized with model: {embedding_model}")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            raise

    def generate_embeddings(self, chunks: List[TextChunk]) -> List[EmbeddingRecord]:
        """
        Generate embeddings for a list of chunks.

        Args:
            chunks: List of TextChunk objects

        Returns:
            List of EmbeddingRecord objects
        """
        logger.info(f"Generating embeddings for {len(chunks)} chunks")

        if not chunks:
            return []

        embedding_records = []

        # Process in batches to avoid rate limits
        batch_size = 100
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            batch_embeddings = self._generate_batch(batch)
            embedding_records.extend(batch_embeddings)

            logger.info(f"  Processed {min(i + batch_size, len(chunks))}/{len(chunks)} chunks")

            # Small delay to avoid rate limits
            if i + batch_size < len(chunks):
                time.sleep(0.5)

        logger.info(f"✓ Generated {len(embedding_records)} embeddings")
        return embedding_records

    def _generate_batch(self, chunks: List[TextChunk]) -> List[EmbeddingRecord]:
        """
        Generate embeddings for a batch of chunks.

        Args:
            chunks: List of TextChunk objects

        Returns:
            List of EmbeddingRecord objects
        """
        try:
            # Extract text content
            texts = [chunk.content for chunk in chunks]

            # Call OpenAI API
            response = self.client.embeddings.create(
                model=self.embedding_model,
                input=texts
            )

            # Create EmbeddingRecord objects
            records = []
            for chunk, embedding_data in zip(chunks, response.data):
                embedding_id = self._generate_embedding_id(chunk)
                record = EmbeddingRecord(
                    chunk=chunk,
                    vector=embedding_data.embedding,
                    embedding_id=embedding_id
                )
                records.append(record)

            return records

        except Exception as e:
            logger.error(f"Failed to generate embeddings: {e}")
            raise

    def _generate_embedding_id(self, chunk: TextChunk) -> str:
        """
        Generate a unique ID for an embedding.

        Args:
            chunk: TextChunk object

        Returns:
            Unique string ID
        """
        # Create ID from file path, chunk index, and content hash
        content_hash = hashlib.md5(chunk.content.encode()).hexdigest()[:8]
        file_hash = hashlib.md5(str(chunk.source_file.file_path).encode()).hexdigest()[:8]

        return f"diagram_{file_hash}_{chunk.chunk_index}_{content_hash}"
