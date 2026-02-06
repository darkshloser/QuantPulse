"""Data Analyzer Service - applies indicators and evaluates trigger criteria."""

import logging
from datetime import datetime
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from shared.config import settings
from shared.database import get_db, engine, Base
from shared.models import Symbol, SelectedSymbol, MarketData, SignalResult, SignalSchema
from shared.events import event_bus, Event, EventType
from shared.logging_config import logger as app_logger

# Create tables (safe to call multiple times)
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    app_logger.warning(f"Error creating tables (may already exist): {e}")

app = FastAPI(
    title="Data Analyzer Service",
    version="1.0.0",
    description="Applies indicators and evaluates signals",
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/signals/{symbol}")
async def get_signals_for_symbol(symbol: str, db: Session = Depends(get_db)):
    """Get recent signals for a symbol."""
    signals = db.query(SignalResult).filter(
        SignalResult.symbol == symbol
    ).order_by(SignalResult.timestamp.desc()).limit(10).all()

    return [SignalSchema.from_orm(s) for s in signals]


@app.post("/analyze/{symbol}")
async def analyze_symbol(symbol: str, db: Session = Depends(get_db)):
    """Analyze a single symbol and generate signals."""
    # Verify symbol exists and is selected
    selected = db.query(SelectedSymbol).filter(
        SelectedSymbol.symbol == symbol
    ).first()
    if not selected:
        return {"symbol": symbol, "status": "not_selected"}

    # TODO: Fetch market data for symbol
    # TODO: Apply technical indicators (RSI, ATR, etc.)
    # TODO: Evaluate trigger criteria
    # TODO: Create SignalResult if criteria met
    # TODO: Publish SIGNAL_TRIGGERED event

    app_logger.info(f"Analyzed symbol: {symbol}")
    return {"symbol": symbol, "status": "analyzed"}


@app.post("/analyze-all")
async def analyze_all_symbols(db: Session = Depends(get_db)):
    """Run daily analysis on all selected symbols."""
    selected = db.query(SelectedSymbol).all()
    app_logger.info(f"Starting analysis for {len(selected)} symbols")

    results = []
    for sel_sym in selected:
        # TODO: Analyze each symbol
        results.append({"symbol": sel_sym.symbol, "status": "analyzed"})

    # Publish analysis completion event
    event = Event(
        EventType.ANALYSIS_COMPLETED,
        {"total_symbols": len(selected), "timestamp": datetime.utcnow().isoformat()},
    )
    event_bus.publish(event)

    return {"total": len(results), "results": results}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8003,
        log_config=None,
    )
