from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_session
from ..models import Emotion
from ..schemas.emotion import EmotionRead

router = APIRouter(prefix="/emotions", tags=["emotions"])


@router.get("", response_model=list[EmotionRead])
async def list_emotions(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> list[EmotionRead]:
    rows = (await session.execute(select(Emotion).order_by(Emotion.id))).scalars().all()
    return [EmotionRead.model_validate(r) for r in rows]
