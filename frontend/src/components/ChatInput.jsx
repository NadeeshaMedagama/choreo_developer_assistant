import React, { useState } from 'react'

export default function ChatInput({ onSend, disabled }) {
  const [value, setValue] = useState('')

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      doSend()
    }
  }

  const doSend = () => {
    if (!value.trim() || disabled) return
    onSend?.(value)
    setValue('')
  }

  return (
    <div className="bg-white border rounded-2xl p-2 flex items-end gap-2">
      <textarea
        className="flex-1 resize-none outline-none p-3 rounded-xl min-h-[48px] max-h-48 text-sm"
        placeholder="Send a message (Shift+Enter for new line)"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={handleKeyDown}
        rows={1}
      />
      <button
        onClick={doSend}
        disabled={disabled}
        className={`px-6 py-3 rounded-xl text-base font-medium ${disabled ? 'bg-gray-200 text-gray-400 cursor-not-allowed' : 'bg-indigo-600 text-white hover:bg-indigo-700'}`}
        aria-label="Send"
      >
        Send
      </button>
    </div>
  )
}

