/**
 * Login page component.
 */

import { useState } from "react"
import { useNavigate, Link } from "react-router-dom"
import { authAPI } from "../api/client"
import { useAuth } from "../context/AuthContext"
import "./Auth.css"

export function Login() {
  const navigate = useNavigate()
  const { refreshUser } = useAuth()
  const [usernameOrEmail, setUsernameOrEmail] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState("")
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("")
    setIsLoading(true)

    try {
      console.log("Attempting login with:", usernameOrEmail)
      const response = await authAPI.login(usernameOrEmail, password)
      console.log("Login response:", response)

      // Update auth context with the returned user
      console.log("Refreshing user context...")
      refreshUser()

      // Small delay to ensure context updates before navigation
      setTimeout(() => {
        console.log("Navigating based on role:", response.user.role)
        // Redirect based on role
        if (response.user.role === "ADMIN") {
          console.log("Redirecting to /admin/dashboard")
          navigate("/admin/dashboard")
        } else {
          console.log("Redirecting to /app")
          navigate("/app")
        }
      }, 100)
    } catch (err: any) {
      console.error("Login error:", err)
      const message =
        err.response?.data?.detail ||
        err.message ||
        "Login failed. Please try again."
      setError(message)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-header">
          <h1>QuantPulse</h1>
          <p>Market Intelligence Platform</p>
        </div>

        <form onSubmit={handleSubmit} className="auth-form">
          <h2>Login</h2>

          {error && <div className="error-message">{error}</div>}

          <div className="form-group">
            <label htmlFor="username">Username or Email</label>
            <input
              id="username"
              type="text"
              value={usernameOrEmail}
              onChange={(e) => setUsernameOrEmail(e.target.value)}
              placeholder="Enter your username or email"
              required
              disabled={isLoading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter your password"
              required
              disabled={isLoading}
            />
          </div>

          <button
            type="submit"
            className="btn btn-primary"
            disabled={isLoading}
          >
            {isLoading ? "Logging in..." : "Login"}
          </button>
        </form>

        <div className="auth-footer">
          <p>
            Don't have an account?{" "}
            <Link to="/register" className="link">
              Register here
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}
