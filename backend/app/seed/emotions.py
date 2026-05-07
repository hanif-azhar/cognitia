from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Emotion

EMOTIONS = [
    {"code": "sadness", "name_en": "Sadness", "name_id": "Kesedihan"},
    {"code": "anxiety", "name_en": "Anxiety", "name_id": "Kecemasan"},
    {"code": "anger", "name_en": "Anger", "name_id": "Kemarahan"},
    {"code": "frustration", "name_en": "Frustration", "name_id": "Frustrasi"},
    {"code": "shame", "name_en": "Shame", "name_id": "Rasa Malu"},
    {"code": "guilt", "name_en": "Guilt", "name_id": "Rasa Bersalah"},
    {"code": "fear", "name_en": "Fear", "name_id": "Ketakutan"},
    {"code": "loneliness", "name_en": "Loneliness", "name_id": "Kesepian"},
    {"code": "hopelessness", "name_en": "Hopelessness", "name_id": "Putus Asa"},
    {"code": "overwhelm", "name_en": "Overwhelm", "name_id": "Kewalahan"},
    {"code": "disappointment", "name_en": "Disappointment", "name_id": "Kekecewaan"},
    {"code": "numbness", "name_en": "Numbness", "name_id": "Mati Rasa"},
]


async def seed_emotions(session: AsyncSession) -> None:
    existing = (await session.execute(select(Emotion.code))).scalars().all()
    existing_codes = set(existing)
    for e in EMOTIONS:
        if e["code"] not in existing_codes:
            session.add(Emotion(**e))
    await session.commit()
