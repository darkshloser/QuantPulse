/**
 * Main panel: Selected symbols, indicators & analysis, and recent signals.
 */

import React, { useState, useEffect, useCallback } from "react";
import { Signal, UserSymbolIndicator } from "../types";
import { analyzerAPI, notifierAPI } from "../api/client";
import { IndicatorModal } from "./IndicatorModal";
import "./SignalPanel.css";

interface SignalPanelProps {
    selectedSymbols: Set<string>;
    onRemoveSymbol?: (symbol: string) => void;
}

export const SignalPanel: React.FC<SignalPanelProps> = ({
    selectedSymbols,
    onRemoveSymbol,
}) => {
    const [activeSymbol, setActiveSymbol] = useState<string | null>(null);
    const [assignedIndicators, setAssignedIndicators] = useState<
        UserSymbolIndicator[]
    >([]);
    const [signals, setSignals] = useState<Signal[]>([]);
    const [showIndicatorModal, setShowIndicatorModal] = useState(false);
    const [error, setError] = useState<string | null>(null);

    // Auto-select first symbol when selected symbols change
    useEffect(() => {
        const symbolsArray = Array.from(selectedSymbols);
        if (symbolsArray.length > 0) {
            if (!activeSymbol || !selectedSymbols.has(activeSymbol)) {
                setActiveSymbol(symbolsArray[0]);
            }
        } else {
            setActiveSymbol(null);
        }
    }, [selectedSymbols]);

    // Load indicators and signals when active symbol changes
    useEffect(() => {
        if (activeSymbol) {
            loadAssignedIndicators(activeSymbol);
            loadSignals(activeSymbol);
        } else {
            setAssignedIndicators([]);
            setSignals([]);
        }
    }, [activeSymbol]);

    // Poll signals every 60 seconds
    useEffect(() => {
        if (!activeSymbol) return;
        const interval = setInterval(
            () => loadSignals(activeSymbol),
            60000,
        );
        return () => clearInterval(interval);
    }, [activeSymbol]);

    const loadAssignedIndicators = async (symbol: string) => {
        try {
            const data = await analyzerAPI.getAssignedIndicators(symbol);
            setAssignedIndicators(data.indicators);
        } catch (err) {
            setError("Failed to load indicators");
        }
    };

    const loadSignals = async (symbol: string) => {
        try {
            const notifications = await notifierAPI.getNotifications(symbol);
            setSignals(notifications);
        } catch (err) {
            setError("Failed to load signals");
        }
    };

    const handleRemoveIndicator = async (indicatorId: number) => {
        if (!activeSymbol) return;
        try {
            await analyzerAPI.removeIndicator(activeSymbol, indicatorId);
            setAssignedIndicators(
                assignedIndicators.filter(
                    (a) => a.indicator_id !== indicatorId,
                ),
            );
        } catch (err) {
            setError("Failed to remove indicator");
        }
    };

    const handleIndicatorModalApply = useCallback(() => {
        setShowIndicatorModal(false);
        if (activeSymbol) {
            loadAssignedIndicators(activeSymbol);
        }
    }, [activeSymbol]);

    const renderResult = (result: boolean | null) => {
        if (result === true)
            return <span className="result-true">&#10003;</span>;
        if (result === false)
            return <span className="result-false">&#10007;</span>;
        return <span className="result-null">&mdash;</span>;
    };

    return (
        <div className="signal-panel">
            {error && (
                <div className="error">
                    {error}
                    <button
                        className="error-dismiss"
                        onClick={() => setError(null)}
                    >
                        &times;
                    </button>
                </div>
            )}

            {/* Section 1: Selected Symbols */}
            <div className="panel-section">
                <h3>Selected Symbols ({selectedSymbols.size})</h3>
                <div className="symbols-grid">
                    {selectedSymbols.size === 0 ? (
                        <p className="empty">No symbols selected</p>
                    ) : (
                        Array.from(selectedSymbols).map((symbol) => (
                            <div
                                key={symbol}
                                className={`symbol-badge ${activeSymbol === symbol ? "active" : ""}`}
                                onClick={() => setActiveSymbol(symbol)}
                            >
                                {symbol}
                                {onRemoveSymbol && (
                                    <button
                                        className="badge-remove-btn"
                                        onClick={(e) => {
                                            e.stopPropagation();
                                            onRemoveSymbol(symbol);
                                        }}
                                        title="Remove"
                                    >
                                        &times;
                                    </button>
                                )}
                            </div>
                        ))
                    )}
                </div>
            </div>

            {/* Section 2: Indicators & Analysis */}
            <div className="panel-section">
                <div className="section-header">
                    <h3>Indicators &amp; Analysis</h3>
                    <div className="section-actions">
                        <button
                            className="btn btn-sm btn-primary"
                            onClick={() => setShowIndicatorModal(true)}
                            disabled={!activeSymbol}
                        >
                            Indicators
                        </button>
                        <button
                            className="btn btn-sm btn-secondary"
                            disabled
                            title="Coming soon"
                        >
                            Editor
                        </button>
                    </div>
                </div>

                {!activeSymbol ? (
                    <p className="empty">Select a symbol to manage indicators</p>
                ) : assignedIndicators.length === 0 ? (
                    <p className="empty">
                        No indicators assigned to {activeSymbol}
                    </p>
                ) : (
                    <div className="indicator-table-wrapper">
                        <table className="indicator-table">
                            <thead>
                                <tr>
                                    <th>Indicator</th>
                                    <th>Result</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {assignedIndicators.map((indicator) => (
                                    <tr key={indicator.id}>
                                        <td className="indicator-name-cell">
                                            {indicator.indicator_name}
                                        </td>
                                        <td className="indicator-result-cell">
                                            {renderResult(indicator.result)}
                                        </td>
                                        <td className="indicator-actions-cell">
                                            <button
                                                className="btn btn-xs btn-danger"
                                                onClick={() =>
                                                    handleRemoveIndicator(
                                                        indicator.indicator_id,
                                                    )
                                                }
                                            >
                                                Remove
                                            </button>
                                            <button
                                                className="btn btn-xs btn-secondary"
                                                disabled
                                                title="Coming soon"
                                            >
                                                Edit
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>

            {/* Section 3: Recent Signals */}
            <div className="panel-section">
                <h3>Recent Signals</h3>
                {!activeSymbol ? (
                    <p className="empty">Select a symbol to view signals</p>
                ) : signals.length === 0 ? (
                    <p className="empty">No signals for {activeSymbol}</p>
                ) : (
                    <div className="signals-list">
                        {signals.map((signal, idx) => (
                            <div key={idx} className="signal-item">
                                <div className="signal-header">
                                    <span className="signal-type">
                                        {signal.signal_type}
                                    </span>
                                    <span className="signal-time">
                                        {new Date(
                                            signal.timestamp,
                                        ).toLocaleString()}
                                    </span>
                                </div>
                                <p className="signal-explanation">
                                    {signal.explanation}
                                </p>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            {/* Indicator Selection Modal */}
            {showIndicatorModal && activeSymbol && (
                <IndicatorModal
                    symbol={activeSymbol}
                    assignedIndicators={assignedIndicators}
                    onClose={() => setShowIndicatorModal(false)}
                    onApply={handleIndicatorModalApply}
                />
            )}
        </div>
    );
};
