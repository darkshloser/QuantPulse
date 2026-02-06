/**
 * Shared type definitions for QuantPulse frontend.
 */

export enum InstrumentType {
  STOCK = "STOCK",
  METAL = "METAL",
}

export interface Symbol {
  symbol: string
  yahoo_symbol: string
  instrument_type: InstrumentType
  exchange?: string
  currency?: string
  is_active: boolean
}

export interface Signal {
  symbol: string
  signal_type: string
  timestamp: string
  confidence: number
  explanation: string
  indicators_passed: string[]
}

export interface MarketData {
  symbol: string
  date: string
  open_price: number
  high: number
  low: number
  close: number
  volume: number
}
