from typing import Annotated

import bcrypt
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_session
from ..models import Settings
from ..schemas.settings import SettingsRead, SettingsUpdate

router = APIRouter(prefix="/settings", tags=["settings"])


async def _get_or_create(session: AsyncSession) -> Settings:
    s = (await session.execute(select(Settings).where(Settings.id == 1))).scalar_one_or_none()
    if s is None:
        s = Settings(id=1, language="en", theme="light")
        session.add(s)
        await session.commit()
    return s


def _to_read(s: Settings) -> SettingsRead:
    return SettingsRead(
        language=s.language,  # type: ignore[arg-type]
        daily_reminder_time=s.daily_reminder_time,
        theme=s.theme,  # type: ignore[arg-type]
        has_pin=bool(s.pin_hash),
    )


@router.get("", response_model=SettingsRead)
async def get_settings(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> SettingsRead:
    return _to_read(await _get_or_create(session))


@router.patch("", response_model=SettingsRead)
async def update_settings(
    payload: SettingsUpdate,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> SettingsRead:
    s = await _get_or_create(session)
    if payload.language is not None:
        s.language = payload.language
    if payload.theme is not None:
        s.theme = payload.theme
    if payload.daily_reminder_time is not None:
        s.daily_reminder_time = payload.daily_reminder_time
    if payload.pin is not None:
        if payload.pin == "":
            s.pin_hash = None
        else:
            if len(payload.pin) < 4:
                raise HTTPException(status_code=400, detail="PIN must be at least 4 characters")
            pin_bytes = payload.pin.encode("utf-8")[:72]
            s.pin_hash = bcrypt.hashpw(pin_bytes, bcrypt.gensalt()).decode("utf-8")
    await session.commit()
    return _to_read(s)
