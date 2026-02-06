/**
 * Main panel: Selected symbols and triggered signals.
 */

import React, { useState, useEffect } from "react"
import { Signal } from "../types"
import { analyzerAPI, notifierAPI } from "../api/client"
import "./SignalPanel.css"

interface SignalPanelProps {
  selectedSymbols: Set<string>
}

export const SignalPanel: React.FC<SignalPanelProps> = ({ selectedSymbols }) => {
  const [signals, setSignals] = useState<Signal[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadSignals()
    // Poll for new signals every 30 seconds
    const interval = setInterval(loadSignals, 30000)
    return () => clearInterval(interval)
  }, [selectedSymbols])

  const loadSignals = async () => {
    try {
      const notifications = await notifierAPI.getNotifications()
      setSignals(notifications)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load signals")
    }
  }

  const runAnalysis = async () => {
    setLoading(true)
    try {
      await analyzerAPI.analyzeAll()
      await loadSignals()
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to run analysis")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="signal-panel">
      <div className="panel-header">
        <h2>Selected Symbols & Signals</h2>
        <button
          onClick={runAnalysis}
          disabled={loading || selectedSymbols.size === 0}
          className="analyze-btn"
        >
          {loading ? "Analyzing..." : "Analyze Now"}
        </button>
      </div>

      {error && <div className="error">{error}</div>}

      <div className="selected-symbols">
        <h3>Selected ({selectedSymbols.size})</h3>
        <div className="symbols-grid">
          {selectedSymbols.size === 0 ? (
            <p className="empty">No symbols selected</p>
          ) : (
            Array.from(selectedSymbols).map((symbol) => (
              <div key={symbol} className="symbol-badge">
                {symbol}
              </div>
            ))
          )}
        </div>
      </div>

      <div className="signals-section">
        <h3>Recent Signals</h3>
        {signals.length === 0 ? (
          <p className="empty">No signals triggered</p>
        ) : (
          <div className="signals-list">
            {signals.map((signal, idx) => (
              <div key={idx} className="signal-item">
                <div className="signal-header">
                  <span className="signal-symbol">{signal.symbol}</span>
                  <span className="signal-type">{signal.signal_type}</span>
                  <span className="signal-confidence">
                    {(signal.confidence * 100).toFixed(0)}%
                  </span>
                </div>
                <div className="signal-body">
                  <p className="signal-explanation">{signal.explanation}</p>
                  <div className="signal-indicators">
                    {signal.indicators_passed.map((ind, i) => (
                      <span key={i} className="indicator-tag">
                        {ind}
                      </span>
                    ))}
                  </div>
                </div>
                <div className="signal-footer">
                  {new Date(signal.timestamp).toLocaleString()}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
