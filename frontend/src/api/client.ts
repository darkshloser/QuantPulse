/**
 * API client for communicating with backend services.
 */

import axios, { AxiosError } from "axios"
import { Symbol, Signal, User, AuthToken } from "../types"

const AUTH_API_BASE =
  (import.meta.env.VITE_AUTH_API_URL as string) || "http://localhost:8000"
const SYMBOL_API_BASE =
  (import.meta.env.VITE_SYMBOL_API_URL as string) || "http://localhost:8001"
const ANALYZER_API_BASE =
  (import.meta.env.VITE_ANALYZER_API_URL as string) || "http://localhost:8002"
const NOTIFIER_API_BASE =
  (import.meta.env.VITE_NOTIFIER_API_URL as string) || "http://localhost:8003"

// API Clients with different base URLs
const authClient = axios.create({
  baseURL: AUTH_API_BASE,
  headers: {
    "Content-Type": "application/json",
  },
})

const symbolClient = axios.create({
  baseURL: SYMBOL_API_BASE,
  headers: {
    "Content-Type": "application/json",
  },
})

const analyzerClient = axios.create({
  baseURL: ANALYZER_API_BASE,
  headers: {
    "Content-Type": "application/json",
  },
})

const notifierClient = axios.create({
  baseURL: NOTIFIER_API_BASE,
  headers: {
    "Content-Type": "application/json",
  },
})

// Interceptors to add auth token to requests
const setupInterceptors = () => {
  ;[authClient, symbolClient, analyzerClient, notifierClient].forEach((client) => {
    client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem("access_token")
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
        }
        return config
      },
      (error) => Promise.reject(error)
    )

    // Handle 401 responses - token expired
    client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response?.status === 401) {
          localStorage.removeItem("access_token")
          localStorage.removeItem("refresh_token")
          localStorage.removeItem("user")
          window.location.href = "/login"
        }
        return Promise.reject(error)
      }
    )
  })
}

setupInterceptors()

// Authentication API
export const authAPI = {
  async register(
    username: string,
    email: string,
    password: string
  ): Promise<User> {
    const response = await authClient.post("/register", {
      username,
      email,
      password,
    })
    return response.data
  },

  async login(
    username_or_email: string,
    password: string
  ): Promise<AuthToken> {
    const response = await authClient.post("/login", {
      username_or_email,
      password,
    })

    // Store tokens
    localStorage.setItem("access_token", response.data.access_token)
    if (response.data.refresh_token) {
      localStorage.setItem("refresh_token", response.data.refresh_token)
    }
    localStorage.setItem("user", JSON.stringify(response.data.user))

    return response.data
  },

  async logout(): Promise<void> {
    localStorage.removeItem("access_token")
    localStorage.removeItem("refresh_token")
    localStorage.removeItem("user")
  },

  async getCurrentUser(): Promise<User> {
    const response = await authClient.get("/me")
    return response.data
  },

  async updateProfile(
    firstName?: string,
    lastName?: string
  ): Promise<User> {
    const response = await authClient.put("/me/profile", {
      first_name: firstName,
      last_name: lastName,
    })
    return response.data
  },

  async listUsers(): Promise<User[]> {
    const response = await authClient.get("/admin/users")
    return response.data.users
  },

  async getPendingUsers(): Promise<User[]> {
    const response = await authClient.get("/admin/users/pending")
    return response.data.users
  },

  async getUserDetails(userId: number): Promise<User> {
    const response = await authClient.get(`/admin/users/${userId}`)
    return response.data
  },

  async approveUser(userId: number): Promise<{ message: string; user: User }> {
    const response = await authClient.post(`/admin/users/${userId}/approve`)
    return response.data
  },

  async rejectUser(userId: number): Promise<{ message: string; user: User }> {
    const response = await authClient.post(`/admin/users/${userId}/reject`)
    return response.data
  },

  async deleteUser(userId: number): Promise<{ message: string }> {
    const response = await authClient.delete(`/admin/users/${userId}`)
    return response.data
  },
}

// Symbol Management API
export const symbolAPI = {
  async listSymbols(): Promise<Symbol[]> {
    const response = await symbolClient.get("/symbols")
    return response.data.symbols
  },

  async getSelectedSymbols(): Promise<string[]> {
    const response = await symbolClient.get("/symbols/selected")
    return response.data.symbols
  },

  async selectSymbol(symbol: string, selected: boolean): Promise<void> {
    await symbolClient.post("/symbols/select", { symbol, selected })
  },

  async importSymbols(symbols: Symbol[]): Promise<{ created: number }> {
    const response = await symbolClient.post("/symbols/import", symbols)
    return response.data
  },

  async importNasdaqSymbols(): Promise<{
    exchange: string
    processed: number
    inserted: number
    updated: number
    skipped: number
    timestamp: string
  }> {
    const response = await symbolClient.post("/symbols/import/nasdaq", {
      source: "NASDAQ_OFFICIAL",
      instrumentType: "STOCK",
    })
    return response.data
  },
}

// Market Data API
export const marketDataAPI = {
  async getMarketData(symbol: string) {
    const response = await symbolClient.get(`/market-data/${symbol}`)
    return response.data
  },

  async fetchSymbolData(symbol: string) {
    const response = await symbolClient.post(`/fetch/${symbol}`)
    return response.data
  },

  async fetchAllData() {
    const response = await symbolClient.post("/fetch-all")
    return response.data
  },
}


// Data Analyzer API
export const analyzerAPI = {
  async getSignals(symbol: string): Promise<Signal[]> {
    const response = await analyzerClient.get(`/signals/${symbol}`)
    return response.data
  },

  async analyzeSymbol(symbol: string) {
    const response = await analyzerClient.post(`/analyze/${symbol}`)
    return response.data
  },

  async analyzeAll() {
    const response = await analyzerClient.post("/analyze-all")
    return response.data
  },
}

// Notifier API
export const notifierAPI = {
  async getNotifications() {
    const response = await notifierClient.get("/notifications")
    return response.data
  },
}

export default authClient
