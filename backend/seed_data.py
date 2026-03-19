"""Seed the database with sample clients, portfolios, holdings, and transactions."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from datetime import date, timedelta
from app.database import SessionLocal, engine, Base
from app.models.models import Client, Portfolio, Holding, Transaction


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Check if already seeded
    if db.query(Client).first():
        print("Database already has data. Skipping seed.")
        db.close()
        return

    # ── Clients ─────────────────────────────────────────────────────
    clients_data = [
        {
            "id": "client-001",
            "name": "John Sharma",
            "email": "john.sharma@example.com",
            "phone": "+91 98765 43210",
            "risk_profile": "aggressive",
            "target_equity_pct": 70.0,
            "target_debt_pct": 30.0,
        },
        {
            "id": "client-002",
            "name": "Priya Mehta",
            "email": "priya.mehta@example.com",
            "phone": "+91 87654 32109",
            "risk_profile": "moderate",
            "target_equity_pct": 60.0,
            "target_debt_pct": 40.0,
        },
        {
            "id": "client-003",
            "name": "Rahul Patel",
            "email": "rahul.patel@example.com",
            "phone": "+91 76543 21098",
            "risk_profile": "conservative",
            "target_equity_pct": 40.0,
            "target_debt_pct": 60.0,
        },
    ]

    for c in clients_data:
        db.add(Client(**c))
    db.flush()

    # ── Portfolios ──────────────────────────────────────────────────
    portfolios_data = [
        {"id": "port-001", "client_id": "client-001", "name": "John - Growth Portfolio", "description": "High-growth equity focused"},
        {"id": "port-002", "client_id": "client-001", "name": "John - Retirement Fund", "description": "Long-term retirement savings"},
        {"id": "port-003", "client_id": "client-002", "name": "Priya - Balanced Portfolio", "description": "60/40 balanced approach"},
        {"id": "port-004", "client_id": "client-003", "name": "Rahul - Conservative Fund", "description": "Capital preservation focus"},
    ]

    for p in portfolios_data:
        db.add(Portfolio(**p))
    db.flush()

    # ── Holdings ────────────────────────────────────────────────────
    holdings_data = [
        # John - Growth Portfolio
        {"portfolio_id": "port-001", "symbol": "RELIANCE", "name": "Reliance Industries", "asset_type": "equity", "sector": "energy", "quantity": 50, "avg_buy_price": 2650.00, "current_price": 2945.50},
        {"portfolio_id": "port-001", "symbol": "TCS", "name": "Tata Consultancy Services", "asset_type": "equity", "sector": "technology", "quantity": 30, "avg_buy_price": 3800.00, "current_price": 4123.75},
        {"portfolio_id": "port-001", "symbol": "INFY", "name": "Infosys", "asset_type": "equity", "sector": "technology", "quantity": 80, "avg_buy_price": 1650.00, "current_price": 1856.40},
        {"portfolio_id": "port-001", "symbol": "BHARTIARTL", "name": "Bharti Airtel", "asset_type": "equity", "sector": "telecom", "quantity": 40, "avg_buy_price": 1450.00, "current_price": 1645.30},
        {"portfolio_id": "port-001", "symbol": "TATAMOTORS", "name": "Tata Motors", "asset_type": "equity", "sector": "consumer_discretionary", "quantity": 100, "avg_buy_price": 850.00, "current_price": 987.40},

        # John - Retirement Fund
        {"portfolio_id": "port-002", "symbol": "HDFCBANK", "name": "HDFC Bank", "asset_type": "equity", "sector": "financials", "quantity": 60, "avg_buy_price": 1520.00, "current_price": 1678.30},
        {"portfolio_id": "port-002", "symbol": "HDFCMF_EQUITY", "name": "HDFC Equity MF", "asset_type": "mutual_fund", "sector": "other", "quantity": 500, "avg_buy_price": 140.00, "current_price": 156.78},
        {"portfolio_id": "port-002", "symbol": "ICICIMF_DEBT", "name": "ICICI Debt MF", "asset_type": "debt", "sector": "other", "quantity": 1000, "avg_buy_price": 32.00, "current_price": 34.56},
        {"portfolio_id": "port-002", "symbol": "GSEC_10Y", "name": "10Y Govt Security", "asset_type": "debt", "sector": "other", "quantity": 200, "avg_buy_price": 99.50, "current_price": 101.25},

        # Priya - Balanced Portfolio
        {"portfolio_id": "port-003", "symbol": "ICICIBANK", "name": "ICICI Bank", "asset_type": "equity", "sector": "financials", "quantity": 100, "avg_buy_price": 1100.00, "current_price": 1234.60},
        {"portfolio_id": "port-003", "symbol": "HINDUNILVR", "name": "Hindustan Unilever", "asset_type": "equity", "sector": "consumer_staples", "quantity": 40, "avg_buy_price": 2400.00, "current_price": 2567.80},
        {"portfolio_id": "port-003", "symbol": "ITC", "name": "ITC Ltd", "asset_type": "equity", "sector": "consumer_staples", "quantity": 200, "avg_buy_price": 430.00, "current_price": 478.90},
        {"portfolio_id": "port-003", "symbol": "SBIMF_BLUECHIP", "name": "SBI Bluechip MF", "asset_type": "mutual_fund", "sector": "other", "quantity": 800, "avg_buy_price": 70.00, "current_price": 78.34},
        {"portfolio_id": "port-003", "symbol": "CORP_BOND_AAA", "name": "AAA Corporate Bond", "asset_type": "debt", "sector": "other", "quantity": 500, "avg_buy_price": 100.00, "current_price": 102.50},

        # Rahul - Conservative Fund
        {"portfolio_id": "port-004", "symbol": "SBIN", "name": "State Bank of India", "asset_type": "equity", "sector": "financials", "quantity": 50, "avg_buy_price": 780.00, "current_price": 834.20},
        {"portfolio_id": "port-004", "symbol": "SUNPHARMA", "name": "Sun Pharma", "asset_type": "equity", "sector": "healthcare", "quantity": 25, "avg_buy_price": 1600.00, "current_price": 1789.60},
        {"portfolio_id": "port-004", "symbol": "ICICIMF_DEBT", "name": "ICICI Debt MF", "asset_type": "debt", "sector": "other", "quantity": 2000, "avg_buy_price": 31.50, "current_price": 34.56},
        {"portfolio_id": "port-004", "symbol": "GSEC_10Y", "name": "10Y Govt Security", "asset_type": "debt", "sector": "other", "quantity": 500, "avg_buy_price": 98.00, "current_price": 101.25},
        {"portfolio_id": "port-004", "symbol": "CORP_BOND_AAA", "name": "AAA Corporate Bond", "asset_type": "debt", "sector": "other", "quantity": 300, "avg_buy_price": 99.00, "current_price": 102.50},
    ]

    for h in holdings_data:
        db.add(Holding(**h))
    db.flush()

    # ── Transactions (for XIRR calculation) ─────────────────────────
    today = date.today()
    base_date = today - timedelta(days=730)  # ~2 years ago

    transactions_data = []

    # John - Growth Portfolio buys over time
    john_growth_buys = [
        ("RELIANCE", 20, 2450.00, base_date),
        ("RELIANCE", 30, 2780.00, base_date + timedelta(days=180)),
        ("TCS", 30, 3800.00, base_date + timedelta(days=90)),
        ("INFY", 50, 1500.00, base_date + timedelta(days=60)),
        ("INFY", 30, 1900.00, base_date + timedelta(days=400)),
        ("BHARTIARTL", 40, 1450.00, base_date + timedelta(days=200)),
        ("TATAMOTORS", 100, 850.00, base_date + timedelta(days=300)),
    ]

    for symbol, qty, price, txn_date in john_growth_buys:
        transactions_data.append({
            "portfolio_id": "port-001",
            "symbol": symbol,
            "transaction_type": "buy",
            "quantity": qty,
            "price": price,
            "date": txn_date,
        })

    # John - Retirement Fund
    john_ret_buys = [
        ("HDFCBANK", 60, 1520.00, base_date + timedelta(days=30)),
        ("HDFCMF_EQUITY", 500, 140.00, base_date + timedelta(days=60)),
        ("ICICIMF_DEBT", 1000, 32.00, base_date + timedelta(days=90)),
        ("GSEC_10Y", 200, 99.50, base_date + timedelta(days=120)),
    ]

    for symbol, qty, price, txn_date in john_ret_buys:
        transactions_data.append({
            "portfolio_id": "port-002",
            "symbol": symbol,
            "transaction_type": "buy",
            "quantity": qty,
            "price": price,
            "date": txn_date,
        })

    # Priya
    priya_buys = [
        ("ICICIBANK", 100, 1100.00, base_date + timedelta(days=45)),
        ("HINDUNILVR", 40, 2400.00, base_date + timedelta(days=150)),
        ("ITC", 200, 430.00, base_date + timedelta(days=200)),
        ("SBIMF_BLUECHIP", 800, 70.00, base_date + timedelta(days=100)),
        ("CORP_BOND_AAA", 500, 100.00, base_date + timedelta(days=250)),
    ]

    for symbol, qty, price, txn_date in priya_buys:
        transactions_data.append({
            "portfolio_id": "port-003",
            "symbol": symbol,
            "transaction_type": "buy",
            "quantity": qty,
            "price": price,
            "date": txn_date,
        })

    # Rahul
    rahul_buys = [
        ("SBIN", 50, 780.00, base_date + timedelta(days=20)),
        ("SUNPHARMA", 25, 1600.00, base_date + timedelta(days=100)),
        ("ICICIMF_DEBT", 2000, 31.50, base_date + timedelta(days=50)),
        ("GSEC_10Y", 500, 98.00, base_date + timedelta(days=70)),
        ("CORP_BOND_AAA", 300, 99.00, base_date + timedelta(days=150)),
    ]

    for symbol, qty, price, txn_date in rahul_buys:
        transactions_data.append({
            "portfolio_id": "port-004",
            "symbol": symbol,
            "transaction_type": "buy",
            "quantity": qty,
            "price": price,
            "date": txn_date,
        })

    # Add a dividend transaction for realism
    transactions_data.append({
        "portfolio_id": "port-001",
        "symbol": "RELIANCE",
        "transaction_type": "dividend",
        "quantity": 50,
        "price": 9.00,
        "date": base_date + timedelta(days=365),
        "notes": "Annual dividend",
    })

    for t in transactions_data:
        db.add(Transaction(**t))

    db.commit()
    db.close()
    print("Database seeded successfully with 3 clients, 4 portfolios, and sample holdings/transactions.")


if __name__ == "__main__":
    seed()
