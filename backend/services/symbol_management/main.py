"""Symbol Management Service - manages financial instruments universe."""

import logging
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import case
from sqlalchemy.orm import Session

from shared.config import settings
from shared.database import get_db, engine, Base
from shared.models import Symbol, SelectedSymbol, SymbolSchema, SymbolListResponse, SelectSymbolRequest, NasdaqImportRequest, ImportSummaryResponse, InstrumentType, User
from shared.events import event_bus, Event, EventType
from shared.logging_config import logger as app_logger
from shared.sec_provider import get_sec_symbols, SecProviderError
from shared.auth import get_admin_user

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

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Startup event: auto-import SEC symbols on service start
@app.on_event("startup")
async def startup_import_sec_symbols():
    """Auto-import SEC symbols when service starts (non-blocking)."""
    try:
        app_logger.info("Starting Symbol Management Service - initiating SEC symbol import on startup")

        # Get a database session
        db = next(get_db())

        try:
            # Fetch SEC symbols
            sec_symbols = get_sec_symbols()
            app_logger.info("Fetched %d SEC symbols", len(sec_symbols))

            # Idempotent import
            metrics = {
                "inserted": 0,
                "updated": 0,
            }

            for sec_sym in sec_symbols:
                symbol = sec_sym["symbol"]
                company_name = sec_sym["company_name"]
                yahoo_symbol = sec_sym["yahoo_symbol"]

                existing = db.query(Symbol).filter(Symbol.symbol == symbol).first()

                if existing:
                    existing.company_name = company_name
                    existing.yahoo_symbol = yahoo_symbol
                    existing.is_active = True
                    db.add(existing)
                    metrics["updated"] += 1
                else:
                    new_symbol = Symbol(
                        symbol=symbol,
                        yahoo_symbol=yahoo_symbol,
                        company_name=company_name,
                        exchange="SEC",
                        currency="USD",
                        instrument_type=InstrumentType.STOCK,
                        is_active=True,
                    )
                    db.add(new_symbol)
                    metrics["inserted"] += 1

            db.commit()

            # Publish startup import event
            event = Event(
                EventType.SYMBOLS_IMPORTED,
                {
                    "exchange": "SEC",
                    "count": metrics["inserted"],
                    "inserted": metrics["inserted"],
                    "updated": metrics["updated"],
                    "source": "startup",
                },
            )
            event_bus.publish(event)

            app_logger.info(
                "SEC startup import completed: inserted=%d, updated=%d (total: %d)",
                metrics["inserted"],
                metrics["updated"],
                len(sec_symbols),
            )

        except SecProviderError as e:
            app_logger.warning(
                "Failed to import SEC symbols on startup (service will continue): %s",
                str(e),
            )
        except Exception as e:
            app_logger.warning(
                "Unexpected error during SEC startup import (service will continue): %s",
                str(e),
            )
        finally:
            db.close()

    except Exception as e:
        app_logger.error(
            "Critical error in startup import event (this should not happen): %s",
            str(e),
        )


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/symbols", response_model=SymbolListResponse)
async def list_symbols(
    search: str | None = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    """Get available symbols with optional search filter and pagination."""
    query = db.query(Symbol).filter(Symbol.is_active == True)
    if search:
        upper_search = search.upper()
        pattern = f"%{upper_search}%"
        query = query.filter(
            (Symbol.symbol.ilike(pattern)) | (Symbol.company_name.ilike(pattern))
        )
        # Rank: exact symbol match first, then symbol prefix, then others
        rank = case(
            (Symbol.symbol.ilike(upper_search), 0),
            (Symbol.symbol.ilike(f"{upper_search}%"), 1),
            else_=2,
        )
        query = query.order_by(rank, Symbol.symbol)
    else:
        query = query.order_by(Symbol.symbol)
    total = query.count()
    symbols = query.offset(offset).limit(limit).all()
    return SymbolListResponse(
        symbols=[SymbolSchema.from_orm(s) for s in symbols],
        total=total,
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
async def import_symbols(
    symbols: list[SymbolSchema],
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
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


@app.post("/symbols/import/sec", response_model=ImportSummaryResponse)
async def import_sec_symbols(
    request: NasdaqImportRequest,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    """
    Import SEC-listed company shares (admin endpoint).

    Downloads official SEC company tickers JSON file, and performs idempotent
    import (updates existing, no duplicates).

    Returns summary of import results: processed, inserted, updated, skipped.
    """
    app_logger.info("Starting SEC symbol import: %s", request)

    # Fetch and filter SEC symbols
    try:
        sec_symbols = get_sec_symbols()
    except SecProviderError as e:
        app_logger.error("Failed to fetch SEC symbols: %s", str(e))
        raise HTTPException(
            status_code=503,
            detail="Failed to fetch SEC ticker directory after retries",
        )

    # Idempotent import with metrics
    metrics = {
        "processed": len(sec_symbols),
        "inserted": 0,
        "updated": 0,
        "skipped": 0,
    }

    for sec_sym in sec_symbols:
        symbol = sec_sym["symbol"]
        company_name = sec_sym["company_name"]
        yahoo_symbol = sec_sym["yahoo_symbol"]

        # Check if symbol exists
        existing = db.query(Symbol).filter(Symbol.symbol == symbol).first()

        if existing:
            # Update existing symbol
            existing.company_name = company_name
            existing.yahoo_symbol = yahoo_symbol
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
                exchange="SEC",
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
            "exchange": "SEC",
            "count": metrics["inserted"],
            "inserted": metrics["inserted"],
            "updated": metrics["updated"],
        },
    )
    event_bus.publish(event)
    app_logger.info(
        "SEC import completed: processed=%d, inserted=%d, updated=%d, skipped=%d",
        metrics["processed"],
        metrics["inserted"],
        metrics["updated"],
        metrics["skipped"],
    )

    # Return summary response
    return ImportSummaryResponse(
        exchange="SEC",
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
