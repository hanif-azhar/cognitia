from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Date, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base

if TYPE_CHECKING:
    from .distortion import EntryDistortion
    from .emotion import EntryEmotion


def _uuid() -> str:
    return str(uuid.uuid4())


class Entry(Base):
    __tablename__ = "entries"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    entry_date: Mapped[date] = mapped_column(Date, default=date.today)

    # A — Activating Event
    situation: Mapped[str | None] = mapped_column(Text, nullable=True)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    people_involved: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # B — Belief
    automatic_thought: Mapped[str | None] = mapped_column(Text, nullable=True)

    # C — Consequences
    emotion_intensity: Mapped[int] = mapped_column(Integer, default=0)
    behavior: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Testing Your Thoughts
    evidence_for: Mapped[str | None] = mapped_column(Text, nullable=True)
    evidence_against: Mapped[str | None] = mapped_column(Text, nullable=True)
    reality_test_response: Mapped[str | None] = mapped_column(Text, nullable=True)
    pragmatic_check_response: Mapped[str | None] = mapped_column(Text, nullable=True)
    alternative_action: Mapped[str | None] = mapped_column(Text, nullable=True)
    reframed_thought: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Meta
    is_complete: Mapped[bool] = mapped_column(Boolean, default=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    language: Mapped[str] = mapped_column(String(2), default="en")

    distortions: Mapped[list["EntryDistortion"]] = relationship(
        "EntryDistortion", back_populates="entry", cascade="all, delete-orphan"
    )
    emotions: Mapped[list["EntryEmotion"]] = relationship(
        "EntryEmotion", back_populates="entry", cascade="all, delete-orphan"
    )
