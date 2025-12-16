# How to Find and Ingest Issues from Repositories

## Quick Answer

To find and ingest issues from a particular repository, use one of these methods:

### Method 1: Direct Ingestion (Simplest)

If you know the repository name:

```bash
cd backend/github_issues_ingestion
python main.py owner/repo --max-issues 50
```

**Example:**
```bash
python main.py wso2/choreo --max-issues 50
```

### Method 2: Using the Repository Finder Tool

Use the new `repo_finder.py` tool:

```bash
# Search for repositories
python repo_finder.py search "wso2"

# List all WSO2 organization repos
python repo_finder.py list-org wso2

# Check a specific repo before ingesting
python repo_finder.py check wso2/choreo

# Ingest a specific repo
python repo_finder.py ingest wso2/choreo --max-issues 50

# Auto-find and ingest multiple repos
python repo_finder.py auto-ingest "org:wso2" --max-repos 3
```

### Method 3: Python Code

```python
from github_issues_ingestion import create_ingestion_pipeline

# Create pipeline
orchestrator = create_ingestion_pipeline()

# Ingest specific repository
stats = orchestrator.ingest_repository(
    owner="wso2",
    repo="choreo",
    max_issues=50
)

print(f"Ingested {stats['total_issues']} issues")
print(f"Created {stats['total_chunks']} chunks")
```

---

## Complete Step-by-Step Guide

### Step 1: Find Repositories

#### Option A: Search by keyword
```bash
python repo_finder.py search "wso2 api"
```

Output shows:
- Repository names
- Star counts
- Issue counts
- Descriptions

#### Option B: List organization repos
```bash
python repo_finder.py list-org wso2
```

#### Option C: Use GitHub directly
Visit: https://github.com/wso2?tab=repositories

### Step 2: Check Repository Details

Before ingesting, check if the repo has issues:

```bash
python repo_finder.py check wso2/choreo
```

This shows:
- ✅ Number of open issues
- ✅ Stars and forks
- ✅ Whether issues are enabled
- ✅ Last update date

### Step 3: Ingest Issues

#### Basic ingestion:
```bash
python main.py wso2/choreo --max-issues 50
```

#### With filters:
```bash
# Only open issues
python main.py wso2/choreo --state open --max-issues 50

# Only specific labels
python main.py wso2/choreo --labels bug,enhancement --max-issues 50

# Only recent issues (last 30 days)
python main.py wso2/choreo --since 2024-10-20T00:00:00Z --max-issues 50
```

### Step 4: Verify Ingestion

The system automatically:
1. ✅ Fetches all issue data (title, body, comments)
2. ✅ Cleans and processes the text
3. ✅ Chunks the text (default: 1000 characters with 200 overlap)
4. ✅ Creates embeddings using Azure OpenAI
5. ✅ Stores in Pinecone with metadata

### Step 5: Query the Ingested Issues

```bash
python main.py wso2/choreo --query "authentication error"
```

Or in Python:
```python
results = orchestrator.query_issues("authentication error", top_k=5)

for result in results:
    print(f"Issue #{result['metadata']['issue_number']}")
    print(f"Title: {result['metadata']['issue_title']}")
    print(f"Score: {result['score']:.4f}")
```

---

## What Gets Stored

For each issue, the system stores:

```python
{
    "issue_number": 123,
    "issue_title": "Authentication fails",
    "repository": "wso2/choreo",
    "state": "open",
    "labels": ["bug", "authentication"],
    "created_at": "2024-11-01T10:00:00Z",
    "updated_at": "2024-11-15T14:30:00Z",
    "url": "https://github.com/wso2/choreo/issues/123",
    "chunk_index": 0,
    "total_chunks": 3,
    "content": "chunk text content..."
}
```

---

## Common Use Cases

### Use Case 1: Ingest All Issues from a Specific Repo

```bash
python main.py wso2/choreo
```

### Use Case 2: Ingest Only Bug Reports

```bash
python main.py wso2/choreo --labels bug --state open
```

### Use Case 3: Ingest Recent Issues (Incremental Update)

```bash
# Get issues from last 7 days
python main.py wso2/choreo --since 2024-11-13T00:00:00Z
```

### Use Case 4: Find and Ingest Multiple WSO2 Repos

```bash
python repo_finder.py auto-ingest "org:wso2" --max-repos 5 --min-issues 10
```

### Use Case 5: Search Ingested Issues

```bash
python main.py wso2/choreo --query "deployment timeout error"
```

---

## Example Workflow: Complete Process

```bash
# 1. List all WSO2 repositories
python repo_finder.py list-org wso2

# Output shows:
# 1. wso2/choreo (⭐ 50 | 🐛 120 issues)
# 2. wso2/product-apim (⭐ 800 | 🐛 350 issues)
# ...

# 2. Check a specific repository
python repo_finder.py check wso2/choreo

# Output shows:
# ✅ This repository has 120 open issues ready to ingest!

# 3. Ingest the repository
python repo_finder.py ingest wso2/choreo --max-issues 50

# Output shows:
# ✅ Ingestion complete!
#    Issues processed: 50
#    Chunks created: 237
#    Embeddings generated: 237

# 4. Query the issues
python main.py wso2/choreo --query "API authentication issues"

# Output shows:
# Top 5 results:
# 1. Issue #123: OAuth authentication fails (Score: 0.8542)
# 2. Issue #456: API key validation error (Score: 0.8231)
# ...
```

---

## Tips

### 💡 Tip 1: Start Small
Test with a small number of issues first:
```bash
python main.py wso2/choreo --max-issues 5
```

### 💡 Tip 2: Use Filters
Filter by state and labels to get relevant issues:
```bash
python main.py wso2/choreo --state open --labels bug,critical
```

### 💡 Tip 3: Incremental Updates
Use `--since` to only ingest new/updated issues:
```bash
python main.py wso2/choreo --since 2024-11-01T00:00:00Z
```

### 💡 Tip 4: Check First
Always check the repo before ingesting:
```bash
python repo_finder.py check owner/repo
```

### 💡 Tip 5: Use Auto-Ingest
For multiple repos, use auto-ingest:
```bash
python repo_finder.py auto-ingest "org:wso2" --max-repos 3
```

---

## Python API Examples

### Find and Ingest in Code

```python
import requests
from github_issues_ingestion import create_ingestion_pipeline
import os

# Setup
github_token = os.getenv("GITHUB_TOKEN")
orchestrator = create_ingestion_pipeline()

# Method 1: Ingest specific repo
stats = orchestrator.ingest_repository("wso2", "choreo", max_issues=50)

# Method 2: Search and ingest
def find_and_ingest(search_query, max_repos=3):
    url = "https://api.github.com/search/repositories"
    headers = {"Authorization": f"Bearer {github_token}"}
    params = {"q": search_query, "sort": "stars", "per_page": max_repos}
    
    response = requests.get(url, headers=headers, params=params)
    repos = response.json()["items"]
    
    for repo in repos:
        owner = repo["owner"]["login"]
        name = repo["name"]
        
        print(f"Ingesting {owner}/{name}...")
        stats = orchestrator.ingest_repository(owner, name, max_issues=30)
        print(f"  ✓ Processed {stats['total_issues']} issues")

# Use it
find_and_ingest("org:wso2", max_repos=3)

# Query
results = orchestrator.query_issues("authentication error", top_k=5)
for r in results:
    print(f"#{r['metadata']['issue_number']}: {r['metadata']['issue_title']}")
```

---

## Summary

**To find issues in a particular repo:**

1. **Know the repo?** → `python main.py owner/repo`
2. **Need to search?** → `python repo_finder.py search "query"`
3. **List org repos?** → `python repo_finder.py list-org org-name`
4. **Check details?** → `python repo_finder.py check owner/repo`
5. **Auto-ingest?** → `python repo_finder.py auto-ingest "query"`

**The system handles everything else automatically!**
- Fetches all issue data
- Processes and cleans text
- Creates chunks
- Generates embeddings
- Stores in vector database
- Enables semantic search

**Ready to start?**
```bash
python repo_finder.py list-org wso2
python repo_finder.py check wso2/choreo
python main.py wso2/choreo --max-issues 10
```

