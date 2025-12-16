# Quick Start: Conversation Memory with Summarization

## 🚀 5-Minute Integration Guide

### Backend (✅ Already Done)
The backend is fully integrated and ready to use. No changes needed!

### Frontend Integration

#### 1. Update TypeScript Types

Add to your types file (e.g., `src/types.ts`):

```typescript
export interface ConversationSummary {
  content: string;
  timestamp: string;
  messages_summarized: number;
  topics_covered: string[];
  key_questions: string[];
  important_decisions: string[];
  token_count: number;
}

export interface MemoryStats {
  total_messages: number;
  total_tokens: number;
  kept_recent: number;
  summarized_count: number;
  summary_created: boolean;
  summary_updated: boolean;
}

export interface AskRequest {
  question: string;
  conversation_history?: Message[];
  summary?: ConversationSummary;
  max_history_tokens?: number;
  enable_summarization?: boolean;
}

export interface AskResponse {
  answer: string;
  sources: Source[];
  context_count: number;
  memory_stats?: MemoryStats;
  summary?: ConversationSummary;
  summary_metadata?: {
    topics_covered: string[];
    key_questions: string[];
    important_decisions: string[];
  };
}
```

#### 2. Update Chat Component State

```typescript
const [messages, setMessages] = useState<Message[]>([]);
const [conversationSummary, setConversationSummary] = useState<ConversationSummary | null>(null);
const [memoryStats, setMemoryStats] = useState<MemoryStats | null>(null);
```

#### 3. Update API Call

**Non-Streaming:**
```typescript
const sendMessage = async (question: string) => {
  const response = await fetch('/api/ask', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      question,
      conversation_history: messages,
      summary: conversationSummary,
      max_history_tokens: 4000,
      enable_summarization: true
    } as AskRequest)
  });
  
  const data: AskResponse = await response.json();
  
  // Update summary for next request
  if (data.summary) {
    setConversationSummary(data.summary);
  }
  
  // Update memory stats (optional)
  if (data.memory_stats) {
    setMemoryStats(data.memory_stats);
  }
  
  // Update messages
  setMessages([
    ...messages,
    { role: 'user', content: question },
    { role: 'assistant', content: data.answer }
  ]);
  
  return data;
};
```

**Streaming:**
```typescript
const sendMessageStream = async (question: string) => {
  const response = await fetch('/api/ask/stream', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      question,
      conversation_history: messages,
      summary: conversationSummary,
      max_history_tokens: 4000,
      enable_summarization: true
    } as AskRequest)
  });
  
  const reader = response.body?.getReader();
  const decoder = new TextDecoder();
  let fullAnswer = '';
  
  while (true) {
    const { done, value } = await reader!.read();
    if (done) break;
    
    const chunk = decoder.decode(value);
    const lines = chunk.split('\n');
    
    for (const line of lines) {
      if (line.startsWith('data: ')) {
        const data = line.slice(6);
        
        if (data === '[DONE]') break;
        
        try {
          const parsed = JSON.parse(data);
          
          if (parsed.content) {
            fullAnswer += parsed.content;
            // Update UI with streaming content
            setMessages(prev => {
              const updated = [...prev];
              if (updated[updated.length - 1]?.role === 'assistant') {
                updated[updated.length - 1].content = fullAnswer;
              } else {
                updated.push({ role: 'assistant', content: fullAnswer });
              }
              return updated;
            });
          }
          
          // Handle summary and memory stats
          if (parsed.summary) {
            setConversationSummary(parsed.summary);
          }
          if (parsed.memory_stats) {
            setMemoryStats(parsed.memory_stats);
          }
        } catch (e) {
          // Ignore parse errors
        }
      }
    }
  }
};
```

#### 4. Clear Conversation (Optional)

```typescript
const startNewConversation = () => {
  setMessages([]);
  setConversationSummary(null);
  setMemoryStats(null);
};
```

#### 5. Display Memory Stats (Optional)

```typescript
const MemoryIndicator = () => {
  if (!memoryStats) return null;
  
  return (
    <div className="memory-stats">
      <span>💬 {memoryStats.total_messages} messages</span>
      <span>🔤 {memoryStats.total_tokens} tokens</span>
      {memoryStats.summary_created && (
        <span className="summary-badge">📝 Summarized</span>
      )}
    </div>
  );
};
```

#### 6. Show Conversation Topics (Optional)

```typescript
const ConversationTopics = ({ summary }: { summary: ConversationSummary }) => {
  return (
    <div className="conversation-topics">
      <h4>Discussion Topics:</h4>
      <ul>
        {summary.topics_covered.map((topic, i) => (
          <li key={i}>{topic}</li>
        ))}
      </ul>
    </div>
  );
};
```

## 📋 Complete Example

```typescript
import React, { useState } from 'react';

export const ChatComponent = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [conversationSummary, setConversationSummary] = useState<ConversationSummary | null>(null);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSend = async () => {
    if (!input.trim()) return;
    
    setIsLoading(true);
    
    try {
      const response = await fetch('/api/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question: input,
          conversation_history: messages,
          summary: conversationSummary,
          enable_summarization: true
        })
      });
      
      const data = await response.json();
      
      // Update summary
      if (data.summary) {
        setConversationSummary(data.summary);
      }
      
      // Update messages
      setMessages([
        ...messages,
        { role: 'user', content: input },
        { role: 'assistant', content: data.answer }
      ]);
      
      setInput('');
    } catch (error) {
      console.error('Failed to send message:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="chat-container">
      <div className="messages">
        {messages.map((msg, i) => (
          <div key={i} className={`message ${msg.role}`}>
            {msg.content}
          </div>
        ))}
      </div>
      
      <div className="input-area">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSend()}
          placeholder="Ask about Choreo..."
        />
        <button onClick={handleSend} disabled={isLoading}>
          Send
        </button>
      </div>
      
      {conversationSummary && (
        <div className="summary-info">
          Topics: {conversationSummary.topics_covered.join(', ')}
        </div>
      )}
    </div>
  );
};
```

## ✅ Checklist

- [ ] Add TypeScript types for summary and memory stats
- [ ] Update state to include `conversationSummary`
- [ ] Modify API calls to send summary
- [ ] Handle summary in response
- [ ] (Optional) Display memory stats
- [ ] (Optional) Show conversation topics
- [ ] (Optional) Add "New Conversation" button

## 🎯 Testing

1. **Test Basic Chat**: Send a few messages, verify responses work
2. **Test Long Conversation**: Send 10+ messages, check if summary appears
3. **Test Follow-up**: Ask follow-up questions, verify context is maintained
4. **Check Console**: Look for `memory_stats` and `summary` in responses

## 🐛 Troubleshooting

**Summary not appearing?**
- Check if `enable_summarization: true` is sent
- Verify conversation has enough messages (>10 typically)
- Check backend logs for summarization trigger

**Context not maintained?**
- Ensure summary is sent back in subsequent requests
- Check that `conversation_history` includes all messages
- Verify frontend state is updated correctly

**Performance issues?**
- Reduce `max_history_tokens` if responses are slow
- Check if summarization is happening too frequently
- Monitor `memory_stats.total_tokens` to track usage

## 🎨 UI/UX Ideas

1. **Indicator Badge**: Show "💭 Summarized" when summary is active
2. **Topic Pills**: Display `topics_covered` as clickable tags
3. **Memory Gauge**: Visual bar showing token usage
4. **Conversation Export**: Allow downloading full history + summary
5. **Smart Suggestions**: Use `key_questions` to suggest follow-ups

## 📊 Monitoring

Log these metrics:
```typescript
console.log('Memory Stats:', {
  messages: data.memory_stats?.total_messages,
  tokens: data.memory_stats?.total_tokens,
  summarized: data.memory_stats?.summarized_count,
  topics: data.summary_metadata?.topics_covered
});
```

## 🚀 You're Done!

The conversation memory system is now integrated. Users will experience:
- ✅ Better context retention
- ✅ More accurate answers
- ✅ Longer conversation support
- ✅ Automatic summarization
- ✅ Topic tracking

Happy coding! 🎉

