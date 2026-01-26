import React, { useEffect, useRef, useState } from 'react'
import mermaid from 'mermaid'

// Initialize mermaid once with configuration
mermaid.initialize({
  startOnLoad: false,
  theme: 'default',
  securityLevel: 'loose',
  logLevel: 'error',
  themeVariables: {
    fontSize: '14px',
    fontFamily: 'ui-sans-serif, system-ui, -apple-system, sans-serif'
  },
  flowchart: {
    useMaxWidth: true,
    htmlLabels: true,
    curve: 'basis'
  }
})

// Helper function to clean mermaid code
function cleanMermaidCode(chart) {
  if (!chart) return ''

  let cleanChart = chart.trim()

  // Valid diagram types that should be at the start
  const validTypes = [
    'flowchart', 'graph', 'sequenceDiagram',
    'stateDiagram-v2', 'stateDiagram', 'classDiagram',
    'pie', 'gantt', 'gitGraph'
  ]

  // Find the first line that starts with a valid diagram type
  const lines = cleanChart.split('\n')
  let startIndex = 0

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim()
    if (validTypes.some(type => line.startsWith(type))) {
      startIndex = i
      break
    }
  }

  // If we found a valid start, remove everything before it
  if (startIndex > 0) {
    cleanChart = lines.slice(startIndex).join('\n').trim()
  }

  return cleanChart
}

// Helper to render with timeout
async function renderWithTimeout(id, code, timeoutMs = 5000) {
  return Promise.race([
    mermaid.render(id, code),
    new Promise((_, reject) =>
      setTimeout(() => reject(new Error('Rendering timeout - diagram may have invalid syntax')), timeoutMs)
    )
  ])
}

export default function MermaidDiagram({ chart, isDark }) {
  const containerRef = useRef(null)
  const [svg, setSvg] = useState('')
  const [error, setError] = useState(null)
  const [isRendering, setIsRendering] = useState(true)
  const renderAttempted = useRef(false)

  useEffect(() => {
    // Reset state when chart changes
    setSvg('')
    setError(null)
    setIsRendering(true)
    renderAttempted.current = false

    const renderDiagram = async () => {
      if (!chart) {
        setError('No diagram code provided')
        setIsRendering(false)
        return
      }

      // Prevent double renders
      if (renderAttempted.current) return
      renderAttempted.current = true

      try {
        // Clean the chart code
        const cleanChart = cleanMermaidCode(chart)

        if (!cleanChart) {
          setError('Invalid diagram code - no valid Mermaid syntax found')
          setIsRendering(false)
          return
        }

        // Update theme based on dark mode
        mermaid.initialize({
          startOnLoad: false,
          theme: isDark ? 'dark' : 'default',
          securityLevel: 'loose',
          logLevel: 'error',
          themeVariables: {
            fontSize: '14px',
            fontFamily: 'ui-sans-serif, system-ui, -apple-system, sans-serif',
          },
          flowchart: {
            useMaxWidth: true,
            htmlLabels: true,
            curve: 'basis'
          }
        })

        // Generate unique ID
        const id = `mermaid-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`

        // Render with 5 second timeout
        const result = await renderWithTimeout(id, cleanChart, 5000)

        if (result && result.svg) {
          setSvg(result.svg)
          setIsRendering(false)
        } else {
          throw new Error('Mermaid returned empty result')
        }
      } catch (err) {
        console.error('Mermaid rendering error:', err)
        setError(err.message || 'Failed to render diagram')
        setIsRendering(false)
      }
    }

    // Small delay to ensure DOM is ready
    const timer = setTimeout(renderDiagram, 100)

    return () => {
      clearTimeout(timer)
    }
  }, [chart, isDark])

  if (error) {
    return (
      <div className={`p-4 rounded-lg border ${
        isDark ? 'bg-red-900/20 border-red-700 text-red-300' : 'bg-red-50 border-red-300 text-red-700'
      }`}>
        <p className="text-sm font-medium">⚠️ Diagram Error</p>
        <p className="text-xs mt-1">{error}</p>
        <details className="mt-2">
          <summary className="text-xs cursor-pointer">Show diagram code</summary>
          <pre className="text-xs mt-2 overflow-x-auto whitespace-pre-wrap">{chart}</pre>
        </details>
      </div>
    )
  }

  if (isRendering) {
    return (
      <div className={`p-8 rounded-lg border ${
        isDark ? 'bg-gray-800 border-gray-700' : 'bg-gray-50 border-gray-300'
      } flex items-center justify-center`}>
        <div className="flex items-center gap-2">
          <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"/>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
          </svg>
          <span className="text-sm">Rendering diagram...</span>
        </div>
      </div>
    )
  }

  if (!svg) {
    return null
  }

  return (
    <div
      ref={containerRef}
      className={`mermaid-diagram p-4 rounded-lg border overflow-x-auto ${
        isDark ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-300'
      }`}
      dangerouslySetInnerHTML={{ __html: svg }}
    />
  )
}
