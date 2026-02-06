/**
 * Main application component.
 */

import { useState, useEffect } from "react"
import { SymbolList } from "./components/SymbolList"
import { SignalPanel } from "./components/SignalPanel"
import { symbolAPI } from "./api/client"
import "./App.css"

function App() {
  const [selectedSymbols, setSelectedSymbols] = useState<Set<string>>(
    new Set()
  )

  useEffect(() => {
    loadSelectedSymbols()
  }, [])

  const loadSelectedSymbols = async () => {
    try {
      const symbols = await symbolAPI.getSelectedSymbols()
      setSelectedSymbols(new Set(symbols))
    } catch (err) {
      console.error("Failed to load selected symbols:", err)
    }
  }

  const handleToggleSymbol = (symbol: string, selected: boolean) => {
    const newSelected = new Set(selectedSymbols)
    if (selected) {
      newSelected.add(symbol)
    } else {
      newSelected.delete(symbol)
    }
    setSelectedSymbols(newSelected)
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>QuantPulse</h1>
        <p>Market Intelligence Platform</p>
      </header>

      <div className="app-layout">
        <SymbolList
          selectedSymbols={selectedSymbols}
          onToggle={handleToggleSymbol}
        />
        <SignalPanel selectedSymbols={selectedSymbols} />
      </div>

      <footer className="app-footer">
        <p>
          ⚠️ This platform is for informational purposes only. Not financial
          advice.
        </p>
      </footer>
    </div>
  )
}

export default App
