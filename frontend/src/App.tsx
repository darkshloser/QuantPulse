/**
 * Main application component with routing and authentication.
 */

import { useState, useEffect, useCallback } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { SymbolList } from "./components/SymbolList";
import { SignalPanel } from "./components/SignalPanel";
import { Login } from "./components/Login";
import { Register } from "./components/Register";
import { Landing } from "./components/Landing";
import { Profile } from "./components/Profile";
import { Settings } from "./components/Settings";
import { AuthProvider, useAuth } from "./context/AuthContext";
import {
    ProtectedRoute,
    AdminRoute,
    UnAuthenticatedRoute,
} from "./components/ProtectedRoute";
import { symbolAPI, authAPI } from "./api/client";
import "./App.css";

function DashboardLayout({
    symbolRefreshKey = 0,
}: {
    symbolRefreshKey?: number;
}) {
    const { user, logout } = useAuth();
    const [selectedSymbols, setSelectedSymbols] = useState<Set<string>>(
        new Set(),
    );

    useEffect(() => {
        loadSelectedSymbols();
    }, []);

    const loadSelectedSymbols = async () => {
        try {
            const symbols = await symbolAPI.getSelectedSymbols();
            setSelectedSymbols(new Set(symbols));
        } catch (err) {
            console.error("Failed to load selected symbols:", err);
        }
    };

    const handleToggleSymbol = (symbol: string, selected: boolean) => {
        const newSelected = new Set(selectedSymbols);
        if (selected) {
            newSelected.add(symbol);
        } else {
            newSelected.delete(symbol);
        }
        setSelectedSymbols(newSelected);
    };

    const handleLogout = () => {
        authAPI.logout();
        logout();
        window.location.href = "/";
    };

    return (
        <div className="app">
            <header className="app-header">
                <div className="header-left">
                    <h1>QuantPulse</h1>
                    <p>Market Intelligence Platform</p>
                </div>
                <div className="header-right">
                    <span className="user-info">
                        Welcome, {user?.first_name || user?.username}
                    </span>
                    {user?.role === "ADMIN" && (
                        <>
                            <a href="/admin/profile" className="nav-link">
                                Profile
                            </a>
                            <a href="/admin/settings" className="nav-link">
                                Settings
                            </a>
                        </>
                    )}
                    <button onClick={handleLogout} className="btn-logout">
                        Logout
                    </button>
                </div>
            </header>

            <div className="app-layout">
                <SymbolList
                    selectedSymbols={selectedSymbols}
                    onToggle={handleToggleSymbol}
                    refreshKey={symbolRefreshKey}
                />
                <SignalPanel selectedSymbols={selectedSymbols} />
            </div>
        </div>
    );
}

function AppRouter() {
    const [symbolRefreshKey, setSymbolRefreshKey] = useState(0);
    const onSymbolsImported = useCallback(
        () => setSymbolRefreshKey((k) => k + 1),
        [],
    );

    return (
        <BrowserRouter>
            <Routes>
                {/* Public Routes */}
                <Route
                    path="/"
                    element={
                        <UnAuthenticatedRoute>
                            <Landing />
                        </UnAuthenticatedRoute>
                    }
                />
                <Route
                    path="/login"
                    element={
                        <UnAuthenticatedRoute>
                            <Login />
                        </UnAuthenticatedRoute>
                    }
                />
                <Route
                    path="/register"
                    element={
                        <UnAuthenticatedRoute>
                            <Register />
                        </UnAuthenticatedRoute>
                    }
                />

                {/* Protected Routes - Main App */}
                <Route
                    path="/app"
                    element={
                        <ProtectedRoute>
                            <DashboardLayout
                                symbolRefreshKey={symbolRefreshKey}
                            />
                        </ProtectedRoute>
                    }
                />

                {/* Admin Routes */}
                <Route
                    path="/admin/profile"
                    element={
                        <AdminRoute>
                            <Profile />
                        </AdminRoute>
                    }
                />
                <Route
                    path="/admin/settings"
                    element={
                        <AdminRoute>
                            <Settings onSymbolsImported={onSymbolsImported} />
                        </AdminRoute>
                    }
                />
                <Route
                    path="/admin/dashboard"
                    element={
                        <AdminRoute>
                            <DashboardLayout
                                symbolRefreshKey={symbolRefreshKey}
                            />
                        </AdminRoute>
                    }
                />

                {/* Catch-all redirect */}
                <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
        </BrowserRouter>
    );
}

function App() {
    return (
        <AuthProvider>
            <AppRouter />
        </AuthProvider>
    );
}

export default App;
