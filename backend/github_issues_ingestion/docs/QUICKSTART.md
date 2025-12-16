# Quick Start Guide

## 1. Verify Configuration

Make sure your `.env` file in the `backend` directory has all required settings:

```bash
# Check if .env exists
ls -la ../backend/.env

# View configuration (be careful not to expose sensitive data)
cat ../backend/.env | grep -E "GITHUB_TOKEN|AZURE_OPENAI|PINECONE" | sed 's/=.*/=***/'
```

## 2. Test the System

Run the test suite to ensure everything is configured correctly:

```bash
python test_system.py
```

This will test:
- ✅ Configuration loading
- ✅ GitHub API connection
- ✅ Text processing
- ✅ Chunking
- ✅ Azure OpenAI embeddings
- ✅ Pinecone vector store
- ✅ Complete pipeline

## 3. Ingest Your First Repository

### Option A: Small Test (Recommended for first time)

```bash
# Ingest just 5 issues for testing
python main.py wso2/choreo --max-issues 5
```

### Option B: Full Repository

```bash
# Ingest all issues
python main.py wso2/choreo
```

### Option C: Filtered Ingestion

```bash
# Only open issues
python main.py wso2/choreo --state open

# Only issues with specific labels
python main.py wso2/choreo --labels bug,enhancement

# Only recent issues (since January 1, 2024)
python main.py wso2/choreo --since 2024-01-01T00:00:00Z

# Combine filters
python main.py wso2/choreo --state open --labels bug --max-issues 50
```

## 4. Query the Vector Database

After ingestion, you can search for similar issues:

```bash
# Search for issues related to authentication
python main.py wso2/choreo --query "authentication error"

# Get more results
python main.py wso2/choreo --query "deployment issues" --top-k 10

# Search for API problems
python main.py wso2/choreo --query "API rate limit exceeded"
```

## 5. Use in Your Code

### Basic Usage

```python
from github_issues_ingestion import create_ingestion_pipeline

# Create pipeline
orchestrator = create_ingestion_pipeline()

# Ingest repository
stats = orchestrator.ingest_repository("wso2", "choreo", max_issues=10)

# Query
results = orchestrator.query_issues("how to deploy")
for result in results:
    print(f"Issue: {result['metadata']['issue_title']}")
    print(f"Score: {result['score']}")
```

### Advanced Usage

```python
from github_issues_ingestion import (
    Settings,
    create_ingestion_pipeline
)

# Load settings
settings = Settings.from_env()

# Customize settings
settings.chunk_size = 500
settings.batch_size = 5

# Create pipeline with custom settings
orchestrator = create_ingestion_pipeline(settings=settings)

# Ingest with filters
stats = orchestrator.ingest_repository(
    owner="wso2",
    repo="choreo",
    state="open",
    labels=["bug"],
    since="2024-01-01T00:00:00Z"
)

# Query with metadata filters
results = orchestrator.query_issues(
    query="authentication error",
    top_k=5,
    filter_dict={
        "state": "open",
        "labels": ["bug"]
    }
)
```

## 6. Common Issues and Solutions

### Issue: "Missing required environment variables"

**Solution**: Make sure your `.env` file has all required variables:
```bash
GITHUB_TOKEN=...
AZURE_OPENAI_API_KEY=...
AZURE_OPENAI_ENDPOINT=...
AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT=...
AZURE_OPENAI_API_VERSION=...
PINECONE_API_KEY=...
PINECONE_INDEX_NAME=...
```

### Issue: "Rate limit exceeded"

**Solution**: The system automatically handles rate limits. If you're still hitting limits:
1. Use a GitHub token with higher rate limits
2. Reduce the number of issues fetched with `--max-issues`
3. Wait for the rate limit to reset

### Issue: "Pinecone index not found"

**Solution**: The system automatically creates indexes. If you see this error:
1. Check your Pinecone API key
2. Verify your Pinecone plan supports serverless indexes
3. Check the region is correct

### Issue: "Azure OpenAI quota exceeded"

**Solution**:
1. Reduce batch size: `--batch-size 5`
2. Process fewer issues: `--max-issues 10`
3. Wait for quota to reset

## 7. Monitoring Progress

The system provides real-time progress updates:

```
================================================================================
Starting ingestion for wso2/choreo
================================================================================

Step 1: Fetching issues from GitHub...
Fetching issues from wso2/choreo...
Fetched 50 issues
✓ Fetched 50 issues

Processing issue 1/50: #123 - Authentication fails with OAuth...
✓ Stored 5 chunks for issue #123

Processing issue 2/50: #124 - Deployment timeout in production...
✓ Stored 3 chunks for issue #124
...
```

## 8. Best Practices

1. **Start Small**: Test with `--max-issues 5` first
2. **Use Filters**: Filter by state, labels, or date to reduce load
3. **Monitor Costs**: Azure OpenAI and Pinecone usage incur costs
4. **Regular Updates**: Re-run ingestion periodically with `--since` to get new issues
5. **Namespace Organization**: Use namespaces to organize different repositories

## 9. Examples

### Example 1: Security Issues

```bash
# Ingest security-related issues
python main.py wso2/choreo --labels security,vulnerability --state all

# Query for similar security issues
python main.py wso2/choreo --query "SQL injection vulnerability"
```

### Example 2: Recent Bugs

```bash
# Ingest bugs from last 30 days
python main.py wso2/choreo --labels bug --since 2024-10-20T00:00:00Z

# Find similar bugs
python main.py wso2/choreo --query "null pointer exception in API"
```

### Example 3: Feature Requests

```bash
# Ingest feature requests
python main.py wso2/choreo --labels enhancement,feature --state open

# Find related feature requests
python main.py wso2/choreo --query "dark mode support"
```

## 10. Clean Up

To delete all data for a repository:

```bash
python main.py wso2/choreo --delete
```

**Warning**: This is permanent and cannot be undone!

## Need Help?

- Check the main [README.md](../README.md) for detailed documentation
- Run tests: `python test_system.py`
- Check logs in the console output
- Review error messages carefully

## Next Steps

1. ✅ Test the system
2. ✅ Ingest a small sample
3. ✅ Try querying
4. ✅ Integrate into your application
5. ✅ Set up regular ingestion for updates

