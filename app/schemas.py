from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional
from app.models import Direction, Outcome

class RoundCreate(BaseModel):
    direction: Direction
    symbol: str = "BTCUSDT"

class RoundPublic(BaseModel):
    id: int
    user_id: Optional[int] = None
    symbol: str
    duration_sec: int
    direction: Direction
    start_price: float
    end_price: Optional[float] = None
    outcome: Outcome
    started_at: datetime
    resolved_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class PriceQuote(BaseModel):
    symbol: str
    price: float
    as_of: datetime
