# Conversation History with Retrieval Implementation

## Overview

This implementation combines **conversation history** with **vector-based retrieval** to provide contextually aware responses. The LLM receives both the conversation context and relevant knowledge base chunks, enabling it to:

- Answer follow-up questions correctly
- Ground responses in your actual knowledge base
- Avoid hallucinating unrelated information

## Architecture

### High-Level Workflow

```
1. User asks a question
   ↓
2. Append question to local conversation history (frontend)
   ↓
3. Send question + conversation_history to backend
   ↓
4. Backend enriches query with recent conversation context
   ↓
5. Retrieve top-k relevant chunks from Pinecone using enriched query
   ↓
6. Send to LLM:
   - System prompt
   - Retrieved knowledge base context
   - Conversation history (last 10 messages)
   - Current question
   ↓
7. LLM generates contextual response
   ↓
8. Stream response back to frontend
   ↓
9. Append assistant response to conversation history
```

## Components

### 1. Frontend (React)

**File:** `/frontend/src/App.jsx`

**Key Features:**
- Stores conversation history locally in state (per conversation)
- Persists conversations to localStorage
- Sends conversation history with each request
- Handles streaming responses

**Conversation History Format:**
```javascript
conversation_history = [
  {"role": "user", "content": "What is Choreo?"},
  {"role": "assistant", "content": "Choreo is a platform for..."},
  {"role": "user", "content": "How do I deploy?"},
  // ... more messages
]
```

**Important Implementation Details:**
- Filters out system messages before sending to backend
- Excludes the initial greeting message
- Sends history for all three actions: new questions, regenerate, and edit

### 2. Backend API Endpoints

**File:** `/backend/app.py`

#### `/api/ask` (Non-streaming)
```python
@app.post("/api/ask")
def ask_ai(
    question: str,
    conversation_history: Optional[List[Dict[str, str]]] = Body(default=None)
):
    # 1. Enrich query with recent conversation context
    # 2. Retrieve relevant chunks from Pinecone
    # 3. Send to LLM with history + context
    # 4. Return response
```

#### `/api/ask/stream` (Streaming - Recommended)
```python
@app.post("/api/ask/stream")
async def ask_ai_stream(
    question: str,
    conversation_history: Optional[List[Dict[str, str]]] = Body(default=None)
):
    # Same as above but streams response using SSE
```

**Query Enrichment Strategy:**
- Takes last 4 messages from conversation history (2 user + 2 assistant)
- Limits each message to 200 characters to avoid noise
- Combines with current question for better retrieval

```python
# Example enriched query:
"""
user: What is Choreo?
assistant: Choreo is a platform for...
user: How do I deploy?
assistant: To deploy in Choreo...
Current question: Can I use Python?
"""
```

### 3. LLM Service

**File:** `/backend/services/llm_service.py`

#### New Methods

##### `get_response_with_history()`
```python
def get_response_with_history(
    question: str,
    context: str,
    conversation_history: Optional[List[dict]] = None,
    max_tokens: int = 4096
) -> str:
    # Builds messages with:
    # 1. System prompt
    # 2. Context from knowledge base
    # 3. Conversation history (last 10 messages)
    # 4. Current question
```

##### `get_response_stream_with_history()`
```python
def get_response_stream_with_history(
    question: str,
    context: str,
    conversation_history: Optional[List[dict]] = None,
    max_tokens: int = 4096
):
    # Same as above but yields chunks for streaming
```

**Message Structure Sent to LLM:**
```python
messages = [
    {
        "role": "system",
        "content": "You are DevChoreo, an AI assistant..."
    },
    {
        "role": "system",
        "content": "Retrieved Knowledge Base Context:\n<chunks from Pinecone>"
    },
    # Conversation history (last 10 messages)
    {"role": "user", "content": "What is Choreo?"},
    {"role": "assistant", "content": "Choreo is..."},
    # ... more history
    # Current question
    {"role": "user", "content": "Current question here"}
]
```

## Key Design Decisions

### 1. Local vs. Remote Storage

**✅ Conversation history is stored locally** (frontend state + localStorage)
- No need to persist in database
- Lightweight and fast
- Per-session/per-conversation
- Automatically cleared when conversation is deleted

**✅ Knowledge base is stored remotely** (Pinecone)
- Persistent across all sessions
- Shared across all users
- Indexed for semantic search

### 2. History Limits

To avoid token limits and improve performance:

**Frontend → Backend:** 
- Sends full conversation history (already filtered)

**Backend → LLM:**
- **Retrieval enrichment:** Last 4 messages (2 turns)
- **LLM context:** Last 10 messages (5 turns)

These limits prevent:
- Token limit errors
- Excessive costs
- Reduced response quality from too much noise

### 3. Query Enrichment

**Why enrich the query?**
Follow-up questions often lack context:
- "What about Python?" (What about Python for what?)
- "How much does it cost?" (What costs?)

**Solution:**
Combine recent conversation with the question before retrieving from Pinecone:
```python
enriched_query = f"""
user: How do I deploy in Choreo?
assistant: To deploy, you need to...
Current question: What about Python?
"""
# Now Pinecone can find relevant Python deployment docs
```

### 4. Context + History Separation

The LLM receives two types of context:

1. **Retrieved Knowledge** (from Pinecone)
   - Always fresh and relevant to the enriched query
   - Grounded in your actual documentation

2. **Conversation History** (from frontend)
   - Maintains continuity
   - Enables follow-up understanding

This separation ensures:
- Answers are always grounded in real knowledge
- The assistant remembers what was discussed
- Follow-ups work correctly

## Usage Examples

### Example 1: Basic Follow-up

```
User: "What is Choreo?"
→ Backend retrieves docs about Choreo from Pinecone
→ LLM: "Choreo is a platform for..."

User: "How do I get started?"
→ Backend enriches query with previous context
→ Retrieves "getting started" docs
→ LLM sees conversation history + new docs
→ LLM: "To get started with Choreo, you can..."
```

### Example 2: Multi-turn Conversation

```
User: "Tell me about Choreo's deployment options"
Assistant: "Choreo supports Docker, Kubernetes..."

User: "Which one is recommended?"
→ Query enriched with previous context about deployments
→ LLM sees full history + relevant docs
→ Assistant: "For production, Kubernetes is recommended because..."

User: "How do I configure it?"
→ Query enriched: knows "it" = Kubernetes
→ Retrieves Kubernetes config docs
→ Assistant: "To configure Kubernetes in Choreo..."
```

### Example 3: Edit Previous Question

When user edits a previous question:
1. Frontend removes all messages after the edited one
2. Sends conversation history up to (but not including) edited message
3. Backend retrieves fresh context
4. LLM generates new response with updated context

## Optional Enhancements

### 1. Conversation Summarization

For very long conversations:
```python
def summarize_old_history(messages):
    # Summarize messages older than N turns
    # Keep only summary + recent messages
    # Reduces token usage while maintaining context
```

### 2. Conversation Memory Database

For persistent cross-session memory:
```python
# Store important conversation facts
user_profile = {
    "preferences": ["Python", "Kubernetes"],
    "experience_level": "intermediate",
    "current_project": "microservices-api"
}
```

### 3. Hybrid Search

Combine semantic search with keyword search:
```python
# Get results from both
semantic_results = pinecone.query(embedding)
keyword_results = pinecone.query(text, sparse=True)
# Merge and re-rank
```

### 4. Context Window Management

Automatically manage token limits:
```python
def fit_to_token_limit(messages, context, max_tokens=4096):
    # Calculate token counts
    # Trim older messages if needed
    # Ensure current question + context always fit
```

## Testing the Implementation

### Test 1: Basic Conversation
```bash
curl -X POST http://localhost:8000/api/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is Choreo?",
    "conversation_history": []
  }'
```

### Test 2: Follow-up Question
```bash
curl -X POST http://localhost:8000/api/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How do I deploy?",
    "conversation_history": [
      {"role": "user", "content": "What is Choreo?"},
      {"role": "assistant", "content": "Choreo is a platform..."}
    ]
  }'
```

### Test 3: Streaming
```bash
curl -X POST http://localhost:8000/api/ask/stream \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Tell me more",
    "conversation_history": [...]
  }'
```

## Monitoring

The implementation includes comprehensive logging:

```python
# In backend/app.py
monitoring.log_info(
    f"AI request received",
    logger_type='ai',
    question_length=len(question),
    history_length=len(conversation_history) if conversation_history else 0
)
```

Monitor these metrics:
- Conversation history length
- Retrieval quality (context_count)
- Response time
- Token usage

## Best Practices

1. **Keep history concise**
   - Limit to recent turns
   - Summarize or truncate old messages

2. **Enrich queries smartly**
   - Don't send too much context for retrieval
   - Focus on last 2-3 turns

3. **Handle edge cases**
   - Empty history (first question)
   - Very long messages
   - Missing context

4. **Test thoroughly**
   - Multi-turn conversations
   - Edit/regenerate scenarios
   - Different conversation lengths

5. **Monitor performance**
   - Token usage
   - Response quality
   - Retrieval relevance

## Troubleshooting

### Issue: "Answers don't use conversation context"
**Solution:** Check that conversation_history is being sent correctly from frontend

### Issue: "Retrieval returns irrelevant results"
**Solution:** Query enrichment might be too noisy. Reduce to last 2 messages or 100 chars per message

### Issue: "Token limit exceeded"
**Solution:** Reduce conversation history limit (currently 10 messages) or truncate longer messages

### Issue: "Assistant forgets earlier context"
**Solution:** Increase history limit or implement conversation summarization

## Summary

Your approach is **100% correct**! This implementation:

✅ Keeps conversation history locally (efficient, no DB needed)  
✅ Enriches queries with context for better retrieval  
✅ Sends both history and knowledge base to LLM  
✅ Maintains context across multiple turns  
✅ Avoids hallucination by grounding in real docs  
✅ Works with streaming for better UX  
✅ Handles edge cases (edit, regenerate, empty history)  

The system now provides contextually aware, knowledge-grounded responses! 🎉

