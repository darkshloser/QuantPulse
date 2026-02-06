/**
 * API client for communicating with backend services.
 */

import axios from "axios"
import { Symbol, Signal } from "../types"

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8001"

const client = axios.create({
  baseURL: API_BASE,
  headers: {
    "Content-Type": "application/json",
  },
})

// Symbol Management API
export const symbolAPI = {
  async listSymbols(): Promise<Symbol[]> {
    const response = await client.get("/symbols")
    return response.data.symbols
  },

  async getSelectedSymbols(): Promise<string[]> {
    const response = await client.get("/symbols/selected")
    return response.data.symbols
  },

  async selectSymbol(symbol: string, selected: boolean): Promise<void> {
    await client.post("/symbols/select", { symbol, selected })
  },
}

// Market Data API
export const marketDataAPI = {
  async getMarketData(symbol: string) {
    const response = await client.get(`/market-data/${symbol}`)
    return response.data
  },

  async fetchSymbolData(symbol: string) {
    const response = await client.post(`/fetch/${symbol}`)
    return response.data
  },

  async fetchAllData() {
    const response = await client.post("/fetch-all")
    return response.data
  },
}

// Data Analyzer API
export const analyzerAPI = {
  async getSignals(symbol: string): Promise<Signal[]> {
    const response = await client.get(`/signals/${symbol}`)
    return response.data
  },

  async analyzeSymbol(symbol: string) {
    const response = await client.post(`/analyze/${symbol}`)
    return response.data
  },

  async analyzeAll() {
    const response = await client.post("/analyze-all")
    return response.data
  },
}

// Notifier API
export const notifierAPI = {
  async getNotifications() {
    const response = await client.get("/notifications")
    return response.data
  },
}

export default client
