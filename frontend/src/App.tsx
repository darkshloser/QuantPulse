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
import { AppHeader } from "./components/AppHeader";
import { AuthProvider } from "./context/AuthContext";
import {
    ProtectedRoute,
    AdminRoute,
    UnAuthenticatedRoute,
} from "./components/ProtectedRoute";
import { symbolAPI } from "./api/client";
import "./App.css";

function DashboardLayout({
    symbolRefreshKey = 0,
}: {
    symbolRefreshKey?: number;
}) {
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

    const handleRemoveSymbol = async (symbol: string) => {
        try {
            await symbolAPI.selectSymbol(symbol, false);
            handleToggleSymbol(symbol, false);
        } catch (err) {
            console.error("Failed to remove symbol:", err);
        }
    };

    return (
        <div className="app">
            <AppHeader />

            <div className="app-layout">
                <SymbolList
                    selectedSymbols={selectedSymbols}
                    onToggle={handleToggleSymbol}
                    refreshKey={symbolRefreshKey}
                />
                <SignalPanel selectedSymbols={selectedSymbols} onRemoveSymbol={handleRemoveSymbol} />
            </div>
            <div className="app-footer"></div>
            <p>&copy; 2024 QuantPulse. All rights reserved.</p>
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

                {/* Profile - available to all authenticated users */}
                <Route
                    path="/profile"
                    element={
                        <ProtectedRoute>
                            <Profile />
                        </ProtectedRoute>
                    }
                />

                {/* Admin Routes */}
                <Route
                    path="/admin/profile"
                    element={
                        <ProtectedRoute>
                            <Profile />
                        </ProtectedRoute>
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
