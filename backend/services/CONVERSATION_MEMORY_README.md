# Conversation Memory Management with Smart Summarization

## Overview

This feature implements an intelligent conversation memory system that maintains context across long conversations while staying within token limits. It uses LLM-powered summarization to compress older messages while keeping recent interactions detailed.

## Key Features

### 1. **Token-Based Tracking**
- Automatically estimates token count for all messages
- Tracks total conversation history size
- Monitors token usage in real-time

### 2. **Smart Summarization**
- Automatically summarizes older conversations when limits are exceeded
- Preserves key facts, decisions, and important context
- Creates hierarchical summaries for very long conversations
- Uses LLM to extract metadata (topics, questions, decisions)

### 3. **Sliding Window Memory**
- Keeps recent messages (last 6 by default) fully detailed
- Ensures precision for follow-up questions
- Maintains conversation flow

### 4. **Context-Aware Retrieval**
- Enriches queries with conversation summary and recent history
- Improves database search relevance
- Better retrieval of relevant knowledge base chunks

### 5. **Metadata Tagging**
- Tracks topics covered in conversation
- Remembers key questions asked
- Records important decisions made
- Enables semantic search through conversation history

## Architecture

```
User Query
    ↓
[1] Conversation Memory Manager
    ├── Check token limits
    ├── Manage sliding window
    └── Create/update summary if needed
    ↓
[2] Query Enrichment
    ├── Add conversation summary
    └── Add recent messages
    ↓
[3] Vector DB Retrieval
    ├── Search with enriched query
    └── Get relevant chunks
    ↓
[4] LLM Message Building
    ├── System prompt
    ├── Conversation summary
    ├── Knowledge base context
    ├── Recent messages
    └── Current question
    ↓
[5] LLM Response
    └── Answer with full context
```

## Configuration

### Default Settings

```python
ConversationMemoryManager(
    llm_service=llm_service,
    max_total_tokens=8000,        # Total tokens for entire request
    max_history_tokens=4000,       # Maximum for conversation history
    recent_window_size=6,          # Keep last 6 messages detailed
    summarization_trigger_ratio=0.75  # Trigger at 75% of limit
)
```

### Customizable Parameters

| Parameter | Description | Default | Recommended Range |
|-----------|-------------|---------|-------------------|
| `max_total_tokens` | Total tokens sent to LLM | 8000 | 4000-16000 |
| `max_history_tokens` | Tokens for conversation | 4000 | 2000-8000 |
| `recent_window_size` | Recent messages kept | 6 | 4-10 |
| `summarization_trigger_ratio` | When to summarize | 0.75 | 0.6-0.9 |

## API Usage

### Request Format

```json
{
  "question": "How do I deploy a service?",
  "conversation_history": [
    {"role": "user", "content": "What is Choreo?"},
    {"role": "assistant", "content": "Choreo is..."}
  ],
  "summary": {
    "content": "Previous discussion about...",
    "topics_covered": ["deployments", "services"],
    "key_questions": ["What is Choreo?"],
    "important_decisions": []
  },
  "max_history_tokens": 4000,
  "enable_summarization": true
}
```

### Response Format

```json
{
  "answer": "To deploy a service in Choreo...",
  "sources": [...],
  "context_count": 10,
  "memory_stats": {
    "total_messages": 8,
    "total_tokens": 3200,
    "kept_recent": 6,
    "summarized_count": 2,
    "summary_created": true,
    "summary_updated": false
  },
  "summary": {
    "content": "Comprehensive summary...",
    "timestamp": "2024-12-01T10:30:00Z",
    "messages_summarized": 2,
    "topics_covered": ["deployments", "services", "CI/CD"],
    "key_questions": ["What is Choreo?", "How to create a project?"],
    "important_decisions": ["Use GitHub integration"],
    "token_count": 150
  },
  "summary_metadata": {
    "topics_covered": ["deployments", "services", "CI/CD"],
    "key_questions": ["What is Choreo?", "How to create a project?"],
    "important_decisions": ["Use GitHub integration"]
  }
}
```

## How It Works

### Step 1: Normal Interaction (Below Token Limit)

When conversation history is small:
- All messages sent to LLM
- No summarization needed
- Full context preserved

### Step 2: Approaching Token Limit

When history reaches 75% of limit (default):
- System identifies older messages
- Creates summary using LLM
- Replaces older messages with summary
- Keeps recent messages intact

### Step 3: Long Conversations

For very long conversations:
- Multiple rounds of summarization
- Hierarchical summary creation
- Preserves critical information
- Maintains conversation context

### Step 4: Query Enrichment

Before database retrieval:
- Combines summary + recent messages + current question
- Creates enriched query
- Improves search relevance

### Step 5: LLM Request

Final message structure:
```
[System Prompt]
[Conversation Summary with Metadata]
[Knowledge Base Context]
[Recent Message 1]
[Recent Message 2]
...
[Recent Message N]
[Current User Question]
```

## Summarization Process

### 1. **Extract Metadata**

```python
{
  "topics_covered": ["API deployment", "authentication", "monitoring"],
  "key_questions": [
    "How do I secure my API?",
    "What monitoring tools are available?"
  ],
  "important_decisions": [
    "Use OAuth 2.0 for authentication",
    "Enable Prometheus metrics"
  ]
}
```

### 2. **Create Summary**

LLM generates concise summary:
```
User is deploying a REST API in Choreo. They've set up GitHub 
integration and configured OAuth 2.0 authentication. Currently 
exploring monitoring options, particularly Prometheus integration 
for metrics collection.
```

### 3. **Update Summary**

When new messages need summarization:
- Combines old summary + new messages
- Creates comprehensive updated summary
- Preserves chronological flow
- Maintains all key information

## Benefits

### ✅ **Better Context Retention**
- Maintains full conversation context
- Remembers decisions from earlier in conversation
- Understands references to previous questions

### ✅ **Improved Answer Accuracy**
- Better query enrichment for database search
- More relevant context retrieval
- LLM has full conversation awareness

### ✅ **Token Efficiency**
- Stays within model limits
- Reduces API costs
- Enables longer conversations

### ✅ **Enhanced User Experience**
- Natural conversation flow
- Follow-up questions work seamlessly
- Context awareness across many turns

### ✅ **Metadata Insights**
- Track conversation topics
- Identify recurring questions
- Monitor decision points

## Example Conversation Flow

### Turn 1-2 (No Summarization)
```
User: What is Choreo?
Bot: Choreo is an internal developer platform...
[All messages kept]
```

### Turn 3-6 (Still Below Limit)
```
User: How do I create a project?
Bot: To create a project in Choreo...
[All messages kept]
```

### Turn 7 (Summarization Triggered)
```
User: Can I deploy a Python service?
Bot: Yes, Choreo supports Python...

[System creates summary of turns 1-4]
Summary: "User learned about Choreo platform and created 
their first project with GitHub integration."

[Keeps turns 5-7 detailed]
```

### Turn 8-10 (Using Summary)
```
User: What about monitoring?
Bot: [Has summary + recent turns 5-7 + current question]
     "Based on your Python service deployment..."
```

## Frontend Integration

### React/TypeScript Example

```typescript
const [conversationHistory, setConversationHistory] = useState<Message[]>([]);
const [conversationSummary, setConversationSummary] = useState<Summary | null>(null);

const sendMessage = async (message: string) => {
  const response = await fetch('/api/ask', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      question: message,
      conversation_history: conversationHistory,
      summary: conversationSummary,
      max_history_tokens: 4000,
      enable_summarization: true
    })
  });
  
  const data = await response.json();
  
  // Update summary for next request
  if (data.summary) {
    setConversationSummary(data.summary);
  }
  
  // Add to conversation history
  setConversationHistory([
    ...conversationHistory,
    { role: 'user', content: message },
    { role: 'assistant', content: data.answer }
  ]);
  
  // Show memory stats (optional)
  if (data.memory_stats) {
    console.log('Memory Stats:', data.memory_stats);
  }
};
```

## Performance Considerations

### Token Estimation
- Current implementation: ~4 chars per token (rough estimate)
- For production: Consider using `tiktoken` library for accurate counting

### Summary Generation
- LLM call required for summarization
- Adds ~1-2 seconds when triggered
- Happens automatically in background
- Only when needed (not every request)

### Memory Overhead
- Summary stored in response
- Frontend sends back in next request
- Minimal overhead (~200-500 tokens)

## Best Practices

### 1. **Configure Limits Based on Model**
- GPT-3.5: 4000-8000 tokens
- GPT-4: 8000-16000 tokens
- Adjust based on your needs

### 2. **Monitor Memory Stats**
- Track summarization frequency
- Adjust triggers if too frequent
- Balance precision vs. efficiency

### 3. **Frontend State Management**
- Always send latest summary
- Store conversation history locally
- Clear on new conversation

### 4. **Handle Long Sessions**
- Consider session timeout
- Option to reset conversation
- Export conversation history

### 5. **Optimize for Your Use Case**
- Increase window size for technical support
- Decrease for general queries
- Adjust based on user feedback

## Troubleshooting

### Issue: Summary Not Creating
**Check:**
- `enable_summarization` is `true`
- Conversation history has messages
- Token limit is being reached

### Issue: Context Lost
**Check:**
- Summary is being sent back from frontend
- Recent window size is adequate
- Metadata extraction working

### Issue: Performance Slow
**Check:**
- Summarization frequency
- Token limits not too aggressive
- LLM response time

## Future Enhancements

- [ ] Use `tiktoken` for accurate token counting
- [ ] Persistent conversation storage (database)
- [ ] User preference for summarization style
- [ ] A/B testing different window sizes
- [ ] Conversation export/import
- [ ] Semantic search through conversation history
- [ ] Multi-language summary support
- [ ] Custom summarization prompts per use case

## Related Files

- `backend/services/conversation_memory_manager.py` - Core implementation
- `backend/app.py` - API integration
- `backend/services/llm_service.py` - LLM service

## References

- [OpenAI Token Counting](https://github.com/openai/tiktoken)
- [Conversation Memory Best Practices](https://platform.openai.com/docs/guides/chat)
- [RAG with Conversation History](https://python.langchain.com/docs/use_cases/question_answering/chat_history)

