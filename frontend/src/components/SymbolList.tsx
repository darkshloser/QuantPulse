/**
 * Left panel: Searchable list of all available symbols.
 * Uses server-side search and pagination to handle 10k+ symbols.
 */

import React, { useState, useEffect, useCallback, useRef } from "react"
import { Symbol } from "../types"
import { symbolAPI } from "../api/client"
import "./SymbolList.css"

interface SymbolListProps {
  selectedSymbols: Set<string>
  onToggle: (symbol: string, selected: boolean) => void
  refreshKey?: number
}

const PAGE_SIZE = 100

export const SymbolList: React.FC<SymbolListProps> = ({
  selectedSymbols,
  onToggle,
  refreshKey = 0,
}) => {
  const [symbols, setSymbols] = useState<Symbol[]>([])
  const [total, setTotal] = useState(0)
  const [search, setSearch] = useState("")
  const [offset, setOffset] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  const loadSymbols = useCallback(async (query: string, pageOffset: number) => {
    setLoading(true)
    setError(null)
    try {
      const data = await symbolAPI.listSymbols(query || undefined, PAGE_SIZE, pageOffset)
      setSymbols(data.symbols)
      setTotal(data.total)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load symbols")
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    loadSymbols(search, offset)
  }, [offset])

  // When refreshKey changes (e.g. after SEC import), reset to first page and reload
  useEffect(() => {
    if (refreshKey > 0) {
      setOffset(0)
      loadSymbols(search, 0)
    }
  }, [refreshKey])

  const handleSearch = (query: string) => {
    setSearch(query)
    setOffset(0)
    if (debounceRef.current) clearTimeout(debounceRef.current)
    debounceRef.current = setTimeout(() => {
      loadSymbols(query, 0)
    }, 300)
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

  const totalPages = Math.ceil(total / PAGE_SIZE)
  const currentPage = Math.floor(offset / PAGE_SIZE) + 1

  // Build the window of page buttons: always show first, last, current ±2
  const pageButtons = (): (number | "...")[] => {
    if (totalPages <= 7) return Array.from({ length: totalPages }, (_, i) => i + 1)
    const pages: (number | "...")[] = []
    const addPage = (p: number) => { if (!pages.includes(p)) pages.push(p) }
    addPage(1)
    if (currentPage > 3) pages.push("...")
    for (let p = Math.max(2, currentPage - 2); p <= Math.min(totalPages - 1, currentPage + 2); p++) addPage(p)
    if (currentPage < totalPages - 2) pages.push("...")
    addPage(totalPages)
    return pages
  }

  const goToPage = (page: number) => setOffset((page - 1) * PAGE_SIZE)

  return (
    <div className="symbol-list">
      <div className="symbol-list-header">
        <h2>Symbols</h2>
        <input
          type="text"
          placeholder="Search symbols..."
          value={search}
          onChange={(e) => handleSearch(e.target.value)}
          className="symbol-search"
        />
        <div className="symbol-count">{total.toLocaleString()} symbols</div>
      </div>

      {error && <div className="error">{error}</div>}
      {loading && <div className="loading">Loading symbols...</div>}

      <div className="symbol-items">
        {!loading && symbols.length === 0 && (
          <div className="no-results">No symbols found</div>
        )}
        {symbols.map((symbol) => (
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
            <div className="symbol-content">
              <div className="symbol-yahoo">{symbol.yahoo_symbol}</div>
              <div className="symbol-company">{symbol.company_name}</div>
            </div>
          </div>
        ))}
      </div>

      {totalPages > 1 && (
        <div className="symbol-pagination">
          <button
            className="page-btn"
            disabled={currentPage === 1}
            onClick={() => goToPage(currentPage - 1)}
            title="Previous page"
          >
            ‹
          </button>

          {pageButtons().map((p, i) =>
            p === "..." ? (
              <span key={`ellipsis-${i}`} className="page-ellipsis">…</span>
            ) : (
              <button
                key={p}
                className={`page-btn ${p === currentPage ? "active" : ""}`}
                onClick={() => goToPage(p as number)}
              >
                {p}
              </button>
            )
          )}

          <button
            className="page-btn"
            disabled={currentPage === totalPages}
            onClick={() => goToPage(currentPage + 1)}
            title="Next page"
          >
            ›
          </button>
        </div>
      )}
    </div>
  )
}
