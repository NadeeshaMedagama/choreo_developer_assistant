"""
Vector Store Repository

Responsible for interacting with Milvus vector database.
Handles storage and retrieval of embeddings.
"""

from typing import List, Dict, Any, Optional
import time

from ..models import EmbeddingRecord
from ..utils.logger import get_logger

logger = get_logger(__name__)


class VectorStoreRepository:
    """Repository for storing and retrieving embeddings in Milvus."""

    def __init__(self, uri: str, token: str, collection_name: str):
        """
        Initialize Milvus repository.

        Args:
            uri: Milvus URI
            token: Milvus token
            collection_name: Name of the collection to use
        """
        self.uri = uri
        self.token = token
        self.collection_name = collection_name

        try:
            from pymilvus import MilvusClient

            # Initialize Milvus
            self.client = MilvusClient(uri=uri, token=token)

            # Check if collection exists, create if not
            if not self.client.has_collection(collection_name=collection_name):
                logger.warning(f"Collection '{collection_name}' not found, creating it...")
                self.client.create_collection(
                    collection_name=collection_name,
                    dimension=1536,  # text-embedding-3-small dimension
                    metric_type='COSINE',
                    auto_id=False,
                    enable_dynamic_field=True
                )
                logger.info(f"✓ Created collection: {collection_name}")

            logger.info(f"✓ Connected to Milvus collection: {collection_name}")

        except Exception as e:
            logger.error(f"Failed to initialize Milvus: {e}")
            raise

    def store_embeddings(self, embedding_records: List[EmbeddingRecord], batch_size: int = 100) -> int:
        """
        Store embeddings in Milvus.

        Args:
            embedding_records: List of EmbeddingRecord objects
            batch_size: Number of embeddings to upload per batch

        Returns:
            Number of embeddings stored
        """
        logger.info(f"Storing {len(embedding_records)} embeddings in Milvus")

        if not embedding_records:
            return 0

        total_stored = 0

        # Process in batches
        for i in range(0, len(embedding_records), batch_size):
            batch = embedding_records[i:i + batch_size]

            try:
                # Convert to Milvus format
                data_list = []
                for record in batch:
                    milvus_data = record.to_milvus_format()
                    data_list.append(milvus_data)

                # Insert to Milvus
                self.client.insert(
                    collection_name=self.collection_name,
                    data=data_list
                )
                total_stored += len(data_list)

                logger.info(f"  Stored batch {i // batch_size + 1}: {len(data_list)} embeddings")

                # Small delay to avoid rate limits
                time.sleep(0.2)

            except Exception as e:
                logger.error(f"Failed to store batch {i // batch_size + 1}: {e}")
                continue

        logger.info(f"✓ Successfully stored {total_stored} embeddings")
        return total_stored

    def query(self, query_vector: List[float], top_k: int = 10, filter_dict: Optional[Dict] = None) -> List[Dict]:
        """
        Query Milvus for similar embeddings.

        Args:
            query_vector: Query embedding vector
            top_k: Number of results to return
            filter_dict: Optional metadata filter

        Returns:
            List of matching results
        """
        try:
            # Build filter expression if provided
            filter_expr = None
            if filter_dict:
                conditions = []
                for key, value in filter_dict.items():
                    if isinstance(value, str):
                        conditions.append(f'{key} == "{value}"')
                    else:
                        conditions.append(f'{key} == {value}')
                filter_expr = " && ".join(conditions) if conditions else None

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
                    matches.append({
                        "id": match.get("id"),
                        "score": match.get("distance", 0.0),
                        "entity": match.get("entity", {})
                    })

            return matches

        except Exception as e:
            logger.error(f"Query failed: {e}")
            return []

    def delete_by_source(self, source_path: str):
        """
        Delete all embeddings from a specific source file.

        Args:
            source_path: Path to source file
        """
        try:
            filter_expr = f'file_path == "{source_path}"'
            self.client.delete(
                collection_name=self.collection_name,
                filter=filter_expr
            )
            logger.info(f"✓ Deleted embeddings from: {source_path}")
        except Exception as e:
            logger.error(f"Failed to delete embeddings: {e}")

    def get_index_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the Milvus collection.

        Returns:
            Dictionary with collection statistics
        """
        try:
            stats = self.client.get_collection_stats(collection_name=self.collection_name)
            return {
                "total_vectors": stats.get("row_count", 0),
                "collection_name": self.collection_name
            }
        except Exception as e:
            logger.error(f"Failed to get collection stats: {e}")
            return {}

