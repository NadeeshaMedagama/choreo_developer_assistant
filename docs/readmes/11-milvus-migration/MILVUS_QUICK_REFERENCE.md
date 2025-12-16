# Milvus Configuration - Quick Reference

## Environment Variables (backend/.env)

```env
# Milvus Cloud Configuration
MILVUS_URI=
MILVUS_TOKEN=
MILVUS_COLLECTION_NAME=readme_embeddings
MILVUS_DIMENSION=1536
MILVUS_METRIC=COSINE

# Azure OpenAI (for embeddings)
AZURE_OPENAI_API_KEY=your_azure_openai_api_key_here
AZURE_OPENAI_ENDPOINT=https://choreo-openai.openai.azure.com/
AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT=text-embedding-3-small
AZURE_OPENAI_API_VERSION=2024-02-01
AZURE_OPENAI_CHAT_DEPLOYMENT=

# GitHub Token
GITHUB_TOKEN=your_github_personal_access_token_here

# Google Vision API
GOOGLE_VISION_API_KEY=your_google_vision_api_key_here
```

## Key Points

✅ **MILVUS_USER and MILVUS_PASSWORD are NOT needed**
- Milvus Cloud uses TOKEN-based authentication only
- Only MILVUS_URI and MILVUS_TOKEN are required

✅ **Collection Name:** `readme_embeddings`
- Matches your Milvus Cloud collection
- Changed from old Pinecone index name

✅ **Dimension:** `1536`
- For Azure OpenAI text-embedding-ada-002 or text-embedding-3-small
- Change to 3072 for text-embedding-3-large
- Change to 384 for sentence-transformers/all-MiniLM-L6-v2

✅ **Metric:** `COSINE`
- Same similarity metric as Pinecone
- Optimal for text embeddings

## Testing the Setup

```bash
# 1. Verify environment variables are loaded
cd /home/nadeeshame/Projects/Choreo\ AI\ Assistant/choreo-ai-assistant
python -c "from backend.utils.config import load_config; c = load_config(); print(f'Milvus URI: {c[\"MILVUS_URI\"][:30]}...')"

# 2. Test Milvus connection
python -c "from backend.db.vector_client import VectorClient; from backend.utils.config import load_config; c = load_config(); vc = VectorClient(**{k.lower().replace('milvus_', ''): v for k, v in c.items() if k.startswith('MILVUS_')}); print('Connected:', vc.test_connection())"

# 3. Run the application
python -m uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000
```

## Files Changed

| File | Status |
|------|--------|
| backend/.env | ✅ Updated |
| .env.example | ✅ Updated |
| backend/utils/config.py | ✅ Updated |
| backend/wiki_ingestion/config.py | ✅ Updated |
| docker/docker-compose.yml | ✅ Updated |
| backend/run_ingestion.py | ✅ Updated |
| backend/scripts/ingest/ingest_wso2_choreo_repos.py | ✅ Updated |
| backend/scripts/ingest/ingest_choreo_readmes_standalone.py | ✅ Updated |
| backend/wiki_ingestion/requirements.txt | ✅ Updated |
| diagram_processor/README.md | ✅ Updated |

## Common Commands

### Start Backend
```bash
cd /home/nadeeshame/Projects/Choreo\ AI\ Assistant/choreo-ai-assistant
python -m uvicorn backend.app:app --reload
```

### Run Ingestion
```bash
python backend/run_ingestion.py
```

### Ingest Choreo Repositories
```bash
python backend/scripts/ingest/ingest_wso2_choreo_repos.py --org wso2-enterprise --keyword choreo
```

### Docker Deployment
```bash
cd docker
docker-compose up -d
```

## Troubleshooting

### Connection Issues
- Verify MILVUS_URI and MILVUS_TOKEN in .env
- Check Milvus Cloud dashboard
- Ensure collection exists or auto_create is enabled

### Import Errors
```bash
pip install pymilvus>=2.3.0
```

### Environment Not Loading
```bash
# Check .env file exists
ls -la backend/.env

# Verify python-dotenv is installed
pip install python-dotenv
```

## Migration Verification

✅ All Pinecone references removed  
✅ All files use Milvus configuration  
✅ No MILVUS_USER or MILVUS_PASSWORD  
✅ Collection name: readme_embeddings  
✅ Dimension: 1536 (Azure OpenAI)  
✅ Metric: COSINE  

**Status:** Migration Complete ✅

