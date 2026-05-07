from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class Distortion(Base):
    __tablename__ = "distortions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    name_en: Mapped[str] = mapped_column(String(128))
    name_id: Mapped[str] = mapped_column(String(128))
    description_en: Mapped[str] = mapped_column(Text)
    description_id: Mapped[str] = mapped_column(Text)
    example_en: Mapped[str] = mapped_column(Text)
    example_id: Mapped[str] = mapped_column(Text)


class EntryDistortion(Base):
    __tablename__ = "entry_distortions"

    entry_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("entries.id", ondelete="CASCADE"), primary_key=True
    )
    distortion_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("distortions.id", ondelete="CASCADE"), primary_key=True
    )

    entry = relationship("Entry", back_populates="distortions")
    distortion = relationship("Distortion")
