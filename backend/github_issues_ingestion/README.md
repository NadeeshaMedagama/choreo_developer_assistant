# GitHub Issues Ingestion System

A comprehensive, SOLID-based system for ingesting GitHub issues, creating embeddings, and storing them in a vector database for semantic search.

## Architecture

This system follows **SOLID principles** and **Clean Architecture**:

```
github_issues_ingestion/
├── interfaces/           # Abstract interfaces (ISP, DIP)
│   ├── issue_fetcher.py
│   ├── text_processor.py
│   ├── chunker.py
│   ├── embedding_service.py
│   └── vector_store.py
├── models/              # Data models
│   ├── github_issue.py
│   └── chunk.py
├── services/            # Concrete implementations (SRP, OCP)
│   ├── github_issue_fetcher.py
│   ├── text_processor_service.py
│   ├── chunking_service.py
│   ├── azure_embedding_service.py
│   ├── pinecone_vector_store.py
│   └── ingestion_orchestrator.py
├── config/              # Configuration
│   └── settings.py
├── utils/               # Utilities
│   └── helpers.py
└── main.py              # Entry point
```

### SOLID Principles Applied

1. **Single Responsibility Principle (SRP)**: Each service has one clear responsibility
   - `GitHubIssueFetcher`: Only fetches issues from GitHub
   - `TextProcessorService`: Only processes and cleans text
   - `ChunkingService`: Only chunks text
   - `AzureEmbeddingService`: Only creates embeddings
   - `PineconeVectorStore`: Only manages vector storage

2. **Open/Closed Principle (OCP)**: Services are open for extension but closed for modification
   - New fetchers, processors, or stores can be added without modifying existing code

3. **Liskov Substitution Principle (LSP)**: All implementations can be substituted
   - Any implementation of `IEmbeddingService` can be swapped (Azure, OpenAI, local models)

4. **Interface Segregation Principle (ISP)**: Small, focused interfaces
   - Each interface defines only the methods needed for its specific purpose

5. **Dependency Inversion Principle (DIP)**: Depend on abstractions, not concretions
   - `IngestionOrchestrator` depends on interfaces, not concrete implementations

## Workflow

```
1. Fetch Issues (GitHubIssueFetcher)
   ↓
2. Process Text (TextProcessorService)
   ↓
3. Chunk Text (ChunkingService)
   ↓
4. Create Embeddings (AzureEmbeddingService)
   ↓
5. Store Vectors (PineconeVectorStore)
```

## Features

- ✅ Fetch all issues from GitHub repositories
- ✅ Extract complete issue information (title, body, comments, labels, etc.)
- ✅ Clean and process text
- ✅ Intelligent text chunking with overlap
- ✅ Azure OpenAI embeddings
- ✅ Pinecone vector storage with namespaces
- ✅ Semantic search/query capabilities
- ✅ Batch processing for efficiency
- ✅ Progress tracking and error handling
- ✅ Configurable via environment variables

## Installation

The system uses existing dependencies from the parent project. Ensure you have:

```bash
pip install openai pinecone python-dotenv requests
```

## Configuration

The system reads configuration from the `.env` file in the backend directory:

```env
# GitHub
GITHUB_TOKEN=your_github_token

# Azure OpenAI
AZURE_OPENAI_API_KEY=your_api_key
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com/
AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT=your_deployment_name
AZURE_OPENAI_API_VERSION=2024-02-01

# Pinecone
PINECONE_API_KEY=your_pinecone_key
PINECONE_INDEX_NAME=your_index_name
PINECONE_DIMENSION=1536
PINECONE_CLOUD=aws
PINECONE_REGION=us-east-1
PINECONE_USE_NAMESPACES=true

# Optional: Processing settings
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
BATCH_SIZE=10
ISSUES_NAMESPACE=github-issues
```

## Usage

### Command Line Interface

```bash
# Navigate to the module directory
cd backend/github_issues_ingestion

# Ingest all issues from a repository
python main.py owner/repo

# Ingest with filters
python main.py wso2/choreo --state open --max-issues 50
python main.py wso2/choreo --labels bug,enhancement
python main.py wso2/choreo --since 2024-01-01

# Query the vector database
python main.py wso2/choreo --query "authentication error"
python main.py wso2/choreo --query "deployment issues" --top-k 10

# Delete repository data
python main.py wso2/choreo --delete
```

### Programmatic Usage

```python
from github_issues_ingestion import create_ingestion_pipeline

# Create pipeline with default settings from .env
orchestrator = create_ingestion_pipeline()

# Ingest a repository
stats = orchestrator.ingest_repository(
    owner="wso2",
    repo="choreo",
    state="all",
    max_issues=100
)

print(f"Processed {stats['total_issues']} issues")
print(f"Created {stats['total_chunks']} chunks")
print(f"Generated {stats['total_embeddings']} embeddings")

# Query for similar issues
results = orchestrator.query_issues(
    query="How to fix authentication problems?",
    top_k=5,
    filter_dict={"state": "open"}
)

for result in results:
    print(f"Issue #{result['metadata']['issue_number']}")
    print(f"Score: {result['score']}")
    print(f"Content: {result['content'][:200]}...")
    print()
```

### Advanced Usage

```python
from github_issues_ingestion import (
    Settings,
    GitHubIssueFetcher,
    TextProcessorService,
    ChunkingService,
    AzureEmbeddingService,
    PineconeVectorStore,
    IngestionOrchestrator,
)

# Load custom settings
settings = Settings.from_env()

# Create custom components
issue_fetcher = GitHubIssueFetcher(token=settings.github_token)
text_processor = TextProcessorService(include_code_blocks=False)  # Exclude code
chunker = ChunkingService(chunk_size=500, overlap=100)  # Smaller chunks

embedding_service = AzureEmbeddingService(
    api_key=settings.azure_openai_api_key,
    endpoint=settings.azure_openai_endpoint,
    deployment=settings.azure_openai_embeddings_deployment,
    api_version=settings.azure_openai_api_version
)

vector_store = PineconeVectorStore(
    api_key=settings.pinecone_api_key,
    index_name=settings.pinecone_index_name,
    dimension=settings.pinecone_dimension,
    namespace="custom-namespace"
)

# Create orchestrator with custom components
orchestrator = IngestionOrchestrator(
    issue_fetcher=issue_fetcher,
    text_processor=text_processor,
    chunker=chunker,
    embedding_service=embedding_service,
    vector_store=vector_store,
    batch_size=20
)

# Run ingestion
stats = orchestrator.ingest_repository("owner", "repo")
```

## Examples

### Example 1: Ingest Recent Issues

```bash
python main.py wso2/choreo --since 2024-11-01 --state open
```

### Example 2: Find Similar Issues

```bash
# First ingest
python main.py wso2/choreo --max-issues 100

# Then query
python main.py wso2/choreo --query "deployment fails with timeout error"
```

### Example 3: Filter by Labels

```bash
python main.py wso2/choreo --labels "bug,critical" --state open
```

## Data Storage

Issues are stored in Pinecone with the following metadata:

```python
{
    "content": "chunk text content...",
    "chunk_index": 0,
    "total_chunks": 3,
    "issue_number": 123,
    "issue_title": "Bug in authentication",
    "repository": "owner/repo",
    "state": "open",
    "labels": ["bug", "authentication"],
    "created_at": "2024-11-20T10:00:00",
    "updated_at": "2024-11-20T15:30:00",
    "url": "https://github.com/owner/repo/issues/123"
}
```

## Testing

You can test individual components:

```python
# Test issue fetching
from github_issues_ingestion.services import GitHubIssueFetcher

fetcher = GitHubIssueFetcher(token="your_token")
issues = fetcher.fetch_issues("wso2", "choreo", max_issues=5)
print(f"Fetched {len(issues)} issues")

# Test text processing
from github_issues_ingestion.services import TextProcessorService

processor = TextProcessorService()
processed_text = processor.process_issue(issues[0])
print(processed_text)

# Test chunking
from github_issues_ingestion.services import ChunkingService

chunker = ChunkingService(chunk_size=500, overlap=100)
chunks = chunker.chunk_text(processed_text)
print(f"Created {len(chunks)} chunks")
```

## Error Handling

The system includes comprehensive error handling:

- GitHub API rate limiting
- Network failures
- Invalid configurations
- Empty or malformed data
- Vector storage errors

All errors are logged and included in the final statistics report.

## Performance Considerations

- **Batch Processing**: Embeddings are created in batches to optimize API calls
- **Memory Management**: Automatic cleanup after each batch
- **Rate Limiting**: Respects GitHub API rate limits
- **Progress Tracking**: Real-time progress updates
- **Chunking**: Intelligent text splitting with sentence boundary detection

## Contributing

When adding new functionality:

1. Define an interface in `interfaces/`
2. Implement the interface in `services/`
3. Add models in `models/` if needed
4. Update `__init__.py` to export new components
5. Follow SOLID principles

## License

[Your License Here]

## Support

For issues or questions, please create an issue in the repository.

