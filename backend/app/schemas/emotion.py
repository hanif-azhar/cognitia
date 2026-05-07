from pydantic import BaseModel, ConfigDict


class EmotionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name_en: str
    name_id: str
