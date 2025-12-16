# AI Models Documentation

This folder contains documentation about the AI models used in the Choreo AI Assistant.

## 📚 Contents

- **[MODELS_DOCUMENTATION.md](./MODELS_DOCUMENTATION.md)** - Comprehensive guide to all AI models used in this project

## 🤖 AI Models Used

### Primary Models

1. **Azure OpenAI GPT-4** - Language generation for chat responses
2. **Azure OpenAI text-embedding-ada-002** - Vector embeddings (1536 dimensions)
3. **Sentence Transformers** - Fallback embeddings (384 dimensions)
4. **Google Cloud Vision API** - Image text extraction (optional)

## 📖 What's Inside

The documentation covers:

- ✅ Detailed model specifications
- ✅ Configuration examples
- ✅ Performance comparisons
- ✅ Cost optimization tips
- ✅ Troubleshooting guide
- ✅ Model switching instructions
- ✅ Usage examples

## 🔧 Quick Configuration

```bash
# Azure OpenAI (Primary)
AZURE_OPENAI_API_KEY=your_api_key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=gpt-4
AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT=text-embedding-ada-002

# Fallback Embeddings
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Optional Image Processing
GOOGLE_VISION_API_KEY=your_google_api_key
```

## 🚀 Quick Start

Read **[MODELS_DOCUMENTATION.md](./MODELS_DOCUMENTATION.md)** for complete information about:
- Which models are used and why
- How to configure them
- How to switch between models
- Cost considerations
- Performance characteristics

## 💡 Need Help?

The documentation includes:
- Step-by-step setup guides
- Troubleshooting common issues
- Model comparison tables
- Best practices and recommendations

