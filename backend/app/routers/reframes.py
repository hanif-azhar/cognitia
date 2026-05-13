from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..database import get_session
from ..models import Entry
from ..schemas.reframe import ReframeItem

router = APIRouter(prefix="/reframes", tags=["reframes"])


def _serialize(e: Entry) -> ReframeItem:
    return ReframeItem(
        entry_id=e.id,
        entry_date=e.entry_date,
        reframed_thought=e.reframed_thought or "",
        automatic_thought=e.automatic_thought,
        situation=e.situation,
        distortion_ids=[d.distortion_id for d in e.distortions],
    )


def _base_filter():
    return and_(
        Entry.deleted_at.is_(None),
        Entry.reframed_thought.is_not(None),
        func.length(func.trim(Entry.reframed_thought)) > 0,
    )


@router.get("", response_model=list[ReframeItem])
async def list_reframes(
    session: Annotated[AsyncSession, Depends(get_session)],
    limit: int = 50,
    offset: int = 0,
) -> list[ReframeItem]:
    stmt = (
        select(Entry)
        .options(selectinload(Entry.distortions))
        .where(_base_filter())
        .order_by(Entry.entry_date.desc(), Entry.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    rows = (await session.execute(stmt)).scalars().unique().all()
    return [_serialize(r) for r in rows]


@router.get("/random", response_model=ReframeItem | None)
async def random_reframe(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ReframeItem | None:
    stmt = (
        select(Entry)
        .options(selectinload(Entry.distortions))
        .where(_base_filter())
        .order_by(func.random())
        .limit(1)
    )
    row = (await session.execute(stmt)).scalar_one_or_none()
    return _serialize(row) if row else None
