/**
 * Shared type definitions for QuantPulse frontend.
 */

export enum InstrumentType {
  STOCK = "STOCK",
  METAL = "METAL",
}

export enum UserRole {
  ADMIN = "ADMIN",
  USER = "USER",
}

export enum ApprovalStatus {
  PENDING = "PENDING",
  APPROVED = "APPROVED",
  REJECTED = "REJECTED",
}

export interface Symbol {
  symbol: string
  yahoo_symbol: string
  company_name?: string
  instrument_type: InstrumentType
  exchange?: string
  currency?: string
  is_active: boolean
}

export interface User {
  id: number
  username: string
  email: string
  role: UserRole
  approval_status: ApprovalStatus
  first_name?: string
  last_name?: string
  profile_picture_url?: string
  is_active: boolean
  created_at: string
  last_login?: string
}

export interface AuthToken {
  access_token: string
  refresh_token?: string
  token_type: string
  user: User
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
