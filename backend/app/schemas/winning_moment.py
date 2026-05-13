from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class WinningMomentCreate(BaseModel):
    text: str = Field(min_length=1)
    tag: str | None = Field(default=None, max_length=64)
    moment_date: date | None = None


class WinningMomentUpdate(BaseModel):
    text: str | None = Field(default=None, min_length=1)
    tag: str | None = Field(default=None, max_length=64)
    moment_date: date | None = None


class WinningMomentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    text: str
    tag: str | None
    moment_date: date
    created_at: datetime
    updated_at: datetime
