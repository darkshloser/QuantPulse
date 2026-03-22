/**
 * Modal for selecting and assigning indicators to a symbol.
 */

import React, { useState, useEffect } from "react";
import { Indicator, UserSymbolIndicator } from "../types";
import { analyzerAPI } from "../api/client";
import "./IndicatorModal.css";

interface IndicatorModalProps {
    symbol: string;
    assignedIndicators: UserSymbolIndicator[];
    onClose: () => void;
    onApply: () => void;
}

export const IndicatorModal: React.FC<IndicatorModalProps> = ({
    symbol,
    assignedIndicators,
    onClose,
    onApply,
}) => {
    const [allIndicators, setAllIndicators] = useState<Indicator[]>([]);
    const [selectedIds, setSelectedIds] = useState<Set<number>>(new Set());
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        loadIndicators();
    }, []);

    useEffect(() => {
        setSelectedIds(new Set(assignedIndicators.map((a) => a.indicator_id)));
    }, [assignedIndicators]);

    const loadIndicators = async () => {
        try {
            const data = await analyzerAPI.getIndicators();
            setAllIndicators(data.indicators);
        } catch (err) {
            setError("Failed to load indicators");
        } finally {
            setLoading(false);
        }
    };

    const toggleIndicator = (id: number) => {
        const next = new Set(selectedIds);
        if (next.has(id)) {
            next.delete(id);
        } else {
            next.add(id);
        }
        setSelectedIds(next);
    };

    const handleApply = async () => {
        setSaving(true);
        setError(null);

        try {
            const currentAssignedIds = new Set(
                assignedIndicators.map((a) => a.indicator_id),
            );

            // Assign newly selected
            for (const id of selectedIds) {
                if (!currentAssignedIds.has(id)) {
                    await analyzerAPI.assignIndicator(symbol, id);
                }
            }

            // Remove unselected
            for (const id of currentAssignedIds) {
                if (!selectedIds.has(id)) {
                    await analyzerAPI.removeIndicator(symbol, id);
                }
            }

            onApply();
        } catch (err) {
            setError("Failed to save indicator assignments");
        } finally {
            setSaving(false);
        }
    };

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div
                className="modal-content"
                onClick={(e) => e.stopPropagation()}
            >
                <div className="modal-header">
                    <h3>Assign Indicators to {symbol}</h3>
                    <button className="modal-close-btn" onClick={onClose}>
                        &times;
                    </button>
                </div>

                <div className="modal-body">
                    {error && <div className="modal-error">{error}</div>}

                    {loading ? (
                        <p className="modal-loading">Loading indicators...</p>
                    ) : allIndicators.length === 0 ? (
                        <p className="modal-empty">
                            No indicators available. Indicators will be added
                            when market data retrieval is implemented.
                        </p>
                    ) : (
                        <div className="indicator-list">
                            {allIndicators.map((indicator) => (
                                <label
                                    key={indicator.id}
                                    className={`indicator-option ${selectedIds.has(indicator.id) ? "selected" : ""}`}
                                >
                                    <input
                                        type="checkbox"
                                        checked={selectedIds.has(indicator.id)}
                                        onChange={() =>
                                            toggleIndicator(indicator.id)
                                        }
                                    />
                                    <div className="indicator-info">
                                        <span className="indicator-name">
                                            {indicator.name}
                                        </span>
                                        {indicator.description && (
                                            <span className="indicator-desc">
                                                {indicator.description}
                                            </span>
                                        )}
                                    </div>
                                </label>
                            ))}
                        </div>
                    )}
                </div>

                <div className="modal-footer">
                    <button
                        className="btn btn-secondary"
                        onClick={onClose}
                        disabled={saving}
                    >
                        Cancel
                    </button>
                    <button
                        className="btn btn-primary"
                        onClick={handleApply}
                        disabled={saving || loading}
                    >
                        {saving ? "Saving..." : "Apply"}
                    </button>
                </div>
            </div>
        </div>
    );
};
