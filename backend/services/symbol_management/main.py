"""Symbol Management Service - manages financial instruments universe."""

import logging
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from shared.config import settings
from shared.database import get_db, engine, Base
from shared.models import Symbol, SelectedSymbol, SymbolSchema, SymbolListResponse, SelectSymbolRequest, NasdaqImportRequest, ImportSummaryResponse, InstrumentType
from shared.events import event_bus, Event, EventType
from shared.logging_config import logger as app_logger
from shared.nasdaq_provider import get_nasdaq_symbols, NasdaqProviderError

# Create tables (safe to call multiple times)
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    app_logger.warning(f"Error creating tables (may already exist): {e}")

app = FastAPI(
    title="Symbol Management Service",
    version="1.0.0",
    description="Manages financial instruments universe",
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/symbols", response_model=SymbolListResponse)
async def list_symbols(db: Session = Depends(get_db)):
    """Get all available symbols."""
    symbols = db.query(Symbol).filter(Symbol.is_active == True).all()
    return SymbolListResponse(
        symbols=[SymbolSchema.from_orm(s) for s in symbols],
        total=len(symbols),
    )


@app.get("/symbols/selected")
async def get_selected_symbols(db: Session = Depends(get_db)):
    """Get user-selected symbols."""
    selected = db.query(SelectedSymbol).all()
    return {"symbols": [s.symbol for s in selected]}


@app.post("/symbols/select")
async def select_symbol(
    request: SelectSymbolRequest,
    db: Session = Depends(get_db),
):
    """Select or deselect a symbol."""
    # Verify symbol exists
    symbol = db.query(Symbol).filter(Symbol.symbol == request.symbol).first()
    if not symbol:
        raise HTTPException(status_code=404, detail="Symbol not found")

    if request.selected:
        # Add to selected symbols
        existing = db.query(SelectedSymbol).filter(
            SelectedSymbol.symbol == request.symbol
        ).first()
        if not existing:
            selected = SelectedSymbol(symbol=request.symbol)
            db.add(selected)
            db.commit()
            db.refresh(selected)

            # Publish event
            event = Event(
                EventType.SYMBOLS_SELECTED,
                {"symbol": request.symbol, "action": "selected"},
            )
            event_bus.publish(event)
            app_logger.info(f"Symbol selected: {request.symbol}")

    else:
        # Remove from selected symbols
        db.query(SelectedSymbol).filter(
            SelectedSymbol.symbol == request.symbol
        ).delete()
        db.commit()
        app_logger.info(f"Symbol deselected: {request.symbol}")

    return {"symbol": request.symbol, "selected": request.selected}


@app.post("/symbols/import")
async def import_symbols(symbols: list[SymbolSchema], db: Session = Depends(get_db)):
    """Import symbols (admin endpoint)."""
    created = 0
    for sym_data in symbols:
        existing = db.query(Symbol).filter(Symbol.symbol == sym_data.symbol).first()
        if not existing:
            symbol = Symbol(**sym_data.dict())
            db.add(symbol)
            created += 1

    db.commit()
    app_logger.info(f"Imported {created} new symbols")
    return {"created": created}


@app.post("/symbols/import/nasdaq", response_model=ImportSummaryResponse)
async def import_nasdaq_symbols(
    request: NasdaqImportRequest,
    db: Session = Depends(get_db),
):
    """
    Import NASDAQ-listed company shares (admin endpoint).

    TODO v1.1: Add API key or bearer token authentication.

    Downloads official NASDAQ symbol directory, filters for stocks only,
    and performs idempotent import (updates existing, no duplicates).

    Returns summary of import results: processed, inserted, updated, skipped.
    """
    app_logger.info("Starting NASDAQ symbol import: %s", request)

    # Fetch and filter NASDAQ symbols
    try:
        nasdaq_symbols = get_nasdaq_symbols()
    except NasdaqProviderError as e:
        app_logger.error("Failed to fetch NASDAQ symbols: %s", str(e))
        raise HTTPException(
            status_code=503,
            detail="Failed to fetch NASDAQ symbol directory after retries",
        )

    # Idempotent import with metrics
    metrics = {
        "processed": len(nasdaq_symbols),
        "inserted": 0,
        "updated": 0,
        "skipped": 0,
    }

    for nasdaq_sym in nasdaq_symbols:
        symbol = nasdaq_sym["symbol"]
        company_name = nasdaq_sym["company_name"]
        yahoo_symbol = nasdaq_sym["yahoo_symbol"]
        market_category = nasdaq_sym.get("market_category", "")
        financial_status = nasdaq_sym.get("financial_status", "")

        # Check if symbol exists
        existing = db.query(Symbol).filter(Symbol.symbol == symbol).first()

        if existing:
            # Update existing symbol
            existing.company_name = company_name
            existing.yahoo_symbol = yahoo_symbol
            existing.market_category = market_category
            existing.financial_status = financial_status
            existing.is_active = True
            db.add(existing)
            metrics["updated"] += 1
            app_logger.debug("Updated symbol: %s", symbol)

        else:
            # Insert new symbol
            new_symbol = Symbol(
                symbol=symbol,
                yahoo_symbol=yahoo_symbol,
                company_name=company_name,
                market_category=market_category,
                financial_status=financial_status,
                exchange="NASDAQ",
                currency="USD",
                instrument_type=InstrumentType.STOCK,
                is_active=True,
            )

            db.add(new_symbol)
            metrics["inserted"] += 1
            app_logger.debug("Inserted new symbol: %s (%s)", symbol, company_name)

    # Commit all changes
    db.commit()

    # Publish import event
    event = Event(
        EventType.SYMBOLS_IMPORTED,
        {
            "exchange": "NASDAQ",
            "count": metrics["inserted"],
            "inserted": metrics["inserted"],
            "updated": metrics["updated"],
        },
    )
    event_bus.publish(event)
    app_logger.info(
        "NASDAQ import completed: processed=%d, inserted=%d, updated=%d, skipped=%d",
        metrics["processed"],
        metrics["inserted"],
        metrics["updated"],
        metrics["skipped"],
    )

    # Return summary response
    return ImportSummaryResponse(
        exchange="NASDAQ",
        processed=metrics["processed"],
        inserted=metrics["inserted"],
        updated=metrics["updated"],
        skipped=metrics["skipped"],
        timestamp=datetime.utcnow(),
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        log_config=None,
    )
