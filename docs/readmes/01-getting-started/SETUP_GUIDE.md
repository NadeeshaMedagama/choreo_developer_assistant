# Complete Guide: Ingesting Choreo Documentation into Pinecone

## 🎯 What This Does

This system:
1. **Connects to GitHub** using REST API (no download needed)
2. **Finds all .md files** in the repository recursively
3. **Chunks the content** intelligently (respects paragraphs/sentences)
4. **Generates embeddings** using AI models
5. **Stores in Pinecone** for semantic search

## 📋 Prerequisites

1. **Pinecone Account** (required)
   - Sign up at https://www.pinecone.io/
   - Get your API key from the dashboard

2. **GitHub Token** (optional but highly recommended)
   - Without token: 60 requests/hour (will hit rate limit quickly)
   - With token: 5000 requests/hour (smooth ingestion)
   - Create at: https://github.com/settings/tokens

3. **Python 3.8+** installed

## 🚀 Quick Start

### Step 1: Install Dependencies

```bash
cd /home/nadeeshame/CHOREO/Choreo\ AI\ Assistant/choreo-ai-assistant
pip install -r requirements.txt
```

### Step 2: Configure Environment

Create a `.env` file:

```bash
cd choreo-ai-assistant
cp .env.example .env
```

Edit `.env` and add your credentials:

```env
# Required
PINECONE_API_KEY=your_pinecone_api_key_here

# Highly Recommended (to avoid rate limits)
GITHUB_TOKEN=your_github_token_here

# Optional - defaults are fine
PINECONE_INDEX_NAME=choreo-docs
PINECONE_DIMENSION=384
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

**How to get a GitHub token:**
1. Go to https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Select scope: `public_repo` (for public repositories)
4. Copy the token and paste it in `.env`

### Step 3: Load Environment Variables

```bash
# Option 1: Export them
export $(cat .env | xargs)

# Option 2: Use python-dotenv (already included in requirements.txt)
# The scripts will load .env automatically
```

### Step 4: Check Setup

```bash
cd backend
python check_setup.py
```

This verifies your environment variables are set correctly.

### Step 5: Test GitHub Connection

```bash
python backend/tests/test_github.py
```

This tests the GitHub API and lists all .md files found (should find ~34 files).

**Expected output:**
```
✓ Found 34 markdown files:
1. README.md
2. en/developer-docs/docs/administer/configure-a-custom-domain-for-your-organization.md
3. en/developer-docs/docs/administer/configure-a-user-store-with-built-in-idp.md
...
```

### Step 6: Run Full Ingestion

```bash
python run_ingestion.py
```

This will:
- Fetch all .md files from the repository
- Chunk them into manageable pieces
- Generate embeddings
- Store everything in Pinecone

**Expected output:**
```
============================================================
Starting Choreo Documentation Ingestion
============================================================
✓ Pinecone connection successful
✓ Using authenticated GitHub API
✓ Ingestion completed!

Files fetched: 34+
Chunks created: 500+
Embeddings stored: 500+
```

## 📊 What Gets Stored

Each chunk stored in Pinecone includes:

```json
{
  "id": "uuid",
  "vector": [384 float values],
  "metadata": {
    "content": "The actual text content...",
    "source": "github",
    "repository": "NadeeshaMedagama/docs-choreo-dev",
    "file_path": "en/developer-docs/docs/administer/...",
    "file_name": "configure-access-control.md",
    "url": "https://github.com/...",
    "chunk_index": 0,
    "start_char": 0,
    "end_char": 1000
  }
}
```

## 🔍 Usage After Ingestion

### Query from Python

```python
import sys
sys.path.insert(0, '/home/nadeeshame/CHOREO/Choreo AI Assistant/choreo-ai-assistant/backend')

from db.vector_client import VectorClient
from services.llm_service import LLMService

# Initialize
vector_client = VectorClient(
    api_key="your_pinecone_api_key",
    index_name="choreo-docs"
)
llm_service = LLMService()

# Ask a question
query = "How do I deploy an application in Choreo?"
query_embedding = llm_service.get_embedding(query)
results = vector_client.query_similar(query_embedding, top_k=5)

# Print results
for i, result in enumerate(results, 1):
    print(f"\n{i}. Score: {result['score']:.4f}")
    print(f"   File: {result['metadata']['file_path']}")
    print(f"   Content: {result['content'][:200]}...")
```

## ⚙️ Configuration Options

| Variable | Default | Description |
|----------|---------|-------------|
| `PINECONE_API_KEY` | *Required* | Your Pinecone API key |
| `PINECONE_INDEX_NAME` | `choreo-docs` | Pinecone index name |
| `PINECONE_DIMENSION` | `384` | Embedding dimension (384 for MiniLM) |
| `GITHUB_TOKEN` | *Optional* | GitHub PAT for 5000 req/hour |
| `EMBEDDING_MODEL` | `sentence-transformers/all-MiniLM-L6-v2` | Free local model |
| `CHUNK_SIZE` | `1000` | Characters per chunk |
| `CHUNK_OVERLAP` | `200` | Overlapping characters |

### Using OpenAI Embeddings (Optional)

If you prefer OpenAI embeddings instead of the free local model:

1. Add to `.env`:
   ```env
   OPENAI_API_KEY=your_openai_key
   PINECONE_DIMENSION=1536
   ```

2. Modify `run_ingestion.py`:
   ```python
   llm_service = LLMService(use_openai=True)
   ```

## 🛠️ Troubleshooting

### Rate Limit Errors

**Problem:** "403 rate limit exceeded"

**Solution:** 
- Add a GitHub token to `.env`
- Wait 1 hour for rate limit to reset
- Or: Fetch files in batches

### Pinecone Index Issues

**Problem:** "Index does not exist"

**Solution:** The system creates it automatically. Ensure:
- `PINECONE_API_KEY` is correct
- `PINECONE_DIMENSION` matches your embedding model
- You have available index quota in Pinecone

### Memory Issues

**Problem:** Out of memory during embedding generation

**Solution:**
- Reduce `CHUNK_SIZE` in `.env`
- Process fewer files at once
- Use a smaller embedding model

## 📁 Project Structure

```
backend/
├── db/
│   └── vector_client.py          # Pinecone operations
├── services/
│   ├── github_service.py         # GitHub API integration
│   ├── llm_service.py            # Embedding generation
│   └── ingestion.py              # Orchestration & chunking
├── utils/
│   ├── config.py                 # Configuration management
│   └── logger.py                 # Logging setup
├── check_setup.py                # Verify environment
├── backend/
│   ├── tests/
│   │   ├── test_github.py        # Test GitHub connection
└── run_ingestion.py              # Main ingestion script
```

## ✨ Features

- ✅ No repository download needed
- ✅ Uses GitHub REST API directly
- ✅ Smart text chunking (respects paragraphs/sentences)
- ✅ Batch processing for efficiency
- ✅ Comprehensive error handling
- ✅ Detailed logging
- ✅ Metadata preservation
- ✅ Free local embeddings (no API costs)
- ✅ Optional OpenAI embeddings support

## 🎓 Next Steps

After successful ingestion:

1. **Build a RAG system** - Use the embeddings for question-answering
2. **Create a chatbot** - Integrate with LangChain/LlamaIndex
3. **Add more repositories** - Ingest other documentation sources
4. **Implement caching** - Cache embeddings for faster queries

## 📝 Notes

- First run takes ~5-10 minutes (depends on repo size)
- ~34 markdown files in the Choreo docs repository
- Results in ~500+ chunks stored in Pinecone
- Each chunk is ~1000 characters with 200 char overlap
- Free tier Pinecone supports up to 100k vectors

## 🤝 Support

If you encounter issues:

3. Test GitHub connection: `python backend/tests/test_github.py`
2. Verify environment variables: `python check_setup.py`
3. Test GitHub connection: `python test_github.py`
4. Ensure Pinecone index is accessible

Congrats! You now have a complete documentation ingestion system! 🚀

