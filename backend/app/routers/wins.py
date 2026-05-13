from datetime import date, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_session
from ..models import WinningMoment
from ..schemas.winning_moment import (
    WinningMomentCreate,
    WinningMomentRead,
    WinningMomentUpdate,
)

router = APIRouter(prefix="/wins", tags=["wins"])


async def _load(session: AsyncSession, win_id: str) -> WinningMoment:
    w = (
        await session.execute(select(WinningMoment).where(WinningMoment.id == win_id))
    ).scalar_one_or_none()
    if w is None or w.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Winning moment not found")
    return w


@router.post(
    "", response_model=WinningMomentRead, status_code=status.HTTP_201_CREATED
)
async def create_win(
    payload: WinningMomentCreate,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> WinningMomentRead:
    w = WinningMoment(
        text=payload.text.strip(),
        tag=payload.tag.strip() if payload.tag else None,
        moment_date=payload.moment_date or date.today(),
    )
    session.add(w)
    await session.commit()
    await session.refresh(w)
    return WinningMomentRead.model_validate(w)


@router.get("", response_model=list[WinningMomentRead])
async def list_wins(
    session: Annotated[AsyncSession, Depends(get_session)],
    from_: date | None = Query(default=None, alias="from"),
    to: date | None = None,
    tag: str | None = None,
    search: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[WinningMomentRead]:
    stmt = select(WinningMoment).where(WinningMoment.deleted_at.is_(None))
    if from_:
        stmt = stmt.where(WinningMoment.moment_date >= from_)
    if to:
        stmt = stmt.where(WinningMoment.moment_date <= to)
    if tag:
        stmt = stmt.where(WinningMoment.tag == tag)
    if search:
        like = f"%{search}%"
        stmt = stmt.where(WinningMoment.text.ilike(like))
    stmt = (
        stmt.order_by(WinningMoment.moment_date.desc(), WinningMoment.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    rows = (await session.execute(stmt)).scalars().all()
    return [WinningMomentRead.model_validate(r) for r in rows]


@router.get("/random", response_model=WinningMomentRead | None)
async def random_win(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> WinningMomentRead | None:
    stmt = (
        select(WinningMoment)
        .where(WinningMoment.deleted_at.is_(None))
        .order_by(func.random())
        .limit(1)
    )
    row = (await session.execute(stmt)).scalar_one_or_none()
    return WinningMomentRead.model_validate(row) if row else None


@router.get("/{win_id}", response_model=WinningMomentRead)
async def get_win(
    win_id: str,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> WinningMomentRead:
    return WinningMomentRead.model_validate(await _load(session, win_id))


@router.patch("/{win_id}", response_model=WinningMomentRead)
async def update_win(
    win_id: str,
    payload: WinningMomentUpdate,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> WinningMomentRead:
    w = await _load(session, win_id)
    data = payload.model_dump(exclude_unset=True)
    if "text" in data and data["text"] is not None:
        w.text = data["text"].strip()
    if "tag" in data:
        w.tag = data["tag"].strip() if data["tag"] else None
    if "moment_date" in data and data["moment_date"] is not None:
        w.moment_date = data["moment_date"]
    await session.commit()
    await session.refresh(w)
    return WinningMomentRead.model_validate(w)


@router.delete("/{win_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_win(
    win_id: str,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> None:
    w = await _load(session, win_id)
    w.deleted_at = datetime.utcnow()
    await session.commit()
