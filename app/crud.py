from datetime import datetime
from sqlalchemy.orm import Session
from app.models import GameRound, Outcome

def create_round(db: Session, *, symbol: str, duration_sec: int, direction, start_price: float, user_id: int | None = None) -> GameRound:
    r = GameRound(
        user_id=user_id,
        symbol=symbol,
        duration_sec=duration_sec,
        direction=direction,
        start_price=start_price,
    )
    db.add(r)
    db.commit()
    db.refresh(r)
    return r

def resolve_round(db: Session, *, round_id: int, end_price: float) -> GameRound:
    r = db.get(GameRound, round_id)
    if not r:
        return None
    r.end_price = end_price
    r.resolved_at = datetime.utcnow()

    # Determine outcome
    if r.end_price == r.start_price:
        r.outcome = Outcome.push
    elif r.end_price > r.start_price and r.direction.value == "UP":
        r.outcome = Outcome.win
    elif r.end_price < r.start_price and r.direction.value == "DOWN":
        r.outcome = Outcome.win
    else:
        r.outcome = Outcome.lose

    db.add(r)
    db.commit()
    db.refresh(r)
    return r
