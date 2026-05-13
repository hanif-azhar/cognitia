from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_session
from ..models import DailyMood
from ..schemas.daily_mood import DailyMoodCreate, DailyMoodRead, DailyMoodUpdate

router = APIRouter(prefix="/mood", tags=["mood"])


async def _load(session: AsyncSession, mood_id: str) -> DailyMood:
    m = (
        await session.execute(select(DailyMood).where(DailyMood.id == mood_id))
    ).scalar_one_or_none()
    if m is None:
        raise HTTPException(status_code=404, detail="Mood entry not found")
    return m


@router.get("", response_model=list[DailyMoodRead])
async def list_moods(
    session: Annotated[AsyncSession, Depends(get_session)],
    from_: date | None = Query(default=None, alias="from"),
    to: date | None = None,
    limit: int = 200,
) -> list[DailyMoodRead]:
    stmt = select(DailyMood)
    if from_:
        stmt = stmt.where(DailyMood.mood_date >= from_)
    if to:
        stmt = stmt.where(DailyMood.mood_date <= to)
    stmt = stmt.order_by(DailyMood.mood_date.desc()).limit(limit)
    rows = (await session.execute(stmt)).scalars().all()
    return [DailyMoodRead.model_validate(r) for r in rows]


@router.get("/today", response_model=DailyMoodRead | None)
async def get_today(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> DailyMoodRead | None:
    today = date.today()
    row = (
        await session.execute(select(DailyMood).where(DailyMood.mood_date == today))
    ).scalar_one_or_none()
    return DailyMoodRead.model_validate(row) if row else None


@router.post("", response_model=DailyMoodRead, status_code=status.HTTP_201_CREATED)
async def create_mood(
    payload: DailyMoodCreate,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> DailyMoodRead:
    target_date = payload.mood_date or date.today()
    existing = (
        await session.execute(
            select(DailyMood).where(DailyMood.mood_date == target_date)
        )
    ).scalar_one_or_none()
    if existing is not None:
        raise HTTPException(
            status_code=409,
            detail="Mood for this date already exists; PATCH /mood/{id} to update.",
        )
    note = payload.note.strip() if payload.note else None
    m = DailyMood(mood_date=target_date, score=payload.score, note=note or None)
    session.add(m)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=409, detail="Mood for this date already exists.")
    await session.refresh(m)
    return DailyMoodRead.model_validate(m)


@router.patch("/{mood_id}", response_model=DailyMoodRead)
async def update_mood(
    mood_id: str,
    payload: DailyMoodUpdate,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> DailyMoodRead:
    m = await _load(session, mood_id)
    data = payload.model_dump(exclude_unset=True)
    if "score" in data and data["score"] is not None:
        m.score = data["score"]
    if "note" in data:
        m.note = data["note"].strip() if data["note"] else None
    await session.commit()
    await session.refresh(m)
    return DailyMoodRead.model_validate(m)


@router.delete("/{mood_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_mood(
    mood_id: str,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> None:
    m = await _load(session, mood_id)
    await session.delete(m)
    await session.commit()
