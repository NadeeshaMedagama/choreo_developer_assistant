"""
Configuration for Wiki Ingestion System.
"""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class WikiIngestionConfig:
    """Configuration for wiki ingestion."""

    # Wiki settings
    wiki_url: str
    max_depth: int = 2
    max_pages: int = 50
    fetch_linked_content: bool = True
    max_linked_urls: int = 50

    # Chunking settings
    chunk_size: int = 1000
    chunk_overlap: int = 200
    min_chunk_size: int = 100

    # Fetching settings
    request_timeout: int = 30
    max_retries: int = 3
    backoff_factor: float = 0.5
    user_agent: Optional[str] = None
    github_token: Optional[str] = None

    # Milvus Vector Database settings (optional)
    milvus_uri: Optional[str] = None
    milvus_token: Optional[str] = None
    milvus_collection_name: Optional[str] = None

    # Embedding settings (optional)
    azure_openai_endpoint: Optional[str] = None
    azure_openai_api_key: Optional[str] = None
    azure_embedding_deployment: Optional[str] = None

    @classmethod
    def from_env(cls) -> 'WikiIngestionConfig':
        """Load configuration from environment variables."""
        return cls(
            # Wiki settings
            wiki_url=os.getenv('WIKI_URL', ''),
            max_depth=int(os.getenv('WIKI_MAX_DEPTH', '2')),
            max_pages=int(os.getenv('WIKI_MAX_PAGES', '50')),
            fetch_linked_content=os.getenv('WIKI_FETCH_LINKED', 'true').lower() == 'true',
            max_linked_urls=int(os.getenv('WIKI_MAX_LINKED_URLS', '50')),

            # Chunking settings
            chunk_size=int(os.getenv('CHUNK_SIZE', '1000')),
            chunk_overlap=int(os.getenv('CHUNK_OVERLAP', '200')),
            min_chunk_size=int(os.getenv('MIN_CHUNK_SIZE', '100')),

            # Fetching settings
            request_timeout=int(os.getenv('REQUEST_TIMEOUT', '30')),
            max_retries=int(os.getenv('MAX_RETRIES', '3')),
            backoff_factor=float(os.getenv('BACKOFF_FACTOR', '0.5')),
            user_agent=os.getenv('USER_AGENT'),
            github_token=os.getenv('GITHUB_TOKEN'),

            # Milvus Vector Database settings
            milvus_uri=os.getenv('MILVUS_URI'),
            milvus_token=os.getenv('MILVUS_TOKEN'),
            milvus_collection_name=os.getenv('MILVUS_COLLECTION_NAME', 'readme_embeddings'),

            # Embedding settings
            azure_openai_endpoint=os.getenv('AZURE_OPENAI_ENDPOINT'),
            azure_openai_api_key=os.getenv('AZURE_OPENAI_API_KEY'),
            azure_embedding_deployment=os.getenv('AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT'),
        )

    def validate(self) -> bool:
        """Validate configuration."""
        if not self.wiki_url:
            raise ValueError("WIKI_URL is required")

        if self.max_depth < 0:
            raise ValueError("max_depth must be >= 0")

        if self.max_pages < 1:
            raise ValueError("max_pages must be >= 1")

        if self.chunk_size < self.min_chunk_size:
            raise ValueError("chunk_size must be >= min_chunk_size")

        if self.chunk_overlap >= self.chunk_size:
            raise ValueError("chunk_overlap must be < chunk_size")

        return True

