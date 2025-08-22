import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Float, Enum, ForeignKey
from sqlalchemy.dialects.sqlite import BLOB
from sqlalchemy.orm import relationship
from app.core.database import Base

class Direction(str, enum.Enum):
    up = "UP"
    down = "DOWN"

class Outcome(str, enum.Enum):
    win = "WIN"
    lose = "LOSE"
    push = "PUSH"
    pending = "PENDING"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    # Optional: anonymous play later
    handle = Column(String, unique=False, nullable=True)

class GameRound(Base):
    __tablename__ = "game_rounds"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    symbol = Column(String, default="BTCUSDT", nullable=False)
    duration_sec = Column(Integer, default=5, nullable=False)

    direction = Column(Enum(Direction), nullable=False)

    start_price = Column(Float, nullable=False)
    end_price = Column(Float, nullable=True)

    outcome = Column(Enum(Outcome), default=Outcome.pending, nullable=False)

    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    resolved_at = Column(DateTime, nullable=True)

    user = relationship("User", lazy="joined")
