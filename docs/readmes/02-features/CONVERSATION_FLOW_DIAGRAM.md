# Conversation History Flow Diagram

## Visual Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           USER INTERFACE (React)                         │
│  ┌────────────────────────────────────────────────────────────────┐    │
│  │  Conversation State (localStorage)                              │    │
│  │  ─────────────────────────────────────                          │    │
│  │  {                                                               │    │
│  │    id: "conv-123",                                               │    │
│  │    title: "What is Choreo?",                                     │    │
│  │    messages: [                                                   │    │
│  │      {role: "user", content: "What is Choreo?"},                │    │
│  │      {role: "assistant", content: "Choreo is..."},              │    │
│  │      {role: "user", content: "How do I deploy?"},               │    │
│  │      {role: "assistant", content: "To deploy..."}               │    │
│  │    ]                                                             │    │
│  │  }                                                               │    │
│  └────────────────────────────────────────────────────────────────┘    │
│                                                                           │
│  User Action: "What languages are supported?"                            │
│  ↓                                                                        │
│  1. Add user message to conversation.messages                            │
│  2. Build conversation_history array (filter out system msgs)            │
│  3. Send POST request                                                    │
└─────────────────────────┬───────────────────────────────────────────────┘
                          ↓
                 ┌────────────────────┐
                 │   HTTP REQUEST     │
                 │  POST /api/ask     │
                 │  ──────────────    │
                 │  {                 │
                 │    question: "...",│
                 │    conversation_   │
                 │    history: [...]  │
                 │  }                 │
                 └─────────┬──────────┘
                          ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                          BACKEND (FastAPI)                               │
│  app.py: /api/ask endpoint                                               │
│  ─────────────────────────────────────────────────                       │
│                                                                           │
│  STEP 1: Query Enrichment                                                │
│  ┌────────────────────────────────────────────────────────────┐         │
│  │  recent_history = conversation_history[-4:]  # Last 4 msgs │         │
│  │                                                             │         │
│  │  enriched_query = """                                       │         │
│  │    user: What is Choreo?                                    │         │
│  │    assistant: Choreo is a platform...                       │         │
│  │    user: How do I deploy?                                   │         │
│  │    assistant: To deploy in Choreo...                        │         │
│  │    Current question: What languages are supported?          │         │
│  │  """                                                         │         │
│  └────────────────────────────────────────────────────────────┘         │
│                          ↓                                                │
│                                                                           │
│  STEP 2: Semantic Search                                                 │
│  ┌────────────────────────────────────────────────────────────┐         │
│  │  context_manager.retrieve_by_text(enriched_query, top_k=5) │         │
│  └────────────────────────────┬───────────────────────────────┘         │
└────────────────────────────────┼─────────────────────────────────────────┘
                                 ↓
                    ┌─────────────────────────┐
                    │   PINECONE (Vector DB)  │
                    │  ───────────────────    │
                    │  1. Embed enriched query│
                    │  2. Find top 5 similar  │
                    │     chunks              │
                    │  3. Return:             │
                    │     - Chunk 1           │
                    │     - Chunk 2           │
                    │     - Chunk 3           │
                    │     - Chunk 4           │
                    │     - Chunk 5           │
                    └────────────┬────────────┘
                                 ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                          BACKEND (FastAPI)                               │
│  STEP 3: Build LLM Messages                                              │
│  ┌────────────────────────────────────────────────────────────┐         │
│  │  llm_service.get_response_with_history(                     │         │
│  │    question="What languages are supported?",                │         │
│  │    context="<5 chunks from Pinecone>",                      │         │
│  │    conversation_history=[...]                               │         │
│  │  )                                                           │         │
│  └────────────────────────────────────────────────────────────┘         │
│                          ↓                                                │
│  llm_service.py: Build messages array                                    │
│  ┌────────────────────────────────────────────────────────────┐         │
│  │  messages = [                                               │         │
│  │    {                                                         │         │
│  │      "role": "system",                                       │         │
│  │      "content": "You are DevChoreo..."                       │         │
│  │    },                                                        │         │
│  │    {                                                         │         │
│  │      "role": "system",                                       │         │
│  │      "content": "Retrieved Context:\n<Pinecone chunks>"      │         │
│  │    },                                                        │         │
│  │    {                                                         │         │
│  │      "role": "user",                                         │         │
│  │      "content": "What is Choreo?"                            │         │
│  │    },                                                        │         │
│  │    {                                                         │         │
│  │      "role": "assistant",                                    │         │
│  │      "content": "Choreo is a platform..."                    │         │
│  │    },                                                        │         │
│  │    {                                                         │         │
│  │      "role": "user",                                         │         │
│  │      "content": "How do I deploy?"                           │         │
│  │    },                                                        │         │
│  │    {                                                         │         │
│  │      "role": "assistant",                                    │         │
│  │      "content": "To deploy in Choreo..."                     │         │
│  │    },                                                        │         │
│  │    {                                                         │         │
│  │      "role": "user",                                         │         │
│  │      "content": "What languages are supported?"              │         │
│  │    }                                                         │         │
│  │  ]                                                           │         │
│  └────────────────────────────────────────────────────────────┘         │
└────────────────────────────────┬────────────────────────────────────────┘
                                 ↓
                   ┌──────────────────────────────┐
                   │   AZURE OPENAI / GPT-4       │
                   │  ──────────────────────────  │
                   │  Receives:                   │
                   │  • System prompt             │
                   │  • Knowledge base context    │
                   │  • Full conversation history │
                   │  • Current question          │
                   │                              │
                   │  Generates:                  │
                   │  "Choreo supports multiple   │
                   │   languages including Python,│
                   │   Java, Node.js, Go..."      │
                   └──────────────┬───────────────┘
                                 ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                          BACKEND (FastAPI)                               │
│  STEP 4: Stream Response                                                 │
│  ┌────────────────────────────────────────────────────────────┐         │
│  │  for chunk in response:                                     │         │
│  │    yield f"data: {json.dumps({'content': chunk})}\n\n"      │         │
│  │                                                             │         │
│  │  yield "data: [DONE]\n\n"                                   │         │
│  └────────────────────────────────────────────────────────────┘         │
└─────────────────────────┬───────────────────────────────────────────────┘
                          ↓
                 ┌────────────────────┐
                 │   HTTP RESPONSE    │
                 │  SSE Stream        │
                 │  ──────────────    │
                 │  data: {"content": │
                 │    "Choreo"}       │
                 │  data: {"content": │
                 │    " supports"}    │
                 │  data: {"content": │
                 │    " Python"}      │
                 │  ...               │
                 │  data: [DONE]      │
                 └─────────┬──────────┘
                          ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                           USER INTERFACE (React)                         │
│  STEP 5: Update UI                                                       │
│  ┌────────────────────────────────────────────────────────────┐         │
│  │  1. Receive streaming chunks                                │         │
│  │  2. Accumulate content: "Choreo supports Python..."         │         │
│  │  3. Update message in real-time                             │         │
│  │  4. On [DONE], add to conversation.messages                 │         │
│  │  5. Save to localStorage                                    │         │
│  └────────────────────────────────────────────────────────────┘         │
│                                                                           │
│  Updated Conversation State:                                             │
│  ┌────────────────────────────────────────────────────────────┐         │
│  │  messages: [                                                │         │
│  │    {role: "user", content: "What is Choreo?"},             │         │
│  │    {role: "assistant", content: "Choreo is..."},           │         │
│  │    {role: "user", content: "How do I deploy?"},            │         │
│  │    {role: "assistant", content: "To deploy..."},           │         │
│  │    {role: "user", content: "What languages...?"},          │         │
│  │    {role: "assistant", content: "Choreo supports..."} ← NEW│         │
│  │  ]                                                          │         │
│  └────────────────────────────────────────────────────────────┘         │
└─────────────────────────────────────────────────────────────────────────┘
```

## Key Points

### 1. Dual Context System
```
┌─────────────────────────────────────┐
│           LLM INPUT                 │
├─────────────────────────────────────┤
│ [System Prompt]                     │ ← Identity & rules
│ You are DevChoreo...                │
├─────────────────────────────────────┤
│ [Retrieved Knowledge]               │ ← Fresh from Pinecone
│ Context: <documentation chunks>     │   (using enriched query)
├─────────────────────────────────────┤
│ [Conversation History]              │ ← From frontend
│ user: previous question             │   (last 10 messages)
│ assistant: previous answer          │
│ ...                                 │
├─────────────────────────────────────┤
│ [Current Question]                  │ ← What user just asked
│ user: new question                  │
└─────────────────────────────────────┘
```

### 2. History Management
```
Frontend (localStorage)
└─ conversations: [
     {
       id: "conv-1",
       messages: [...]  ← Full history
     }
   ]
   
   ↓ Filter (no system msgs)
   
Backend receives
└─ conversation_history: [
     {role: "user", content: "..."},
     {role: "assistant", content: "..."}
   ]
   
   ↓ Split usage
   
For Retrieval: Last 4 messages
For LLM: Last 10 messages
```

### 3. Query Enrichment Example
```
Without Enrichment:
User: "What about Python?"
Pinecone Query: "What about Python?"
Result: ❌ Too vague, poor results

With Enrichment:
User: "What about Python?"
Context: "user: How to deploy? assistant: Use Docker..."
Pinecone Query: "user: How to deploy?\n...Current: What about Python?"
Result: ✅ Finds Python deployment docs
```

## Benefits

✅ **No Hallucination**: Always grounded in retrieved docs
✅ **Context Aware**: Understands follow-ups and references
✅ **Efficient**: History stored locally, not in database
✅ **Scalable**: No per-conversation database overhead
✅ **Fast**: Streaming responses with full context
✅ **Flexible**: Easy to tune history limits

