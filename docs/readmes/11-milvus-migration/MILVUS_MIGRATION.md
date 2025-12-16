# Milvus Migration Guide

## Overview
This project has been migrated from Pinecone to Milvus Cloud as the vector database.

## What Changed

### 1. Environment Variables
The following environment variables have been replaced:

**OLD (Pinecone):**
```env
PINECONE_API_KEY=xxx
PINECONE_INDEX_NAME=choreo-ai-assistant-v2
PINECONE_DIMENSION=1536
PINECONE_CLOUD=aws
PINECONE_REGION=us-east-1
PINECONE_USE_NAMESPACES=true
```

**NEW (Milvus):**
```env
MILVUS_URI=https://in03-6c2efe91d7af234.serverless.aws-eu-central-1.cloud.zilliz.com
MILVUS_TOKEN=77d024d0f06829755b87c884d9475a8667579a000c48a411c9c8e972b5fb7471cb07abc8b3e1b7e0d62da73ba9b740f2ed1e7b40
MILVUS_COLLECTION_NAME=readme_embeddings
MILVUS_DIMENSION=1536
MILVUS_METRIC=COSINE
```

### 2. Dependencies
**requirements.txt changes:**
- Removed: `pinecone-client` or `pinecone`
- Added: `pymilvus>=2.3.0`

### 3. Code Changes

#### Updated Files:
1. **backend/.env** - Updated with Milvus credentials
2. **backend/utils/config.py** - Changed from Pinecone to Milvus configuration
3. **backend/db/vector_client.py** - Complete rewrite to use Milvus API
4. **backend/app.py** - Updated to use Milvus configuration
5. **backend/monitoring/health/health_checker.py** - MilvusHealthChecker (was PineconeHealthChecker)
6. **backend/github_issues_ingestion/config/settings.py** - Milvus settings
7. **backend/github_issues_ingestion/services/milvus_vector_store.py** - New Milvus implementation
8. **backend/github_issues_ingestion/services/__init__.py** - Export MilvusVectorStore
9. **backend/github_issues_ingestion/__init__.py** - Use MilvusVectorStore
10. **diagram_processor/utils/__init__.py** - Milvus configuration
11. **diagram_processor/services/__init__.py** - Milvus initialization
12. **diagram_processor/repositories/__init__.py** - Milvus repository
13. **diagram_processor/models/__init__.py** - Added to_milvus_format() method
14. **All requirements.txt files** - Updated dependencies

### 4. API Differences

#### Pinecone API vs Milvus API

**Initialization:**
```python
# OLD (Pinecone)
from pinecone import Pinecone
pc = Pinecone(api_key=api_key)
index = pc.Index(index_name)

# NEW (Milvus)
from pymilvus import MilvusClient
client = MilvusClient(uri=uri, token=token)
```

**Insert:**
```python
# OLD (Pinecone)
index.upsert(vectors=[(id, vector, metadata)])

# NEW (Milvus)
client.insert(collection_name=collection_name, data=[{
    "id": id,
    "vector": vector,
    "content": content,
    **metadata
}])
```

**Search:**
```python
# OLD (Pinecone)
results = index.query(vector=query_vector, top_k=5, include_metadata=True)

# NEW (Milvus)
results = client.search(
    collection_name=collection_name,
    data=[query_vector],
    limit=5,
    output_fields=["*"]
)
```

**Delete:**
```python
# OLD (Pinecone)
index.delete(ids=ids_list)
# OR
index.delete(filter=metadata_filter)

# NEW (Milvus)
client.delete(
    collection_name=collection_name,
    filter=filter_expression  # e.g., 'repository == "org/repo"'
)
```

## Installation Steps

1. **Install Milvus SDK:**
```bash
pip install pymilvus>=2.3.0
```

2. **Uninstall Pinecone (optional):**
```bash
pip uninstall pinecone-client pinecone
```

3. **Update .env file:**
   - Copy the Milvus credentials to your `backend/.env` file
   - Remove old Pinecone variables

4. **Test the connection:**
```bash
python -m backend.app
```

## Migration Checklist

- [x] Update environment variables
- [x] Install pymilvus
- [x] Update backend/db/vector_client.py
- [x] Update backend/utils/config.py
- [x] Update backend/app.py
- [x] Update health checker
- [x] Update GitHub issues ingestion services
- [x] Update diagram processor
- [x] Update all requirements.txt files
- [x] Update .env.example
- [x] Test connection

## Key Differences to Note

1. **Collection vs Index**: Milvus uses "collections" instead of Pinecone's "indexes"
2. **Metric Types**: Milvus uses `COSINE`, `L2`, `IP` (uppercase) vs Pinecone's `cosine`, `euclidean`, `dotproduct`
3. **Data Format**: Milvus stores data as dictionaries with fields, Pinecone uses tuples of (id, values, metadata)
4. **Dynamic Fields**: Milvus supports dynamic fields when `enable_dynamic_field=True`
5. **Filters**: Milvus uses expression strings like `'field == "value"'` vs Pinecone's dictionary filters

## Testing

After migration, verify:
1. Connection to Milvus Cloud works
2. Collections are created automatically
3. Embeddings can be inserted
4. Search queries return results
5. Health check passes

## Rollback Plan

If you need to rollback to Pinecone:
1. Restore the old `.env` file
2. Reinstall pinecone-client
3. Git revert the code changes
4. Restart the application

## Support

- Milvus Documentation: https://milvus.io/docs
- Zilliz Cloud Support: https://cloud.zilliz.com/
- PyMilvus API Reference: https://milvus.io/api-reference/pymilvus/v2.3.x/About.md

## Notes

- The migration maintains backward compatibility by keeping `to_pinecone_format()` methods
- All collections will be created automatically on first use
- Milvus serverless handles scaling automatically
- No data was migrated - this is a fresh start with Milvus

