"""Shared data models and Pydantic schemas."""

from typing import Optional, List
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, EmailStr
from sqlalchemy import Column, String, DateTime, Boolean, Enum as SQLEnum, Float, Integer
from sqlalchemy.sql import func

from shared.database import Base


class InstrumentType(str, Enum):
    """Types of financial instruments."""
    STOCK = "STOCK"
    METAL = "METAL"


class UserRole(str, Enum):
    """User roles for authorization."""
    ADMIN = "ADMIN"
    USER = "USER"


class ApprovalStatus(str, Enum):
    """User approval status."""
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


# ============================================================================
# SQLAlchemy Models
# ============================================================================

class User(Base):
    """User account database model."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True)
    email = Column(String(255), unique=True, index=True)
    hashed_password = Column(String(255))
    role = Column(SQLEnum(UserRole), default=UserRole.USER, index=True)
    approval_status = Column(
        SQLEnum(ApprovalStatus), default=ApprovalStatus.PENDING, index=True
    )
    profile_picture_url = Column(String(500), nullable=True)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    last_login = Column(DateTime, nullable=True)


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

class UserSchema(BaseModel):
    """User API schema."""
    id: int
    username: str
    email: str
    role: UserRole
    approval_status: ApprovalStatus
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    profile_picture_url: Optional[str] = None
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserCreateRequest(BaseModel):
    """Request to create a new user (registration)."""
    username: str
    email: EmailStr
    password: str


class UserLoginRequest(BaseModel):
    """Request to login."""
    username_or_email: str
    password: str


class TokenResponse(BaseModel):
    """JWT token response."""
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    user: UserSchema


class UserApprovalRequest(BaseModel):
    """Request to approve/reject a user."""
    user_id: int
    approved: bool


class UserListResponse(BaseModel):
    """Response for user list endpoint."""
    users: List[UserSchema]
    total: int


class ProfileUpdateRequest(BaseModel):
    """Request to update user profile."""
    first_name: Optional[str] = None
    last_name: Optional[str] = None


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
