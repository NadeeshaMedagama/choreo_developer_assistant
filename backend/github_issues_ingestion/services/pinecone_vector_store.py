"""
Pinecone Vector Store Service.
Implements IVectorStore interface.
"""

from typing import List, Dict, Any, Optional
import uuid

from pinecone import Pinecone, ServerlessSpec

from ..interfaces.vector_store import IVectorStore
from ..models.chunk import TextChunk


class PineconeVectorStore(IVectorStore):
    """Service for storing and querying vectors in Pinecone."""

    def __init__(
        self,
        api_key: str,
        index_name: str,
        dimension: int = 1536,
        metric: str = "cosine",
        cloud: str = "aws",
        region: str = "us-east-1",
        namespace: Optional[str] = None
    ):
        """
        Initialize Pinecone Vector Store.

        Args:
            api_key: Pinecone API key
            index_name: Pinecone index name
            dimension: Embedding dimension
            metric: Distance metric (cosine, euclidean, dotproduct)
            cloud: Cloud provider
            region: Cloud region
            namespace: Optional namespace for organizing vectors
        """
        self.api_key = api_key
        self.index_name = index_name
        self.dimension = dimension
        self.metric = metric
        self.cloud = cloud
        self.region = region
        self.namespace = namespace

        # Initialize Pinecone
        self.pc = Pinecone(api_key=api_key)

        # Get or create index
        existing_indexes = [idx.name for idx in self.pc.list_indexes()]

        if index_name not in existing_indexes:
            print(f"Creating new Pinecone index: {index_name}")
            self.pc.create_index(
                name=index_name,
                dimension=dimension,
                metric=metric,
                spec=ServerlessSpec(
                    cloud=cloud,
                    region=region
                )
            )
            print(f"Index {index_name} created successfully")
        else:
            print(f"Using existing Pinecone index: {index_name}")

        # Connect to index
        self.index = self.pc.Index(index_name)
        print(f"Connected to Pinecone index: {index_name}")

    def store_chunk(self, chunk: TextChunk, vector: List[float]) -> str:
        """
        Store a single chunk with its vector.

        Args:
            chunk: TextChunk object
            vector: Embedding vector

        Returns:
            ID of the stored chunk
        """
        # Generate ID if not present
        chunk_id = chunk.chunk_id or str(uuid.uuid4())
        chunk.chunk_id = chunk_id

        # Prepare metadata
        metadata = {
            "content": chunk.content[:1000],  # Limit content size in metadata
            "chunk_index": chunk.chunk_index,
            "total_chunks": chunk.total_chunks,
            "created_at": chunk.created_at.isoformat(),
            **chunk.metadata  # Include all custom metadata
        }

        # Ensure metadata values are valid types
        metadata = self._sanitize_metadata(metadata)

        # Upsert to Pinecone
        self.index.upsert(
            vectors=[(chunk_id, vector, metadata)],
            namespace=self.namespace or ""
        )

        return chunk_id

    def store_chunks_batch(self, chunks: List[TextChunk], vectors: List[List[float]]) -> List[str]:
        """
        Store multiple chunks with their vectors in batch.

        Args:
            chunks: List of TextChunk objects
            vectors: List of embedding vectors

        Returns:
            List of IDs for stored chunks
        """
        if len(chunks) != len(vectors):
            raise ValueError("Number of chunks must match number of vectors")

        if not chunks:
            return []

        # Prepare batch data
        upsert_data = []
        chunk_ids = []

        for chunk, vector in zip(chunks, vectors):
            # Generate ID if not present
            chunk_id = chunk.chunk_id or str(uuid.uuid4())
            chunk.chunk_id = chunk_id
            chunk_ids.append(chunk_id)

            # Prepare metadata
            metadata = {
                "content": chunk.content[:1000],  # Limit content size
                "chunk_index": chunk.chunk_index,
                "total_chunks": chunk.total_chunks,
                "created_at": chunk.created_at.isoformat(),
                **chunk.metadata
            }

            # Sanitize metadata
            metadata = self._sanitize_metadata(metadata)

            upsert_data.append((chunk_id, vector, metadata))

        # Batch upsert (Pinecone supports up to 100 vectors per request)
        batch_size = 100
        for i in range(0, len(upsert_data), batch_size):
            batch = upsert_data[i:i + batch_size]
            self.index.upsert(
                vectors=batch,
                namespace=self.namespace or ""
            )
            
            print(f"Stored {min(i + batch_size, len(upsert_data))}/{len(upsert_data)} chunks")

        print(f"Successfully stored {len(chunks)} chunks in Pinecone")
        return chunk_ids

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
        # Query Pinecone
        results = self.index.query(
            vector=query_vector,
            top_k=top_k,
            include_metadata=True,
            namespace=self.namespace or "",
            filter=filter_dict
        )

        # Format results
        matches = []
        for match in results.get("matches", []):
            matches.append({
                "id": match.get("id"),
                "score": match.get("score"),
                "metadata": match.get("metadata", {}),
                "content": match.get("metadata", {}).get("content", "")
            })

        return matches

    def delete_by_metadata(self, filter_dict: Dict[str, Any]) -> int:
        """
        Delete vectors by metadata filter.

        Args:
            filter_dict: Metadata filters

        Returns:
            Number of vectors deleted (Note: Pinecone doesn't return count)
        """
        try:
            self.index.delete(
                filter=filter_dict,
                namespace=self.namespace or ""
            )
            print(f"Deleted vectors matching filter: {filter_dict}")
            return -1  # Pinecone doesn't return count
        except Exception as e:
            print(f"Error deleting vectors: {e}")
            raise

    def get_stats(self) -> Dict[str, Any]:
        """
        Get index statistics.

        Returns:
            Dictionary with index stats
        """
        return self.index.describe_index_stats()

    def _sanitize_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize metadata to ensure all values are valid Pinecone types.

        Args:
            metadata: Raw metadata dictionary

        Returns:
            Sanitized metadata dictionary
        """
        sanitized = {}
        
        for key, value in metadata.items():
            # Pinecone supports: str, int, float, bool, list of str
            if isinstance(value, (str, int, float, bool)):
                sanitized[key] = value
            elif isinstance(value, list):
                # Convert list items to strings
                sanitized[key] = [str(item) for item in value]
            elif value is None:
                continue  # Skip None values
            else:
                # Convert other types to string
                sanitized[key] = str(value)
        
        return sanitized

