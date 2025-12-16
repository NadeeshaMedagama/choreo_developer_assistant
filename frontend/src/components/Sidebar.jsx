import React, { useState } from 'react'

export default function Sidebar({ conversations, currentId, onNewChat, onSelect, onDelete, onRename }) {
  const [editingId, setEditingId] = useState(null)
  const [tempTitle, setTempTitle] = useState('')
  const [searchQuery, setSearchQuery] = useState('')
  const [isSearching, setIsSearching] = useState(false)

  const startEdit = (c) => {
    setEditingId(c.id)
    setTempTitle(c.title || 'Untitled')
  }
  const commitEdit = (c) => {
    const title = tempTitle.trim() || 'Untitled'
    onRename?.(c.id, title)
    setEditingId(null)
    setTempTitle('')
  }

  // Filter conversations based on search query
  const filteredConversations = React.useMemo(() => {
    if (!searchQuery.trim()) return conversations || []

    const query = searchQuery.toLowerCase()
    return (conversations || []).filter(c => {
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

  return (
    <aside className="w-64 border-r bg-white flex flex-col">
      <div className="p-3 border-b space-y-2">
        <button
          onClick={onNewChat}
          className="w-full bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg py-2 text-sm font-medium"
        >
          + New chat
        </button>
        <button
          onClick={toggleSearch}
          className={`w-full ${isSearching ? 'bg-indigo-100 text-indigo-700' : 'bg-gray-100 hover:bg-gray-200 text-gray-700'} rounded-lg py-2 text-sm font-medium transition-colors`}
        >
          🔍 Search Chats
        </button>
        {isSearching && (
          <input
            type="text"
            placeholder="Search conversations..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
            autoFocus
          />
        )}
      </div>

      <div className="flex-1 overflow-y-auto">
        {isSearching && searchQuery && (
          <div className="px-3 py-2 text-xs text-gray-500 border-b">
            {filteredConversations.length} result{filteredConversations.length !== 1 ? 's' : ''} found
          </div>
        )}
        <ul className="p-2 space-y-1">
          {filteredConversations.length === 0 && isSearching && searchQuery ? (
            <li className="px-3 py-4 text-sm text-gray-400 text-center">
              No conversations found
            </li>
          ) : (
            filteredConversations.map((c) => {
              const active = c.id === currentId
              return (
                <li key={c.id} className={`group flex items-center gap-2 rounded-lg px-2 py-2 ${active ? 'bg-indigo-50 border border-indigo-200' : 'hover:bg-gray-50'}`}>
                  <button
                    className="flex-1 text-left text-sm truncate"
                    onClick={() => onSelect?.(c.id)}
                  >
                    {editingId === c.id ? (
                      <input
                        autoFocus
                        className="w-full bg-white border rounded px-2 py-1 text-sm"
                        value={tempTitle}
                        onChange={(e) => setTempTitle(e.target.value)}
                        onBlur={() => commitEdit(c)}
                        onKeyDown={(e) => {
                          if (e.key === 'Enter') commitEdit(c)
                          if (e.key === 'Escape') { setEditingId(null); setTempTitle('') }
                        }}
                      />
                    ) : (
                      <span title={c.title} onDoubleClick={() => startEdit(c)}>
                        {c.title || 'Untitled'}
                      </span>
                    )}
                  </button>
                  <button
                    className="invisible group-hover:visible text-gray-400 hover:text-gray-600"
                    title="Rename"
                    onClick={() => startEdit(c)}
                  >
                    ✎
                  </button>
                  <button
                    className="invisible group-hover:visible text-gray-400 hover:text-red-600"
                    title="Delete"
                    onClick={() => onDelete?.(c.id)}
                  >
                    🗑
                  </button>
                </li>
              )
            })
          )}
        </ul>
      </div>

      <div className="p-3 text-xs text-gray-400 border-t">
        DevChoreo
      </div>
    </aside>
  )
}

