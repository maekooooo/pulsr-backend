from datetime import datetime
import httpx
from app.schemas import PriceQuote

class PriceProvider:
    async def get_price(self, symbol: str) -> PriceQuote:
        raise NotImplementedError

class BinancePriceProvider(PriceProvider):
    # Maps "BTCUSDT" (internal) to Binance symbol "BTCUSDT"
    BASE = "https://api.binance.com"

    async def get_price(self, symbol: str) -> PriceQuote:
        url = f"{self.BASE}/api/v3/ticker/price"
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.get(url, params={"symbol": symbol})
            r.raise_for_status()
            data = r.json()
            return PriceQuote(symbol=symbol, price=float(data["price"]), as_of=datetime.utcnow())

def get_price_provider(kind: str) -> PriceProvider:
    # We can add "kraken" later; for now default to binance
    return BinancePriceProvider()
