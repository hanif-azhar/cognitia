from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import AsyncSessionLocal, Base, engine
from .routers import analytics, distortions, emotions, entries, settings as settings_router
from .seed.distortions import seed_distortions
from .seed.emotions import seed_emotions
from .seed.settings import seed_settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with AsyncSessionLocal() as session:
        await seed_distortions(session)
        await seed_emotions(session)
        await seed_settings(session)
    yield


app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["meta"])
async def health() -> dict[str, str]:
    return {"status": "ok", "app": settings.app_name}


api_prefix = "/api/v1"
app.include_router(entries.router, prefix=api_prefix)
app.include_router(distortions.router, prefix=api_prefix)
app.include_router(emotions.router, prefix=api_prefix)
app.include_router(analytics.router, prefix=api_prefix)
app.include_router(settings_router.router, prefix=api_prefix)
