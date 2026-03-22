"""Data Analyzer Service - applies indicators and evaluates trigger criteria."""

import logging
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from shared.config import settings
from shared.database import get_db, engine, Base
from sqlalchemy import or_
from shared.models import (
    Symbol, SelectedSymbol, MarketData, SignalResult, SignalSchema, User,
    Indicator, UserSymbolIndicator, IndicatorSchema, UserSymbolIndicatorSchema,
    AssignIndicatorRequest,
)
from shared.events import event_bus, Event, EventType
from shared.logging_config import logger as app_logger
from shared.auth import get_current_user

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


@app.get("/signals/{symbol}")
async def get_signals_for_symbol(
    symbol: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get recent signals for a symbol (scoped to current user)."""
    signals = db.query(SignalResult).filter(
        SignalResult.user_id == current_user.id,
        SignalResult.symbol == symbol,
    ).order_by(SignalResult.timestamp.desc()).limit(10).all()

    return [SignalSchema.from_orm(s) for s in signals]


@app.post("/analyze/{symbol}")
async def analyze_symbol(
    symbol: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Analyze a single symbol and generate signals for the current user."""
    # Verify symbol is selected by this user
    selected = db.query(SelectedSymbol).filter(
        SelectedSymbol.user_id == current_user.id,
        SelectedSymbol.symbol == symbol,
    ).first()
    if not selected:
        return {"symbol": symbol, "status": "not_selected"}

    # TODO: Fetch market data for symbol
    # TODO: Apply technical indicators (RSI, ATR, etc.)
    # TODO: Evaluate trigger criteria
    # TODO: Create SignalResult if criteria met (with user_id=current_user.id)
    # TODO: Publish SIGNAL_TRIGGERED event (with user_id)

    app_logger.info(f"Analyzed symbol: {symbol} for user {current_user.id}")
    return {"symbol": symbol, "status": "analyzed"}


@app.post("/analyze-all")
async def analyze_all_symbols(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Run analysis on all of the current user's selected symbols."""
    selected = db.query(SelectedSymbol).filter(
        SelectedSymbol.user_id == current_user.id
    ).all()
    app_logger.info(f"Starting analysis for {len(selected)} symbols (user {current_user.id})")

    results = []
    for sel_sym in selected:
        # TODO: Analyze each symbol
        results.append({"symbol": sel_sym.symbol, "status": "analyzed"})

    # Publish analysis completion event
    event = Event(
        EventType.ANALYSIS_COMPLETED,
        {
            "total_symbols": len(selected),
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": current_user.id,
        },
    )
    event_bus.publish(event)

    return {"total": len(results), "results": results}


# ============================================================================
# Indicator CRUD Endpoints
# ============================================================================

@app.get("/indicators")
async def list_indicators(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all indicators visible to the current user (public + owned)."""
    indicators = db.query(Indicator).filter(
        or_(
            Indicator.is_public == True,
            Indicator.owner_id == current_user.id,
        )
    ).order_by(Indicator.name).all()

    return {"indicators": [IndicatorSchema.from_orm(i) for i in indicators]}


@app.get("/indicators/{symbol}/assigned")
async def get_assigned_indicators(
    symbol: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List indicators assigned to a symbol for the current user."""
    assignments = (
        db.query(UserSymbolIndicator, Indicator.name)
        .join(Indicator, UserSymbolIndicator.indicator_id == Indicator.id)
        .filter(
            UserSymbolIndicator.user_id == current_user.id,
            UserSymbolIndicator.symbol == symbol,
        )
        .order_by(Indicator.name)
        .all()
    )

    return {
        "indicators": [
            UserSymbolIndicatorSchema(
                id=assignment.id,
                indicator_id=assignment.indicator_id,
                indicator_name=name,
                symbol=assignment.symbol,
                params=assignment.params,
                result=assignment.result,
                evaluated_at=assignment.evaluated_at,
            )
            for assignment, name in assignments
        ]
    }


@app.post("/indicators/{symbol}/assign")
async def assign_indicator(
    symbol: str,
    request: AssignIndicatorRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Assign an indicator to a symbol for the current user."""
    # Verify indicator exists and is visible to user
    indicator = db.query(Indicator).filter(
        Indicator.id == request.indicator_id,
        or_(
            Indicator.is_public == True,
            Indicator.owner_id == current_user.id,
        ),
    ).first()
    if not indicator:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Indicator not found")

    # Check if already assigned
    existing = db.query(UserSymbolIndicator).filter(
        UserSymbolIndicator.user_id == current_user.id,
        UserSymbolIndicator.symbol == symbol,
        UserSymbolIndicator.indicator_id == request.indicator_id,
    ).first()
    if existing:
        return {"message": "Indicator already assigned", "id": existing.id}

    assignment = UserSymbolIndicator(
        user_id=current_user.id,
        symbol=symbol,
        indicator_id=request.indicator_id,
    )
    db.add(assignment)
    db.commit()
    db.refresh(assignment)

    return {"message": f"Indicator '{indicator.name}' assigned to {symbol}", "id": assignment.id}


@app.delete("/indicators/{symbol}/assign/{indicator_id}")
async def remove_indicator(
    symbol: str,
    indicator_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Remove an indicator assignment from a symbol for the current user."""
    deleted = (
        db.query(UserSymbolIndicator)
        .filter(
            UserSymbolIndicator.user_id == current_user.id,
            UserSymbolIndicator.symbol == symbol,
            UserSymbolIndicator.indicator_id == indicator_id,
        )
        .delete(synchronize_session="fetch")
    )
    db.commit()

    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignment not found")

    return {"message": "Indicator removed"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8003,
        log_config=None,
    )
