/**
 * Authentication context and hooks for managing user state.
 */

import { createContext, useContext, useState, useEffect, ReactNode } from "react"
import { User, UserRole } from "../types"

interface AuthContextType {
  user: User | null
  isAuthenticated: boolean
  isAdmin: boolean
  isLoading: boolean
  logout: () => void
  setUser: (user: User | null) => void
  refreshUser: () => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // Load user from localStorage on mount
    const storedUser = localStorage.getItem("user")
    if (storedUser) {
      try {
        setUser(JSON.parse(storedUser))
      } catch (e) {
        console.error("Failed to parse stored user:", e)
        localStorage.removeItem("user")
      }
    }
    setIsLoading(false)
  }, [])

  const logout = () => {
    localStorage.removeItem("access_token")
    localStorage.removeItem("refresh_token")
    localStorage.removeItem("user")
    setUser(null)
  }

  const refreshUser = () => {
    // Reload user from localStorage
    const storedUser = localStorage.getItem("user")
    if (storedUser) {
      try {
        setUser(JSON.parse(storedUser))
      } catch (e) {
        console.error("Failed to parse stored user:", e)
        localStorage.removeItem("user")
        setUser(null)
      }
    } else {
      setUser(null)
    }
  }

  const value: AuthContextType = {
    user,
    isAuthenticated: user !== null,
    isAdmin: user?.role === UserRole.ADMIN,
    isLoading,
    logout,
    setUser,
    refreshUser,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider")
  }
  return context
}
