import React, { useState, useRef, useEffect } from 'react'
import { Send, Plus, MessageSquare, Trash2, Edit2, Check, X, Menu, Moon, Sun, ArrowDown, Search } from 'lucide-react'
import Message from './components/Message'
import MonitoringButton from './components/MonitoringButton.jsx'

const INITIAL_ASSISTANT = {
  id: 1,
  role: 'assistant',
  content: "Hi, I'm DevChoreo. Ask me anything about your project!",
}

const STORAGE_KEY = 'devchoreo_conversations'
const THEME_STORAGE_KEY = 'devchoreo_theme'

function newConversationTemplate() {
  const now = Date.now()
  return {
    id: String(now),
    title: 'New Chat',
    createdAt: now,
    messages: [ { ...INITIAL_ASSISTANT, id: now } ],
    summary: null, // Conversation summary for memory management
    memoryStats: null, // Memory statistics
  }
}

// Load conversations from localStorage
function loadConversations() {
  try {
    const stored = localStorage.getItem(STORAGE_KEY)
    if (stored) {
      const parsed = JSON.parse(stored)
      if (Array.isArray(parsed) && parsed.length > 0) {
        return parsed
      }
    }
  } catch (e) {
    console.error('Failed to load conversations from localStorage:', e)
  }
  return [newConversationTemplate()]
}

// Save conversations to localStorage
function saveConversations(conversations) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(conversations))
  } catch (e) {
    console.error('Failed to save conversations to localStorage:', e)
  }
}

// Load theme from localStorage
function loadTheme() {
  try {
    const stored = localStorage.getItem(THEME_STORAGE_KEY)
    return stored === 'dark' ? 'dark' : 'light'
  } catch (e) {
    return 'light'
  }
}

// Save theme to localStorage
function saveTheme(theme) {
  try {
    localStorage.setItem(THEME_STORAGE_KEY, theme)
  } catch (e) {
    console.error('Failed to save theme to localStorage:', e)
  }
}

export default function App() {
  const [status, setStatus] = useState('checking')
  const [conversations, setConversations] = useState(loadConversations)
  const [currentId, setCurrentId] = useState(() => {
    const loaded = loadConversations()
    return loaded[0]?.id || String(Date.now())
  })
  const [inputValue, setInputValue] = useState('')
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [editingId, setEditingId] = useState(null)
  const [editTitle, setEditTitle] = useState('')
  const [theme, setTheme] = useState(loadTheme)
  const [showScrollButton, setShowScrollButton] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [isSearching, setIsSearching] = useState(false)
  const listRef = useRef(null)
  const inputRef = useRef(null)

  const current = conversations.find(c => c.id === currentId) || conversations[0]
  const isDark = theme === 'dark'

  // Filter conversations based on search query
  const filteredConversations = React.useMemo(() => {
    if (!searchQuery.trim()) return conversations

    const query = searchQuery.toLowerCase()
    return conversations.filter(c => {
      // Search in title
      if (c.title?.toLowerCase().includes(query)) return true

      // Search in message content
      return c.messages?.some(m =>
        m.content?.toLowerCase().includes(query)
      )
    })
  }, [conversations, searchQuery])

  const toggleSearch = () => {
    setIsSearching(!isSearching)
    if (isSearching) {
      setSearchQuery('') // Clear search when closing
    }
  }

  useEffect(() => {
    const check = async () => {
      try {
        const res = await fetch('/api/health')
        await res.json().catch(() => ({}))
        setStatus(res.ok ? 'online' : 'offline')
      } catch {
        setStatus('offline')
      }
    }
    check()
  }, [])

  // Save conversations to localStorage whenever they change
  useEffect(() => {
    saveConversations(conversations)
  }, [conversations])

  // Save theme to localStorage whenever it changes
  useEffect(() => {
    saveTheme(theme)
  }, [theme])

  useEffect(() => {
    listRef.current?.scrollTo({ top: listRef.current.scrollHeight, behavior: 'smooth' })
  }, [current?.messages?.length])

  // Handle scroll detection to show/hide scroll-to-bottom button
  useEffect(() => {
    const handleScroll = () => {
      if (!listRef.current) return

      const { scrollTop, scrollHeight, clientHeight } = listRef.current
      const isNearBottom = scrollHeight - scrollTop - clientHeight < 100

      setShowScrollButton(!isNearBottom)
    }

    const listElement = listRef.current
    if (listElement) {
      listElement.addEventListener('scroll', handleScroll)
      return () => listElement.removeEventListener('scroll', handleScroll)
    }
  }, [])

  const scrollToBottom = () => {
    if (listRef.current) {
      listRef.current.scrollTo({
        top: listRef.current.scrollHeight,
        behavior: 'smooth'
      })
    }
  }

  // Auto-resize textarea when inputValue changes
  useEffect(() => {
    const textarea = inputRef.current
    if (!textarea) return

    textarea.style.height = 'auto'
    textarea.style.height = `${Math.min(textarea.scrollHeight, 200)}px` // 200px = max-h-60
  }, [inputValue])

  const updateConversation = (updater) => {
    setConversations(prev => prev.map(c => c.id === current.id ? updater(c) : c))
  }

  const createNewChat = () => {
    const c = newConversationTemplate()
    setConversations(prev => [c, ...prev])
    setCurrentId(c.id)
  }

  const switchChat = (id) => {
    if (id === currentId) return
    setCurrentId(id)
  }

  const deleteChat = (id) => {
    setConversations(prev => prev.filter(c => c.id !== id))
    if (id === currentId) {
      setTimeout(() => {
        const next = conversations.find(c => c.id !== id)
        if (next) setCurrentId(next.id)
        else {
          const c = newConversationTemplate()
          setConversations([c])
          setCurrentId(c.id)
        }
      }, 0)
    }
  }

  const startEdit = (id, title) => {
    setEditingId(id)
    setEditTitle(title)
  }

  const saveEdit = () => {
    if (editTitle.trim()) {
      setConversations(prev => prev.map(c => c.id === editingId ? { ...c, title: editTitle.trim() } : c))
    }
    setEditingId(null)
    setEditTitle('')
  }

  const cancelEdit = () => {
    setEditingId(null)
    setEditTitle('')
  }

  const toggleTheme = () => {
    setTheme(prev => prev === 'light' ? 'dark' : 'light')
  }

  const sendQuestion = async () => {
    const trimmed = inputValue.trim()
    if (!trimmed) return

    setInputValue('')
    const now = Date.now()
    const userMsg = { id: now, role: 'user', content: trimmed }

    updateConversation(c => {
      const isFirstUser = !c.messages?.some(m => m.role === 'user')
      const title = isFirstUser ? trimmed.slice(0, 48) : c.title
      return { ...c, title, messages: [...(c.messages||[]), userMsg] }
    })

    // Add placeholder for streaming assistant message
    const assistantMsgId = now + 1
    const assistantMsg = { id: assistantMsgId, role: 'assistant', content: '', streaming: true }

    updateConversation(c => ({
      ...c,
      messages: [...(c.messages||[]), assistantMsg]
    }))

    // Prepare conversation history (exclude the initial assistant greeting and the placeholder)
    const conversationHistory = current?.messages
      ?.filter(m => m.id !== assistantMsgId && m.role !== 'system')
      .map(m => ({ role: m.role, content: m.content })) || []

    try {
      // Use streaming endpoint with conversation history and summary
      const response = await fetch('/api/ask/stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question: trimmed,
          conversation_history: conversationHistory,
          summary: current?.summary || null,
          max_history_tokens: 4000,
          enable_summarization: true
        })
      })

      if (!response.ok) {
        throw new Error('Network response was not ok')
      }

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let accumulatedContent = ''
      let sources = []
      let summary = null
      let memoryStats = null

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const chunk = decoder.decode(value, { stream: true })
        const lines = chunk.split('\n')

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6)
            if (data === '[DONE]') {
              // Mark streaming as complete and add sources, update summary
              updateConversation(c => ({
                ...c,
                messages: c.messages.map(m =>
                  m.id === assistantMsgId
                    ? { ...m, streaming: false, sources }
                    : m
                ),
                summary: summary || c.summary, // Update summary if received
                memoryStats: memoryStats || c.memoryStats // Update memory stats
              }))
              break
            }

            try {
              const parsed = JSON.parse(data)
              if (parsed.content) {
                accumulatedContent += parsed.content
                // Update message content progressively
                updateConversation(c => ({
                  ...c,
                  messages: c.messages.map(m =>
                    m.id === assistantMsgId
                      ? { ...m, content: accumulatedContent }
                      : m
                  )
                }))
              } else if (parsed.sources) {
                // Capture sources when received
                sources = parsed.sources
              } else if (parsed.summary) {
                // Capture summary for next request
                summary = parsed.summary
              } else if (parsed.memory_stats) {
                // Capture memory stats
                memoryStats = parsed.memory_stats
              } else if (parsed.error) {
                accumulatedContent = `Error: ${parsed.error}`
                updateConversation(c => ({
                  ...c,
                  messages: c.messages.map(m =>
                    m.id === assistantMsgId
                      ? { ...m, content: accumulatedContent, streaming: false }
                      : m
                  )
                }))
              }
            } catch (e) {
              // Skip invalid JSON
              console.warn('Failed to parse SSE data:', data)
            }
          }
        }
      }
    } catch (e) {
      console.error('Streaming error:', e)
      // Fallback to regular API if streaming fails
      try {
        const res = await fetch('/api/ask', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            question: trimmed,
            conversation_history: conversationHistory,
            summary: current?.summary || null,
            max_history_tokens: 4000,
            enable_summarization: true
          })
        })
        const data = await res.json().catch(() => ({}))
        const answer = data?.answer ?? 'No answer returned.'
        const sources = data?.sources ?? []
        const summary = data?.summary || current?.summary
        const memoryStats = data?.memory_stats || current?.memoryStats
        updateConversation(c => ({
          ...c,
          messages: c.messages.map(m =>
            m.id === assistantMsgId
              ? { ...m, content: String(answer), streaming: false, sources }
              : m
          ),
          summary: summary,
          memoryStats: memoryStats
        }))
      } catch (fallbackError) {
        const errMsg = 'Sorry, something went wrong talking to the backend.'
        updateConversation(c => ({
          ...c,
          messages: c.messages.map(m =>
            m.id === assistantMsgId
              ? { ...m, content: errMsg, streaming: false }
              : m
          )
        }))
      }
    }
  }

  const handleRegenerate = async (messageId) => {
    const messages = current?.messages || []
    const msgIndex = messages.findIndex(m => m.id === messageId)

    if (msgIndex === -1) return

    // Find the previous user message
    let userQuestion = null
    for (let i = msgIndex - 1; i >= 0; i--) {
      if (messages[i].role === 'user') {
        userQuestion = messages[i].content
        break
      }
    }

    if (!userQuestion) return

    // Update the message to show it's regenerating
    updateConversation(c => ({
      ...c,
      messages: c.messages.map(m =>
        m.id === messageId
          ? { ...m, content: '', streaming: true }
          : m
      )
    }))

    // Prepare conversation history (up to the message being regenerated, excluding it)
    const conversationHistory = messages
      .slice(0, msgIndex)
      .filter(m => m.role !== 'system')
      .map(m => ({ role: m.role, content: m.content }))

    try {
      // Use streaming endpoint with conversation history and summary
      const response = await fetch('/api/ask/stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question: userQuestion,
          conversation_history: conversationHistory,
          summary: current?.summary || null,
          max_history_tokens: 4000,
          enable_summarization: true
        })
      })

      if (!response.ok) {
        throw new Error('Network response was not ok')
      }

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let accumulatedContent = ''
      let sources = []
      let summary = null
      let memoryStats = null

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const chunk = decoder.decode(value, { stream: true })
        const lines = chunk.split('\n')

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6)
            if (data === '[DONE]') {
              updateConversation(c => ({
                ...c,
                messages: c.messages.map(m =>
                  m.id === messageId
                    ? { ...m, streaming: false, sources }
                    : m
                ),
                summary: summary || c.summary,
                memoryStats: memoryStats || c.memoryStats
              }))
              break
            }

            try {
              const parsed = JSON.parse(data)
              if (parsed.content) {
                accumulatedContent += parsed.content
                updateConversation(c => ({
                  ...c,
                  messages: c.messages.map(m =>
                    m.id === messageId
                      ? { ...m, content: accumulatedContent }
                      : m
                  )
                }))
              } else if (parsed.sources) {
                // Capture sources when received
                sources = parsed.sources
              } else if (parsed.summary) {
                // Capture summary for next request
                summary = parsed.summary
              } else if (parsed.memory_stats) {
                // Capture memory stats
                memoryStats = parsed.memory_stats
              } else if (parsed.error) {
                accumulatedContent = `Error: ${parsed.error}`
                updateConversation(c => ({
                  ...c,
                  messages: c.messages.map(m =>
                    m.id === messageId
                      ? { ...m, content: accumulatedContent, streaming: false }
                      : m
                  )
                }))
              }
            } catch (e) {
              console.warn('Failed to parse SSE data:', data)
            }
          }
        }
      }
    } catch (e) {
      console.error('Regenerate streaming error:', e)
      // Fallback to regular API
      try {
        const res = await fetch('/api/ask', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            question: userQuestion,
            conversation_history: conversationHistory,
            summary: current?.summary || null,
            max_history_tokens: 4000,
            enable_summarization: true
          })
        })
        const data = await res.json().catch(() => ({}))
        const answer = data?.answer ?? 'No answer returned.'
        const sources = data?.sources ?? []
        updateConversation(c => ({
          ...c,
          messages: c.messages.map(m =>
            m.id === messageId
              ? { ...m, content: String(answer), streaming: false, sources }
              : m
          )
        }))
      } catch (fallbackError) {
        const errMsg = 'Sorry, something went wrong talking to the backend.'
        updateConversation(c => ({
          ...c,
          messages: c.messages.map(m =>
            m.id === messageId
              ? { ...m, content: errMsg, streaming: false }
              : m
          )
        }))
      }
    }
  }

  const handleEditQuestion = async (messageId, newContent) => {
    const messages = current?.messages || []
    const msgIndex = messages.findIndex(m => m.id === messageId)

    if (msgIndex === -1) return

    // Update the user message with new content
    updateConversation(c => ({
      ...c,
      messages: c.messages.map(m =>
        m.id === messageId
          ? { ...m, content: newContent }
          : m
      )
    }))

    // Remove all messages after the edited one
    const messagesToKeep = messages.slice(0, msgIndex + 1)
    updateConversation(c => ({
      ...c,
      messages: messagesToKeep.map(m =>
        m.id === messageId
          ? { ...m, content: newContent }
          : m
      )
    }))

    // Add placeholder for new streaming assistant message
    const assistantMsgId = Date.now()
    const assistantMsg = { id: assistantMsgId, role: 'assistant', content: '', streaming: true }

    updateConversation(c => ({
      ...c,
      messages: [...(c.messages||[]), assistantMsg]
    }))

    // Prepare conversation history (up to the edited message, excluding it and after)
    const conversationHistory = messagesToKeep
      .slice(0, msgIndex)
      .filter(m => m.role !== 'system')
      .map(m => ({ role: m.role, content: m.content }))

    try {
      // Use streaming endpoint with edited question and conversation history
      const response = await fetch('/api/ask/stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question: newContent,
          conversation_history: conversationHistory
        })
      })

      if (!response.ok) {
        throw new Error('Network response was not ok')
      }

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let accumulatedContent = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const chunk = decoder.decode(value, { stream: true })
        const lines = chunk.split('\n')

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6)
            if (data === '[DONE]') {
              updateConversation(c => ({
                ...c,
                messages: c.messages.map(m =>
                  m.id === assistantMsgId
                    ? { ...m, streaming: false }
                    : m
                )
              }))
              break
            }

            try {
              const parsed = JSON.parse(data)
              if (parsed.content) {
                accumulatedContent += parsed.content
                updateConversation(c => ({
                  ...c,
                  messages: c.messages.map(m =>
                    m.id === assistantMsgId
                      ? { ...m, content: accumulatedContent }
                      : m
                  )
                }))
              } else if (parsed.error) {
                accumulatedContent = `Error: ${parsed.error}`
                updateConversation(c => ({
                  ...c,
                  messages: c.messages.map(m =>
                    m.id === assistantMsgId
                      ? { ...m, content: accumulatedContent, streaming: false }
                      : m
                  )
                }))
              }
            } catch (e) {
              console.warn('Failed to parse SSE data:', data)
            }
          }
        }
      }
    } catch (e) {
      console.error('Edit question streaming error:', e)
      // Fallback to regular API
      try {
        const res = await fetch('/api/ask', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            question: newContent,
            conversation_history: conversationHistory
          })
        })
        const data = await res.json().catch(() => ({}))
        const answer = data?.answer ?? 'No answer returned.'
        updateConversation(c => ({
          ...c,
          messages: c.messages.map(m =>
            m.id === assistantMsgId
              ? { ...m, content: String(answer), streaming: false }
              : m
          )
        }))
      } catch (fallbackError) {
        const errMsg = 'Sorry, something went wrong talking to the backend.'
        updateConversation(c => ({
          ...c,
          messages: c.messages.map(m =>
            m.id === assistantMsgId
              ? { ...m, content: errMsg, streaming: false }
              : m
          )
        }))
      }
    }
  }

  return (
    <div className={`flex h-screen ${isDark ? 'bg-gray-900 text-gray-100' : 'bg-white text-gray-900'}`}>
      {/* Sidebar */}
      <div className={`${sidebarOpen ? 'w-64' : 'w-0'} transition-all duration-300 ${isDark ? 'bg-gray-950' : 'bg-gray-950'} flex flex-col overflow-hidden`}>
        <div className="p-3 border-b border-gray-800 space-y-2">
          <button
            onClick={createNewChat}
            className="w-full flex items-center gap-2 px-3 py-2.5 rounded-lg border border-gray-700 hover:bg-gray-800 transition text-sm text-white"
          >
            <Plus className="w-4 h-4" />
            New chat
          </button>
          <button
            onClick={toggleSearch}
            className={`w-full flex items-center gap-2 px-3 py-2.5 rounded-lg border transition text-sm ${
              isSearching
                ? 'border-indigo-500 bg-indigo-900/30 text-indigo-300'
                : 'border-gray-700 hover:bg-gray-800 text-white'
            }`}
          >
            <Search className="w-4 h-4" />
            Search Chats
          </button>
          {isSearching && (
            <input
              type="text"
              placeholder="Search conversations..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full px-3 py-2 text-sm bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              autoFocus
            />
          )}
        </div>

        <div className="flex-1 overflow-y-auto p-2">
          {isSearching && searchQuery && (
            <div className="px-3 py-2 text-xs text-gray-400 mb-2">
              {filteredConversations.length} result{filteredConversations.length !== 1 ? 's' : ''} found
            </div>
          )}
          {filteredConversations.length === 0 && isSearching && searchQuery ? (
            <div className="px-3 py-4 text-sm text-gray-400 text-center">
              No conversations found
            </div>
          ) : (
            filteredConversations.map(conv => (
            <div key={conv.id} className="group relative mb-1">
              {editingId === conv.id ? (
                <div className="flex items-center gap-1 px-3 py-2">
                  <input
                    type="text"
                    value={editTitle}
                    onChange={(e) => setEditTitle(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && saveEdit()}
                    className="flex-1 bg-gray-800 text-white text-sm px-2 py-1 rounded outline-none"
                    autoFocus
                  />
                  <button onClick={saveEdit} className="text-green-500 hover:text-green-400">
                    <Check className="w-4 h-4" />
                  </button>
                  <button onClick={cancelEdit} className="text-red-500 hover:text-red-400">
                    <X className="w-4 h-4" />
                  </button>
                </div>
              ) : (
                <button
                  onClick={() => switchChat(conv.id)}
                  className={`w-full text-left px-3 py-2.5 rounded-lg text-sm flex items-center gap-3 transition ${
                    conv.id === currentId ? 'bg-gray-800 text-white' : 'text-gray-300 hover:bg-gray-800/50'
                  }`}
                >
                  <MessageSquare className="w-4 h-4 flex-shrink-0" />
                  <span className="flex-1 truncate">{conv.title}</span>
                  {conv.id === currentId && (
                    <div className="opacity-0 group-hover:opacity-100 flex gap-1">
                      <button
                        onClick={(e) => { e.stopPropagation(); startEdit(conv.id, conv.title) }}
                        className="p-1 hover:bg-gray-700 rounded"
                      >
                        <Edit2 className="w-3.5 h-3.5" />
                      </button>
                      <button
                        onClick={(e) => { e.stopPropagation(); deleteChat(conv.id) }}
                        className="p-1 hover:bg-gray-700 rounded text-red-400"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  )}
                </button>
              )}
            </div>
          ))
          )}
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className={`border-b ${isDark ? 'border-gray-700 bg-gray-800' : 'border-gray-200 bg-white'} px-4 py-3 flex items-center gap-3`}>
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className={`p-2 ${isDark ? 'hover:bg-gray-700' : 'hover:bg-gray-100'} rounded-lg transition`}
          >
            <Menu className="w-5 h-5" />
          </button>
          <h1 className="text-lg font-semibold">DevChoreo</h1>
          <div className="ml-auto flex items-center gap-3">
            <button
              onClick={toggleTheme}
              className={`p-2 ${isDark ? 'hover:bg-gray-700' : 'hover:bg-gray-100'} rounded-lg transition`}
              title={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
            >
              {isDark ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
            </button>
            <div className="flex items-center gap-2">
              <div className={`w-2 h-2 rounded-full ${status==='online' ? 'bg-green-500' : status==='checking' ? 'bg-yellow-500' : 'bg-red-500'}`}></div>
              <span className={`text-sm ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
                {status === 'online' ? 'Online' : status === 'checking' ? 'Checking...' : 'Offline'}
              </span>
            </div>
          </div>
        </div>

        {/* Messages */}
        <div
          ref={listRef}
          className={`flex-1 overflow-y-auto overflow-x-hidden ${isDark ? 'bg-gray-900' : 'bg-white'} relative`}
        >
          <div className="max-w-4xl mx-auto px-1">
            {(current?.messages || []).map((msg, index, array) => {
              // Only show regenerate button for assistant messages that are the last message or last assistant message
              const isLastMessage = index === array.length - 1
              const canRegenerate = msg.role === 'assistant' && isLastMessage
              const canEdit = msg.role === 'user'

              return (
                <Message
                  key={msg.id}
                  message={msg}
                  isDark={isDark}
                  onRegenerate={canRegenerate ? () => handleRegenerate(msg.id) : null}
                  onEdit={canEdit ? handleEditQuestion : null}
                />
              )
            })}
          </div>

          {/* Scroll to Bottom Button */}
          {showScrollButton && (
            <div className="sticky bottom-4 left-0 right-0 flex justify-center pointer-events-none">
              <button
                onClick={scrollToBottom}
                className={`pointer-events-auto shadow-lg ${
                  isDark
                    ? 'bg-gray-700 hover:bg-gray-600 text-white border border-gray-600'
                    : 'bg-white hover:bg-gray-50 text-gray-700 border border-gray-300'
                } rounded-full p-2 transition-all duration-200 hover:scale-105`}
                aria-label="Scroll to bottom"
                title="Scroll to bottom"
              >
                <ArrowDown className="w-5 h-5" />
              </button>
            </div>
          )}
        </div>

        {/* Input */}
        <div className={`border-t ${isDark ? 'border-gray-700 bg-gray-800' : 'border-gray-200 bg-white'} p-2`}>
          <div className="max-w-4xl mx-auto">
            <div className={`flex items-end gap-3 ${isDark ? 'bg-gray-700 border-gray-600' : 'bg-white border-gray-300'} border rounded-xl shadow-sm p-2 focus-within:border-${isDark ? 'gray-500' : 'gray-400'} transition`}>
              <textarea
                ref={inputRef}
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault()
                    sendQuestion()
                  }
                }}
                placeholder="Message DevChoreo..."
                className={`flex-1 resize-none outline-none px-2 py-2 text-sm max-h-60 overflow-y-auto ${isDark ? 'bg-gray-700 text-gray-100 placeholder-gray-400' : 'bg-white text-gray-900'}`}
                style={{ minHeight: '35px', height: '35px' }}
              />
              <button
                onClick={sendQuestion}
                disabled={!inputValue.trim()}
                className={`p-3 rounded-lg transition flex-shrink-0 ${
                  inputValue.trim()
                    ? isDark ? 'bg-white text-black hover:bg-gray-200' : 'bg-black text-white hover:bg-gray-800'
                    : isDark ? 'bg-gray-600 text-gray-400 cursor-not-allowed' : 'bg-gray-200 text-gray-400 cursor-not-allowed'
                }`}
              >
                <Send className="w-4 h-4" />
              </button>
            </div>
            <p className={`text-xs text-center ${isDark ? 'text-gray-500' : 'text-gray-500'} mt-1`}>
              DevChoreo can make mistakes. Consider verifying critical information.
            </p>
          </div>
        </div>
      </div>

      {/* Monitoring Button */}
      <MonitoringButton isDark={isDark} />
    </div>
  )
}