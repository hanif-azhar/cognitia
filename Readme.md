# Cognitia

Personal CBT (Cognitive Behavioral Therapy) journal app — a private digital companion for practicing the ABC model between therapy sessions.

> *Built from a therapist's whiteboard. The triangle, square, and circle on the home screen aren't just decoration — they're the original framework, preserved.*

## What it does
Walks you through a guided CBT flow: capture the situation, identify the automatic thought, recognize cognitive distortions, weigh the evidence, and land on a more balanced reframed thought. Tracks your distortion patterns over time.

## Stack
- **Backend:** FastAPI + SQLAlchemy + SQLite + Alembic
- **Frontend:** React + Vite + Tailwind + shadcn/ui + Recharts
- **Languages:** English & Bahasa Indonesia (first-class bilingual)

## Quick start

```bash
# Backend
cd backend
python -m venv .venv
source .venv/bin/activate    # or .venv\Scripts\activate on Windows
pip install -e .
alembic upgrade head
python -m app.seed.distortions
python -m app.seed.emotions
uvicorn app.main:app --reload --port 8003

# Frontend (new terminal)
cd frontend
pnpm install
pnpm dev    # runs on port 5173
```

Open http://localhost:5173

## Build spec
See **[GUIDELINES.md](./GUIDELINES.md)** for the full product specification — data models, API design, UI flow, build order, and non-negotiables.

## Bilingual seed data
See **[DISTORTIONS_SEED.md](./DISTORTIONS_SEED.md)** for the EN/ID content of the seven cognitive distortions and seeded emotions.

## Ports (Lunavia portfolio convention)
- Emitly: `8001`
- Compliya: `8002`
- **Cognitia: `8003`**
- Frontend: `5173` (per project, run one at a time)

Each project has its own venv. Never share. (Lessons from past PATH conflicts.)

## Status
v1 — personal use, single-user, local-first.