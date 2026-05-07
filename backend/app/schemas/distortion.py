from pydantic import BaseModel, ConfigDict


class DistortionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name_en: str
    name_id: str
    description_en: str
    description_id: str
    example_en: str
    example_id: str
