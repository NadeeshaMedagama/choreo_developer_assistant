# API Reference

Complete API documentation for GitHub Issues Ingestion System.

## Table of Contents

- [Factory Functions](#factory-functions)
- [Interfaces](#interfaces)
- [Services](#services)
- [Models](#models)
- [Configuration](#configuration)
- [Utilities](#utilities)

---

## Factory Functions

### `create_ingestion_pipeline()`

Create a fully configured ingestion orchestrator.

```python
def create_ingestion_pipeline(
    settings: Settings = None,
    batch_size: int = 10
) -> IngestionOrchestrator
```

**Parameters:**
- `settings` (Settings, optional): Configuration settings. Loads from .env if not provided.
- `batch_size` (int, optional): Batch size for processing. Default: 10.

**Returns:**
- `IngestionOrchestrator`: Configured orchestrator instance

**Example:**
```python
from github_issues_ingestion import create_ingestion_pipeline

orchestrator = create_ingestion_pipeline()
stats = orchestrator.ingest_repository("owner", "repo")
```

---

## Interfaces

### IIssueFetcher

Interface for fetching GitHub issues.

#### Methods

**`fetch_issues()`**
```python
def fetch_issues(
    owner: str,
    repo: str,
    state: str = "all",
    labels: Optional[List[str]] = None,
    since: Optional[str] = None,
    max_issues: Optional[int] = None
) -> List[GitHubIssue]
```

**`fetch_issue_comments()`**
```python
def fetch_issue_comments(
    owner: str,
    repo: str,
    issue_number: int
) -> List[Dict[str, Any]]
```

### ITextProcessor

Interface for text processing.

#### Methods

**`process_issue()`**
```python
def process_issue(issue: GitHubIssue) -> str
```

**`clean_text()`**
```python
def clean_text(text: str) -> str
```

### IChunker

Interface for text chunking.

#### Methods

**`chunk_text()`**
```python
def chunk_text(
    text: str,
    metadata: dict = None
) -> List[TextChunk]
```

**`get_chunk_size()`**
```python
def get_chunk_size() -> int
```

**`get_overlap()`**
```python
def get_overlap() -> int
```

### IEmbeddingService

Interface for embedding generation.

#### Methods

**`create_embedding()`**
```python
def create_embedding(text: str) -> List[float]
```

**`create_embeddings_batch()`**
```python
def create_embeddings_batch(texts: List[str]) -> List[List[float]]
```

**`get_embedding_dimension()`**
```python
def get_embedding_dimension() -> int
```

### IVectorStore

Interface for vector storage.

#### Methods

**`store_chunk()`**
```python
def store_chunk(chunk: TextChunk, vector: List[float]) -> str
```

**`store_chunks_batch()`**
```python
def store_chunks_batch(
    chunks: List[TextChunk],
    vectors: List[List[float]]
) -> List[str]
```

**`query_similar()`**
```python
def query_similar(
    query_vector: List[float],
    top_k: int = 5,
    filter_dict: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]
```

**`delete_by_metadata()`**
```python
def delete_by_metadata(filter_dict: Dict[str, Any]) -> int
```

---

## Services

### GitHubIssueFetcher

Concrete implementation of `IIssueFetcher`.

**Constructor:**
```python
def __init__(self, token: str)
```

**Additional Methods:**
- `get_rate_limit_status()`: Get current GitHub API rate limit status

**Example:**
```python
from github_issues_ingestion.services import GitHubIssueFetcher

fetcher = GitHubIssueFetcher(token="your_token")
issues = fetcher.fetch_issues("owner", "repo", max_issues=10)
```

### TextProcessorService

Concrete implementation of `ITextProcessor`.

**Constructor:**
```python
def __init__(self, include_code_blocks: bool = True)
```

**Additional Methods:**
- `extract_keywords(text: str, max_keywords: int = 10)`: Extract keywords from text

**Example:**
```python
from github_issues_ingestion.services import TextProcessorService

processor = TextProcessorService(include_code_blocks=False)
processed = processor.process_issue(issue)
```

### ChunkingService

Concrete implementation of `IChunker`.

**Constructor:**
```python
def __init__(self, chunk_size: int = 1000, overlap: int = 200)
```

**Additional Methods:**
- `chunk_by_tokens()`: Chunk by token count
- `set_chunk_size(chunk_size: int)`: Update chunk size
- `set_overlap(overlap: int)`: Update overlap

**Example:**
```python
from github_issues_ingestion.services import ChunkingService

chunker = ChunkingService(chunk_size=500, overlap=100)
chunks = chunker.chunk_text(text, metadata={"key": "value"})
```

### AzureEmbeddingService

Concrete implementation of `IEmbeddingService`.

**Constructor:**
```python
def __init__(
    api_key: str,
    endpoint: str,
    deployment: str,
    api_version: str = "2024-02-01"
)
```

**Additional Methods:**
- `set_embedding_dimension(dimension: int)`: Set embedding dimension

**Example:**
```python
from github_issues_ingestion.services import AzureEmbeddingService

embedder = AzureEmbeddingService(
    api_key="key",
    endpoint="https://...",
    deployment="deployment-name",
    api_version="2024-02-01"
)
embedding = embedder.create_embedding("text")
```

### PineconeVectorStore

Concrete implementation of `IVectorStore`.

**Constructor:**
```python
def __init__(
    api_key: str,
    index_name: str,
    dimension: int = 1536,
    metric: str = "cosine",
    cloud: str = "aws",
    region: str = "us-east-1",
    namespace: Optional[str] = None
)
```

**Additional Methods:**
- `get_stats()`: Get index statistics

**Example:**
```python
from github_issues_ingestion.services import PineconeVectorStore

store = PineconeVectorStore(
    api_key="key",
    index_name="index",
    dimension=1536,
    namespace="issues"
)
chunk_id = store.store_chunk(chunk, vector)
```

### IngestionOrchestrator

Orchestrates the complete ingestion workflow.

**Constructor:**
```python
def __init__(
    issue_fetcher: IIssueFetcher,
    text_processor: ITextProcessor,
    chunker: IChunker,
    embedding_service: IEmbeddingService,
    vector_store: IVectorStore,
    batch_size: int = 10
)
```

**Methods:**

**`ingest_repository()`**
```python
def ingest_repository(
    owner: str,
    repo: str,
    state: str = "all",
    labels: Optional[List[str]] = None,
    since: Optional[str] = None,
    max_issues: Optional[int] = None
) -> Dict[str, Any]
```

**`query_issues()`**
```python
def query_issues(
    query: str,
    top_k: int = 5,
    filter_dict: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]
```

**`delete_repository_data()`**
```python
def delete_repository_data(owner: str, repo: str) -> None
```

**`get_stats()`**
```python
def get_stats() -> Dict[str, Any]
```

**`reset_stats()`**
```python
def reset_stats() -> None
```

**Example:**
```python
orchestrator = IngestionOrchestrator(
    fetcher, processor, chunker, embedder, store
)

stats = orchestrator.ingest_repository("owner", "repo")
results = orchestrator.query_issues("query text")
```

---

## Models

### GitHubIssue

Data model for GitHub issues.

**Attributes:**
- `number` (int): Issue number
- `title` (str): Issue title
- `body` (str): Issue body
- `state` (str): Issue state (open/closed)
- `owner` (str): Repository owner
- `repo` (str): Repository name
- `created_at` (datetime): Creation timestamp
- `updated_at` (datetime): Update timestamp
- `closed_at` (datetime, optional): Close timestamp
- `labels` (List[str]): Issue labels
- `comments` (List[Dict]): Issue comments
- `user` (str, optional): Issue author
- `assignees` (List[str]): Assignees
- `milestone` (str, optional): Milestone
- `url` (str, optional): Issue URL
- `raw_data` (Dict): Raw API response

**Methods:**

**`from_api_response()`** (classmethod)
```python
@classmethod
def from_api_response(
    data: Dict[str, Any],
    owner: str,
    repo: str
) -> GitHubIssue
```

**`add_comments()`**
```python
def add_comments(comments: List[Dict[str, Any]]) -> None
```

**`to_dict()`**
```python
def to_dict() -> Dict[str, Any]
```

### TextChunk

Data model for text chunks.

**Attributes:**
- `content` (str): Chunk content
- `chunk_index` (int): Chunk index (0-based)
- `total_chunks` (int): Total number of chunks
- `metadata` (Dict): Additional metadata
- `chunk_id` (str, optional): Unique chunk ID
- `created_at` (datetime): Creation timestamp

**Methods:**

**`to_dict()`**
```python
def to_dict() -> Dict[str, Any]
```

**`from_dict()`** (classmethod)
```python
@classmethod
def from_dict(data: Dict[str, Any]) -> TextChunk
```

---

## Configuration

### Settings

Configuration settings loaded from environment.

**Attributes:**
- `github_token` (str): GitHub API token
- `azure_openai_api_key` (str): Azure OpenAI API key
- `azure_openai_endpoint` (str): Azure OpenAI endpoint
- `azure_openai_embeddings_deployment` (str): Deployment name
- `azure_openai_api_version` (str): API version
- `pinecone_api_key` (str): Pinecone API key
- `pinecone_index_name` (str): Pinecone index name
- `pinecone_dimension` (int): Embedding dimension
- `pinecone_cloud` (str): Cloud provider
- `pinecone_region` (str): Cloud region
- `pinecone_use_namespaces` (bool): Use namespaces
- `chunk_size` (int): Chunk size (default: 1000)
- `chunk_overlap` (int): Chunk overlap (default: 200)
- `batch_size` (int): Batch size (default: 10)
- `max_workers` (int): Max workers (default: 5)
- `issues_namespace` (str): Issues namespace (default: "github-issues")

**Methods:**

**`from_env()`** (classmethod)
```python
@classmethod
def from_env(env_file: Optional[str] = None) -> Settings
```

**Example:**
```python
from github_issues_ingestion.config import Settings

settings = Settings.from_env()
print(settings.chunk_size)
```

---

## Utilities

### Helpers

**`format_timestamp()`**
```python
def format_timestamp(
    dt: Optional[datetime] = None,
    iso_format: bool = True
) -> str
```

**`validate_repo_format()`**
```python
def validate_repo_format(repo_string: str) -> Tuple[str, str]
```

**`truncate_text()`**
```python
def truncate_text(
    text: str,
    max_length: int = 100,
    suffix: str = "..."
) -> str
```

**`sanitize_filename()`**
```python
def sanitize_filename(filename: str) -> str
```

**`calculate_progress_percentage()`**
```python
def calculate_progress_percentage(current: int, total: int) -> float
```

**`estimate_time_remaining()`**
```python
def estimate_time_remaining(
    current: int,
    total: int,
    elapsed_seconds: float
) -> Optional[float]
```

**Example:**
```python
from github_issues_ingestion.utils import validate_repo_format

owner, repo = validate_repo_format("wso2/choreo")
```

---

## Error Handling

All services raise appropriate exceptions:

- `ValueError`: Invalid parameters
- `RuntimeError`: System/runtime errors
- `requests.HTTPError`: GitHub API errors
- `Exception`: Generic errors (with descriptive messages)

**Example:**
```python
try:
    orchestrator.ingest_repository("owner", "repo")
except ValueError as e:
    print(f"Invalid input: {e}")
except requests.HTTPError as e:
    print(f"GitHub API error: {e}")
except Exception as e:
    print(f"Error: {e}")
```

---

## Complete Example

```python
from github_issues_ingestion import (
    create_ingestion_pipeline,
    Settings,
    GitHubIssueFetcher,
    TextProcessorService,
    ChunkingService,
    AzureEmbeddingService,
    PineconeVectorStore,
    IngestionOrchestrator,
)

# Option 1: Use factory (recommended)
orchestrator = create_ingestion_pipeline()
stats = orchestrator.ingest_repository("wso2", "choreo", max_issues=10)

# Option 2: Manual configuration
settings = Settings.from_env()

fetcher = GitHubIssueFetcher(token=settings.github_token)
processor = TextProcessorService(include_code_blocks=True)
chunker = ChunkingService(chunk_size=1000, overlap=200)
embedder = AzureEmbeddingService(
    api_key=settings.azure_openai_api_key,
    endpoint=settings.azure_openai_endpoint,
    deployment=settings.azure_openai_embeddings_deployment,
    api_version=settings.azure_openai_api_version
)
store = PineconeVectorStore(
    api_key=settings.pinecone_api_key,
    index_name=settings.pinecone_index_name,
    dimension=settings.pinecone_dimension,
    namespace="custom"
)

orchestrator = IngestionOrchestrator(
    fetcher, processor, chunker, embedder, store, batch_size=10
)

# Ingest
stats = orchestrator.ingest_repository("wso2", "choreo")

# Query
results = orchestrator.query_issues("authentication error", top_k=5)

# Delete
orchestrator.delete_repository_data("wso2", "choreo")
```

---

For more information, see:
- [README.md](../README.md) - Complete documentation
- [QUICKSTART.md](QUICKSTART.md) - Quick start guide
- [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - Project overview

