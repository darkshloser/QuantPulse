"""Symbol Management Service - manages financial instruments universe."""

import logging
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from shared.config import settings
from shared.database import get_db, engine, Base
from shared.models import Symbol, SelectedSymbol, SymbolSchema, SymbolListResponse, SelectSymbolRequest
from shared.events import event_bus, Event, EventType
from shared.logging_config import logger as app_logger

# Create tables
Base.metadata.create_all(bind=engine)

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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        log_config=None,
    )
