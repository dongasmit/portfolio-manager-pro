"""Portfolio analytics service - XIRR, CAGR, and breakdown calculations."""
from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from sqlalchemy.orm import Session
import pyxirr

from app.models.models import (
    Portfolio, Holding, Transaction, TransactionType, AssetType
)


def calculate_cagr(
    beginning_value: float,
    ending_value: float,
    years: float,
) -> Optional[float]:
    """Calculate Compound Annual Growth Rate."""
    if beginning_value <= 0 or years <= 0:
        return None
    return ((ending_value / beginning_value) ** (1.0 / years) - 1) * 100


def calculate_xirr(transactions: list[Transaction], current_value: float) -> Optional[float]:
    """
    Calculate XIRR using actual transaction cashflows.
    Buy = negative cashflow (money going out)
    Sell/Dividend = positive cashflow (money coming in)
    Current portfolio value = final positive cashflow at today's date
    """
    if not transactions:
        return None

    dates = []
    amounts = []

    for txn in transactions:
        txn_date = txn.date if isinstance(txn.date, date) else datetime.strptime(str(txn.date), "%Y-%m-%d").date()
        dates.append(txn_date)

        amount = float(txn.quantity * txn.price)
        if txn.transaction_type == TransactionType.BUY.value:
            amounts.append(-amount)  # money out
        elif txn.transaction_type in (TransactionType.SELL.value, TransactionType.DIVIDEND.value):
            amounts.append(amount)  # money in

    # Add current portfolio value as final positive cashflow
    dates.append(date.today())
    amounts.append(current_value)

    try:
        result = pyxirr.xirr(dates, amounts)
        if result is None:
            return None
        return round(result * 100, 2)  # Return as percentage
    except Exception:
        return None


def get_portfolio_summary(db: Session, portfolio_id: str) -> dict:
    """Get comprehensive portfolio summary with all metrics."""
    portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
    if not portfolio:
        return {}

    holdings = db.query(Holding).filter(Holding.portfolio_id == portfolio_id).all()
    transactions = (
        db.query(Transaction)
        .filter(Transaction.portfolio_id == portfolio_id)
        .order_by(Transaction.date)
        .all()
    )

    total_invested = sum(float(h.quantity * h.avg_buy_price) for h in holdings)
    total_current = sum(float(h.quantity * h.current_price) for h in holdings)
    total_pnl = total_current - total_invested
    pnl_pct = (total_pnl / total_invested * 100) if total_invested > 0 else 0

    # XIRR
    xirr_value = calculate_xirr(transactions, total_current)

    # CAGR - from first transaction to now
    years = 0.0
    if transactions:
        first_date = transactions[0].date
        if isinstance(first_date, str):
            first_date = datetime.strptime(first_date, "%Y-%m-%d").date()
        delta = date.today() - first_date
        years = delta.days / 365.25

    cagr_value = calculate_cagr(total_invested, total_current, years) if years > 0 else None

    # Asset allocation breakdown
    asset_allocation = {}
    sector_allocation = {}
    holdings_detail = []

    for h in holdings:
        current_val = float(h.quantity * h.current_price)
        invested_val = float(h.quantity * h.avg_buy_price)

        # Asset type breakdown
        asset_type = h.asset_type or AssetType.EQUITY.value
        asset_allocation[asset_type] = asset_allocation.get(asset_type, 0) + current_val

        # Sector breakdown
        sector = h.sector or "other"
        sector_allocation[sector] = sector_allocation.get(sector, 0) + current_val

        holdings_detail.append({
            "id": h.id,
            "symbol": h.symbol,
            "name": h.name,
            "asset_type": h.asset_type,
            "sector": h.sector,
            "quantity": float(h.quantity),
            "avg_buy_price": float(h.avg_buy_price),
            "current_price": float(h.current_price),
            "invested_value": invested_val,
            "current_value": current_val,
            "pnl": current_val - invested_val,
            "pnl_pct": ((current_val - invested_val) / invested_val * 100) if invested_val > 0 else 0,
        })

    # Convert allocations to percentages
    asset_alloc_pct = {
        k: round(v / total_current * 100, 2) if total_current > 0 else 0
        for k, v in asset_allocation.items()
    }
    sector_alloc_pct = {
        k: round(v / total_current * 100, 2) if total_current > 0 else 0
        for k, v in sector_allocation.items()
    }

    return {
        "portfolio_id": portfolio_id,
        "portfolio_name": portfolio.name,
        "client_id": portfolio.client_id,
        "summary": {
            "total_invested": round(total_invested, 2),
            "total_current_value": round(total_current, 2),
            "total_pnl": round(total_pnl, 2),
            "total_pnl_pct": round(pnl_pct, 2),
            "xirr": xirr_value,
            "cagr": round(cagr_value, 2) if cagr_value is not None else None,
            "holdings_count": len(holdings),
        },
        "asset_allocation": asset_alloc_pct,
        "asset_allocation_value": {k: round(v, 2) for k, v in asset_allocation.items()},
        "sector_allocation": sector_alloc_pct,
        "sector_allocation_value": {k: round(v, 2) for k, v in sector_allocation.items()},
        "holdings": sorted(holdings_detail, key=lambda x: x["current_value"], reverse=True),
    }


def get_client_summary(db: Session, client_id: str) -> dict:
    """Aggregate all portfolios for a client."""
    portfolios = db.query(Portfolio).filter(Portfolio.client_id == client_id).all()

    portfolio_summaries = []
    total_invested = 0
    total_current = 0

    for p in portfolios:
        summary = get_portfolio_summary(db, p.id)
        if summary:
            portfolio_summaries.append(summary)
            total_invested += summary["summary"]["total_invested"]
            total_current += summary["summary"]["total_current_value"]

    total_pnl = total_current - total_invested

    return {
        "client_id": client_id,
        "total_invested": round(total_invested, 2),
        "total_current_value": round(total_current, 2),
        "total_pnl": round(total_pnl, 2),
        "total_pnl_pct": round(total_pnl / total_invested * 100, 2) if total_invested > 0 else 0,
        "portfolios": portfolio_summaries,
    }
