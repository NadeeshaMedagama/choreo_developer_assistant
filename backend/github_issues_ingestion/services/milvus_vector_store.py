"""
Milvus Vector Store Service.
Implements IVectorStore interface.
"""

from typing import List, Dict, Any, Optional
import uuid

from pymilvus import MilvusClient

from ..interfaces.vector_store import IVectorStore
from ..models.chunk import TextChunk


class MilvusVectorStore(IVectorStore):
    """Service for storing and querying vectors in Milvus."""

    def __init__(
        self,
        uri: str,
        token: str,
        collection_name: str,
        dimension: int = 1536,
        metric: str = "COSINE",
        **kwargs  # For backward compatibility
    ):
        """
        Initialize Milvus Vector Store.

        Args:
            uri: Milvus URI
            token: Milvus token
            collection_name: Milvus collection name
            dimension: Embedding dimension
            metric: Distance metric (COSINE, L2, IP)
        """
        self.uri = uri
        self.token = token
        self.collection_name = collection_name
        self.dimension = dimension
        self.metric = metric

        # Initialize Milvus
        self.client = MilvusClient(uri=uri, token=token)

        # Get or create collection
        if not self.client.has_collection(collection_name=collection_name):
            print(f"Creating new Milvus collection: {collection_name}")
            self.client.create_collection(
                collection_name=collection_name,
                dimension=dimension,
                metric_type=metric,
                auto_id=False,
                enable_dynamic_field=True
            )
            print(f"Collection {collection_name} created successfully")
        else:
            print(f"Using existing Milvus collection: {collection_name}")

        print(f"Connected to Milvus collection: {collection_name}")

    def store_chunk(self, chunk: TextChunk, vector: List[float]) -> str:
        """
        Store a single chunk with its vector.

        Args:
            chunk: TextChunk object
            vector: Embedding vector

        Returns:
            ID of the stored chunk
        """
        # Generate string ID if not present
        chunk_id_str = chunk.chunk_id or str(uuid.uuid4())
        chunk.chunk_id = chunk_id_str

        # Convert string ID to int64 for Milvus (using hash)
        chunk_id_int = abs(hash(chunk_id_str)) % (2**63 - 1)

        # Prepare metadata
        metadata = {
            "id": chunk_id_int,  # Use int64 ID
            "vector": vector,
            "content": chunk.content[:1000],  # Limit content size in metadata
            "chunk_id_str": chunk_id_str,  # Store original string ID in dynamic field
            "chunk_index": chunk.chunk_index,
            "total_chunks": chunk.total_chunks,
            "created_at": chunk.created_at.isoformat(),
            **chunk.metadata  # Include all custom metadata
        }

        # Ensure metadata values are valid types
        metadata = self._sanitize_metadata(metadata)

        # Insert to Milvus
        self.client.insert(
            collection_name=self.collection_name,
            data=[metadata]
        )

        return chunk_id_str

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
        data_list = []
        chunk_ids = []

        for chunk, vector in zip(chunks, vectors):
            # Generate string ID if not present
            chunk_id_str = chunk.chunk_id or str(uuid.uuid4())
            chunk.chunk_id = chunk_id_str
            chunk_ids.append(chunk_id_str)

            # Convert string ID to int64 for Milvus (using hash)
            chunk_id_int = abs(hash(chunk_id_str)) % (2**63 - 1)

            # Prepare metadata
            metadata = {
                "id": chunk_id_int,  # Use int64 ID
                "vector": vector,
                "content": chunk.content[:1000],  # Limit content size
                "chunk_id_str": chunk_id_str,  # Store original string ID in dynamic field
                "chunk_index": chunk.chunk_index,
                "total_chunks": chunk.total_chunks,
                "created_at": chunk.created_at.isoformat(),
                **chunk.metadata
            }

            # Sanitize metadata
            metadata = self._sanitize_metadata(metadata)
            data_list.append(metadata)

        # Batch insert (Milvus can handle large batches)
        batch_size = 100
        for i in range(0, len(data_list), batch_size):
            batch = data_list[i:i + batch_size]
            self.client.insert(
                collection_name=self.collection_name,
                data=batch
            )
            
            print(f"Stored {min(i + batch_size, len(data_list))}/{len(data_list)} chunks")

        print(f"Successfully stored {len(chunks)} chunks in Milvus")
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
        # Build filter expression if provided
        filter_expr = None
        if filter_dict:
            filter_expr = self._build_filter_expression(filter_dict)

        # Query Milvus
        results = self.client.search(
            collection_name=self.collection_name,
            data=[query_vector],
            limit=top_k,
            output_fields=["*"],
            filter=filter_expr
        )

        # Format results
        matches = []
        if results and len(results) > 0:
            for match in results[0]:
                entity = match.get("entity", {})
                matches.append({
                    "id": match.get("id"),
                    "score": match.get("distance", 0.0),
                    "metadata": {k: v for k, v in entity.items() if k not in ["id", "vector"]},
                    "content": entity.get("content", "")
                })

        return matches

    def delete_by_metadata(self, filter_dict: Dict[str, Any]) -> int:
        """
        Delete vectors by metadata filter.

        Args:
            filter_dict: Metadata filters

        Returns:
            Number of vectors deleted
        """
        try:
            # Build filter expression
            filter_expr = self._build_filter_expression(filter_dict)
            
            # Delete entities matching the filter
            self.client.delete(
                collection_name=self.collection_name,
                filter=filter_expr
            )
            print(f"Deleted vectors matching filter: {filter_dict}")
            return -1  # Milvus doesn't return exact count in serverless
        except Exception as e:
            print(f"Error deleting vectors: {e}")
            raise

    def get_stats(self) -> Dict[str, Any]:
        """
        Get collection statistics.

        Returns:
            Dictionary with collection stats
        """
        try:
            stats = self.client.get_collection_stats(collection_name=self.collection_name)
            return stats
        except Exception as e:
            print(f"Error getting stats: {e}")
            return {}

    def _sanitize_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize metadata to ensure all values are valid Milvus types.

        Args:
            metadata: Raw metadata dictionary

        Returns:
            Sanitized metadata dictionary
        """
        sanitized = {}
        
        for key, value in metadata.items():
            # Milvus supports: str, int, float, bool, list
            if isinstance(value, (str, int, float, bool, list)):
                sanitized[key] = value
            elif value is None:
                continue  # Skip None values
            else:
                # Convert other types to string
                sanitized[key] = str(value)
        
        return sanitized

    def _build_filter_expression(self, filter_dict: Dict[str, Any]) -> str:
        """
        Build Milvus filter expression from filter dictionary.

        Args:
            filter_dict: Dictionary of filters

        Returns:
            Milvus filter expression string
        """
        conditions = []
        for key, value in filter_dict.items():
            if isinstance(value, dict) and "$eq" in value:
                val = value["$eq"]
                if isinstance(val, str):
                    conditions.append(f'{key} == "{val}"')
                else:
                    conditions.append(f'{key} == {val}')
            elif isinstance(value, str):
                conditions.append(f'{key} == "{value}"')
            elif isinstance(value, (int, float, bool)):
                conditions.append(f'{key} == {value}')
        
        return " && ".join(conditions) if conditions else ""

