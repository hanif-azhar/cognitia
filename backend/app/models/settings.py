from datetime import time

from sqlalchemy import Integer, String, Time
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base


class Settings(Base):
    __tablename__ = "settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    language: Mapped[str] = mapped_column(String(2), default="en")
    pin_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    daily_reminder_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    theme: Mapped[str] = mapped_column(String(8), default="light")
