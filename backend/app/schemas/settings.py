from datetime import time
from typing import Literal

from pydantic import BaseModel, ConfigDict


class SettingsRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    language: Literal["en", "id"]
    daily_reminder_time: time | None
    theme: Literal["light", "dark", "auto"]
    has_pin: bool


class SettingsUpdate(BaseModel):
    language: Literal["en", "id"] | None = None
    daily_reminder_time: time | None = None
    theme: Literal["light", "dark", "auto"] | None = None
    pin: str | None = None  # plain; hashed before storage. empty string clears.
