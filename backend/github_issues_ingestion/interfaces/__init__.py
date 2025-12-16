"""
Interfaces package for GitHub Issues Ingestion system.
Following Interface Segregation Principle (ISP) from SOLID.
"""

from .issue_fetcher import IIssueFetcher
from .text_processor import ITextProcessor
from .chunker import IChunker
from .embedding_service import IEmbeddingService
from .vector_store import IVectorStore

__all__ = [
    "IIssueFetcher",
    "ITextProcessor",
    "IChunker",
    "IEmbeddingService",
    "IVectorStore",
]

