from datetime import date

from pydantic import BaseModel


class ReframeItem(BaseModel):
    entry_id: str
    entry_date: date
    reframed_thought: str
    automatic_thought: str | None
    situation: str | None
    distortion_ids: list[int] = []
