from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class EntryBase(BaseModel):
    entry_date: date | None = None
    situation: str | None = None
    location: str | None = None
    people_involved: str | None = None
    automatic_thought: str | None = None
    emotion_intensity: int | None = Field(default=None, ge=0, le=10)
    behavior: str | None = None
    evidence_for: str | None = None
    evidence_against: str | None = None
    reality_test_response: str | None = None
    pragmatic_check_response: str | None = None
    alternative_action: str | None = None
    reframed_thought: str | None = None
    language: Literal["en", "id"] | None = None
    distortion_ids: list[int] | None = None
    emotion_ids: list[int] | None = None


class EntryCreate(EntryBase):
    pass


class EntryUpdate(EntryBase):
    pass


class EntryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
    updated_at: datetime
    entry_date: date
    situation: str | None
    location: str | None
    people_involved: str | None
    automatic_thought: str | None
    emotion_intensity: int
    behavior: str | None
    evidence_for: str | None
    evidence_against: str | None
    reality_test_response: str | None
    pragmatic_check_response: str | None
    alternative_action: str | None
    reframed_thought: str | None
    is_complete: bool
    language: str
    distortion_ids: list[int] = []
    emotion_ids: list[int] = []
