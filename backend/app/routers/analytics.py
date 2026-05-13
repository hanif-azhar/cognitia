from datetime import date, datetime
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..database import get_session
from ..models import (
    Distortion,
    Emotion,
    Entry,
    EntryEmotion,
    TherapistFeedback,
    WinningMoment,
)
from ..schemas.analytics import (
    AnalyticsSummary,
    DistortionFrequency,
    EmotionTrendPoint,
    StreakInfo,
    WeeklyRecap,
)
from ..services import analytics as svc
from ..services.pdf import render_insights_pdf, render_session_summary_pdf

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/distortion-frequency", response_model=list[DistortionFrequency])
async def get_distortion_frequency(
    session: Annotated[AsyncSession, Depends(get_session)],
    from_: date | None = Query(default=None, alias="from"),
    to: date | None = None,
) -> list[DistortionFrequency]:
    return await svc.distortion_frequency(session, from_, to)


@router.get("/emotion-trend", response_model=list[EmotionTrendPoint])
async def get_emotion_trend(
    session: Annotated[AsyncSession, Depends(get_session)],
    from_: date | None = Query(default=None, alias="from"),
    to: date | None = None,
    granularity: str = "day",
) -> list[EmotionTrendPoint]:
    return await svc.emotion_trend(session, from_, to, granularity)


@router.get("/streak", response_model=StreakInfo)
async def get_streak(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> StreakInfo:
    return await svc.streak(session)


@router.get("/summary", response_model=AnalyticsSummary)
async def get_summary(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> AnalyticsSummary:
    return await svc.summary(session)


@router.get("/weekly-recap", response_model=WeeklyRecap)
async def get_weekly_recap(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> WeeklyRecap:
    return await svc.weekly_recap(session)


@router.get("/session-summary/pdf")
async def session_summary_pdf(
    session: Annotated[AsyncSession, Depends(get_session)],
    from_: date | None = Query(default=None, alias="from"),
    to: date | None = None,
    lang: Literal["en", "id"] = "en",
) -> Response:
    from datetime import timedelta
    from sqlalchemy import func

    today = date.today()
    if to is None:
        to = today
    if from_ is None:
        from_ = to - timedelta(days=13)

    period_summary = await svc.summary(session)
    period_freq = await svc.distortion_frequency(session, from_, to)
    period_summary.top_distortions = period_freq[:3]

    top_e_rows = (
        await session.execute(
            select(
                Emotion.id,
                Emotion.code,
                Emotion.name_en,
                Emotion.name_id,
                func.avg(Entry.emotion_intensity),
                func.count(Entry.id),
            )
            .join(EntryEmotion, EntryEmotion.emotion_id == Emotion.id)
            .join(Entry, Entry.id == EntryEmotion.entry_id)
            .where(
                and_(
                    Entry.deleted_at.is_(None),
                    Entry.entry_date >= from_,
                    Entry.entry_date <= to,
                )
            )
            .group_by(Emotion.id)
            .order_by(func.count(Entry.id).desc())
            .limit(3)
        )
    ).all()
    period_summary.top_emotions = [
        EmotionTrendPoint(
            bucket=today,
            emotion_id=r[0],
            code=r[1],
            name_en=r[2],
            name_id=r[3],
            avg_intensity=float(r[4] or 0),
            count=int(r[5]),
        )
        for r in top_e_rows
    ]

    # Completed entries in range
    entries_stmt = (
        select(Entry)
        .options(selectinload(Entry.distortions), selectinload(Entry.emotions))
        .where(
            and_(
                Entry.deleted_at.is_(None),
                Entry.is_complete.is_(True),
                Entry.entry_date >= from_,
                Entry.entry_date <= to,
            )
        )
        .order_by(Entry.entry_date.desc(), Entry.created_at.desc())
    )
    entries = list((await session.execute(entries_stmt)).scalars().unique().all())

    # Resolve distortion/emotion objects for each entry
    all_d_ids: set[int] = set()
    all_e_ids: set[int] = set()
    for e in entries:
        for d in e.distortions:
            all_d_ids.add(d.distortion_id)
        for em in e.emotions:
            all_e_ids.add(em.emotion_id)
    d_objects: dict[int, Distortion] = {}
    e_objects: dict[int, Emotion] = {}
    if all_d_ids:
        d_rows = (
            await session.execute(select(Distortion).where(Distortion.id.in_(all_d_ids)))
        ).scalars().all()
        d_objects = {d.id: d for d in d_rows}
    if all_e_ids:
        e_rows = (
            await session.execute(select(Emotion).where(Emotion.id.in_(all_e_ids)))
        ).scalars().all()
        e_objects = {em.id: em for em in e_rows}
    entry_distortion_map = {
        e.id: [d_objects[d.distortion_id] for d in e.distortions if d.distortion_id in d_objects]
        for e in entries
    }
    entry_emotion_map = {
        e.id: [e_objects[em.emotion_id] for em in e.emotions if em.emotion_id in e_objects]
        for e in entries
    }

    # Wins in range
    wins = list(
        (
            await session.execute(
                select(WinningMoment)
                .where(
                    and_(
                        WinningMoment.deleted_at.is_(None),
                        WinningMoment.moment_date >= from_,
                        WinningMoment.moment_date <= to,
                    )
                )
                .order_by(WinningMoment.moment_date.desc())
            )
        )
        .scalars()
        .all()
    )

    # Feedback in range — by feedback created_at date inside the period, paired with entry
    fb_stmt = (
        select(TherapistFeedback, Entry)
        .join(Entry, Entry.id == TherapistFeedback.entry_id)
        .where(
            and_(
                Entry.deleted_at.is_(None),
                TherapistFeedback.created_at >= datetime.combine(from_, datetime.min.time()),
                TherapistFeedback.created_at
                < datetime.combine(to, datetime.min.time()).replace(hour=23, minute=59, second=59),
            )
        )
        .order_by(TherapistFeedback.created_at.desc())
    )
    feedback_rows = list((await session.execute(fb_stmt)).all())
    feedback_items: list[tuple[TherapistFeedback, Entry]] = [(r[0], r[1]) for r in feedback_rows]

    pdf = render_session_summary_pdf(
        summary=period_summary,
        distortion_freq=period_freq,
        period_from=from_,
        period_to=to,
        entries=entries,
        entry_distortion_map=entry_distortion_map,
        entry_emotion_map=entry_emotion_map,
        wins=wins,
        feedback_items=feedback_items,
        lang=lang,
    )
    fname = f"cognitia-session-{from_.isoformat()}-to-{to.isoformat()}.pdf"
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{fname}"'},
    )


@router.get("/pdf")
async def insights_pdf(
    session: Annotated[AsyncSession, Depends(get_session)],
    from_: date | None = Query(default=None, alias="from"),
    to: date | None = None,
    lang: Literal["en", "id"] = "en",
) -> Response:
    summary = await svc.summary(session)
    freq = await svc.distortion_frequency(session, from_, to)
    trend = await svc.emotion_trend(session, from_, to, "week")
    pdf = render_insights_pdf(summary, freq, trend, from_, to, lang=lang)
    today = date.today().isoformat()
    fname = f"cognitia-insights-{today}.pdf"
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{fname}"'},
    )
