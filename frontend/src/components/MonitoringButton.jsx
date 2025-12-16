import React, { useState } from 'react'
import { Activity, X } from 'lucide-react'

export default function MonitoringButton({ isDark }) {
  const [showMenu, setShowMenu] = useState(false)

  const openMetrics = () => {
    // Open raw Prometheus metrics (always available when backend is running)
    window.open('http://localhost:8000/metrics', '_blank', 'noopener,noreferrer')
  }

  const openGrafana = () => {
    // Try to open Grafana (may not be running)
    window.open('http://localhost:3000', '_blank', 'noopener,noreferrer')
  }

  const openPrometheus = () => {
    // Try to open Prometheus (may not be running)
    window.open('http://localhost:9090', '_blank', 'noopener,noreferrer')
  }

  const openHealth = () => {
    // Open health check endpoint
    window.open('http://localhost:8000/api/health', '_blank', 'noopener,noreferrer')
  }

  return (
    <>
      {/* Monitoring Menu */}
      {showMenu && (
        <div className={`fixed bottom-24 right-6 rounded-lg shadow-2xl z-40 ${
          isDark ? 'bg-gray-800 border border-gray-700' : 'bg-white border border-gray-200'
        }`}>
          <div className="p-3 space-y-2 min-w-[200px]">
            <div className={`text-xs font-semibold mb-2 pb-2 border-b ${
              isDark ? 'text-gray-300 border-gray-700' : 'text-gray-600 border-gray-200'
            }`}>
              Monitoring Options
            </div>

            <button
              onClick={() => { openMetrics(); setShowMenu(false); }}
              className={`w-full text-left px-3 py-2 rounded text-sm transition ${
                isDark
                  ? 'hover:bg-gray-700 text-gray-200'
                  : 'hover:bg-gray-100 text-gray-700'
              }`}
            >
              📊 Metrics (Always Available)
            </button>

            <button
              onClick={() => { openHealth(); setShowMenu(false); }}
              className={`w-full text-left px-3 py-2 rounded text-sm transition ${
                isDark
                  ? 'hover:bg-gray-700 text-gray-200'
                  : 'hover:bg-gray-100 text-gray-700'
              }`}
            >
              💚 Health Check
            </button>

            <button
              onClick={() => { openPrometheus(); setShowMenu(false); }}
              className={`w-full text-left px-3 py-2 rounded text-sm transition ${
                isDark
                  ? 'hover:bg-gray-700 text-gray-200'
                  : 'hover:bg-gray-100 text-gray-700'
              }`}
            >
              🔍 Prometheus (if running)
            </button>

            <button
              onClick={() => { openGrafana(); setShowMenu(false); }}
              className={`w-full text-left px-3 py-2 rounded text-sm transition ${
                isDark
                  ? 'hover:bg-gray-700 text-gray-200'
                  : 'hover:bg-gray-100 text-gray-700'
              }`}
            >
              📈 Grafana (if running)
            </button>
          </div>
        </div>
      )}

      {/* Monitoring Button */}
      <button
        onClick={() => setShowMenu(!showMenu)}
        className={`fixed bottom-8 right-7 p-2 rounded-full shadow-lg transition-all duration-300 hover:scale-110 z-50 ${
          isDark
            ? 'bg-blue-600 hover:bg-blue-500 text-white'
            : 'bg-blue-500 hover:bg-blue-600 text-white'
        }`}
        title="Open Monitoring Options"
        aria-label="Open monitoring options"
      >
        {showMenu ? <X className="w-6 h-6" /> : <Activity className="w-6 h-6" />}
      </button>

      {/* Click outside to close menu */}
      {showMenu && (
        <div
          className="fixed inset-0 z-30"
          onClick={() => setShowMenu(false)}
        />
      )}
    </>
  )
}

