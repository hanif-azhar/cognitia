from datetime import date, datetime, timedelta

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Distortion, Emotion, Entry, EntryDistortion, EntryEmotion
from ..schemas.analytics import (
    AnalyticsSummary,
    DistortionFrequency,
    EmotionTrendPoint,
    StreakInfo,
    WeeklyRecap,
)


async def distortion_frequency(
    session: AsyncSession, from_: date | None, to: date | None, limit: int | None = None
) -> list[DistortionFrequency]:
    stmt = (
        select(
            Distortion.id,
            Distortion.code,
            Distortion.name_en,
            Distortion.name_id,
            func.count(EntryDistortion.entry_id).label("count"),
        )
        .join(EntryDistortion, EntryDistortion.distortion_id == Distortion.id)
        .join(Entry, Entry.id == EntryDistortion.entry_id)
        .where(Entry.deleted_at.is_(None))
        .group_by(Distortion.id)
        .order_by(func.count(EntryDistortion.entry_id).desc())
    )
    if from_:
        stmt = stmt.where(Entry.entry_date >= from_)
    if to:
        stmt = stmt.where(Entry.entry_date <= to)
    if limit:
        stmt = stmt.limit(limit)
    rows = (await session.execute(stmt)).all()
    return [
        DistortionFrequency(
            distortion_id=r[0], code=r[1], name_en=r[2], name_id=r[3], count=r[4]
        )
        for r in rows
    ]


async def emotion_trend(
    session: AsyncSession,
    from_: date | None,
    to: date | None,
    granularity: str = "day",
) -> list[EmotionTrendPoint]:
    if granularity not in {"day", "week", "month"}:
        granularity = "day"
    fmt = {"day": "%Y-%m-%d", "week": "%Y-%W", "month": "%Y-%m"}[granularity]
    bucket = func.strftime(fmt, Entry.entry_date).label("bucket")
    stmt = (
        select(
            bucket,
            Emotion.id,
            Emotion.code,
            Emotion.name_en,
            Emotion.name_id,
            func.avg(Entry.emotion_intensity).label("avg_intensity"),
            func.count(Entry.id).label("count"),
        )
        .join(EntryEmotion, EntryEmotion.entry_id == Entry.id)
        .join(Emotion, Emotion.id == EntryEmotion.emotion_id)
        .where(Entry.deleted_at.is_(None))
        .group_by("bucket", Emotion.id)
        .order_by("bucket")
    )
    if from_:
        stmt = stmt.where(Entry.entry_date >= from_)
    if to:
        stmt = stmt.where(Entry.entry_date <= to)
    rows = (await session.execute(stmt)).all()
    out: list[EmotionTrendPoint] = []
    for bucket_str, eid, code, name_en, name_id, avg_int, cnt in rows:
        try:
            if granularity == "day":
                bucket_date = datetime.strptime(bucket_str, "%Y-%m-%d").date()
            elif granularity == "week":
                year, week = bucket_str.split("-")
                bucket_date = datetime.strptime(f"{year}-W{int(week):02d}-1", "%Y-W%W-%w").date()
            else:
                bucket_date = datetime.strptime(bucket_str + "-01", "%Y-%m-%d").date()
        except ValueError:
            bucket_date = date.today()
        out.append(
            EmotionTrendPoint(
                bucket=bucket_date,
                emotion_id=eid,
                code=code,
                name_en=name_en,
                name_id=name_id,
                avg_intensity=float(avg_int or 0),
                count=int(cnt),
            )
        )
    return out


async def streak(session: AsyncSession) -> StreakInfo:
    stmt = (
        select(Entry.entry_date)
        .where(Entry.deleted_at.is_(None))
        .group_by(Entry.entry_date)
        .order_by(Entry.entry_date.desc())
    )
    dates = [r[0] for r in (await session.execute(stmt)).all()]
    if not dates:
        return StreakInfo(current_streak=0, longest_streak=0, last_entry_date=None)

    today = date.today()
    current = 0
    if dates[0] == today or dates[0] == today - timedelta(days=1):
        cursor = dates[0]
        for d in dates:
            if d == cursor:
                current += 1
                cursor = cursor - timedelta(days=1)
            elif d < cursor:
                break

    longest = 1
    run = 1
    for i in range(1, len(dates)):
        if dates[i - 1] - dates[i] == timedelta(days=1):
            run += 1
            longest = max(longest, run)
        else:
            run = 1
    return StreakInfo(current_streak=current, longest_streak=longest, last_entry_date=dates[0])


async def summary(session: AsyncSession) -> AnalyticsSummary:
    total = (
        await session.execute(
            select(func.count(Entry.id)).where(Entry.deleted_at.is_(None))
        )
    ).scalar_one()
    completed = (
        await session.execute(
            select(func.count(Entry.id)).where(
                and_(Entry.deleted_at.is_(None), Entry.is_complete.is_(True))
            )
        )
    ).scalar_one()
    avg = (
        await session.execute(
            select(func.avg(Entry.emotion_intensity)).where(Entry.deleted_at.is_(None))
        )
    ).scalar_one() or 0
    top_d = await distortion_frequency(session, None, None, limit=3)
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
            .where(Entry.deleted_at.is_(None))
            .group_by(Emotion.id)
            .order_by(func.count(Entry.id).desc())
            .limit(3)
        )
    ).all()
    top_e = [
        EmotionTrendPoint(
            bucket=date.today(),
            emotion_id=r[0],
            code=r[1],
            name_en=r[2],
            name_id=r[3],
            avg_intensity=float(r[4] or 0),
            count=int(r[5]),
        )
        for r in top_e_rows
    ]
    return AnalyticsSummary(
        total_entries=total,
        completed_entries=completed,
        reframe_rate=(completed / total) if total else 0.0,
        average_intensity=float(avg),
        top_distortions=top_d,
        top_emotions=top_e,
        streak=await streak(session),
    )


ALERT_THRESHOLD = 3


async def weekly_recap(session: AsyncSession) -> WeeklyRecap:
    today = date.today()
    period_from = today - timedelta(days=6)
    period_to = today

    total = (
        await session.execute(
            select(func.count(Entry.id)).where(
                and_(
                    Entry.deleted_at.is_(None),
                    Entry.entry_date >= period_from,
                    Entry.entry_date <= period_to,
                )
            )
        )
    ).scalar_one()
    completed = (
        await session.execute(
            select(func.count(Entry.id)).where(
                and_(
                    Entry.deleted_at.is_(None),
                    Entry.is_complete.is_(True),
                    Entry.entry_date >= period_from,
                    Entry.entry_date <= period_to,
                )
            )
        )
    ).scalar_one()

    top_d = await distortion_frequency(session, period_from, period_to, limit=3)
    alert = next((d for d in top_d if d.count >= ALERT_THRESHOLD), None)

    dominant_row = (
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
                    Entry.entry_date >= period_from,
                    Entry.entry_date <= period_to,
                )
            )
            .group_by(Emotion.id)
            .order_by(func.count(Entry.id).desc(), func.avg(Entry.emotion_intensity).desc())
            .limit(1)
        )
    ).first()
    dominant = (
        EmotionTrendPoint(
            bucket=today,
            emotion_id=dominant_row[0],
            code=dominant_row[1],
            name_en=dominant_row[2],
            name_id=dominant_row[3],
            avg_intensity=float(dominant_row[4] or 0),
            count=int(dominant_row[5]),
        )
        if dominant_row
        else None
    )

    return WeeklyRecap(
        period_from=period_from,
        period_to=period_to,
        total_entries=total,
        completed_entries=completed,
        completion_rate=(completed / total) if total else 0.0,
        top_distortions=top_d,
        dominant_emotion=dominant,
        alert_distortion=alert,
    )
