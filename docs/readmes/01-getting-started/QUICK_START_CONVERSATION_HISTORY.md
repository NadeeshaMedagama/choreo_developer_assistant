# Conversation History with Retrieval - Quick Start

## What Was Implemented

✅ **Conversation history tracking** - Stored locally in frontend (localStorage)  
✅ **Context-aware retrieval** - Queries enriched with conversation context  
✅ **LLM with dual context** - Receives both conversation history and knowledge base  
✅ **Streaming support** - Real-time responses with history  
✅ **Edit/Regenerate support** - Maintains history correctly  

## How It Works

```
User Question
    ↓
Frontend sends: question + conversation_history[]
    ↓
Backend enriches query with recent context (last 4 messages)
    ↓
Pinecone retrieval using enriched query (top 5 chunks)
    ↓
LLM receives:
  - System prompt
  - Retrieved knowledge chunks
  - Conversation history (last 10 messages)
  - Current question
    ↓
Contextual response streamed back
```

## Files Modified

### Backend
- `backend/app.py` - Added conversation_history parameter to endpoints
- `backend/services/llm_service.py` - Added methods to handle history

### Frontend
- `frontend/src/App.jsx` - Sends conversation history with all requests

### Documentation
- `docs/CONVERSATION_HISTORY_WITH_RETRIEVAL.md` - Full documentation
- `backend/tests/test_conversation_history.py` - Test suite

## Testing

### 1. Start Backend
```bash
cd backend
python -m app
```

### 2. Run Tests
```bash
cd backend
python tests/test_conversation_history.py
```

### 3. Test in Frontend
```bash
cd frontend
npm run dev
```

Then try:
1. Ask: "What is Choreo?"
2. Follow-up: "How do I deploy?"
3. Follow-up: "What languages are supported?"
4. Try editing a previous question
5. Try regenerating a response

## API Examples

### Basic Request
```bash
curl -X POST http://localhost:8000/api/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is Choreo?",
    "conversation_history": []
  }'
```

### With History
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

### Streaming
```bash
curl -X POST http://localhost:8000/api/ask/stream \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Tell me more",
    "conversation_history": [...]
  }'
```

## Key Configuration

### History Limits (Configurable)

**In backend/app.py:**
```python
# For retrieval enrichment
recent_history = conversation_history[-4:]  # Last 2 turns

# For LLM context (in llm_service.py)
recent_history = conversation_history[-10:]  # Last 5 turns
```

Adjust these based on:
- Your token limits
- Response quality
- Cost considerations

### Message Truncation

**In backend/app.py:**
```python
history_text = "\n".join(
    f"{msg['role']}: {msg['content'][:200]}"  # Limit to 200 chars
    for msg in recent_history
)
```

Increase/decrease 200 based on your needs.

## Troubleshooting

### Issue: Backend returns 422 error
**Cause:** Body parameter parsing issue  
**Fix:** Check that request has `Content-Type: application/json` header

### Issue: History not being used
**Cause:** Frontend not sending history  
**Fix:** Check browser console for network requests, verify body contains `conversation_history`

### Issue: Token limit exceeded
**Cause:** History + context too long  
**Fix:** Reduce history limits in `llm_service.py` (line ~240)

### Issue: Irrelevant retrieval results
**Cause:** Query enrichment adding noise  
**Fix:** Reduce enrichment history from 4 to 2 messages in `app.py`

## Performance Tips

1. **Limit history size** - Keep only recent N turns
2. **Truncate long messages** - Limit each message to 200-300 chars
3. **Monitor token usage** - Check logs for token counts
4. **Use streaming** - Better UX for long responses
5. **Cache common queries** - Optional enhancement

## What's Next?

### Optional Enhancements

1. **Conversation Summarization**
   - Summarize older history
   - Keep summary + recent messages
   
2. **User Profiles**
   - Store user preferences
   - Personalize responses
   
3. **Hybrid Search**
   - Combine semantic + keyword search
   - Better retrieval accuracy
   
4. **Automatic Context Management**
   - Smart token limit handling
   - Dynamic history truncation

5. **Conversation Analytics**
   - Track conversation patterns
   - Improve prompts based on data

## Support

For detailed information, see:
- Full documentation: `docs/CONVERSATION_HISTORY_WITH_RETRIEVAL.md`
- Test suite: `backend/tests/test_conversation_history.py`
- Architecture docs: `docs/architecture.md`

## Summary

Your implementation is **production-ready**! The system now:

✅ Maintains conversation context  
✅ Grounds responses in knowledge base  
✅ Handles multi-turn conversations  
✅ Works with streaming  
✅ Supports edit/regenerate  
✅ Stores history efficiently  

**Test it out and enjoy contextual, knowledge-grounded conversations!** 🎉

