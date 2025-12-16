"""
GitHub Issues Ingestion System

A SOLID-based system for ingesting GitHub issues, chunking text,
creating embeddings, and storing in a vector database.

Architecture:
- Interfaces: Define contracts (Interface Segregation Principle)
- Models: Data structures
- Services: Implementations (Single Responsibility Principle)
- Config: Configuration management
- Utils: Helper functions

Usage:
    from github_issues_ingestion import create_ingestion_pipeline
    
    # Create pipeline with default settings from .env
    orchestrator = create_ingestion_pipeline()
    
    # Ingest a repository
    stats = orchestrator.ingest_repository("owner", "repo")
    
    # Query issues
    results = orchestrator.query_issues("your query here")
"""

from .config import Settings
from .services import (
    GitHubIssueFetcher,
    TextProcessorService,
    ChunkingService,
    AzureEmbeddingService,
    MilvusVectorStore,
    IngestionOrchestrator,
)


def create_ingestion_pipeline(
    settings: Settings = None,
    batch_size: int = 10
) -> IngestionOrchestrator:
    """
    Factory function to create a fully configured ingestion orchestrator.
    
    Args:
        settings: Settings object (loads from .env if not provided)
        batch_size: Batch size for processing
    
    Returns:
        Configured IngestionOrchestrator instance
    """
    # Load settings from environment if not provided
    if settings is None:
        settings = Settings.from_env()
    
    # Create all services (Dependency Injection)
    issue_fetcher = GitHubIssueFetcher(token=settings.github_token)
    
    text_processor = TextProcessorService(include_code_blocks=True)
    
    chunker = ChunkingService(
        chunk_size=settings.chunk_size,
        overlap=settings.chunk_overlap
    )
    
    embedding_service = AzureEmbeddingService(
        api_key=settings.azure_openai_api_key,
        endpoint=settings.azure_openai_endpoint,
        deployment=settings.azure_openai_embeddings_deployment,
        api_version=settings.azure_openai_api_version
    )
    
    vector_store = MilvusVectorStore(
        uri=settings.milvus_uri,
        token=settings.milvus_token,
        collection_name=settings.milvus_collection_name,
        dimension=settings.milvus_dimension
    )
    
    # Create orchestrator with all dependencies
    orchestrator = IngestionOrchestrator(
        issue_fetcher=issue_fetcher,
        text_processor=text_processor,
        chunker=chunker,
        embedding_service=embedding_service,
        vector_store=vector_store,
        batch_size=batch_size or settings.batch_size
    )
    
    return orchestrator


__all__ = [
    "Settings",
    "GitHubIssueFetcher",
    "TextProcessorService",
    "ChunkingService",
    "AzureEmbeddingService",
    "MilvusVectorStore",
    "IngestionOrchestrator",
    "create_ingestion_pipeline",
]

