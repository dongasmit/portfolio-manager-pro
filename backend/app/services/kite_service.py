"""Kite Connect API integration for live market data."""
import httpx
from typing import Optional
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.models import Holding

settings = get_settings()

# Simulated market data for development (when Kite API keys aren't configured)
SIMULATED_PRICES: dict[str, dict] = {
    "RELIANCE": {"price": 2945.50, "change": 1.2, "sector": "energy"},
    "TCS": {"price": 4123.75, "change": -0.5, "sector": "technology"},
    "HDFCBANK": {"price": 1678.30, "change": 0.8, "sector": "financials"},
    "INFY": {"price": 1856.40, "change": -1.1, "sector": "technology"},
    "ICICIBANK": {"price": 1234.60, "change": 0.3, "sector": "financials"},
    "HINDUNILVR": {"price": 2567.80, "change": -0.2, "sector": "consumer_staples"},
    "ITC": {"price": 478.90, "change": 1.5, "sector": "consumer_staples"},
    "SBIN": {"price": 834.20, "change": 0.7, "sector": "financials"},
    "BHARTIARTL": {"price": 1645.30, "change": 2.1, "sector": "telecom"},
    "KOTAKBANK": {"price": 1823.45, "change": -0.4, "sector": "financials"},
    "LT": {"price": 3567.80, "change": 0.9, "sector": "industrials"},
    "WIPRO": {"price": 567.30, "change": -1.3, "sector": "technology"},
    "AXISBANK": {"price": 1178.90, "change": 0.6, "sector": "financials"},
    "SUNPHARMA": {"price": 1789.60, "change": 1.8, "sector": "healthcare"},
    "TATAMOTORS": {"price": 987.40, "change": -0.9, "sector": "consumer_discretionary"},
    # Mutual Funds (simulated NAVs)
    "HDFCMF_EQUITY": {"price": 156.78, "change": 0.4, "sector": "other"},
    "SBIMF_BLUECHIP": {"price": 78.34, "change": 0.6, "sector": "other"},
    "ICICIMF_DEBT": {"price": 34.56, "change": 0.1, "sector": "other"},
    "AXISMF_MIDCAP": {"price": 98.23, "change": -0.3, "sector": "other"},
    # Government Bonds / Debt instruments
    "GSEC_10Y": {"price": 101.25, "change": 0.05, "sector": "other"},
    "CORP_BOND_AAA": {"price": 102.50, "change": 0.02, "sector": "other"},
}


class KiteService:
    """
    Service for fetching market data.
    Uses Kite Connect API when credentials are available,
    falls back to simulated data for development.
    """

    def __init__(self):
        self.api_key = settings.kite_api_key
        self.api_secret = settings.kite_api_secret
        self.access_token: Optional[str] = None
        self.base_url = "https://api.kite.trade"

    def is_configured(self) -> bool:
        return bool(self.api_key and self.api_secret and self.api_key != "your_kite_api_key")

    async def get_quote(self, symbol: str) -> dict:
        """Get current price for a symbol."""
        if self.is_configured() and self.access_token:
            return await self._fetch_kite_quote(symbol)
        return self._get_simulated_quote(symbol)

    async def get_quotes(self, symbols: list[str]) -> dict[str, dict]:
        """Get current prices for multiple symbols."""
        if self.is_configured() and self.access_token:
            return await self._fetch_kite_quotes(symbols)
        return {s: self._get_simulated_quote(s) for s in symbols}

    def _get_simulated_quote(self, symbol: str) -> dict:
        """Return simulated market data for development."""
        if symbol in SIMULATED_PRICES:
            data = SIMULATED_PRICES[symbol]
            return {
                "symbol": symbol,
                "last_price": data["price"],
                "change_pct": data["change"],
                "sector": data["sector"],
            }
        # Default fallback for unknown symbols
        return {
            "symbol": symbol,
            "last_price": 100.0,
            "change_pct": 0.0,
            "sector": "other",
        }

    async def _fetch_kite_quote(self, symbol: str) -> dict:
        """Fetch quote from Kite Connect API."""
        async with httpx.AsyncClient() as client:
            headers = {
                "X-Kite-Version": "3",
                "Authorization": f"token {self.api_key}:{self.access_token}",
            }
            resp = await client.get(
                f"{self.base_url}/quote?i=NSE:{symbol}",
                headers=headers,
            )
            if resp.status_code == 200:
                data = resp.json()["data"][f"NSE:{symbol}"]
                return {
                    "symbol": symbol,
                    "last_price": data["last_price"],
                    "change_pct": data.get("net_change", 0),
                    "sector": "other",
                }
        return self._get_simulated_quote(symbol)

    async def _fetch_kite_quotes(self, symbols: list[str]) -> dict[str, dict]:
        """Fetch multiple quotes from Kite Connect API."""
        instruments = "&".join([f"i=NSE:{s}" for s in symbols])
        async with httpx.AsyncClient() as client:
            headers = {
                "X-Kite-Version": "3",
                "Authorization": f"token {self.api_key}:{self.access_token}",
            }
            resp = await client.get(
                f"{self.base_url}/quote?{instruments}",
                headers=headers,
            )
            if resp.status_code == 200:
                data = resp.json()["data"]
                result = {}
                for symbol in symbols:
                    key = f"NSE:{symbol}"
                    if key in data:
                        result[symbol] = {
                            "symbol": symbol,
                            "last_price": data[key]["last_price"],
                            "change_pct": data[key].get("net_change", 0),
                            "sector": "other",
                        }
                    else:
                        result[symbol] = self._get_simulated_quote(symbol)
                return result
        return {s: self._get_simulated_quote(s) for s in symbols}

    async def refresh_holdings_prices(self, db: Session, portfolio_id: str) -> int:
        """Update all holdings in a portfolio with current market prices."""
        holdings = db.query(Holding).filter(Holding.portfolio_id == portfolio_id).all()
        if not holdings:
            return 0

        symbols = [h.symbol for h in holdings]
        quotes = await self.get_quotes(symbols)

        updated = 0
        for holding in holdings:
            if holding.symbol in quotes:
                quote = quotes[holding.symbol]
                holding.current_price = quote["last_price"]
                updated += 1

        db.commit()
        return updated


# Singleton
kite_service = KiteService()
