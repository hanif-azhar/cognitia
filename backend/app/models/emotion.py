from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class Emotion(Base):
    __tablename__ = "emotions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    name_en: Mapped[str] = mapped_column(String(128))
    name_id: Mapped[str] = mapped_column(String(128))


class EntryEmotion(Base):
    __tablename__ = "entry_emotions"

    entry_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("entries.id", ondelete="CASCADE"), primary_key=True
    )
    emotion_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("emotions.id", ondelete="CASCADE"), primary_key=True
    )

    entry = relationship("Entry", back_populates="emotions")
    emotion = relationship("Emotion")
