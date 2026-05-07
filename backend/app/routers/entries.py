from datetime import date, datetime
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import Response
from sqlalchemy import and_, delete, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..database import get_session
from ..models import Distortion, Emotion, Entry, EntryDistortion, EntryEmotion
from ..schemas.entry import EntryCreate, EntryRead, EntryUpdate
from ..services.pdf import render_entry_pdf, slugify_filename

router = APIRouter(prefix="/entries", tags=["entries"])


def _serialize(e: Entry) -> EntryRead:
    return EntryRead(
        id=e.id,
        created_at=e.created_at,
        updated_at=e.updated_at,
        entry_date=e.entry_date,
        situation=e.situation,
        location=e.location,
        people_involved=e.people_involved,
        automatic_thought=e.automatic_thought,
        emotion_intensity=e.emotion_intensity,
        behavior=e.behavior,
        evidence_for=e.evidence_for,
        evidence_against=e.evidence_against,
        reality_test_response=e.reality_test_response,
        pragmatic_check_response=e.pragmatic_check_response,
        alternative_action=e.alternative_action,
        reframed_thought=e.reframed_thought,
        is_complete=e.is_complete,
        language=e.language,
        distortion_ids=[d.distortion_id for d in e.distortions],
        emotion_ids=[em.emotion_id for em in e.emotions],
    )


async def _load(session: AsyncSession, entry_id: str) -> Entry:
    stmt = (
        select(Entry)
        .options(selectinload(Entry.distortions), selectinload(Entry.emotions))
        .where(Entry.id == entry_id)
    )
    e = (await session.execute(stmt)).scalar_one_or_none()
    if e is None or e.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Entry not found")
    return e


def _is_complete(e: Entry) -> bool:
    required = [e.situation, e.automatic_thought, e.behavior, e.reframed_thought]
    return all(bool(x and x.strip()) for x in required)


async def _apply_payload(
    session: AsyncSession, entry: Entry, payload: EntryCreate | EntryUpdate
) -> None:
    data = payload.model_dump(exclude_unset=True)
    distortion_ids = data.pop("distortion_ids", None)
    emotion_ids = data.pop("emotion_ids", None)
    for k, v in data.items():
        setattr(entry, k, v)
    expire_attrs: list[str] = []
    if distortion_ids is not None:
        await session.execute(
            delete(EntryDistortion).where(EntryDistortion.entry_id == entry.id)
        )
        for did in distortion_ids:
            session.add(EntryDistortion(entry_id=entry.id, distortion_id=did))
        expire_attrs.append("distortions")
    if emotion_ids is not None:
        await session.execute(
            delete(EntryEmotion).where(EntryEmotion.entry_id == entry.id)
        )
        for eid in emotion_ids:
            session.add(EntryEmotion(entry_id=entry.id, emotion_id=eid))
        expire_attrs.append("emotions")
    entry.is_complete = _is_complete(entry)
    if expire_attrs:
        await session.flush()
        session.expire(entry, expire_attrs)


@router.post("", response_model=EntryRead, status_code=status.HTTP_201_CREATED)
async def create_entry(
    payload: EntryCreate,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> EntryRead:
    entry = Entry(
        entry_date=payload.entry_date or date.today(),
        language=payload.language or "en",
        emotion_intensity=payload.emotion_intensity or 0,
    )
    session.add(entry)
    await session.flush()
    await _apply_payload(session, entry, payload)
    await session.commit()
    fresh = await _load(session, entry.id)
    return _serialize(fresh)


@router.get("", response_model=list[EntryRead])
async def list_entries(
    session: Annotated[AsyncSession, Depends(get_session)],
    from_: date | None = Query(default=None, alias="from"),
    to: date | None = None,
    distortion: int | None = None,
    emotion: int | None = None,
    search: str | None = None,
    include_deleted: bool = False,
    limit: int = 100,
    offset: int = 0,
) -> list[EntryRead]:
    stmt = select(Entry).options(
        selectinload(Entry.distortions), selectinload(Entry.emotions)
    )
    if not include_deleted:
        stmt = stmt.where(Entry.deleted_at.is_(None))
    if from_:
        stmt = stmt.where(Entry.entry_date >= from_)
    if to:
        stmt = stmt.where(Entry.entry_date <= to)
    if distortion:
        stmt = stmt.join(EntryDistortion).where(EntryDistortion.distortion_id == distortion)
    if emotion:
        stmt = stmt.join(EntryEmotion).where(EntryEmotion.emotion_id == emotion)
    if search:
        like = f"%{search}%"
        stmt = stmt.where(
            or_(
                Entry.situation.ilike(like),
                Entry.automatic_thought.ilike(like),
                Entry.reframed_thought.ilike(like),
                Entry.behavior.ilike(like),
            )
        )
    stmt = stmt.order_by(Entry.entry_date.desc(), Entry.created_at.desc()).limit(limit).offset(offset)
    rows = (await session.execute(stmt)).scalars().unique().all()
    return [_serialize(r) for r in rows]


@router.get("/{entry_id}", response_model=EntryRead)
async def get_entry(
    entry_id: str,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> EntryRead:
    return _serialize(await _load(session, entry_id))


@router.patch("/{entry_id}", response_model=EntryRead)
async def update_entry(
    entry_id: str,
    payload: EntryUpdate,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> EntryRead:
    entry = await _load(session, entry_id)
    await _apply_payload(session, entry, payload)
    await session.commit()
    fresh = await _load(session, entry.id)
    return _serialize(fresh)


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_entry(
    entry_id: str,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> None:
    entry = await _load(session, entry_id)
    entry.deleted_at = datetime.utcnow()
    await session.commit()


@router.post("/{entry_id}/restore", response_model=EntryRead)
async def restore_entry(
    entry_id: str,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> EntryRead:
    stmt = (
        select(Entry)
        .options(selectinload(Entry.distortions), selectinload(Entry.emotions))
        .where(Entry.id == entry_id)
    )
    e = (await session.execute(stmt)).scalar_one_or_none()
    if e is None:
        raise HTTPException(status_code=404, detail="Entry not found")
    e.deleted_at = None
    await session.commit()
    return _serialize(e)


@router.get("/{entry_id}/pdf")
async def entry_pdf(
    entry_id: str,
    session: Annotated[AsyncSession, Depends(get_session)],
    lang: Literal["en", "id"] | None = None,
) -> Response:
    entry = await _load(session, entry_id)
    distortion_ids = [d.distortion_id for d in entry.distortions]
    emotion_ids = [em.emotion_id for em in entry.emotions]
    distortions: list[Distortion] = []
    emotions: list[Emotion] = []
    if distortion_ids:
        distortions = list(
            (
                await session.execute(
                    select(Distortion).where(Distortion.id.in_(distortion_ids)).order_by(Distortion.id)
                )
            )
            .scalars()
            .all()
        )
    if emotion_ids:
        emotions = list(
            (
                await session.execute(
                    select(Emotion).where(Emotion.id.in_(emotion_ids)).order_by(Emotion.id)
                )
            )
            .scalars()
            .all()
        )
    pdf = render_entry_pdf(entry, distortions, emotions, lang=lang)
    fname = f"cognitia-entry-{entry.entry_date.isoformat()}-{slugify_filename(entry.id[:8], entry.id[:8])}.pdf"
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{fname}"'},
    )


@router.post("/{entry_id}/complete", response_model=EntryRead)
async def complete_entry(
    entry_id: str,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> EntryRead:
    entry = await _load(session, entry_id)
    entry.is_complete = True
    await session.commit()
    return _serialize(entry)
