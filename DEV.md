# Cognitia — Dev quickstart

This file documents the actual v1 build. The full product spec lives in [GUIDELINES.md](./Guidelines.md); the bilingual seed content in [distortion_seed.md](./distortion_seed.md).

> **Note on Alembic:** v1 skips Alembic and uses SQLAlchemy `create_all` plus auto-seeding on app startup. The DB file (`backend/cognitia.db`) is created on first run. If you need migrations later, add Alembic and snapshot from the existing schema.

## Backend (port 8003)

```bash
cd backend
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -e .
uvicorn app.main:app --reload --port 8003
```

API docs at http://127.0.0.1:8003/docs

On first start the app auto-creates `cognitia.db` and seeds the 7 distortions, 12 emotions, and the singleton settings row.

## Frontend (port 5173)

```bash
cd frontend
pnpm install      # or: npm install
pnpm dev          # or: npm run dev
```

Open http://localhost:5173. The Vite dev server proxies `/api` → `http://127.0.0.1:8003`.

## What's built

- **Backend:** FastAPI + async SQLAlchemy + SQLite. Models for `Entry`, `Distortion`, `Emotion`, `Settings` plus join tables. Routers: `entries` (CRUD + soft delete + restore + complete), `distortions`, `emotions`, `settings`, `analytics` (distortion frequency, emotion trend, streak, summary).
- **Frontend:** React + Vite + Tailwind + Recharts + TanStack Query + react-i18next + Zustand. EN/ID toggle in the header. Light/Dark theme toggle.
- **Pages:** Dashboard (greeting, streak, recent entries), New entry (5-step stepper in C → A → B → Distortion → Test → Reframe order, then summary), History (search + distortion + emotion filters), Entry detail (read + edit + soft-delete), Insights (distortion frequency bar, emotion trend lines, 90-day calendar heatmap, reframe rate), Settings (language, theme, daily reminder time, optional PIN).
- **Visual motif:** Triangle / Square / Circle SVGs are used for activating event / belief / consequences throughout — header trio, stepper, dashboard, entry rows, detail headers.
- **Keyboard:** `N` from anywhere (outside an input) opens a new entry.

## Non-negotiables honored

- No telemetry, no analytics SDKs, no third-party trackers.
- All user-written content stored verbatim. No translation, no auto-correction.
- Seven distortions are fixed; defined in `backend/app/seed/distortions.py`.
- Works offline once frontend assets are loaded and backend is local.
- EN/ID first-class — every label and distortion is bilingual.
- Stepper order matches the source diagram: Consequences → Event → Belief → Distortions → Test.
- Backend port 8003, frontend 5173.
