from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TherapistFeedbackCreate(BaseModel):
    author_name: str = Field(min_length=1, max_length=120)
    note: str = Field(min_length=1)


class TherapistFeedbackUpdate(BaseModel):
    author_name: str | None = Field(default=None, min_length=1, max_length=120)
    note: str | None = Field(default=None, min_length=1)


class TherapistFeedbackRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    entry_id: str
    author_name: str
    note: str
    created_at: datetime
    updated_at: datetime
