from typing import List, Dict, Any, Optional
import uuid

try:
    from utils.logger import get_logger
except ImportError:
    # Fallback logger if utils.logger is not available
    import logging
    def get_logger(name):
        return logging.getLogger(name)

logger = get_logger(__name__)

try:
    from pymilvus import MilvusClient, DataType, Collection, connections
    MILVUS_AVAILABLE = True
except ImportError:
    MilvusClient = None
    DataType = None
    Collection = None
    connections = None
    MILVUS_AVAILABLE = False
    logger.warning("Milvus not installed. Install with: pip install pymilvus")


class VectorClient:
    """Client for Milvus vector database operations."""

    def __init__(
        self,
        uri: str,
        token: str,
        collection_name: str,
        dimension: Optional[int] = None,
        metric: str = "COSINE",
        **kwargs  # Accept extra args for backward compatibility
    ):
        if not MILVUS_AVAILABLE:
            raise RuntimeError("Milvus SDK not installed. Install with: pip install pymilvus")

        self.uri = uri
        self.token = token
        self.collection_name = collection_name
        self.dimension = dimension or 1536
        self.metric = metric
        self.client = None

        # Initialize Milvus client
        try:
            self.client = MilvusClient(
                uri=self.uri,
                token=self.token
            )

            # Check if collection exists, create if not
            if not self.client.has_collection(collection_name=self.collection_name):
                logger.info(f"Creating new Milvus collection: {self.collection_name}")
                self._create_collection()
            else:
                logger.info(f"Using existing Milvus collection: {self.collection_name}")

            logger.info(f"Connected to Milvus collection: {self.collection_name}")

        except Exception as e:
            logger.warning(f"Failed to connect to Milvus: {e}")
            logger.info("Application will continue but vector operations will fail until Milvus is accessible")

    def _create_collection(self):
        """Create a new Milvus collection with the appropriate schema."""
        try:
            # Create collection with auto-id and vector field
            self.client.create_collection(
                collection_name=self.collection_name,
                dimension=self.dimension,
                metric_type=self.metric,
                auto_id=False,  # We'll provide IDs
                enable_dynamic_field=True  # Allow dynamic metadata fields
            )
            logger.info(f"Created Milvus collection '{self.collection_name}' with dimension {self.dimension}")
        except Exception as e:
            logger.error(f"Failed to create collection: {e}")
            raise

    def _collection_exists(self, name: str) -> bool:
        """Check if a Milvus collection exists."""
        try:
            return self.client.has_collection(collection_name=name)
        except Exception as e:
            logger.warning(f"Failed to check Milvus collection: {e}")
            return False

    def _ensure_collection(self, dimension: Optional[int] = None):
        """Ensure the target collection exists; create if necessary."""
        if self.client is None:
            raise RuntimeError("Milvus client not initialized")

        if not self._collection_exists(self.collection_name):
            dim = self.dimension or dimension
            if not dim:
                raise ValueError("Milvus collection does not exist and dimension is unknown")

            logger.info(
                f"Creating Milvus collection '{self.collection_name}' with dimension {dim}, "
                f"metric {self.metric}"
            )

            self.client.create_collection(
                collection_name=self.collection_name,
                dimension=int(dim),
                metric_type=self.metric,
                auto_id=False,
                enable_dynamic_field=True
            )

        if not self.dimension and dimension:
            self.dimension = int(dimension)

    def insert_embedding(self, content: str, vector: List[float], metadata: Optional[Dict[str, Any]] = None):
        """Insert a single embedding into Milvus."""
        self._ensure_collection(dimension=len(vector))

        doc_id = str(uuid.uuid4())
        meta = metadata or {}

        # Prepare data for insertion
        data = {
            "id": doc_id,
            "vector": vector,
            "content": content,
            **meta  # Include all metadata fields
        }

        try:
            self.client.insert(
                collection_name=self.collection_name,
                data=[data]
            )
            logger.info(f"Inserted embedding with id: {doc_id}")
            return doc_id
        except Exception as e:
            logger.error(f"Failed to insert embedding: {e}")
            raise

    def insert_embeddings_batch(self, items: List[Dict[str, Any]]):
        """Insert multiple embeddings in batch.

        Args:
            items: List of dicts with keys 'content', 'vector', and optional 'metadata'
        """
        if not items:
            return []

        self._ensure_collection(dimension=len(items[0]["vector"]))

        data_list = []
        doc_ids = []

        import random
        import time
        base_time = int(time.time() * 1000000)

        for idx, item in enumerate(items):
            # Generate a unique integer ID from timestamp, index, and random number
            doc_id = base_time + idx * 1000 + random.randint(100, 999)
            doc_ids.append(doc_id)
            meta = item.get("metadata", {})

            data = {
                "id": doc_id,
                "vector": item["vector"],
                "content": item["content"],
                **meta  # Include all metadata fields
            }
            data_list.append(data)

        try:
            self.client.insert(
                collection_name=self.collection_name,
                data=data_list
            )
            logger.info(f"Inserted {len(data_list)} embeddings in batch")
            return doc_ids
        except Exception as e:
            logger.error(f"Failed to insert batch embeddings: {e}")
            raise

    def query_similar(self, vector: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """Query for similar vectors."""
        self._ensure_collection(dimension=len(vector))

        try:
            res = self.client.search(
                collection_name=self.collection_name,
                data=[vector],
                limit=top_k,
                output_fields=["*"]  # Return all fields including metadata
            )
        except Exception as e:
            logger.error(f"Milvus query failed: {e}")
            raise

        results: List[Dict[str, Any]] = []

        # Milvus returns results as list of lists
        if res and len(res) > 0:
            for match in res[0]:
                entity = match.get("entity", {})
                results.append({
                    "content": entity.get("content", ""),
                    "score": match.get("distance", 0.0),  # Milvus uses 'distance' instead of 'score'
                    "id": match.get("id"),
                    "metadata": {k: v for k, v in entity.items() if k not in ["id", "vector", "content"]}
                })

        return results

    def query_by_metadata(self, metadata_filter: Dict[str, Any], top_k: int = 1) -> List[Dict[str, Any]]:
        """Query vectors by metadata filter.

        Args:
            metadata_filter: Dictionary of metadata fields to filter by
            top_k: Number of results to return

        Returns:
            List of matching vectors with metadata
        """
        self._ensure_collection()

        try:
            # Build filter expression for Milvus
            filter_expr = self._build_filter_expression(metadata_filter)

            # Use query with filter (no vector search, just filtering)
            res = self.client.query(
                collection_name=self.collection_name,
                filter=filter_expr,
                output_fields=["*"],
                limit=top_k
            )

            results: List[Dict[str, Any]] = []
            for entity in res:
                results.append({
                    "id": entity.get("id"),
                    "metadata": {k: v for k, v in entity.items() if k not in ["id", "vector", "content"]}
                })

            return results
        except Exception as e:
            logger.error(f"Failed to query by metadata: {e}")
            return []

    def _build_filter_expression(self, metadata_filter: Dict[str, Any]) -> str:
        """Build Milvus filter expression from metadata filter dict."""
        conditions = []
        for key, value in metadata_filter.items():
            if isinstance(value, dict) and "$eq" in value:
                conditions.append(f'{key} == "{value["$eq"]}"')
            elif isinstance(value, str):
                conditions.append(f'{key} == "{value}"')
            else:
                conditions.append(f'{key} == {value}')

        return " && ".join(conditions) if conditions else ""

    def file_already_processed(self, repository: str, file_path: str, file_sha: str) -> bool:
        """Check if a file with the same SHA was already processed.

        Args:
            repository: Repository identifier (owner/repo)
            file_path: Path to the file in the repository
            file_sha: Git SHA hash of the file

        Returns:
            True if file with same SHA exists, False otherwise
        """
        try:
            metadata_filter = {
                "repository": repository,
                "file_path": file_path,
                "file_sha": file_sha
            }

            results = self.query_by_metadata(metadata_filter, top_k=1)
            exists = len(results) > 0

            if exists:
                logger.info(f"File already processed: {file_path} (SHA: {file_sha[:8]})")

            return exists
        except Exception as e:
            logger.warning(f"Could not check if file was processed: {e}")
            return False

    def delete_file_chunks(self, repository: str, file_path: str):
        """Delete all chunks for a specific file.

        Args:
            repository: Repository identifier (owner/repo)
            file_path: Path to the file in the repository
        """
        self._ensure_collection()

        try:
            # Build filter expression for Milvus
            filter_expr = f'repository == "{repository}" && file_path == "{file_path}"'

            # Delete entities matching the filter
            self.client.delete(
                collection_name=self.collection_name,
                filter=filter_expr
            )
            logger.info(f"Deleted old chunks for {file_path}")
        except Exception as e:
            logger.warning(f"Could not delete old chunks for {file_path}: {e}")

    def test_connection(self) -> bool:
        """Test the Milvus connection."""
        try:
            if self.client is None:
                return False

            # Try to list collections
            collections = self.client.list_collections()

            # Check if our collection exists
            if self._collection_exists(self.collection_name):
                # Try to get collection stats
                try:
                    stats = self.client.get_collection_stats(collection_name=self.collection_name)
                    logger.info(f"Milvus collection stats: {stats}")
                except Exception:
                    pass
            return True
        except Exception as e:
            logger.error(f"Milvus health check failed: {e}")
            return False
