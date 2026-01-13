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
    from pymilvus import MilvusClient, DataType, Collection, connections, utility
    MILVUS_AVAILABLE = True
    logger.info("Milvus SDK successfully imported")
except ImportError as import_error:
    MilvusClient = None
    DataType = None
    Collection = None
    connections = None
    utility = None
    MILVUS_AVAILABLE = False
    logger.error(f"Milvus not installed or import failed: {import_error}")
    logger.warning("Install Milvus with: pip install pymilvus")


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
        logger.info("=" * 80)
        logger.info("INITIALIZING MILVUS VECTOR CLIENT")
        logger.info("=" * 80)

        # Log SDK availability
        logger.info(f"Milvus SDK Available: {MILVUS_AVAILABLE}")

        if not MILVUS_AVAILABLE:
            logger.error("CRITICAL: Milvus SDK not installed or failed to import")
            raise RuntimeError("Milvus SDK not installed. Install with: pip install pymilvus")

        # Log connection parameters (mask sensitive data)
        logger.info(f"URI: {uri}")
        logger.info(f"Token: {'*' * 10 if token else 'NOT_PROVIDED'}")
        logger.info(f"Collection Name: {collection_name}")
        logger.info(f"Dimension: {dimension or 1536}")
        logger.info(f"Metric: {metric}")

        self.uri = uri
        self.token = token
        self.collection_name = collection_name
        self.dimension = dimension or 1536
        self.metric = metric
        self.client = None

        # Validate required parameters
        if not uri:
            logger.error("CRITICAL: Milvus URI is missing or empty")
            raise ValueError("Milvus URI is required")

        if not token:
            logger.error("CRITICAL: Milvus token is missing or empty")
            raise ValueError("Milvus token is required")

        if not collection_name:
            logger.error("CRITICAL: Collection name is missing or empty")
            raise ValueError("Collection name is required")

        # Initialize Milvus client
        logger.info("Attempting to create Milvus client connection...")
        try:
            self.client = MilvusClient(
                uri=self.uri,
                token=self.token
            )

            logger.info(f"✓ Milvus client created successfully")
            logger.info(f"Client instance: {type(self.client).__name__}")
            logger.info(f"Client object: {self.client}")

            # Check if collection exists using utility module (compatible with older pymilvus versions)
            logger.info(f"Checking if collection '{self.collection_name}' exists...")
            collection_exists = False
            try:
                # Try new API first
                if hasattr(self.client, 'has_collection'):
                    logger.info("Using client.has_collection() method")
                    collection_exists = self.client.has_collection(collection_name=self.collection_name)
                    logger.info(f"Collection exists check result: {collection_exists}")
                else:
                    # Fall back to utility module for older versions
                    logger.info("Using utility.has_collection() method (fallback)")
                    collection_exists = utility.has_collection(self.collection_name)
                    logger.info(f"Collection exists check result: {collection_exists}")
            except Exception as check_error:
                logger.warning(f"Error checking collection existence: {check_error}")
                logger.warning(f"Error type: {type(check_error).__name__}")
                logger.warning("Assuming collection doesn't exist, will attempt to create")
                collection_exists = False

            if not collection_exists:
                logger.info(f"Collection '{self.collection_name}' does not exist, creating new collection...")
                self._create_collection()
                logger.info(f"✓ Collection '{self.collection_name}' created successfully")
            else:
                logger.info(f"✓ Using existing collection '{self.collection_name}'")

            logger.info("=" * 80)
            logger.info(f"✓ MILVUS INITIALIZATION SUCCESSFUL")
            logger.info(f"✓ Connected to collection: {self.collection_name}")
            logger.info("=" * 80)

        except Exception as e:
            logger.error("=" * 80)
            logger.error("✗ MILVUS INITIALIZATION FAILED")
            logger.error("=" * 80)
            logger.error(f"Error type: {type(e).__name__}")
            logger.error(f"Error message: {str(e)}")
            logger.error(f"URI used: {self.uri}")
            logger.error(f"Collection name: {self.collection_name}")

            # Import traceback for detailed error info
            import traceback
            logger.error("Full traceback:")
            logger.error(traceback.format_exc())

            logger.error("Vector operations will fail until Milvus is accessible")
            logger.error("Please verify:")
            logger.error("  1. MILVUS_URI is correct and accessible")
            logger.error("  2. MILVUS_TOKEN is valid")
            logger.error("  3. Network connectivity to Milvus server")
            logger.error("  4. Firewall rules allow connection")
            logger.error("=" * 80)

            # Set client to None to signal initialization failure
            self.client = None
            raise  # Re-raise to signal initialization failure

    def _create_collection(self):
        """Create a new Milvus collection with the appropriate schema."""
        logger.info("-" * 80)
        logger.info("CREATING MILVUS COLLECTION")
        logger.info("-" * 80)

        try:
            # Check if collection already exists using utility module
            logger.info(f"Double-checking if collection '{self.collection_name}' already exists...")
            collection_exists = False
            try:
                if hasattr(self.client, 'has_collection'):
                    collection_exists = self.client.has_collection(collection_name=self.collection_name)
                else:
                    collection_exists = utility.has_collection(self.collection_name)
                logger.info(f"Collection exists: {collection_exists}")
            except Exception as check_err:
                logger.warning(f"Error during existence check: {check_err}")
                collection_exists = False

            if collection_exists:
                logger.info(f"✓ Collection '{self.collection_name}' already exists, skipping creation")
                logger.info("-" * 80)
                return

            # Create collection with auto-id and vector field
            logger.info("Creating new collection with parameters:")
            logger.info(f"  - collection_name: {self.collection_name}")
            logger.info(f"  - dimension: {self.dimension}")
            logger.info(f"  - metric_type: {self.metric}")
            logger.info(f"  - auto_id: False")
            logger.info(f"  - enable_dynamic_field: True")

            self.client.create_collection(
                collection_name=self.collection_name,
                dimension=self.dimension,
                metric_type=self.metric,
                auto_id=False,  # We'll provide IDs
                enable_dynamic_field=True  # Allow dynamic metadata fields
            )

            logger.info(f"✓ Successfully created Milvus collection '{self.collection_name}'")
            logger.info(f"✓ Collection dimension: {self.dimension}")
            logger.info(f"✓ Metric type: {self.metric}")
            logger.info("-" * 80)

            # Note: create_collection automatically creates an index on the vector field
            # Do NOT manually create another index to avoid "at most one distinct index" error
            logger.info("Note: Vector index automatically created by create_collection()")

        except Exception as e:
            logger.error("-" * 80)
            logger.error("✗ COLLECTION CREATION FAILED")
            logger.error("-" * 80)
            logger.error(f"Error type: {type(e).__name__}")
            logger.error(f"Error message: {str(e)}")

            # Log the error but don't raise if collection already exists
            if "already exist" in str(e).lower():
                logger.warning(f"Collection '{self.collection_name}' already exists (detected in error message)")
                logger.warning("Continuing despite error...")
                logger.info("-" * 80)
            else:
                logger.error("This is a critical error, re-raising exception")
                logger.error("-" * 80)
                raise

    def _collection_exists(self, name: str) -> bool:
        """Check if a Milvus collection exists."""
        try:
            if hasattr(self.client, 'has_collection'):
                return self.client.has_collection(collection_name=name)
            else:
                return utility.has_collection(name)
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

            try:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    dimension=int(dim),
                    metric_type=self.metric,
                    auto_id=False,
                    enable_dynamic_field=True
                )
            except Exception as e:
                # Handle case where collection was created by another process
                if "already exist" in str(e).lower() or "duplicate" in str(e).lower():
                    logger.warning(f"Collection '{self.collection_name}' already exists, continuing...")
                else:
                    raise

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
        logger.info("=" * 80)
        logger.info("TESTING MILVUS CONNECTION")
        logger.info("=" * 80)

        try:
            if self.client is None:
                logger.error("✗ Client is None - connection was not initialized")
                logger.error("=" * 80)
                return False

            logger.info("✓ Client object exists")

            # Try to list collections
            logger.info("Attempting to list collections...")
            collections = self.client.list_collections()
            logger.info(f"✓ Successfully listed collections: {collections}")

            # Check if our collection exists
            logger.info(f"Checking if target collection '{self.collection_name}' exists...")
            if self._collection_exists(self.collection_name):
                logger.info(f"✓ Target collection '{self.collection_name}' exists")

                # Try to get collection stats
                try:
                    logger.info("Fetching collection statistics...")
                    stats = self.client.get_collection_stats(collection_name=self.collection_name)
                    logger.info(f"✓ Collection stats: {stats}")
                except Exception as stats_error:
                    logger.warning(f"Could not fetch collection stats: {stats_error}")
            else:
                logger.warning(f"✗ Target collection '{self.collection_name}' does not exist")

            logger.info("=" * 80)
            logger.info("✓ MILVUS CONNECTION TEST SUCCESSFUL")
            logger.info("=" * 80)
            return True

        except Exception as e:
            logger.error("=" * 80)
            logger.error("✗ MILVUS CONNECTION TEST FAILED")
            logger.error("=" * 80)
            logger.error(f"Error type: {type(e).__name__}")
            logger.error(f"Error message: {str(e)}")

            import traceback
            logger.error("Full traceback:")
            logger.error(traceback.format_exc())
            logger.error("=" * 80)
            return False
