#!/usr/bin/env python3
"""Quick test to verify Milvus int64 ID works."""

import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

from github_issues_ingestion.config import Settings
from github_issues_ingestion.services import MilvusVectorStore
from github_issues_ingestion.models.chunk import TextChunk
from datetime import datetime

print("Loading settings...")
settings = Settings.from_env()

print(f"Connecting to Milvus collection: {settings.milvus_collection_name}")
vector_store = MilvusVectorStore(
    uri=settings.milvus_uri,
    token=settings.milvus_token,
    collection_name=settings.milvus_collection_name,
    dimension=settings.milvus_dimension
)

# Create a test chunk
test_chunk = TextChunk(
    content="This is a test GitHub issue chunk for verification.",
    chunk_index=0,
    total_chunks=1,
    metadata={
        "source": "test",
        "repository": "test/repo",
        "issue_number": 999,
        "issue_title": "Test Issue"
    },
    created_at=datetime.now()
)

# Create a dummy vector (1536 dimensions)
test_vector = [0.1] * 1536

print("\nStoring test chunk...")
try:
    chunk_id = vector_store.store_chunk(test_chunk, test_vector)
    print(f"✓ Successfully stored chunk with ID: {chunk_id}")
    print("✓ The int64 ID fix is working!")
except Exception as e:
    print(f"✗ Error storing chunk: {e}")
    sys.exit(1)

print("\nTest completed successfully!")

