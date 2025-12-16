# AI Models Used in Choreo AI Assistant

## Overview

This project uses multiple AI models for different purposes: **language generation**, **embeddings**, and **image processing**.

---

## 🤖 Primary AI Models

### 1. **Azure OpenAI GPT-4** (Language Generation)

**Purpose**: Generate intelligent responses to user queries about Choreo

**Model Details**:
- **Provider**: Azure OpenAI Service
- **Model**: GPT-4 (or GPT-4 Turbo)
- **Use Case**: Chat completions, answering questions, generating explanations
- **API Version**: 2024-02-15-preview (configurable)

**Configuration** (`backend/.env`):
```bash
AZURE_OPENAI_API_KEY=your_api_key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=your-gpt4-deployment-name
AZURE_OPENAI_CHAT_DEPLOYMENT=your-gpt4-deployment-name  # Alternative
AZURE_OPENAI_API_VERSION=2024-02-15-preview
```

**Where it's used**:
- `backend/app.py` - Main chat endpoints (`/api/ask`, `/api/ask/stream`)
- `backend/services/llm_service.py` - LLM service initialization
- Conversation summarization (when enabled)

**Example Usage**:
```python
response = llm_service.client.chat.completions.create(
    model=llm_service.deployment,  # Your GPT-4 deployment
    messages=messages,
    max_tokens=1000,
    temperature=0.7
)
```

---

### 2. **Azure OpenAI Text-Embedding-Ada-002** (Embeddings)

**Purpose**: Convert text into vector embeddings for semantic search

**Model Details**:
- **Provider**: Azure OpenAI Service
- **Model**: text-embedding-ada-002
- **Embedding Dimension**: 1536
- **Use Case**: Creating embeddings for documents and queries

**Configuration** (`backend/.env`):
```bash
AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT=your-embedding-deployment-name
AZURE_OPENAI_API_VERSION=2024-02-15-preview
```

**Where it's used**:
- Document ingestion (converting content to vectors)
- Query processing (converting user questions to vectors)
- Vector similarity search in Pinecone

**Example Usage**:
```python
embedding = client.embeddings.create(
    model=embeddings_deployment,  # text-embedding-ada-002
    input=text
)
```

---

### 3. **Sentence Transformers** (Alternative Embeddings)

**Purpose**: Local/open-source alternative for embeddings

**Model Details**:
- **Provider**: Hugging Face
- **Default Model**: `sentence-transformers/all-MiniLM-L6-v2`
- **Embedding Dimension**: 384
- **Use Case**: Lightweight embeddings when Azure OpenAI is not available

**Configuration** (`backend/.env`):
```bash
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

**Other Popular Options**:
- `sentence-transformers/all-mpnet-base-v2` (768 dimensions, higher quality)
- `sentence-transformers/multi-qa-MiniLM-L6-cos-v1` (384 dimensions, optimized for Q&A)

**Where it's used**:
- `backend/services/llm_service.py` - Fallback when Azure OpenAI is not configured
- Local development and testing

---

### 4. **Google Cloud Vision API** (Image Processing)

**Purpose**: Extract text and analyze images in documentation

**Model Details**:
- **Provider**: Google Cloud
- **API**: Vision API
- **Use Case**: OCR (text extraction) from images, diagrams, and screenshots

**Configuration** (`backend/.env`):
```bash
GOOGLE_VISION_API_KEY=your_google_vision_api_key
```

**Where it's used**:
- `backend/services/image_service.py` - Image processing service
- Processing diagrams and visual documentation
- Extracting text from screenshots

---

## 📊 Model Selection Logic

### For Embeddings

```python
# Priority order:
1. Azure OpenAI (if configured)
   └─ text-embedding-ada-002 (1536 dimensions)

2. OpenAI API (if configured)
   └─ text-embedding-ada-002 (1536 dimensions)

3. Sentence Transformers (fallback/default)
   └─ all-MiniLM-L6-v2 (384 dimensions)
```

**Code Reference** (`backend/services/llm_service.py`):
```python
if self.use_azure:
    self._init_azure_openai()
elif use_openai:
    self._init_openai()
else:
    self._init_sentence_transformer()
```

### For Chat/Completions

```python
# Only Azure OpenAI is used
Azure OpenAI GPT-4
└─ Configured via AZURE_OPENAI_DEPLOYMENT
```

---

## 🔧 Model Configuration Files

### Main Configuration
- `backend/utils/config.py` - Configuration loader
- `backend/.env` - Environment variables (create from `.env.example`)
- `.env.example` - Example configuration

### Service Files
- `backend/services/llm_service.py` - LLM and embedding service
- `backend/services/image_service.py` - Google Vision service
- `backend/app.py` - Service initialization

---

## 📝 Model Usage by Feature

| Feature | Model | Purpose |
|---------|-------|---------|
| **Chat Responses** | GPT-4 (Azure) | Generate answers to user questions |
| **Streaming Responses** | GPT-4 (Azure) | Progressive word-by-word responses |
| **Document Embeddings** | text-embedding-ada-002 or SentenceTransformers | Convert docs to vectors |
| **Query Embeddings** | text-embedding-ada-002 or SentenceTransformers | Convert questions to vectors |
| **Conversation Summaries** | GPT-4 (Azure) | Summarize long conversations |
| **Image Text Extraction** | Google Vision API | Extract text from images |
| **Semantic Search** | Pinecone + Embeddings | Find relevant documents |

---

## 💰 Cost Considerations

### Azure OpenAI Pricing (as of 2024)

**GPT-4**:
- Input: ~$0.03 per 1K tokens
- Output: ~$0.06 per 1K tokens

**text-embedding-ada-002**:
- ~$0.0001 per 1K tokens

**Cost Optimization Tips**:
1. Use streaming for better UX (same cost)
2. Enable conversation summarization to reduce context tokens
3. Use Sentence Transformers for embeddings (free, but lower quality)
4. Implement caching for repeated queries

---

## 🚀 Performance Characteristics

### Embedding Models Comparison

| Model | Dimension | Speed | Quality | Cost |
|-------|-----------|-------|---------|------|
| **text-embedding-ada-002** | 1536 | Fast | Excellent | $0.0001/1K tokens |
| **all-MiniLM-L6-v2** | 384 | Very Fast | Good | Free (local) |
| **all-mpnet-base-v2** | 768 | Medium | Excellent | Free (local) |

### Language Models

| Model | Response Time | Quality | Cost |
|-------|---------------|---------|------|
| **GPT-4** | 2-5s | Excellent | High |
| **GPT-4 Turbo** | 1-3s | Excellent | Medium |

---

## 🔄 Switching Models

### To Use Different Embedding Model

**Option 1: Azure OpenAI (Recommended for Production)**
```bash
# In backend/.env
AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT=your-deployment-name
```

**Option 2: Sentence Transformers (Free, Local)**
```bash
# In backend/.env
EMBEDDING_MODEL=sentence-transformers/all-mpnet-base-v2
```

**Note**: If you change embedding models, you must **re-index** all documents in Pinecone!

### To Use Different Chat Model

```bash
# In backend/.env
AZURE_OPENAI_DEPLOYMENT=your-gpt4-turbo-deployment
# or
AZURE_OPENAI_CHAT_DEPLOYMENT=your-gpt4-turbo-deployment
```

---

## 🧪 Testing Different Models

### Test Embeddings
```python
from backend.services.llm_service import LLMService

# Test Azure OpenAI
llm = LLMService(
    endpoint="https://your-resource.openai.azure.com/",
    api_key="your-key",
    deployment="your-deployment"
)
embedding = llm.get_embedding("test text")
print(f"Dimension: {len(embedding)}")

# Test Sentence Transformers
llm = LLMService(model_name="sentence-transformers/all-MiniLM-L6-v2")
embedding = llm.get_embedding("test text")
print(f"Dimension: {len(embedding)}")
```

### Test Chat
```bash
curl -X POST "http://localhost:8000/api/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is Choreo?"}'
```

---

## 📚 Documentation References

### Azure OpenAI
- [Azure OpenAI Documentation](https://learn.microsoft.com/en-us/azure/ai-services/openai/)
- [GPT-4 Model Overview](https://platform.openai.com/docs/models/gpt-4)
- [Embeddings Guide](https://platform.openai.com/docs/guides/embeddings)

### Sentence Transformers
- [Sentence Transformers Documentation](https://www.sbert.net/)
- [Model Hub](https://www.sbert.net/docs/pretrained_models.html)

### Google Cloud Vision
- [Vision API Documentation](https://cloud.google.com/vision/docs)

### Pinecone
- [Pinecone Documentation](https://docs.pinecone.io/)

---

## 🎯 Summary

**Primary Models in Use**:

1. **GPT-4** (Azure OpenAI) → Answering questions
2. **text-embedding-ada-002** (Azure OpenAI) → Document embeddings
3. **Sentence Transformers** (Fallback) → Local embeddings
4. **Google Vision API** (Optional) → Image text extraction

**Model Selection**:
- **Production**: Azure OpenAI (GPT-4 + text-embedding-ada-002)
- **Development**: Sentence Transformers (free, local)
- **Image Processing**: Google Vision API (optional)

**Configuration**: All model settings are in `backend/.env` file.

---

## 🆘 Troubleshooting

### Issue: "Azure OpenAI not initialized"
**Solution**: Check `backend/.env` has:
```bash
AZURE_OPENAI_API_KEY=xxx
AZURE_OPENAI_ENDPOINT=https://xxx.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=xxx
```

### Issue: "Dimension mismatch in Pinecone"
**Solution**: Embedding dimension must match Pinecone index:
- Azure OpenAI: 1536
- all-MiniLM-L6-v2: 384
- all-mpnet-base-v2: 768

Update `PINECONE_DIMENSION` in `.env` and recreate index if needed.

### Issue: "Model not found"
**Solution**: Check deployment name in Azure portal matches `.env` file.

---

For more information, see:
- `backend/services/llm_service.py` - Model implementation
- `backend/utils/config.py` - Configuration
- `README.md` - Project overview

