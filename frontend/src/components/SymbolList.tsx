/**
 * Left panel: Searchable list of all available symbols.
 */

import React, { useState, useEffect } from "react"
import { Symbol } from "../types"
import { symbolAPI } from "../api/client"
import "./SymbolList.css"

interface SymbolListProps {
  selectedSymbols: Set<string>
  onToggle: (symbol: string, selected: boolean) => void
}

export const SymbolList: React.FC<SymbolListProps> = ({
  selectedSymbols,
  onToggle,
}) => {
  const [symbols, setSymbols] = useState<Symbol[]>([])
  const [filtered, setFiltered] = useState<Symbol[]>([])
  const [search, setSearch] = useState("")
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadSymbols()
  }, [])

  const loadSymbols = async () => {
    try {
      const data = await symbolAPI.listSymbols()
      setSymbols(data)
      setFiltered(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load symbols")
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = (query: string) => {
    setSearch(query)
    const q = query.toLowerCase()
    setFiltered(
      symbols.filter(
        (s) =>
          s.symbol.toLowerCase().includes(q) ||
          s.yahoo_symbol.toLowerCase().includes(q)
      )
    )
  }

  const handleToggle = async (symbol: string) => {
    const newSelected = !selectedSymbols.has(symbol)
    try {
      await symbolAPI.selectSymbol(symbol, newSelected)
      onToggle(symbol, newSelected)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to toggle symbol")
    }
  }

  return (
    <div className="symbol-list">
      <div className="symbol-list-header">
        <h2>Symbols</h2>
        <input
          type="text"
          placeholder="Search..."
          value={search}
          onChange={(e) => handleSearch(e.target.value)}
          className="symbol-search"
        />
      </div>

      {error && <div className="error">{error}</div>}
      {loading && <div className="loading">Loading symbols...</div>}

      <div className="symbol-items">
        {filtered.map((symbol) => (
          <div
            key={symbol.symbol}
            className={`symbol-item ${
              selectedSymbols.has(symbol.symbol) ? "selected" : ""
            }`}
          >
            <input
              type="checkbox"
              checked={selectedSymbols.has(symbol.symbol)}
              onChange={() => handleToggle(symbol.symbol)}
            />
            <span className="symbol-name">{symbol.symbol}</span>
            <span className="symbol-type">{symbol.instrument_type}</span>
          </div>
        ))}
      </div>
    </div>
  )
}
