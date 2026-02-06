"""Notifier Service - delivers alerts via Slack and GUI."""

import logging
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from shared.config import settings
from shared.database import get_db, engine, Base
from shared.models import SignalResult
from shared.logging_config import logger as app_logger

# Create tables (safe to call multiple times)
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    app_logger.warning(f"Error creating tables (may already exist): {e}")

app = FastAPI(
    title="Notifier Service",
    version="1.0.0",
    description="Delivers alerts via Slack and GUI",
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/notify/slack/{signal_id}")
async def send_slack_notification(signal_id: str, db: Session = Depends(get_db)):
    """Send Slack notification for a signal."""
    signal = db.query(SignalResult).filter(SignalResult.id == signal_id).first()
    if not signal:
        return {"error": "Signal not found"}

    # TODO: Format message with symbol, signal type, confidence, explanation
    # TODO: Include Yahoo Finance link
    # TODO: Check if it's a working day
    # TODO: Avoid duplicate notifications (one per symbol per run)
    # TODO: Send to Slack webhook

    app_logger.info(f"Slack notification sent for signal: {signal_id}")
    signal.notified = True
    db.commit()

    return {"signal_id": signal_id, "status": "sent"}


@app.post("/notify/gui/{signal_id}")
async def send_gui_notification(signal_id: str, db: Session = Depends(get_db)):
    """Send GUI notification for a signal."""
    signal = db.query(SignalResult).filter(SignalResult.id == signal_id).first()
    if not signal:
        return {"error": "Signal not found"}

    # TODO: Format message for GUI
    # TODO: Send via WebSocket to connected clients
    # TODO: Highlight symbol in selected symbols list

    app_logger.info(f"GUI notification sent for signal: {signal_id}")
    return {"signal_id": signal_id, "status": "sent"}


@app.get("/notifications")
async def get_recent_notifications(db: Session = Depends(get_db)):
    """Get recent notifications (for GUI)."""
    signals = db.query(SignalResult).filter(
        SignalResult.notified == True
    ).order_by(SignalResult.notified_at.desc()).limit(20).all()

    return [
        {
            "symbol": s.symbol,
            "signal_type": s.signal_type,
            "confidence": s.confidence,
            "explanation": s.explanation,
            "timestamp": s.notified_at,
        }
        for s in signals
    ]


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8004,
        log_config=None,
    )
