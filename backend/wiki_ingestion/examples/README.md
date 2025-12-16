# Wiki Ingestion Examples

This directory contains example scripts demonstrating different uses of the wiki ingestion system.

## 📋 Available Examples

### 1. **Ingest to Milvus** (`ingest_to_milvus.py`)
Complete pipeline that crawls GitHub wiki, creates embeddings with Azure OpenAI, and stores in Milvus vector database.

**Usage:**
```bash
cd backend
python -m wiki_ingestion.examples.ingest_to_milvus
```

**Features:**
- Crawls GitHub wikis with configurable depth
- Creates semantic chunks with overlap
- Generates embeddings using Azure OpenAI
- Stores in Milvus with rich metadata
- Batch processing with progress tracking

### 2. **Verify Milvus Data** (`verify_milvus_data.py`)
Verification script to check if data was ingested correctly into Milvus.

**Usage:**
```bash
cd backend
python -m wiki_ingestion.examples.verify_milvus_data
```

**Features:**
- Tests Milvus connection
- Shows collection statistics
- Displays sample records
- Tests search functionality

### 3. **Ingest to Pinecone** (`ingest_to_vector_db.py`)
Similar to Milvus integration but uses Pinecone as the vector database.

### 4. **Ingest Choreo Wiki** (`ingest_choreo_wiki.py`)
Pre-configured script specifically for Choreo documentation.

### 5. **Complete Choreo Ingestion** (`ingest_choreo_complete.py`)
Comprehensive ingestion for all Choreo documentation sources.

### 6. **Simple Crawl** (`simple_crawl.py`)
Basic example showing just the crawling functionality without vector database integration.

## 📁 Available Examples

### 📄 simple_crawl.py
Basic wiki crawl without vector database integration.

```bash
cd backend
export WIKI_URL="https://github.com/wso2/docs-choreo-dev/wiki"
python -m wiki_ingestion.examples.simple_crawl
```

**What it does:**
- Crawls wiki pages
- Extracts and chunks content
- Saves output to JSON file

**Best for:**
- Testing the system
- Exploring wiki structure
- Offline processing

---

### 🗄️ ingest_to_vector_db.py
Complete pipeline with Pinecone vector database integration.

```bash
cd backend
# Ensure .env has Pinecone credentials
python -m wiki_ingestion.examples.ingest_to_vector_db
```

**What it does:**
- Crawls wiki
- Creates embeddings via Azure OpenAI
- Stores in Pinecone vector database

**Requirements:**
- `PINECONE_API_KEY` in .env
- `AZURE_OPENAI_*` credentials in .env

---

### 🎯 ingest_choreo_complete.py
Complete Choreo wiki ingestion (web-based crawling).

```bash
cd backend
export WIKI_URL="https://github.com/wso2-enterprise/choreo/wiki"
python wiki_ingestion/examples/ingest_choreo_complete.py
```

**What it does:**
- Attempts web-based crawling
- Full embedding and storage
- Comprehensive error handling

**Note:** Use `ingest_via_git.py` instead for private wikis.

---

### 📚 ingest_choreo_wiki.py
Alternative Choreo ingestion script.

```bash
cd backend
python wiki_ingestion/examples/ingest_choreo_wiki.py
```

**What it does:**
- Similar to ingest_choreo_complete.py
- Different configuration options
- Alternative implementation

---

## 🎯 Recommended Usage

### For Testing
```bash
# Use simple_crawl.py
export WIKI_URL="https://github.com/wso2/docs-apim/wiki"
export WIKI_MAX_PAGES=5
python -m wiki_ingestion.examples.simple_crawl
```

### For Production (Public Wiki)
```bash
# Use ingest_to_vector_db.py
python -m wiki_ingestion.examples.ingest_to_vector_db
```

### For Production (Private Wiki)
```bash
# Use ../ingest_via_git.py (in parent directory)
python -m backend.wiki_ingestion.ingest_via_git
```

---

## 🔧 Configuration

All examples use environment variables from `backend/.env`:

```bash
# Wiki settings
WIKI_URL=https://github.com/owner/repo/wiki
WIKI_MAX_DEPTH=2
WIKI_MAX_PAGES=50

# Authentication (for private repos)
GITHUB_TOKEN=your_token

# Vector DB
PINECONE_API_KEY=your_key
PINECONE_INDEX_NAME=your_index

# Embeddings
AZURE_OPENAI_ENDPOINT=https://...
AZURE_OPENAI_API_KEY=your_key
AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT=model_name
```

---

## 📊 Output Examples

### simple_crawl.py
Creates `wiki_crawl_YYYYMMDD_HHMMSS.json` with:
- All wiki pages
- All chunks
- Statistics

### ingest_to_vector_db.py
Stores in Pinecone and shows:
- Number of chunks stored
- Success rate
- Pinecone index name

---

## 🔙 Back to Main

See [../README.md](../README.md) for complete documentation.

