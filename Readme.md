# Cognitia

Personal CBT (Cognitive Behavioral Therapy) journal app — a private digital companion for practicing the ABC model between therapy sessions.

> *Built from a therapist's whiteboard. The triangle, square, and circle on the home screen aren't just decoration — they're the original framework, preserved.*

---

## What it does

Cognitia walks you through a guided CBT flow modeled on the ABC technique (Ellis / Beck):

1. **C — Consequences.** Start where it hurts. Tag the emotions you notice and rate intensity 0–10.
2. **A — Activating event.** Describe what happened. Just the facts — situation, location, people involved.
3. **B — Belief.** Capture the automatic thought, unfiltered.
4. **Distortions.** Identify which of the seven cognitive distortions are at play (optional — this is for you, not a test).
5. **Test the thought.** Weigh evidence for and against, run a reality check and a pragmatic check, brainstorm an alternative action.
6. **Reframe.** Land on a more balanced thought you'd like to hold.

Then it tracks your patterns over time so you (and your therapist) can see what keeps coming up.

---

## Features

### Daily CBT journaling
- Five-step guided stepper in **C → A → B → Distortion → Test → Reframe** order (matches the source diagram).
- Save as draft at any step; come back to finish later. An entry is "complete" once situation, automatic thought, behavior, and reframed thought are all filled in.
- Soft delete with restore (entries go to trash, not gone).
- Per-entry PDF export — great for bringing to your therapist.

### Quick daily mood check-in
- A floating "How are you today?" card on the Dashboard with a 1–10 slider and an optional one-line note. Submit in under 10 seconds.
- One mood per day, enforced at the database level. If today's check-in already exists, the card flips to a compact view of today's score with an **Edit** button.
- The score is overlaid on the **Emotion trend** chart in Insights as a dashed sky-blue line — so you can see how your gut weekly feeling lines up with the emotions you tagged in actual entries.

### This week's pattern (distortion recap)
- A Dashboard card showing the **top 3 most frequent distortions from the last 7 days**, each with a mini bar and a count badge.
- If any one distortion shows up 3+ times in a week, a gentle amber alert appears:
  > *"You've noticed [Distortion] a lot this week. You're seeing it — that's the work."*
- Three stat tiles below: entries this week, completion rate, and dominant emotion of the week.

### Reframe library (evidence wall)
- A dedicated **Library** page at `/reframes` that surfaces every reframed thought you've written, reverse chronological.
- Each card shows the reframed thought front-and-center, the original automatic thought (smaller, muted), the date, and which distortions were tagged on that entry. One click jumps back to the full entry.
- **Reshuffle** card at the top — for bad days when you need to hear past-you's wisdom. Also surfaced as a small "From your reframe library" card on the Dashboard.

### Therapist feedback
- A "Therapist feedback" section appears on every entry detail page.
- Your therapist (or counselor, or a trusted reviewer) can open the entry on your device and leave a note: reviewer name + the note itself, with timestamp.
- Multiple notes per entry; each one is editable and deletable inline.
- No auth required — designed for the simple case where the reviewer is sitting next to you.

### Winning moments
- A daily log of small and big wins, separate from CBT entries — a gratitude / cherish stream.
- Quick-add card on the **Wins** page: text, optional tag (`work`, `family`, `health`, …), and date.
- Dashboard shows an amber "A win to cherish" card with a random past win you can reshuffle — so the good days re-surface on the gray ones.

### Insights
- **Distortion frequency** bar chart — see which patterns recur.
- **Emotion trend** line chart — average intensity over time, by emotion, with day/week/month granularity, with daily mood overlaid as a dashed line.
- **90-day calendar heatmap** — entries per day at a glance.
- **Reframe rate** — how often you make it to a reframed thought.
- **Streaks** — current and longest.
- Full insights PDF export.

### Session summary PDF (for your therapist)
- A "Session summary" section on the Insights page with a date range picker and one-click presets: last 14 / 30 / 90 days.
- **Generate session summary** downloads a clean, print-ready PDF designed to be handed to a psychologist.
- The PDF includes, scoped to the date range:
  - Total entries, completed entries, reframe rate, journaling streak
  - Top 3 distortions with a frequency bar
  - Top 3 emotions with average intensity
  - Every completed entry: date, situation, automatic thought, distortions tagged, reframed thought
  - All winning moments logged in the range
  - All therapist feedback notes in the range
- Honors the language toggle (EN/ID). Built on the same visual language as the rest of the app — triangle / square / circle palette, emerald reframe accent, soft footer rule.

### Bilingual, by design
- English and Bahasa Indonesia are first-class. Every label, every distortion, every emotion is bilingual.
- Toggle in the header. PDF exports honor your selected language.

### Privacy & ergonomics
- No telemetry, no analytics SDKs, no third-party trackers. Ever.
- All user-written content stored verbatim. No translation, no auto-correction, no LLM rewrite.
- Local-first SQLite database (`backend/cognitia.db`). Works offline once frontend assets are loaded and the backend is local.
- Optional PIN lock (set in **Settings**).
- Daily reminder time (also in **Settings**) — a gentle nudge, no spam.
- Light / Dark theme toggle, persisted.
- Keyboard shortcut: press **`N`** anywhere (outside an input) to open a new entry.

---

## Stack

- **Backend:** FastAPI + async SQLAlchemy + SQLite. Python 3.11+. ReportLab for PDF rendering.
- **Frontend:** React 18 + Vite + TypeScript + Tailwind. TanStack Query for data, Zustand for UI state, Recharts for charts, react-i18next for translations, react-hook-form for forms.
- **No migrations tool yet** — uses `Base.metadata.create_all` plus auto-seeding on startup. The DB file is created on first run. If you need versioned migrations later, add Alembic and snapshot from the existing schema.

---

## Quick start

### Backend (port 8003)

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

API docs: <http://127.0.0.1:8003/docs>

On first start the app auto-creates `cognitia.db` and seeds the 7 distortions, 12 emotions, and the singleton settings row. **No separate seed commands are needed.** New tables added later (therapist feedback, wins, daily mood) are auto-created on the next startup.

### Frontend (port 5173)

```bash
cd frontend
pnpm install      # or: npm install
pnpm dev          # or: npm run dev
```

Open <http://localhost:5173>. The Vite dev server proxies `/api` → `http://127.0.0.1:8003`.

### Production build

```bash
cd frontend
pnpm build        # type-checks then builds to dist/
```

---

## Project layout

```
Cognitia/
├── backend/
│   └── app/
│       ├── main.py                  # FastAPI app, lifespan, router wiring
│       ├── config.py                # app settings (env-driven)
│       ├── database.py              # async engine + session
│       ├── models/                  # SQLAlchemy models
│       │   ├── entry.py
│       │   ├── distortion.py        # Distortion + EntryDistortion join
│       │   ├── emotion.py           # Emotion + EntryEmotion join
│       │   ├── feedback.py          # TherapistFeedback
│       │   ├── winning_moment.py    # WinningMoment
│       │   ├── daily_mood.py        # DailyMood (unique per day)
│       │   └── settings.py
│       ├── schemas/                 # Pydantic request/response models
│       │                            # (incl. reframe.py, daily_mood.py)
│       ├── routers/                 # entries, distortions, emotions,
│       │                            # analytics, settings, feedback, wins,
│       │                            # mood, reframes
│       ├── services/
│       │   ├── analytics.py         # streak / freq / trend / weekly recap
│       │   └── pdf.py               # entry / insights / session-summary PDFs
│       └── seed/                    # distortions, emotions, settings
└── frontend/
    └── src/
        ├── App.tsx                  # routes
        ├── main.tsx
        ├── components/
        │   ├── ui/Layout.tsx
        │   ├── shapes/              # triangle / square / circle SVGs
        │   ├── entry/               # stepper + sections + therapist feedback
        │   └── dashboard/           # MoodCheckIn / WeeklyPattern / ReframeLibrary cards
        ├── pages/                   # Dashboard, NewEntry, EntryList,
        │                            # EntryDetail, Insights, Wins,
        │                            # ReframeLibrary, Settings
        ├── lib/                     # api client, i18n, utils
        ├── locales/                 # en.json, id.json
        └── stores/uiStore.ts        # Zustand store (theme, language)
```

---

## API surface

Base path: `/api/v1`.

| Resource | Endpoints |
|----------|-----------|
| Entries | `GET/POST /entries`, `GET/PATCH/DELETE /entries/{id}`, `POST /entries/{id}/restore`, `POST /entries/{id}/complete`, `GET /entries/{id}/pdf` |
| Distortions | `GET /distortions` |
| Emotions | `GET /emotions` |
| Analytics | `GET /analytics/summary`, `/distortion-frequency`, `/emotion-trend`, `/streak`, `/weekly-recap`, `/pdf`, `/session-summary/pdf` |
| Settings | `GET/PATCH /settings` |
| Therapist feedback | `GET/POST /entries/{id}/feedback`, `PATCH/DELETE /feedback/{fb_id}` |
| Wins | `GET/POST /wins`, `GET /wins/random`, `GET/PATCH/DELETE /wins/{id}` |
| Daily mood | `GET/POST /mood`, `GET /mood/today`, `PATCH/DELETE /mood/{id}` |
| Reframes | `GET /reframes`, `GET /reframes/random` |

Full OpenAPI at <http://127.0.0.1:8003/docs>.

---

## Visual motif

Triangle, square, and circle SVGs represent **activating event**, **belief**, and **consequences** throughout the app — header trio, stepper, dashboard, entry rows, detail headers, and the PDF exports. The shapes are the original whiteboard framework, kept literal so the geometry stays a memory aid rather than abstract branding.

Palette:
- Triangle / event: purple `#A855F7`
- Square / belief: blue `#3B82F6`
- Circle / consequences: red `#EF4444`
- Reframe accent: emerald `#10B981`
- Mood overlay (Insights chart): sky `#0EA5E9`

---

## Build spec & seed content

- **[Guidelines.md](./Guidelines.md)** — the full product specification: data models, API design, UI flow, build order, and non-negotiables.
- **[distortion_seed.md](./distortion_seed.md)** — bilingual EN/ID content for the seven cognitive distortions and seeded emotions.
- **[DEV.md](./DEV.md)** — short developer quickstart (mirrors the Quick start section above).

---

## Ports (Lunavia portfolio convention)

| Project   | Backend port |
|-----------|--------------|
| Emitly    | `8001`       |
| Compliya  | `8002`       |
| **Cognitia** | **`8003`** |

Frontend ports are per-project (5173 here), run one at a time. Each project keeps its own venv. Never share. (Lessons from past PATH conflicts.)

---

## Roadmap notes (not commitments)

- Versioned migrations via Alembic, once the schema stops shifting weekly.
- Optional shareable per-entry link so a remote therapist can leave feedback without touching your device.
- Resurfacing tuned to mood: pull a cherished win or reframe when the recent mood line dips.
- Day / month granularity for the mood overlay in Insights (currently weekly-bucketed).
- Custom distortions and emotions.

---

## Status

v1.5 — personal use, single-user, local-first. No accounts, no cloud, no telemetry. Built to outlast a side project.
