from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Settings


async def seed_settings(session: AsyncSession) -> None:
    existing = (await session.execute(select(Settings).where(Settings.id == 1))).scalar_one_or_none()
    if existing is None:
        session.add(Settings(id=1, language="en", theme="light"))
        await session.commit()
