import React, { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { Copy, ThumbsUp, ThumbsDown, Share2, RotateCcw, Check, Edit2, X, FileText, ExternalLink, ChevronDown, ChevronUp } from 'lucide-react'

export default function Message({ message, isDark, onRegenerate, onEdit }) {
  const [copied, setCopied] = useState(false)
  const [liked, setLiked] = useState(false)
  const [disliked, setDisliked] = useState(false)
  const [isEditing, setIsEditing] = useState(false)
  const [editedContent, setEditedContent] = useState(message.content)
  const [showSources, setShowSources] = useState(true)

  const isAssistant = message.role === 'assistant'

  // Check if the message contains OpenChoreo mentions
  const containsOpenChoreo = isAssistant &&
    (message.content.toLowerCase().includes('openchoreo') ||
     message.content.toLowerCase().includes('open choreo'))

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(message.content)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch (err) {
      console.error('Failed to copy:', err)
    }
  }

  const handleLike = () => {
    setLiked(!liked)
    if (disliked) setDisliked(false)
  }

  const handleDislike = () => {
    setDisliked(!disliked)
    if (liked) setLiked(false)
  }

  const handleShare = async () => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: 'DevChoreo Response',
          text: message.content
        })
      } catch (err) {
        if (err.name !== 'AbortError') {
          console.error('Error sharing:', err)
        }
      }
    } else {
      // Fallback to copy
      handleCopy()
    }
  }

  const handleEdit = () => {
    setIsEditing(true)
    setEditedContent(message.content)
  }

  const handleSaveEdit = () => {
    if (editedContent.trim() && onEdit) {
      onEdit(message.id, editedContent.trim())
      setIsEditing(false)
    }
  }

  const handleCancelEdit = () => {
    setIsEditing(false)
    setEditedContent(message.content)
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSaveEdit()
    } else if (e.key === 'Escape') {
      handleCancelEdit()
    }
  }

  return (
    <div
      className={`px-4 py-6 ${
        isAssistant
          ? isDark ? 'bg-gray-800' : 'bg-gray-50'
          : isDark ? 'bg-gray-900' : 'bg-white'
      }`}
    >
      <div className="max-w-3xl mx-auto flex gap-4 overflow-hidden">
        <div className={`w-8 h-8 rounded-sm flex items-center justify-center flex-shrink-0 text-white font-semibold ${
          isAssistant ? 'bg-green-600' : 'bg-purple-600'
        }`}>
          {isAssistant ? 'D' : 'U'}
        </div>
        <div className="flex-1 pt-1 min-w-0 overflow-hidden">
          {isEditing ? (
            <div className="space-y-2">
              <textarea
                value={editedContent}
                onChange={(e) => setEditedContent(e.target.value)}
                onKeyDown={handleKeyDown}
                className={`w-full px-3 py-2 rounded-lg border resize-none focus:outline-none focus:ring-2 focus:ring-purple-500 ${
                  isDark
                    ? 'bg-gray-800 border-gray-700 text-gray-100'
                    : 'bg-white border-gray-300 text-gray-900'
                }`}
                rows={3}
                autoFocus
              />
              <div className="flex gap-2">
                <button
                  onClick={handleSaveEdit}
                  className="px-3 py-1.5 bg-purple-600 hover:bg-purple-700 text-white rounded-lg text-sm transition"
                >
                  Save & Submit
                </button>
                <button
                  onClick={handleCancelEdit}
                  className={`px-3 py-1.5 rounded-lg text-sm transition ${
                    isDark
                      ? 'bg-gray-700 hover:bg-gray-600 text-gray-200'
                      : 'bg-gray-200 hover:bg-gray-300 text-gray-700'
                  }`}
                >
                  Cancel
                </button>
              </div>
            </div>
          ) : (
            <>
              {/* Warning Banner for OpenChoreo mentions */}
              {containsOpenChoreo && (
                <div className={`mb-3 p-3 rounded-lg border-l-4 border-yellow-500 ${
                  isDark ? 'bg-yellow-900/20 text-yellow-200' : 'bg-yellow-50 text-yellow-800'
                }`}>
                  <p className="text-sm font-medium">
                    ⚠️ This response may contain information about OpenChoreo. DevChoreo is designed exclusively for WSO2's Choreo platform.
                  </p>
                </div>
              )}

              <div className={`text-base leading-relaxed prose prose-lg ${isDark ? 'prose-invert' : ''} max-w-none`}>
                <ReactMarkdown
                  remarkPlugins={[remarkGfm]}
                  components={{
                    a: ({ node, ...props }) => (
                      <a {...props} target="_blank" rel="noopener noreferrer" />
                    ),
                    table: ({ node, ...props }) => (
                      <table {...props} style={{ fontSize: '13px' }} />
                    ),
                    th: ({ node, ...props }) => (
                      <th {...props} style={{ fontSize: '13px' }} className="font-semibold" />
                    ),
                    td: ({ node, ...props }) => (
                      <td {...props} style={{ fontSize: '13px' }} />
                    )
                  }}
                >
                  {message.content}
                </ReactMarkdown>
                {message.streaming && (
                  <span className={`inline-block w-2 h-5 ml-1 ${isDark ? 'bg-gray-300' : 'bg-gray-700'} animate-pulse`}></span>
                )}
              </div>

              {/* Action Buttons for User messages */}
              {!isAssistant && (
                <div className="flex items-center gap-2 mt-3 pt-2">
                  <button
                    onClick={handleCopy}
                    className={`p-1.5 rounded-lg transition ${
                      isDark
                        ? 'hover:bg-gray-700 text-gray-400 hover:text-gray-200'
                        : 'hover:bg-gray-200 text-gray-600 hover:text-gray-800'
                    }`}
                    title={copied ? 'Copied!' : 'Copy'}
                  >
                    {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                  </button>

                  {onEdit && (
                    <button
                      onClick={handleEdit}
                      className={`p-1.5 rounded-lg transition ${
                        isDark
                          ? 'hover:bg-gray-700 text-gray-400 hover:text-gray-200'
                          : 'hover:bg-gray-200 text-gray-600 hover:text-gray-800'
                      }`}
                      title="Edit question"
                    >
                      <Edit2 className="w-4 h-4" />
                    </button>
                  )}
                </div>
              )}

              {/* Action Buttons for Assistant messages */}
              {isAssistant && (
                <>
                  <div className="flex items-center gap-2 mt-3 pt-2">
                    <button
                      onClick={handleCopy}
                      className={`p-1.5 rounded-lg transition ${
                        isDark
                          ? 'hover:bg-gray-700 text-gray-400 hover:text-gray-200'
                          : 'hover:bg-gray-200 text-gray-600 hover:text-gray-800'
                      }`}
                      title={copied ? 'Copied!' : 'Copy'}
                    >
                      {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                    </button>

                    <button
                      onClick={handleLike}
                      className={`p-1.5 rounded-lg transition ${
                        liked
                          ? 'text-green-600'
                          : isDark
                            ? 'hover:bg-gray-700 text-gray-400 hover:text-gray-200'
                            : 'hover:bg-gray-200 text-gray-600 hover:text-gray-800'
                      }`}
                      title="Good response"
                    >
                      <ThumbsUp className={`w-4 h-4 ${liked ? 'fill-current' : ''}`} />
                    </button>

                    <button
                      onClick={handleDislike}
                      className={`p-1.5 rounded-lg transition ${
                        disliked
                          ? 'text-red-600'
                          : isDark
                            ? 'hover:bg-gray-700 text-gray-400 hover:text-gray-200'
                            : 'hover:bg-gray-200 text-gray-600 hover:text-gray-800'
                      }`}
                      title="Bad response"
                    >
                      <ThumbsDown className={`w-4 h-4 ${disliked ? 'fill-current' : ''}`} />
                    </button>

                    <button
                      onClick={handleShare}
                      className={`p-1.5 rounded-lg transition ${
                        isDark
                          ? 'hover:bg-gray-700 text-gray-400 hover:text-gray-200'
                          : 'hover:bg-gray-200 text-gray-600 hover:text-gray-800'
                      }`}
                      title="Share"
                    >
                      <Share2 className="w-4 h-4" />
                    </button>

                    {onRegenerate && (
                      <button
                        onClick={onRegenerate}
                        className={`p-1.5 rounded-lg transition ${
                          isDark
                            ? 'hover:bg-gray-700 text-gray-400 hover:text-gray-200'
                            : 'hover:bg-gray-200 text-gray-600 hover:text-gray-800'
                        }`}
                        title="Regenerate response"
                      >
                        <RotateCcw className="w-4 h-4" />
                      </button>
                    )}
                  </div>

                  {/* Sources Section */}
                  {message.sources && message.sources.length > 0 && (
                    <div className={`mt-4 pt-4 border-t ${isDark ? 'border-gray-700' : 'border-gray-200'}`}>
                      <button
                        onClick={() => setShowSources(!showSources)}
                        className={`flex items-center gap-2 text-sm font-medium mb-2 ${
                          isDark ? 'text-gray-300' : 'text-gray-700'
                        }`}
                      >
                        {showSources ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                        Sources ({message.sources.length})
                      </button>

                      {showSources && (
                        <div className="space-y-2">
                          {message.sources.map((source, idx) => (
                            <div
                              key={idx}
                              className={`p-3 rounded-lg border text-sm ${
                                isDark
                                  ? 'bg-gray-700/50 border-gray-600'
                                  : 'bg-gray-50 border-gray-200'
                              }`}
                            >
                              <div className="flex items-start gap-2">
                                <FileText className={`w-4 h-4 mt-0.5 flex-shrink-0 ${
                                  isDark ? 'text-gray-400' : 'text-gray-500'
                                }`} />
                                <div className="flex-1 min-w-0">
                                  {/* Title or File Path */}
                                  <div className="font-medium mb-1">
                                    {source.title || source.file_path || `Document ${idx + 1}`}
                                  </div>

                                  {/* Repository */}
                                  {source.repository && (
                                    <div className={`text-xs mb-1 ${
                                      isDark ? 'text-gray-400' : 'text-gray-600'
                                    }`}>
                                      Repository: {source.repository}
                                    </div>
                                  )}

                                  {/* Source Type */}
                                  {source.source_type && (
                                    <div className={`text-xs mb-1 ${
                                      isDark ? 'text-gray-400' : 'text-gray-600'
                                    }`}>
                                      Type: {source.source_type}
                                    </div>
                                  )}

                                  {/* Content Preview */}
                                  {source.content && (
                                    <div className={`text-xs mt-2 ${
                                      isDark ? 'text-gray-400' : 'text-gray-600'
                                    }`}>
                                      {source.content}
                                    </div>
                                  )}

                                  {/* URL Link */}
                                  {source.url && (
                                    <a
                                      href={source.url}
                                      target="_blank"
                                      rel="noopener noreferrer"
                                      className={`inline-flex items-center gap-1 mt-2 text-xs hover:underline ${
                                        isDark ? 'text-blue-400' : 'text-blue-600'
                                      }`}
                                    >
                                      View source
                                      <ExternalLink className="w-3 h-3" />
                                    </a>
                                  )}

                                  {/* Relevance Score */}
                                  {source.score !== undefined && (
                                    <div className={`text-xs mt-1 ${
                                      isDark ? 'text-gray-500' : 'text-gray-500'
                                    }`}>
                                      Relevance: {(source.score * 100).toFixed(1)}%
                                    </div>
                                  )}
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  )}
                </>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  )
}
