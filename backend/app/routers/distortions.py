from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_session
from ..models import Distortion
from ..schemas.distortion import DistortionRead

router = APIRouter(prefix="/distortions", tags=["distortions"])


@router.get("", response_model=list[DistortionRead])
async def list_distortions(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> list[DistortionRead]:
    rows = (await session.execute(select(Distortion).order_by(Distortion.id))).scalars().all()
    return [DistortionRead.model_validate(r) for r in rows]
