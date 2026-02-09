/**
 * Admin settings page component.
 */

import { useState, useEffect } from "react"
import { authAPI, symbolAPI } from "../api/client"
import { User } from "../types"
import "./Settings.css"

type SettingsTab = "user-management" | "pending-approvals" | "symbol-management"

export function Settings() {
  const [activeTab, setActiveTab] = useState<SettingsTab>("pending-approvals")
  const [users, setUsers] = useState<User[]>([])
  const [pendingUsers, setPendingUsers] = useState<User[]>([])
  const [error, setError] = useState("")
  const [success, setSuccess] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [isImporting, setIsImporting] = useState(false)

  useEffect(() => {
    if (activeTab === "user-management") {
      loadUsers()
    } else if (activeTab === "pending-approvals") {
      loadPendingUsers()
    }
  }, [activeTab])

  const loadUsers = async () => {
    setIsLoading(true)
    try {
      const data = await authAPI.listUsers()
      setUsers(data)
      setError("")
    } catch (err: any) {
      setError("Failed to load users")
      console.error(err)
    } finally {
      setIsLoading(false)
    }
  }

  const loadPendingUsers = async () => {
    setIsLoading(true)
    try {
      const data = await authAPI.getPendingUsers()
      setPendingUsers(data)
      setError("")
    } catch (err: any) {
      setError("Failed to load pending users")
      console.error(err)
    } finally {
      setIsLoading(false)
    }
  }

  const handleApproveUser = async (userId: number) => {
    try {
      await authAPI.approveUser(userId)
      setSuccess("User approved successfully")
      setPendingUsers(pendingUsers.filter((u) => u.id !== userId))
      setError("")
    } catch (err: any) {
      setError("Failed to approve user")
      console.error(err)
    }
  }

  const handleRejectUser = async (userId: number) => {
    try {
      await authAPI.rejectUser(userId)
      setSuccess("User rejected successfully")
      setPendingUsers(pendingUsers.filter((u) => u.id !== userId))
      setError("")
    } catch (err: any) {
      setError("Failed to reject user")
      console.error(err)
    }
  }

  const handleDeleteUser = async (userId: number) => {
    if (!window.confirm("Are you sure you want to deactivate this user?")) {
      return
    }

    try {
      await authAPI.deleteUser(userId)
      setSuccess("User deactivated successfully")
      setUsers(users.filter((u) => u.id !== userId))
      setError("")
    } catch (err: any) {
      setError("Failed to delete user")
      console.error(err)
    }
  }

  const handleImportNasdaq = async () => {
    if (!window.confirm("This will import all NASDAQ symbols. Continue?")) {
      return
    }

    setIsImporting(true)
    try {
      const result = await symbolAPI.importNasdaqSymbols()
      setSuccess(
        `NASDAQ import complete: ${result.inserted} inserted, ${result.updated} updated`
      )
      setError("")
    } catch (err: any) {
      setError("Failed to import NASDAQ symbols")
      console.error(err)
    } finally {
      setIsImporting(false)
    }
  }

  return (
    <div className="settings-container">
      <h1>Settings</h1>

      <div className="settings-tabs">
        <button
          className={`tab ${activeTab === "pending-approvals" ? "active" : ""}`}
          onClick={() => setActiveTab("pending-approvals")}
        >
          Pending Approvals
        </button>
        <button
          className={`tab ${activeTab === "user-management" ? "active" : ""}`}
          onClick={() => setActiveTab("user-management")}
        >
          User Management
        </button>
        <button
          className={`tab ${activeTab === "symbol-management" ? "active" : ""}`}
          onClick={() => setActiveTab("symbol-management")}
        >
          Symbol Management
        </button>
      </div>

      <div className="settings-content">
        {error && <div className="error-message">{error}</div>}
        {success && <div className="success-message">{success}</div>}

        {activeTab === "pending-approvals" && (
          <div className="pending-approvals">
            <h2>Pending User Approvals</h2>
            {isLoading ? (
              <p>Loading...</p>
            ) : pendingUsers.length === 0 ? (
              <p>No pending approvals</p>
            ) : (
              <div className="users-list">
                {pendingUsers.map((user) => (
                  <div key={user.id} className="user-item">
                    <div className="user-info">
                      <p className="user-email">{user.email}</p>
                      <p className="user-username">@{user.username}</p>
                      <p className="user-date">
                        Registered:{" "}
                        {new Date(user.created_at).toLocaleDateString()}
                      </p>
                    </div>
                    <div className="user-actions">
                      <button
                        className="btn btn-success"
                        onClick={() => handleApproveUser(user.id)}
                      >
                        Approve
                      </button>
                      <button
                        className="btn btn-danger"
                        onClick={() => handleRejectUser(user.id)}
                      >
                        Reject
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === "user-management" && (
          <div className="user-management">
            <h2>All Users</h2>
            {isLoading ? (
              <p>Loading...</p>
            ) : users.length === 0 ? (
              <p>No users found</p>
            ) : (
              <div className="users-table">
                <table>
                  <thead>
                    <tr>
                      <th>Username</th>
                      <th>Email</th>
                      <th>Role</th>
                      <th>Status</th>
                      <th>Registered</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {users.map((user) => (
                      <tr key={user.id}>
                        <td>{user.username}</td>
                        <td>{user.email}</td>
                        <td>
                          <span className="badge" data-role={user.role}>
                            {user.role}
                          </span>
                        </td>
                        <td>
                          <span className="badge" data-status={user.approval_status}>
                            {user.approval_status}
                          </span>
                        </td>
                        <td>
                          {new Date(user.created_at).toLocaleDateString()}
                        </td>
                        <td>
                          {user.is_active && (
                            <button
                              className="btn btn-sm btn-danger"
                              onClick={() => handleDeleteUser(user.id)}
                            >
                              Deactivate
                            </button>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {activeTab === "symbol-management" && (
          <div className="symbol-management">
            <h2>Symbol Management</h2>
            <div className="symbol-operations">
              <div className="operation">
                <h3>Import NASDAQ Symbols</h3>
                <p>
                  Download and import all NASDAQ-listed company shares. This
                  will create or update symbols in the database.
                </p>
                <button
                  className="btn btn-primary"
                  onClick={handleImportNasdaq}
                  disabled={isImporting}
                >
                  {isImporting ? "Importing..." : "Import NASDAQ Symbols"}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
