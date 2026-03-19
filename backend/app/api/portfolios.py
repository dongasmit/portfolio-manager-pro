"""Portfolio, holdings, and transaction endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Portfolio, Holding, Transaction
from app.api.schemas import PortfolioCreate, HoldingCreate, TransactionCreate
from app.services.portfolio_service import get_portfolio_summary
from app.services.kite_service import kite_service

router = APIRouter()


# ── Portfolios ──────────────────────────────────────────────────────

@router.get("/")
def list_portfolios(client_id: str = None, db: Session = Depends(get_db)):
    query = db.query(Portfolio)
    if client_id:
        query = query.filter(Portfolio.client_id == client_id)
    portfolios = query.all()
    return [
        {
            "id": p.id,
            "client_id": p.client_id,
            "name": p.name,
            "description": p.description,
        }
        for p in portfolios
    ]


@router.post("/")
def create_portfolio(data: PortfolioCreate, db: Session = Depends(get_db)):
    portfolio = Portfolio(
        client_id=data.client_id,
        name=data.name,
        description=data.description,
    )
    db.add(portfolio)
    db.commit()
    db.refresh(portfolio)
    return {"id": portfolio.id, "name": portfolio.name}


@router.get("/{portfolio_id}")
def get_portfolio(portfolio_id: str, db: Session = Depends(get_db)):
    return get_portfolio_summary(db, portfolio_id)


@router.post("/{portfolio_id}/refresh-prices")
async def refresh_prices(portfolio_id: str, db: Session = Depends(get_db)):
    updated = await kite_service.refresh_holdings_prices(db, portfolio_id)
    return {"updated": updated, "message": f"Refreshed {updated} holdings"}


# ── Holdings ────────────────────────────────────────────────────────

@router.post("/{portfolio_id}/holdings")
def add_holding(portfolio_id: str, data: HoldingCreate, db: Session = Depends(get_db)):
    portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    holding = Holding(
        portfolio_id=portfolio_id,
        symbol=data.symbol,
        name=data.name,
        asset_type=data.asset_type,
        sector=data.sector,
        quantity=data.quantity,
        avg_buy_price=data.avg_buy_price,
        current_price=data.current_price or data.avg_buy_price,
    )
    db.add(holding)
    db.commit()
    db.refresh(holding)
    return {"id": holding.id, "symbol": holding.symbol}


@router.delete("/{portfolio_id}/holdings/{holding_id}")
def remove_holding(portfolio_id: str, holding_id: str, db: Session = Depends(get_db)):
    holding = (
        db.query(Holding)
        .filter(Holding.id == holding_id, Holding.portfolio_id == portfolio_id)
        .first()
    )
    if not holding:
        raise HTTPException(status_code=404, detail="Holding not found")
    db.delete(holding)
    db.commit()
    return {"status": "deleted"}


# ── Transactions ────────────────────────────────────────────────────

@router.get("/{portfolio_id}/transactions")
def list_transactions(portfolio_id: str, db: Session = Depends(get_db)):
    txns = (
        db.query(Transaction)
        .filter(Transaction.portfolio_id == portfolio_id)
        .order_by(Transaction.date.desc())
        .all()
    )
    return [
        {
            "id": t.id,
            "symbol": t.symbol,
            "transaction_type": t.transaction_type,
            "quantity": float(t.quantity),
            "price": float(t.price),
            "date": str(t.date),
            "notes": t.notes,
        }
        for t in txns
    ]


@router.post("/{portfolio_id}/transactions")
def add_transaction(portfolio_id: str, data: TransactionCreate, db: Session = Depends(get_db)):
    portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    txn = Transaction(
        portfolio_id=portfolio_id,
        symbol=data.symbol,
        transaction_type=data.transaction_type,
        quantity=data.quantity,
        price=data.price,
        date=data.date,
        notes=data.notes,
    )
    db.add(txn)
    db.commit()
    db.refresh(txn)
    return {"id": txn.id, "symbol": txn.symbol, "type": txn.transaction_type}
