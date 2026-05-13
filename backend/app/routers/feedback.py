from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_session
from ..models import Entry, TherapistFeedback
from ..schemas.feedback import (
    TherapistFeedbackCreate,
    TherapistFeedbackRead,
    TherapistFeedbackUpdate,
)

router = APIRouter(tags=["feedback"])


async def _entry_or_404(session: AsyncSession, entry_id: str) -> Entry:
    e = (
        await session.execute(select(Entry).where(Entry.id == entry_id))
    ).scalar_one_or_none()
    if e is None or e.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Entry not found")
    return e


async def _feedback_or_404(session: AsyncSession, fb_id: str) -> TherapistFeedback:
    fb = (
        await session.execute(
            select(TherapistFeedback).where(TherapistFeedback.id == fb_id)
        )
    ).scalar_one_or_none()
    if fb is None:
        raise HTTPException(status_code=404, detail="Feedback not found")
    return fb


@router.get(
    "/entries/{entry_id}/feedback", response_model=list[TherapistFeedbackRead]
)
async def list_feedback(
    entry_id: str,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> list[TherapistFeedbackRead]:
    await _entry_or_404(session, entry_id)
    rows = (
        await session.execute(
            select(TherapistFeedback)
            .where(TherapistFeedback.entry_id == entry_id)
            .order_by(TherapistFeedback.created_at.desc())
        )
    ).scalars().all()
    return [TherapistFeedbackRead.model_validate(r) for r in rows]


@router.post(
    "/entries/{entry_id}/feedback",
    response_model=TherapistFeedbackRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_feedback(
    entry_id: str,
    payload: TherapistFeedbackCreate,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> TherapistFeedbackRead:
    await _entry_or_404(session, entry_id)
    fb = TherapistFeedback(
        entry_id=entry_id,
        author_name=payload.author_name.strip(),
        note=payload.note.strip(),
    )
    session.add(fb)
    await session.commit()
    await session.refresh(fb)
    return TherapistFeedbackRead.model_validate(fb)


@router.patch("/feedback/{fb_id}", response_model=TherapistFeedbackRead)
async def update_feedback(
    fb_id: str,
    payload: TherapistFeedbackUpdate,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> TherapistFeedbackRead:
    fb = await _feedback_or_404(session, fb_id)
    data = payload.model_dump(exclude_unset=True)
    if "author_name" in data and data["author_name"] is not None:
        fb.author_name = data["author_name"].strip()
    if "note" in data and data["note"] is not None:
        fb.note = data["note"].strip()
    await session.commit()
    await session.refresh(fb)
    return TherapistFeedbackRead.model_validate(fb)


@router.delete("/feedback/{fb_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_feedback(
    fb_id: str,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> None:
    fb = await _feedback_or_404(session, fb_id)
    await session.delete(fb)
    await session.commit()
