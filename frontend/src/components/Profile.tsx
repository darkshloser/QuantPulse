/**
 * Admin profile page component.
 */

import { useState, useEffect } from "react"
import { useAuth } from "../context/AuthContext"
import { authAPI } from "../api/client"
import { User } from "../types"
import "./Profile.css"

export function Profile() {
  const { user } = useAuth()
  const [firstName, setFirstName] = useState(user?.first_name || "")
  const [lastName, setLastName] = useState(user?.last_name || "")
  const [error, setError] = useState("")
  const [success, setSuccess] = useState("")
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("")
    setSuccess("")
    setIsLoading(true)

    try {
      await authAPI.updateProfile(firstName, lastName)
      setSuccess("Profile updated successfully!")

      // Update localStorage
      const updatedUser = {
        ...user!,
        first_name: firstName,
        last_name: lastName,
      }
      localStorage.setItem("user", JSON.stringify(updatedUser))
    } catch (err: any) {
      const message =
        err.response?.data?.detail ||
        err.message ||
        "Failed to update profile"
      setError(message)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="profile-container">
      <div className="profile-card">
        <h1>Profile</h1>

        <div className="profile-info">
          <div className="info-group">
            <label>Username</label>
            <p>{user?.username}</p>
          </div>

          <div className="info-group">
            <label>Email</label>
            <p>{user?.email}</p>
          </div>

          <div className="info-group">
            <label>Role</label>
            <p>
              <span className="badge badge-admin">{user?.role}</span>
            </p>
          </div>

          <div className="info-group">
            <label>Member Since</label>
            <p>{new Date(user?.created_at || "").toLocaleDateString()}</p>
          </div>

          {user?.last_login && (
            <div className="info-group">
              <label>Last Login</label>
              <p>{new Date(user.last_login).toLocaleString()}</p>
            </div>
          )}
        </div>

        <form onSubmit={handleSubmit} className="profile-form">
          <h2>Edit Personal Information</h2>

          {error && <div className="error-message">{error}</div>}
          {success && <div className="success-message">{success}</div>}

          <div className="form-group">
            <label htmlFor="firstName">First Name</label>
            <input
              id="firstName"
              type="text"
              value={firstName}
              onChange={(e) => setFirstName(e.target.value)}
              placeholder="Enter first name"
              disabled={isLoading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="lastName">Last Name</label>
            <input
              id="lastName"
              type="text"
              value={lastName}
              onChange={(e) => setLastName(e.target.value)}
              placeholder="Enter last name"
              disabled={isLoading}
            />
          </div>

          <button
            type="submit"
            className="btn btn-primary"
            disabled={isLoading}
          >
            {isLoading ? "Saving..." : "Save Changes"}
          </button>
        </form>
      </div>
    </div>
  )
}
