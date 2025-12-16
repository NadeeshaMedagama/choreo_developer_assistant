# Quick Start: Ingest WSO2 Choreo Repositories

This is a quick reference guide to get you started with ingesting markdown files from wso2 organization repositories (the choreo repositories are in the `wso2` org, not `wso2-enterprise`).

## Prerequisites

Make sure your `.env` file exists in the `choreo-ai-assistant` directory with these required values:

```env
# Required for Pinecone
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_INDEX_NAME=choreo-ai-assistant-v2

# Required for Azure OpenAI
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com/
AZURE_OPENAI_KEY=your_azure_openai_key
AZURE_OPENAI_DEPLOYMENT=your_deployment_name
AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT=your_embeddings_deployment  # Optional

# Required for GitHub
GITHUB_TOKEN=your_github_personal_access_token
```

## Run the Ingestion

Simply run the standalone script:

```bash
cd choreo-ai-assistant
python backend/scripts/ingest/ingest_wso2_choreo_repos.py
```

That's it! The script will:
- ✅ Find all repositories in wso2 containing "choreo"
- ✅ Read all .md files from each repository
- ✅ Chunk the content intelligently
- ✅ Generate embeddings using Azure OpenAI
- ✅ Store embeddings in your Pinecone database (choreo-ai-assistant-v2)
- ✅ Skip already-processed files (incremental updates)
- ✅ Handle memory management automatically

## Options

### Limit to first N repositories (for testing):
```bash
python backend/scripts/ingest/ingest_wso2_choreo_repos.py --max-repos 3
```

### Use different organization/keyword:
```bash
python backend/scripts/ingest/ingest_wso2_choreo_repos.py --org my-org --keyword my-keyword
```

### Get help:
```bash
python backend/scripts/ingest/ingest_wso2_choreo_repos.py --help
```

## What Happens During Ingestion?

The script will display progress like this:

```
================================================================================
WSO2 Choreo Repositories Ingestion Script
================================================================================
Organization: wso2
Keyword filter: choreo
Max repositories: All
================================================================================
✓ Configuration loaded successfully
✓ Pinecone client initialized
✓ Azure OpenAI service initialized
✓ GitHub service initialized
✓ Ingestion service initialized
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
```

## Alternative Methods

### Method 2: Using the API endpoint (if backend is running)

```bash
curl -X POST "http://localhost:8000/api/ingest/org?org=wso2&keyword=choreo"
```

### Method 3: From Python code

```python
from backend.services.ingestion import IngestionService
from backend.utils.config import load_config
# ... initialize services ...

result = ingestion_service.ingest_org_repositories(
    org="wso2",
    keyword="choreo"
)
```

## Troubleshooting

**Issue: "Missing required configuration keys"**  
→ Check your `.env` file has all required variables

**Issue: "GitHub API rate limit exceeded"**  
→ Make sure GITHUB_TOKEN is set in `.env`

**Issue: "Pinecone connection failed"**  
→ Verify PINECONE_API_KEY and PINECONE_INDEX_NAME

## Next Steps

After ingestion completes:
1. Query your AI assistant with Choreo-related questions
2. Re-run the script periodically to get updates (only changed files will be processed)
3. Use the frontend to interact with the knowledge base

For detailed documentation, see `INGEST_WSO2_CHOREO_REPOS.md`
