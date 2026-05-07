from datetime import date
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_session
from ..schemas.analytics import (
    AnalyticsSummary,
    DistortionFrequency,
    EmotionTrendPoint,
    StreakInfo,
)
from ..services import analytics as svc
from ..services.pdf import render_insights_pdf

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
