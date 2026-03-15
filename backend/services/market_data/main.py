"""Market Data Retriever Service - fetches and maintains historical price data."""

import logging
from datetime import datetime, timedelta
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from shared.config import settings
from shared.database import get_db, engine, Base
from shared.models import Symbol, SelectedSymbol, MarketData, MarketDataSchema, User
from shared.events import event_bus, Event, EventType
from shared.logging_config import logger as app_logger
from shared.auth import get_current_user

# Create tables (safe to call multiple times)
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    app_logger.warning(f"Error creating tables (may already exist): {e}")

app = FastAPI(
    title="Market Data Retriever Service",
    version="1.0.0",
    description="Fetches and maintains historical price data",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/market-data/{symbol}")
async def get_market_data(
    symbol: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get historical market data for a symbol."""
    data = db.query(MarketData).filter(MarketData.symbol == symbol).order_by(
        MarketData.date.desc()
    ).limit(90).all()

    if not data:
        raise HTTPException(status_code=404, detail="No market data found")

    return [MarketDataSchema.from_orm(d) for d in data]


@app.post("/fetch/{symbol}")
async def fetch_symbol_data(
    symbol: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Manually trigger data fetch for a symbol."""
    app_logger.info(f"Fetching market data for {symbol} (user {current_user.id})")

    # Check if symbol is in current user's selected symbols
    selected = db.query(SelectedSymbol).filter(
        SelectedSymbol.user_id == current_user.id,
        SelectedSymbol.symbol == symbol,
    ).first()
    if not selected:
        raise HTTPException(status_code=400, detail="Symbol not selected")

    # TODO: Implement Yahoo Finance fetching
    # TODO: Implement idempotent writes (check existing dates)
    # TODO: Publish MARKET_DATA_UPDATED event

    return {"symbol": symbol, "status": "fetching"}


@app.post("/fetch-all")
async def fetch_all_selected_symbols(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Fetch market data for all of the current user's selected symbols."""
    selected = db.query(SelectedSymbol).filter(
        SelectedSymbol.user_id == current_user.id
    ).all()
    app_logger.info(f"Fetching data for {len(selected)} symbols (user {current_user.id})")

    results = []
    for sel_sym in selected:
        # TODO: Batch fetch from Yahoo Finance
        results.append({"symbol": sel_sym.symbol, "status": "queued"})

    return {"total": len(results), "results": results}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8002,
        log_config=None,
    )
