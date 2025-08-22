import asyncio
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import get_db
from app.schemas import RoundCreate, RoundPublic, PriceQuote
from app.services.pricing import get_price_provider
from app import crud

router = APIRouter(prefix="/bets", tags=["bets"])

@router.get("/price", response_model=PriceQuote)
async def get_current_price(symbol: str = "BTCUSDT"):
    provider = get_price_provider(settings.PRICE_PROVIDER)
    return await provider.get_price(symbol)

@router.post("/", response_model=RoundPublic)
async def start_bet(payload: RoundCreate, bg: BackgroundTasks, db: Session = Depends(get_db)):
    provider = get_price_provider(settings.PRICE_PROVIDER)
    # 1) Snapshot start price
    quote = await provider.get_price(payload.symbol)

    # 2) Create round
    round_row = crud.create_round(
        db,
        symbol=payload.symbol,
        duration_sec=settings.ROUND_DURATION_SEC,
        direction=payload.direction,
        start_price=quote.price,
        user_id=None,  # anonymous for now
    )

    # 3) Schedule resolve after N seconds (server-side truth)
    async def _resolve_after_delay(round_id: int, symbol: str, seconds: int):
        await asyncio.sleep(seconds)
        q2 = await provider.get_price(symbol)
        # Re-open a DB session in task:
        from app.core.database import SessionLocal
        with SessionLocal() as tdb:
            crud.resolve_round(tdb, round_id=round_id, end_price=q2.price)

    bg.add_task(_resolve_after_delay, round_row.id, payload.symbol, settings.ROUND_DURATION_SEC)
    return round_row

@router.get("/{round_id}", response_model=RoundPublic)
def get_round(round_id: int, db: Session = Depends(get_db)):
    row = db.get(crud.GameRound, round_id)  # type: ignore[attr-defined]
    if not row:
        raise HTTPException(status_code=404, detail="Round not found")
    return row
