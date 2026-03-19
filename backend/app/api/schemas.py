"""Pydantic schemas for API request/response."""
from pydantic import BaseModel
from typing import Optional
from datetime import date


class ClientCreate(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    risk_profile: str = "moderate"
    target_equity_pct: float = 60.0
    target_debt_pct: float = 40.0


class ClientResponse(BaseModel):
    id: str
    name: str
    email: str
    phone: Optional[str]
    risk_profile: str
    target_equity_pct: float
    target_debt_pct: float

    model_config = {"from_attributes": True}


class PortfolioCreate(BaseModel):
    client_id: str
    name: str
    description: Optional[str] = None


class HoldingCreate(BaseModel):
    portfolio_id: str
    symbol: str
    name: str
    asset_type: str = "equity"
    sector: str = "other"
    quantity: float
    avg_buy_price: float
    current_price: Optional[float] = None


class TransactionCreate(BaseModel):
    portfolio_id: str
    symbol: str
    transaction_type: str  # buy, sell, dividend
    quantity: float
    price: float
    date: date
    notes: Optional[str] = None


class AgentRequest(BaseModel):
    message: str
    client_id: Optional[str] = None


class AgentResponse(BaseModel):
    response: str
    actions_taken: list[dict] = []
    context_used: list[str] = []
