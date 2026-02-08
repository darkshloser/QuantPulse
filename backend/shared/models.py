"""Shared data models and Pydantic schemas."""

from typing import Optional, List
from datetime import datetime
from enum import Enum
from pydantic import BaseModel
from sqlalchemy import Column, String, DateTime, Boolean, Enum as SQLEnum, Float, Integer
from sqlalchemy.sql import func

from shared.database import Base


class InstrumentType(str, Enum):
    """Types of financial instruments."""
    STOCK = "STOCK"
    METAL = "METAL"


# ============================================================================
# SQLAlchemy Models
# ============================================================================

class Symbol(Base):
    """Symbol database model."""
    __tablename__ = "symbols"

    symbol = Column(String(50), primary_key=True, index=True)
    yahoo_symbol = Column(String(50), unique=True, index=True)
    company_name = Column(String(255))
    instrument_type = Column(SQLEnum(InstrumentType), nullable=False)
    exchange = Column(String(10), index=True)
    currency = Column(String(3))
    market_category = Column(String(50))
    financial_status = Column(String(50))
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class SelectedSymbol(Base):
    """User-selected symbols tracking."""
    __tablename__ = "selected_symbols"

    symbol = Column(String(50), primary_key=True, index=True)
    selected_at = Column(DateTime, server_default=func.now())


class MarketData(Base):
    """Historical market data model."""
    __tablename__ = "market_data"

    id = Column(String, primary_key=True, index=True)  # symbol:date composite
    symbol = Column(String(50), index=True)
    date = Column(DateTime, index=True)
    open_price = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Float)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class SignalResult(Base):
    """Analysis results and signal triggers."""
    __tablename__ = "signal_results"

    id = Column(String, primary_key=True, index=True)  # symbol:timestamp
    symbol = Column(String(50), index=True)
    signal_type = Column(String(50))  # e.g., "RSI_OVERSOLD", "ATR_EXPANSION"
    timestamp = Column(DateTime, server_default=func.now())
    confidence = Column(Float)  # 0.0 to 1.0
    explanation = Column(String(1000))
    indicators_passed = Column(String(500))  # JSON string
    notified = Column(Boolean, default=False)
    notified_at = Column(DateTime, nullable=True)


# ============================================================================
# Pydantic Schemas
# ============================================================================

class SymbolSchema(BaseModel):
    """Symbol API schema."""
    symbol: str
    yahoo_symbol: str
    company_name: Optional[str] = None
    instrument_type: InstrumentType
    exchange: Optional[str] = None
    currency: Optional[str] = None
    market_category: Optional[str] = None
    financial_status: Optional[str] = None
    is_active: bool = True

    class Config:
        from_attributes = True


class SymbolListResponse(BaseModel):
    """Response for symbol list endpoint."""
    symbols: List[SymbolSchema]
    total: int


class SelectSymbolRequest(BaseModel):
    """Request to select/deselect symbols."""
    symbol: str
    selected: bool


class MarketDataSchema(BaseModel):
    """Market data API schema."""
    symbol: str
    date: datetime
    open_price: float
    high: float
    low: float
    close: float
    volume: float

    class Config:
        from_attributes = True


class SignalSchema(BaseModel):
    """Signal result API schema."""
    symbol: str
    signal_type: str
    timestamp: datetime
    confidence: float
    explanation: str
    indicators_passed: List[str]

    class Config:
        from_attributes = True


class NasdaqImportRequest(BaseModel):
    """Request body for NASDAQ symbol import endpoint."""
    source: str = "NASDAQ_OFFICIAL"
    instrumentType: str = "STOCK"


class ImportSummaryResponse(BaseModel):
    """Response body for symbol import endpoint."""
    exchange: str
    processed: int
    inserted: int
    updated: int
    skipped: int
    timestamp: datetime
