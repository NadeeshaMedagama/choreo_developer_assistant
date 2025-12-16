# Choreo Documentation Ingestion

This module handles the ingestion of Choreo documentation from GitHub into Pinecone vector database.

## Features

- ✅ Fetches all `.md` files from GitHub repository using REST API
- ✅ No need to download repository - uses GitHub API directly
- ✅ Chunks documents intelligently (respects paragraphs and sentences)
- ✅ Generates embeddings using SentenceTransformers or OpenAI
- ✅ Stores embeddings in Pinecone with metadata
- ✅ Batch processing for efficiency
- ✅ Comprehensive logging

## Setup

### 1. Install Dependencies

```bash
cd choreo-ai-assistant
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy the example environment file and update with your credentials:

```bash
cp .env.example .env
```

Edit `.env` and add your credentials:

```env
PINECONE_API_KEY=your_pinecone_api_key_here
GITHUB_TOKEN=your_github_token_here  # Optional but recommended
```

### 3. Run the Ingestion

```bash
cd backend
python run_ingestion.py
```

## Architecture

### Components

1. **GitHubService** (`services/github_service.py`)
   - Connects to GitHub REST API
   - Recursively finds all `.md` files
   - Fetches file contents (base64 decoded)

2. **DocumentChunker** (`services/ingestion.py`)
   - Splits documents into chunks with overlap
   - Respects paragraph and sentence boundaries
   - Adds metadata to each chunk

3. **LLMService** (`services/llm_service.py`)
   - Generates embeddings
   - Supports SentenceTransformers (local, free)
   - Supports OpenAI (cloud, requires API key)

4. **VectorClient** (`db/vector_client.py`)
   - Manages Pinecone connection
   - Handles index creation
   - Batch insert operations

5. **IngestionService** (`services/ingestion.py`)
   - Orchestrates the entire pipeline
   - Fetches → Chunks → Embeds → Stores

## Configuration Options

| Variable | Default | Description |
|----------|---------|-------------|
| `PINECONE_API_KEY` | *Required* | Your Pinecone API key |
| `PINECONE_INDEX_NAME` | `choreo-docs` | Name of the Pinecone index |
| `PINECONE_DIMENSION` | `384` | Embedding dimension (384 for MiniLM, 1536 for OpenAI) |
| `GITHUB_TOKEN` | *Optional* | GitHub PAT for higher rate limits (5000/hour vs 60/hour) |
| `EMBEDDING_MODEL` | `sentence-transformers/all-MiniLM-L6-v2` | Model for embeddings |
| `CHUNK_SIZE` | `1000` | Characters per chunk |
| `CHUNK_OVERLAP` | `200` | Overlapping characters |

## Process Flow

```
1. GitHub API Connection
   └─> Authenticate with token (optional)

2. Fetch .md Files
   └─> Recursively scan repository
   └─> Download file contents via API
   └─> Base64 decode

3. Chunk Documents
   └─> Split into manageable pieces
   └─> Add metadata (path, filename, etc.)

4. Generate Embeddings
   └─> Batch process chunks
   └─> Create vector representations

5. Store in Pinecone
   └─> Batch insert (100 at a time)
   └─> Include full metadata
```

## Example Output

```
============================================================
Starting Choreo Documentation Ingestion
============================================================
Target repository: NadeeshaMedagama/docs-choreo-dev

============================================================
Initializing Services
============================================================
1. Initializing Pinecone Vector Client...
   ✓ Pinecone connection successful
2. Initializing LLM Service for embeddings...
   Using SentenceTransformer: sentence-transformers/all-MiniLM-L6-v2
   Embedding dimension: 384
3. Initializing GitHub Service...
   ✓ Using authenticated GitHub API (higher rate limits)
4. Initializing Ingestion Service...
   Chunk size: 1000, Overlap: 200

============================================================
Starting Ingestion Process
============================================================
Step 1: Fetching markdown files from GitHub...
Found markdown file: README.md
Found markdown file: docs/architecture.md
Fetched 50 markdown files

Step 2: Chunking documents...
Created 500 chunks from 50 files

Step 3: Generating embeddings...
Generated 500 embeddings

Step 4: Storing embeddings in Pinecone...
Inserted batch 1: 100/500 embeddings
Inserted batch 2: 200/500 embeddings
...

============================================================
Ingestion Complete - Summary
============================================================
Status: completed
Repository: NadeeshaMedagama/docs-choreo-dev
Files fetched: 50
Chunks created: 500
Embeddings stored: 500
============================================================
✓ Ingestion completed successfully!
```

## Troubleshooting

### Rate Limits
- **Without token**: 60 requests/hour
- **With token**: 5000 requests/hour
- Set `GITHUB_TOKEN` for large repositories

### Pinecone Index
- Index is created automatically if it doesn't exist
- Ensure dimension matches your embedding model
- MiniLM-L6-v2: 384 dimensions
- OpenAI ada-002: 1536 dimensions

### Memory Issues
- Reduce `CHUNK_SIZE` if running out of memory
- Process smaller batches by modifying `batch_size` in code

## Using the Ingested Data

After ingestion, you can query the embeddings:

```python
from backend.db.vector_client import VectorClient
from backend.services.llm_service import LLMService

# Initialize
vector_client = VectorClient(api_key="...", index_name="choreo-docs")
llm_service = LLMService()

# Query
query = "How do I deploy an application in Choreo?"
query_embedding = llm_service.get_embedding(query)
results = vector_client.query_similar(query_embedding, top_k=5)

for result in results:
    print(f"Score: {result['score']}")
    print(f"Content: {result['content'][:200]}...")
    print(f"Source: {result['metadata']['file_path']}")
    print("---")
```

## License

MIT

