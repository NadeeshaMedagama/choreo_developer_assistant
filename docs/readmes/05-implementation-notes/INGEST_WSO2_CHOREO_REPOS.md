# Ingesting WSO2 Choreo Repositories

This guide explains how to ingest all markdown files from wso2-enterprise organization repositories filtered by "choreo" into your Pinecone database.

## Overview

The system can automatically:
1. Search for all repositories in the `wso2-enterprise` organization containing the keyword "choreo"
2. Fetch all `.md` files from each repository
3. Chunk the markdown content intelligently
4. Generate embeddings using Azure OpenAI
5. Store embeddings in your Pinecone database (`choreo-ai-assistant-v2`)

## Prerequisites

Make sure your `.env` file contains the following credentials:

```env
# Pinecone Configuration
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_INDEX_NAME=choreo-ai-assistant-v2

# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=your_azure_endpoint
AZURE_OPENAI_KEY=your_azure_key
AZURE_OPENAI_DEPLOYMENT=your_deployment_name
AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT=your_embeddings_deployment  # Optional

# GitHub Configuration
GITHUB_TOKEN=your_github_token  # Required for accessing organization repositories
```

## Method 1: Using the Standalone Script (Recommended)

The easiest way to ingest all repositories is using the standalone script:

```bash
# Navigate to the project directory
cd choreo-ai-assistant

# Run the script to ingest all choreo repositories
python backend/scripts/ingest/ingest_wso2_choreo_repos.py
```

### Options

You can customize the ingestion with command-line options:

```bash
# Limit to first 5 repositories (for testing)
python backend/scripts/ingest/ingest_wso2_choreo_repos.py --max-repos 5

# Search a different organization and keyword
python backend/scripts/ingest/ingest_wso2_choreo_repos.py --org my-org --keyword my-keyword

# Show help
python backend/scripts/ingest/ingest_wso2_choreo_repos.py --help
```

### What the Script Does

1. ✓ Loads configuration from `.env` file
2. ✓ Validates all required credentials
3. ✓ Initializes Pinecone, Azure OpenAI, and GitHub services
4. ✓ Tests Pinecone connection
5. ✓ Searches for all repositories matching the keyword
6. ✓ Processes each repository one at a time
7. ✓ Provides detailed progress and statistics
8. ✓ Handles memory management automatically
9. ✓ Skips already-processed files (incremental updates)

## Method 2: Using the Backend API

If your backend server is running, you can also use the API endpoint:

```bash
# Start the backend server first
cd backend
uvicorn app:app --reload

# Then call the API endpoint
curl -X POST "http://localhost:8000/api/ingest/org?org=wso2&keyword=choreo"

# Or with a limit
curl -X POST "http://localhost:8000/api/ingest/org?org=wso2&keyword=choreo&max_repos=5"
```

## Method 3: Using Python Code

You can also integrate this into your own Python scripts:

```python
from backend.services.github_service import GitHubService
from backend.services.llm_service import LLMService
from backend.services.ingestion import IngestionService
from backend.db.vector_client import VectorClient
from backend.utils.config import load_config

# Load configuration
config = load_config()

# Initialize services
vector_client = VectorClient(
    api_key=config["PINECONE_API_KEY"],
    index_name=config["PINECONE_INDEX_NAME"]
)

llm_service = LLMService(
    endpoint=config["AZURE_OPENAI_ENDPOINT"],
    api_key=config["AZURE_OPENAI_KEY"],
    deployment=config["AZURE_OPENAI_DEPLOYMENT"]
)

github_service = GitHubService(token=config["GITHUB_TOKEN"])

ingestion_service = IngestionService(
    github_service=github_service,
    llm_service=llm_service,
    vector_client=vector_client
)

# Ingest all choreo repositories
result = ingestion_service.ingest_org_repositories(
    org="wso2-enterprise",
    keyword="choreo",
    max_repos=None  # Process all repositories
)

print(f"Processed {result['repositories_processed']} repositories")
print(f"Total embeddings: {result['total_embeddings_stored']}")
```

## Features

### ✅ Incremental Updates
The system automatically skips files that have already been processed (based on SHA hash). This means:
- Re-running the script only processes new or changed files
- Saves time and API costs
- Keeps your database up-to-date

### ✅ Memory Management
The system includes smart memory management:
- Processes repositories one at a time
- Waits if memory usage is too high (>85%)
- Forces garbage collection between repositories
- Prevents crashes on large repositories

### ✅ Error Handling
- Continues processing even if one repository fails
- Provides detailed error messages
- Shows which repositories succeeded/failed

### ✅ Progress Tracking
- Real-time progress updates
- Memory usage monitoring
- Per-repository statistics
- Final summary with totals

## Example Output

```
================================================================================
WSO2 Choreo Repositories Ingestion Script
================================================================================
Organization: wso2
Keyword filter: choreo
Max repositories: All
================================================================================
Loading configuration from .env file...
✓ Configuration loaded successfully
  - Pinecone Index: choreo-ai-assistant-v2
  - Azure OpenAI Endpoint: https://your-endpoint.openai.azure.com/
  - Azure Deployment: gpt-4
  - GitHub Token: ✓ Configured

Initializing services...
✓ Pinecone client initialized
✓ Azure OpenAI service initialized
✓ GitHub service initialized
✓ Ingestion service initialized

Testing Pinecone connection...
✓ Pinecone connection successful

================================================================================
Starting bulk ingestion process...
================================================================================
Found 18 repositories matching criteria

================================================================================
Repository 1/18: wso2/docs-choreo-dev
Description: Choreo documentation repository for ongoing dev tasks.
Memory before processing: 245.3MB (12.3%)
================================================================================
Processing file 1/25: README.md [Memory: 247.1MB (12.4%)]
Created 3 chunks from README.md
Stored batch of 3 embeddings from README.md
✓ Completed README.md (1/25)
...

================================================================================
BULK INGESTION COMPLETED
================================================================================
Organization: wso2
Keyword filter: 'choreo'
Repositories processed: 18/18
Repositories failed: 0
Total files processed: 342
Total files skipped: 28
Total embeddings stored: 1,847
Final memory usage: 298.5MB (14.9%)
================================================================================

Per-Repository Details:
--------------------------------------------------------------------------------
✓ wso2/docs-choreo-dev: 25 files, 134 embeddings
✓ wso2/choreo-samples: 18 files, 89 embeddings
✓ wso2/choreo-cli: 12 files, 67 embeddings
...
--------------------------------------------------------------------------------

✓ Ingestion completed successfully!
```

## Troubleshooting

### Issue: "Missing required configuration keys"
**Solution**: Make sure your `.env` file contains all required credentials (Pinecone, Azure OpenAI, GitHub token)

### Issue: "GitHub API rate limit exceeded"
**Solution**: Make sure you have a valid GitHub token in your `.env` file. Without a token, you're limited to 60 requests/hour. With a token, you get 5,000 requests/hour.

### Issue: "Memory usage too high"
**Solution**: The system automatically handles this by waiting when memory is high. If it persists, try using `--max-repos` to process fewer repositories at once.

### Issue: "Pinecone connection failed"
**Solution**: Verify your `PINECONE_API_KEY` and `PINECONE_INDEX_NAME` in the `.env` file. Make sure the index exists in your Pinecone account.

## Next Steps

After ingestion, you can:
1. Query the AI assistant with questions about Choreo
2. Use the frontend to interact with the knowledge base
3. Re-run the script periodically to get updates from repositories

The system will automatically detect and process only new or changed files on subsequent runs.
