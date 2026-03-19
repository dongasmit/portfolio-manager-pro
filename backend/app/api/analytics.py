"""Analytics endpoints - XIRR, CAGR, breakdowns."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Client, Portfolio, Holding, Transaction
from app.services.portfolio_service import (
    get_portfolio_summary,
    get_client_summary,
    calculate_xirr,
    calculate_cagr,
)

router = APIRouter()


@router.get("/dashboard")
def dashboard_overview(db: Session = Depends(get_db)):
    """Top-level dashboard: all clients and their portfolio stats."""
    clients = db.query(Client).all()
    dashboard = []

    total_aum = 0
    total_clients = len(clients)

    for client in clients:
        summary = get_client_summary(db, client.id)
        total_aum += summary.get("total_current_value", 0)
        dashboard.append({
            "client_id": client.id,
            "client_name": client.name,
            "risk_profile": client.risk_profile,
            "total_invested": summary.get("total_invested", 0),
            "total_current_value": summary.get("total_current_value", 0),
            "total_pnl": summary.get("total_pnl", 0),
            "total_pnl_pct": summary.get("total_pnl_pct", 0),
            "portfolios_count": len(summary.get("portfolios", [])),
        })

    return {
        "total_aum": round(total_aum, 2),
        "total_clients": total_clients,
        "clients": dashboard,
    }


@router.get("/portfolio/{portfolio_id}/xirr")
def portfolio_xirr(portfolio_id: str, db: Session = Depends(get_db)):
    """Calculate XIRR for a specific portfolio."""
    holdings = db.query(Holding).filter(Holding.portfolio_id == portfolio_id).all()
    transactions = (
        db.query(Transaction)
        .filter(Transaction.portfolio_id == portfolio_id)
        .order_by(Transaction.date)
        .all()
    )

    total_current = sum(float(h.quantity * h.current_price) for h in holdings)
    xirr = calculate_xirr(transactions, total_current)

    return {"portfolio_id": portfolio_id, "xirr": xirr}


@router.get("/portfolio/{portfolio_id}/allocation")
def portfolio_allocation(portfolio_id: str, db: Session = Depends(get_db)):
    """Get asset and sector allocation for a portfolio."""
    summary = get_portfolio_summary(db, portfolio_id)
    return {
        "asset_allocation": summary.get("asset_allocation", {}),
        "asset_allocation_value": summary.get("asset_allocation_value", {}),
        "sector_allocation": summary.get("sector_allocation", {}),
        "sector_allocation_value": summary.get("sector_allocation_value", {}),
    }


@router.get("/client/{client_id}/performance")
def client_performance(client_id: str, db: Session = Depends(get_db)):
    """Get full performance metrics for a client."""
    return get_client_summary(db, client_id)
