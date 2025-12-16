# Wiki Ingestion to Milvus Vector Database - Complete Guide

This guide walks you through ingesting GitHub wiki content into your Milvus vector database.

## 📋 Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Configuration](#configuration)
4. [Running the Ingestion](#running-the-ingestion)
5. [What Happens During Ingestion](#what-happens-during-ingestion)
6. [Verifying the Data](#verifying-the-data)
7. [Troubleshooting](#troubleshooting)
8. [Advanced Usage](#advanced-usage)

---

## 🎯 Overview

The `ingest_to_milvus.py` script performs the following steps:

1. **Crawls** the GitHub wiki pages (starting from a root URL)
2. **Extracts** clean content from each page
3. **Chunks** the content into manageable pieces (1000 chars with 200 char overlap)
4. **Embeds** each chunk using Azure OpenAI embeddings
5. **Stores** the embeddings in your Milvus vector database

### What Gets Stored

Each chunk stored in Milvus contains:
- **Vector**: 1536-dimensional embedding (from Azure OpenAI)
- **Text**: The actual text content
- **Metadata**: Source URL, title, repository, chunk info, etc.

---

## ✅ Prerequisites

### 1. Environment Setup

Make sure you have:
- ✅ Python 3.8+ installed
- ✅ Required packages installed
- ✅ Access to Milvus cloud instance
- ✅ Access to Azure OpenAI

### 2. Install Dependencies

```bash
cd /home/nadeeshame/Projects/Choreo\ AI\ Assistant/choreo-ai-assistant/backend

# Install wiki ingestion requirements
pip install -r wiki_ingestion/requirements.txt

# Ensure you have these packages
pip install pymilvus openai python-dotenv beautifulsoup4 html2text requests
```

---

## ⚙️ Configuration

### 1. Environment Variables

Your `.env` file (located at `backend/.env`) should contain:

```bash
# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com/
AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT=choreo-ai-embedding
AZURE_OPENAI_EMBEDDINGS_VERSION=2024-02-01

# Milvus Configuration
MILVUS_URI=https://your-instance.vectordb.zillizcloud.com:19530
MILVUS_TOKEN=your-milvus-token
MILVUS_COLLECTION_NAME=choreo_developer_assistant
MILVUS_DIMENSION=1536

# Wiki Ingestion Configuration
WIKI_URL=https://github.com/wso2/docs-choreo-dev/wiki
WIKI_MAX_DEPTH=2
WIKI_MAX_PAGES=50
WIKI_FETCH_LINKED=true

# GitHub Token (optional, for higher rate limits)
GITHUB_TOKEN=your-github-token
```

### 2. Configuration Explanation

| Variable | Description | Default |
|----------|-------------|---------|
| `WIKI_URL` | Starting wiki URL to crawl | Required |
| `WIKI_MAX_DEPTH` | How deep to crawl (0 = only start page) | 2 |
| `WIKI_MAX_PAGES` | Maximum pages to crawl | 50 |
| `WIKI_FETCH_LINKED` | Fetch external linked content | true |
| `MILVUS_DIMENSION` | Embedding dimension (1536 for ada-002) | 1536 |

---

## 🚀 Running the Ingestion

### Quick Start

```bash
# Navigate to backend directory
cd /home/nadeeshame/Projects/Choreo\ AI\ Assistant/choreo-ai-assistant/backend

# Run the ingestion script
python -m wiki_ingestion.examples.ingest_to_milvus
```

### Expected Output

```
╔══════════════════════════════════════════════════════════════╗
║       WIKI INGESTION + MILVUS VECTOR DATABASE                ║
╚══════════════════════════════════════════════════════════════╝

Configuration:
  📚 Wiki URL: https://github.com/wso2/docs-choreo-dev/wiki
  🔍 Max Depth: 2
  📄 Max Pages: 50
  🔗 Fetch Linked Content: True
  
  🗄️  Milvus Collection: choreo_developer_assistant
  📏 Embedding Dimension: 1536
  🤖 Embedding Model: choreo-ai-embedding

🔧 Initializing wiki ingestion services...
✅ Wiki ingestion services initialized

🕷️  Starting wiki crawl and ingestion...

[Crawling progress...]

✅ Successfully crawled 45 pages
✅ Created 234 chunks from wiki pages
✅ Processed 12 linked URLs

🔧 Initializing Milvus vector database...
✅ Connected to Milvus vector database

🔧 Initializing Azure OpenAI embedding service...
✅ Azure OpenAI embedding service initialized

📦 Embedding and storing 234 chunks in Milvus...
================================================================================

📦 Processing batch 1/24 (10 chunks)...
   🔄 Creating embeddings...
   💾 Storing in Milvus...
   ✅ Batch complete (10/234 total)

[... more batches ...]

================================================================================
✅ WIKI INGESTION TO MILVUS COMPLETE
================================================================================

📊 Statistics:
   • Wiki pages crawled: 45
   • Linked URLs processed: 12
   • Total chunks created: 234
   • Chunks stored in Milvus: 234
   • Failed chunks: 0
   • Success rate: 100.0%

🗄️  Milvus Collection: choreo_developer_assistant
📏 Embedding Dimension: 1536
================================================================================
```

---

## 🔍 What Happens During Ingestion

### Phase 1: Wiki Crawling (30-60 seconds)

```
🕷️  Starting wiki crawl...
```

The script:
- Fetches the starting wiki page
- Extracts all internal wiki links
- Crawls each page (respecting `MAX_DEPTH` and `MAX_PAGES`)
- Uses BFS (Breadth-First Search) strategy

### Phase 2: Content Processing (10-20 seconds)

```
📄 Processing pages and creating chunks...
```

For each page:
- Extracts clean text content
- Converts HTML to markdown
- Splits into chunks (~1000 chars each)
- Preserves context with overlap (200 chars)

### Phase 3: Embedding & Storage (2-5 minutes)

```
📦 Embedding and storing chunks...
```

For each batch of 10 chunks:
- Sends text to Azure OpenAI
- Gets 1536-dimensional embeddings
- Stores in Milvus with metadata

**Why batches of 10?**
- Prevents API rate limits
- Allows progress tracking
- Enables error recovery

---

## ✅ Verifying the Data

### Option 1: Check Milvus Collection

```python
from db.vector_client import VectorClient
import os
from dotenv import load_dotenv

load_dotenv()

client = VectorClient(
    uri=os.getenv('MILVUS_URI'),
    token=os.getenv('MILVUS_TOKEN'),
    collection_name=os.getenv('MILVUS_COLLECTION_NAME')
)

# Get collection stats
stats = client.get_collection_stats()
print(f"Total entities: {stats['row_count']}")
```

### Option 2: Test Search

```python
# Search for wiki content
from openai import AzureOpenAI

# Create embedding for query
openai_client = AzureOpenAI(
    api_key=os.getenv('AZURE_OPENAI_API_KEY'),
    api_version="2024-02-01",
    azure_endpoint=os.getenv('AZURE_OPENAI_ENDPOINT')
)

query = "How do I deploy to Choreo?"
response = openai_client.embeddings.create(
    model="choreo-ai-embedding",
    input=[query]
)
query_embedding = response.data[0].embedding

# Search in Milvus
results = client.search(
    data=[query_embedding],
    limit=5,
    output_fields=["text", "source_title", "source_url"]
)

for hit in results[0]:
    print(f"\nTitle: {hit['entity']['source_title']}")
    print(f"URL: {hit['entity']['source_url']}")
    print(f"Text: {hit['entity']['text'][:200]}...")
    print(f"Score: {hit['distance']}")
```

### Option 3: Check via Milvus Console

1. Go to [Zilliz Cloud Console](https://cloud.zilliz.com/)
2. Navigate to your collection
3. Check the entity count
4. Use the query interface to search

---

## 🐛 Troubleshooting

### Issue: "Missing required environment variables"

**Cause**: `.env` file not properly configured

**Solution**:
```bash
cd backend
cat .env | grep -E "MILVUS|AZURE_OPENAI"
```

Make sure all required variables are set.

### Issue: "Failed to connect to Milvus"

**Cause**: Incorrect Milvus credentials or network issues

**Solution**:
```python
# Test Milvus connection
from pymilvus import MilvusClient

client = MilvusClient(
    uri="your-milvus-uri",
    token="your-milvus-token"
)
print(client.list_collections())
```

### Issue: "Rate limit exceeded" from Azure OpenAI

**Cause**: Too many requests to Azure OpenAI

**Solution**:
- Reduce batch size in the script (change `batch_size = 10` to `batch_size = 5`)
- Add delay between batches:
  ```python
  import time
  time.sleep(1)  # Add after each batch
  ```

### Issue: "Dimension mismatch"

**Cause**: Wrong embedding dimension configured

**Solution**:
- Check your Azure OpenAI deployment model
- `text-embedding-ada-002` = 1536 dimensions
- `text-embedding-3-small` = 1536 dimensions  
- `text-embedding-3-large` = 3072 dimensions

Update `MILVUS_DIMENSION` in `.env` accordingly.

### Issue: Some chunks failed to store

**Cause**: Network issues, temporary errors

**Solution**:
- The script continues on errors
- Check the failed count in the summary
- Re-run the script (it will update existing chunks)

---

## 🔧 Advanced Usage

### Custom Wiki URL

```bash
export WIKI_URL="https://github.com/your-org/your-repo/wiki"
python -m wiki_ingestion.examples.ingest_to_milvus
```

### Deeper Crawl

```bash
export WIKI_MAX_DEPTH=3
export WIKI_MAX_PAGES=100
python -m wiki_ingestion.examples.ingest_to_milvus
```

### Skip Linked Content

```bash
export WIKI_FETCH_LINKED=false
python -m wiki_ingestion.examples.ingest_to_milvus
```

### Custom Chunk Size

Edit the script to change chunking parameters:

```python
chunking_service = WikiChunkingService(
    chunk_size=1500,      # Larger chunks
    chunk_overlap=300,    # More overlap
    min_chunk_size=200    # Higher minimum
)
```

### Use Different Collection

```bash
export MILVUS_COLLECTION_NAME="my_custom_collection"
python -m wiki_ingestion.examples.ingest_to_milvus
```

---

## 📊 Understanding the Data Structure

### Milvus Schema

Each record in Milvus has:

```python
{
    'id': 'unique-chunk-id',           # UUID
    'vector': [0.1, 0.2, ...],         # 1536 dimensions
    'text': 'actual chunk content',    # String
    'source_url': 'https://...',       # Source page URL
    'source_title': 'Page Title',      # Source page title
    'source_type': 'wiki_page',        # Type: wiki_page or linked_content
    'repository': 'wso2/docs-choreo',  # GitHub repo
    'owner': 'wso2',                   # GitHub owner
    'chunk_index': 0,                  # Index of chunk in source
    'chunk_size': 1024,                # Size in characters
    'total_chunks': 5,                 # Total chunks from source
    'wiki_name': 'docs-choreo-dev',    # Wiki name (if wiki_page)
    'page_path': 'Getting-Started',    # Page path (if wiki_page)
    'depth': 1                         # Crawl depth (if wiki_page)
}
```

### Querying with Metadata Filters

```python
# Search only wiki pages (not linked content)
results = client.search(
    data=[query_embedding],
    filter="source_type == 'wiki_page'",
    limit=5
)

# Search specific repository
results = client.search(
    data=[query_embedding],
    filter="repository == 'wso2/docs-choreo-dev'",
    limit=5
)

# Search by depth
results = client.search(
    data=[query_embedding],
    filter="depth <= 2",
    limit=5
)
```

---

## 🎯 Best Practices

### 1. Start Small

First run with conservative settings:
```bash
export WIKI_MAX_PAGES=10
export WIKI_MAX_DEPTH=1
export WIKI_FETCH_LINKED=false
```

### 2. Monitor Progress

The script shows real-time progress. Watch for:
- ✅ Successful batches
- ❌ Failed batches
- Success rate at the end

### 3. Incremental Updates

The script uses chunk IDs based on content. Re-running will:
- Update existing chunks (if content changed)
- Add new chunks (if new pages)
- Keep old chunks (if pages still exist)

### 4. Regular Updates

Schedule periodic ingestion to keep data fresh:
```bash
# Cron job example (daily at 2 AM)
0 2 * * * cd /path/to/backend && python -m wiki_ingestion.examples.ingest_to_milvus >> logs/ingestion.log 2>&1
```

---

## 📝 Next Steps

After successful ingestion:

1. **Test Search**: Verify data with test queries
2. **Integrate with Chat**: Use in your RAG pipeline
3. **Monitor Usage**: Track search performance
4. **Update Regularly**: Keep wiki content fresh

---

## 🤝 Need Help?

- Check the main [README.md](../../README.md) for architecture details
- Review [examples/](examples/) for more use cases
- Check logs in `backend/logs/` for detailed errors

---

**Happy Ingesting! 🚀**

