from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class DailyMoodCreate(BaseModel):
    score: int = Field(ge=1, le=10)
    note: str | None = None
    mood_date: date | None = None


class DailyMoodUpdate(BaseModel):
    score: int | None = Field(default=None, ge=1, le=10)
    note: str | None = None


class DailyMoodRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    mood_date: date
    score: int
    note: str | None
    created_at: datetime
    updated_at: datetime
