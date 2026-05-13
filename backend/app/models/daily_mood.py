from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import CheckConstraint, Date, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base


def _uuid() -> str:
    return str(uuid.uuid4())


class DailyMood(Base):
    __tablename__ = "daily_moods"
    __table_args__ = (
        CheckConstraint("score >= 1 AND score <= 10", name="ck_daily_mood_score_range"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    mood_date: Mapped[date] = mapped_column(Date, unique=True, index=True, default=date.today)
    score: Mapped[int] = mapped_column(Integer)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
