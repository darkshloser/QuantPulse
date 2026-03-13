/**
 * Shared header component for authenticated pages.
 */

import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { authAPI } from "../api/client";

export function AppHeader() {
    const { user, isAuthenticated, logout } = useAuth();

    const handleLogout = () => {
        authAPI.logout();
        logout();
        window.location.href = "/";
    };

    return (
        <header className="app-header">
            <div className="header-left">
                {isAuthenticated ? (
                    <Link to="/app" className="header-title-link">
                        <h1>QuantPulse</h1>
                        <p>Market Intelligence Platform</p>
                    </Link>
                ) : (
                    <>
                        <h1>QuantPulse</h1>
                        <p>Market Intelligence Platform</p>
                    </>
                )}
            </div>
            <div className="header-right">
                <span className="user-info">
                    Welcome, {user?.first_name || user?.username}
                </span>
                {user?.role === "ADMIN" && (
                    <>
                        <Link to="/admin/profile" className="nav-link">
                            Profile
                        </Link>
                        <Link to="/admin/settings" className="nav-link">
                            Settings
                        </Link>
                    </>
                )}
                <button onClick={handleLogout} className="btn-logout">
                    Logout
                </button>
            </div>
        </header>
    );
}
