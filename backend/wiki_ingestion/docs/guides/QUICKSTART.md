# Wiki Ingestion - Quick Start Guide

## 🚀 Getting Started in 5 Minutes

### Step 1: Install Dependencies

```bash
cd backend/wiki_ingestion
pip install -r requirements.txt
```

### Step 2: Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and set your wiki URL
nano .env
```

Minimal configuration:
```bash
WIKI_URL=https://github.com/wso2/docs-choreo-dev/wiki
```

### Step 3: Run the System

**Option A: Basic Test Run**
```bash
cd backend
python -m wiki_ingestion.test_system
```

**Option B: Full Ingestion (Save to JSON)**
```bash
cd backend
python -m wiki_ingestion.main
```

**Option C: Ingest to Vector Database**
```bash
# Set additional env vars in .env:
# PINECONE_API_KEY=your-key
# PINECONE_INDEX=your-index
# AZURE_OPENAI_ENDPOINT=https://...
# AZURE_OPENAI_API_KEY=your-key

cd backend
python -m wiki_ingestion.examples.ingest_to_vector_db
```

### Step 4: Use Programmatically

```python
from wiki_ingestion.services import (
    UrlFetcherService,
    ContentExtractorService,
    WebCrawlerService,
    WikiChunkingService,
    WikiIngestionOrchestrator
)

# Initialize services
url_fetcher = UrlFetcherService()
content_extractor = ContentExtractorService()
web_crawler = WebCrawlerService(url_fetcher, content_extractor)
chunking_service = WikiChunkingService()

# Create orchestrator
orchestrator = WikiIngestionOrchestrator(
    web_crawler=web_crawler,
    url_fetcher=url_fetcher,
    content_extractor=content_extractor,
    chunking_service=chunking_service
)

# Run ingestion
result = orchestrator.ingest_wiki(
    wiki_url='https://github.com/owner/repo/wiki',
    max_depth=2,
    max_pages=50
)

# Access results
chunks = result['chunks']
pages = result['pages']
stats = result['statistics']

print(f"Created {len(chunks)} chunks from {len(pages)} pages")
```

## 📊 What Gets Produced

### 1. WikiPage Objects
Each wiki page becomes a `WikiPage` object with:
- Full content (text and markdown)
- All linked URLs (internal and external)
- Metadata (title, repository, timestamps)

### 2. WikiChunk Objects
Each page is chunked into `WikiChunk` objects with:
- Chunk text (smart chunking respects structure)
- Source traceability (URL, title, position)
- Rich metadata for filtering

### 3. Embedding-Ready Data
Output format ready for any vector database:
```python
{
    "id": "unique-chunk-id",
    "text": "chunk content...",
    "metadata": {
        "source_url": "...",
        "source_title": "...",
        "chunk_index": 0,
        "total_chunks": 5,
        "repository": "owner/repo",
        ...
    }
}
```

## 🎯 Common Use Cases

### Use Case 1: Crawl Entire Wiki
```python
result = orchestrator.ingest_wiki(
    wiki_url='https://github.com/owner/repo/wiki',
    max_depth=10,  # Deep crawl
    max_pages=None  # No limit
)
```

### Use Case 2: Quick Sample (First Few Pages)
```python
result = orchestrator.ingest_wiki(
    wiki_url='https://github.com/owner/repo/wiki',
    max_depth=1,  # Shallow
    max_pages=10  # Just 10 pages
)
```

### Use Case 3: Wiki Only (Skip Linked Content)
```python
orchestrator = WikiIngestionOrchestrator(
    web_crawler=web_crawler,
    url_fetcher=url_fetcher,
    content_extractor=content_extractor,
    chunking_service=chunking_service,
    fetch_linked_content=False  # Skip links
)
```

### Use Case 4: Large Chunks
```python
chunking_service = WikiChunkingService(
    chunk_size=2000,  # Larger chunks
    chunk_overlap=400,
    min_chunk_size=500
)
```

## 🔧 Troubleshooting

### Problem: "Failed to fetch page"
**Solution**: Check if the wiki is public and URL is correct
```python
from wiki_ingestion.services import UrlFetcherService
fetcher = UrlFetcherService()
html = fetcher.fetch('YOUR_WIKI_URL')
print(html[:200] if html else "Failed")
```

### Problem: "Too many chunks"
**Solution**: Increase chunk size
```python
chunking_service = WikiChunkingService(chunk_size=2000)
```

### Problem: "Crawling too slow"
**Solution**: Reduce depth or disable linked content
```python
result = orchestrator.ingest_wiki(
    wiki_url='...',
    max_depth=1,  # Reduce depth
    max_pages=20  # Limit pages
)
```

## 📈 Performance Tips

1. **Start Small**: Test with `max_pages=5` first
2. **Monitor Memory**: Large wikis can use significant RAM
3. **Adjust Chunk Size**: Balance between context and quantity
4. **Use Batches**: Process embeddings in batches of 10-50

## 🎓 Next Steps

1. ✅ Read the full [README.md](../../README.md)
2. ✅ Check [examples/](examples/) for more use cases
3. ✅ Extend with custom implementations
4. ✅ Integrate with your RAG system

---

**Questions?** Check the main README.md or open an issue!

