# Document Sources Feature

## Overview

The AI assistant now displays source documents with each response, similar to ChatGPT and Gemini. Users can see which documents were used to generate the answer, along with metadata and links.

## Features Implemented

### Backend (Python/FastAPI)

**File: `backend/app.py`**

#### 1. Sources Extraction
- Extracts metadata from vector search results
- Includes: `file_path`, `repository`, `url`, `source_type`, `title`
- Provides content preview (first 200 characters)
- Returns relevance score (0.0 to 1.0)

#### 2. API Endpoints

**`POST /api/ask`** - Regular endpoint
```json
{
  "answer": "The answer text...",
  "sources": [
    {
      "title": "Document Title",
      "file_path": "path/to/file.md",
      "repository": "owner/repo",
      "url": "https://github.com/...",
      "source_type": "markdown",
      "content": "Preview of content...",
      "score": 0.89
    }
  ],
  "context_count": 5
}
```

**`POST /api/ask/stream`** - Streaming endpoint
- Streams content chunks as before
- Sends sources as SSE event before `[DONE]`
```
data: {"content": "chunk..."}
data: {"sources": [...]}
data: [DONE]
```

### Frontend (React)

**File: `frontend/src/components/Message.jsx`**

#### Sources Display Component
- Collapsible section showing all sources
- Displays for each source:
  - Document title or file path
  - Repository name
  - Source type (markdown, code, issue, etc.)
  - Content preview
  - Clickable URL (opens in new tab)
  - Relevance score as percentage

#### Features:
- ✅ Dark/light mode support
- ✅ Expandable/collapsible with icon toggle
- ✅ Clean card-based layout
- ✅ External link icons
- ✅ Shows source count

**File: `frontend/src/App.jsx`**

#### Updated Handlers
1. `sendQuestion()` - Captures sources from streaming/fallback
2. `handleRegenerate()` - Handles sources for regenerated responses
3. Both streaming and fallback API calls now store sources

## Usage

### For Users

When you ask a question, the AI will respond with an answer followed by a "Sources" section showing:

```
Sources (3) ▼

📄 Getting Started Guide
   Repository: wso2/docs-choreo-dev
   Type: markdown
   "This comprehensive guide will walk you through..."
   View source ↗
   Relevance: 92.5%

📄 API Documentation
   Repository: wso2/choreo-api
   ...
```

### For Developers

#### Adding Metadata to Documents

When ingesting documents, include metadata:

```python
metadata = {
    "file_path": "docs/guide.md",
    "repository": "owner/repo",
    "url": "https://github.com/owner/repo/blob/main/docs/guide.md",
    "source_type": "markdown",
    "title": "Getting Started Guide"
}

vector_client.insert_embedding(content, vector, metadata=metadata)
```

#### Metadata Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `file_path` | string | No | Path to file in repository |
| `repository` | string | No | Repository identifier (owner/repo) |
| `url` | string | No | Direct link to source |
| `source_type` | string | No | Type: markdown, code, issue, etc. |
| `title` | string | No | Human-readable title |
| `content` | string | Yes | Document content (stored separately) |

## Benefits

1. **Transparency** - Users see where information comes from
2. **Verification** - Can check original sources
3. **Trust** - Increases confidence in AI responses
4. **Debugging** - Developers can see which documents are being retrieved
5. **UX** - Familiar pattern from ChatGPT/Gemini

## Examples

### Example 1: Documentation Query

**User**: "How do I deploy a service in Choreo?"

**Response**: 
- Answer with deployment steps
- Sources showing:
  - Deployment guide from docs
  - API reference for deploy endpoint
  - Example from GitHub repository

### Example 2: Troubleshooting

**User**: "Why is my webhook failing?"

**Response**:
- Troubleshooting steps
- Sources showing:
  - Troubleshooting guide
  - Related GitHub issues
  - Webhook configuration docs

## Customization

### Changing Number of Sources

In `backend/app.py`, modify `top_k` parameter:
```python
similar_rows = context_manager.retrieve_by_text(enriched_query, top_k=5)
```

### Hiding Sources by Default

In `frontend/src/components/Message.jsx`, change initial state:
```javascript
const [showSources, setShowSources] = useState(false)  // collapsed by default
```

### Styling Sources

Modify the sources section in `Message.jsx` - all classes use Tailwind CSS and respect the dark/light theme.

## Troubleshooting

### Sources Not Showing

1. Check if backend is returning sources:
   ```bash
   curl -X POST http://localhost:8000/api/ask \
     -H "Content-Type: application/json" \
     -d '{"question": "test"}'
   ```

2. Verify metadata exists in Pinecone documents

3. Check browser console for errors

### Metadata Missing

- Ensure documents were ingested with metadata
- Re-ingest documents if metadata structure changed
- Check `vector_client.insert_embedding()` calls include metadata parameter

## Future Enhancements

- [ ] Source citation numbers in answer text
- [ ] Filter sources by type
- [ ] Source snippet highlighting
- [ ] Copy individual sources
- [ ] Share with sources included
- [ ] Analytics on source usage

