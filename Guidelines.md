# GUIDELINES.md — Cognitia (CBT Journal App)

## 1. Project Overview

**Product Name:** Cognitia
**Tagline:** Your personal CBT companion — rewire one thought at a time.
**Type:** Personal CBT (Cognitive Behavioral Therapy) journaling app
**Owner:** Zana (single-user, self-hosted)
**Inspiration:** Therapist's hand-drawn ABC framework (Activating Event → Belief → Consequences) with cognitive distortion identification and Socratic thought-testing.

### Purpose
Cognitia is a private digital companion for practicing CBT exercises between therapy sessions. It guides the user through the classic ABC model, helps identify cognitive distortions, and walks them through evidence-based thought restructuring. The goal is to build self-awareness, track distortion patterns over time, and create a searchable record of healing progress.

### Design Philosophy
- **Calm, not clinical.** This is a healing space, not a medical device. Soft palette, generous whitespace, gentle micro-interactions.
- **Guided, not gatekept.** The app walks you through the flow but never blocks progress. Skip fields if you need to.
- **Private by design.** Single-user. Local database. No analytics SDKs. No telemetry.
- **Bilingual native.** English and Bahasa Indonesia are first-class equals. Every label, prompt, and distortion description has both.

---

## 2. Tech Stack

Matches the Lunavia portfolio standard.

### Backend
- **Framework:** FastAPI (Python 3.11+)
- **ORM:** SQLAlchemy 2.0 (async)
- **Database:** SQLite (file-based, single-user; upgradeable to Postgres if needed)
- **Migrations:** Alembic
- **Validation:** Pydantic v2
- **Auth:** Single-user PIN/passphrase (optional, stored hashed) — no multi-user system
- **API Docs:** Auto-generated via FastAPI `/docs`

### Frontend
- **Framework:** React 18 + Vite
- **Routing:** React Router v6
- **State:** TanStack Query (server state) + Zustand (UI state)
- **Styling:** Tailwind CSS + shadcn/ui components
- **Charts:** Recharts
- **Icons:** Lucide React
- **i18n:** react-i18next (EN/ID toggle)
- **Forms:** React Hook Form + Zod

### Dev Environment
- **Backend venv:** Python venv at `backend/.venv` — must be activated independently from other Lunavia projects (no PATH mixing — see lessons learned from Emitly/Compliya)
- **Frontend:** Node 18+, pnpm preferred
- **Ports:** Backend `8003`, Frontend `5173` (avoid conflicts with Emitly `8001` and Compliya `8002`)

---

## 3. Core Concepts (CBT Framework)

The app is structured around three primary concepts derived directly from the source diagram.

### 3.1 The ABC Model
Every journal entry follows the same three-stage flow:

**A — Activating Event** (the trigger)
- Prompt EN: *"What was the situation?"*
- Prompt ID: *"Ada situasi apa?"*
- Free-text field. Optional metadata: date, time, location, people involved.

**B — Belief** (the automatic thought)
- Prompt EN: *"What automatic thought came up?"*
- Prompt ID: *"Pikiran otomatis apa yang muncul?"*
- Tagged as: automatic, irrational, "unhelpful"
- User then identifies which **cognitive distortion(s)** apply (multi-select).

**C — Consequences** (emotional and behavioral response)
- Prompt EN: *"What was your emotional and behavioral response?"*
- Prompt ID: *"Respon emosi dan perilaku?"*
- Two sub-fields: emotion(s) felt + intensity (0–10 slider), and behavior(s) taken.

### 3.2 The Seven Cognitive Distortions
Hard-coded enum, taken directly from the therapist's list:

| Code | English | Bahasa Indonesia | Short description |
|------|---------|------------------|-------------------|
| `fortune_telling` | Fortune Telling | Meramal Masa Depan | Predicting bad outcomes without evidence |
| `personalization` | Personalization | Personalisasi | Blaming yourself for things outside your control |
| `mental_filtering` | Mental Filtering | Penyaringan Mental | Focusing only on the negative, ignoring positives |
| `overgeneralization` | Overgeneralization | Generalisasi Berlebihan | One bad event = "always" or "never" |
| `should_must` | "Should" / "Must" Statements | Pernyataan "Harusnya" / "Wajib" | Rigid rules about how things ought to be |
| `magnification_minimization` | Magnification / Minimization | Pembesaran / Pengecilan | Blowing up negatives, shrinking positives |
| `all_or_none` | All-or-None Thinking | Pemikiran Hitam-Putih | Black-and-white thinking, no middle ground |

Each distortion has:
- `code` (string ID, used in DB)
- `name_en`, `name_id`
- `description_en`, `description_id`
- `example_en`, `example_id` (a short illustrative example)

### 3.3 Testing Your Thoughts (the Socratic flow)
After identifying distortions, the user is guided through a three-step thought-testing exercise based on the bottom-right notes in the source diagram.

**Step 1 — Evidence Weighing**
Two parallel text columns:
- *Evidence supporting the belief*
- *Evidence against the belief*

**Step 2 — Reality Testing (Uji Realitas)**
Reframe prompt:
- EN: *"I'm thinking I'm [X]. Is there proof in my life that I am [X] or feel [X]?"*
- ID: *"Aku berpikir aku [X]. Ada bukti dalam hidupku ketika aku merasa [X]?"*

**Step 3 — Pragmatic Check**
Two prompts:
- EN: *"With this thought pattern, will it help me reach my goal (calmness)?"*
- ID: *"Dengan pola pikir ini, apakah pola pikir itu akan membantuku mencapai tujuan (tenang)?"*
- EN: *"How else could I do/think to improve the situation?"*

**Output:** A "Reframed Thought" — the new, more balanced belief the user lands on after the exercise.

---

## 4. Data Models

### 4.1 `Entry`
The top-level journal entry. One ABC cycle = one Entry.

```python
class Entry(Base):
    id: UUID (PK)
    created_at: datetime
    updated_at: datetime
    entry_date: date  # the day the event happened (may differ from created_at)

    # A — Activating Event
    situation: str  # free text
    location: str | None
    people_involved: str | None

    # B — Belief
    automatic_thought: str  # free text
    # distortions linked via EntryDistortion join table

    # C — Consequences
    emotion_intensity: int  # 0–10
    behavior: str  # free text

    # Testing Your Thoughts (optional — user may save partial entries)
    evidence_for: str | None
    evidence_against: str | None
    reality_test_response: str | None
    pragmatic_check_response: str | None
    alternative_action: str | None
    reframed_thought: str | None

    # Meta
    is_complete: bool  # true once all sections including reframe are filled
    language: str  # 'en' or 'id' — language used when writing this entry
```

### 4.2 `Emotion`
Many-to-many with Entry. User can tag multiple emotions per entry.

```python
class Emotion(Base):
    id: int (PK)
    code: str  # 'sadness', 'anxiety', 'anger', 'shame', 'guilt', 'fear', 'frustration', 'hopelessness', etc.
    name_en: str
    name_id: str

class EntryEmotion(Base):
    entry_id: UUID (FK)
    emotion_id: int (FK)
```

Seed with ~12 common emotions. Allow user-defined emotions later (v2).

### 4.3 `Distortion`
Static seed table — the seven distortions from §3.2.

```python
class Distortion(Base):
    id: int (PK)
    code: str  # see §3.2
    name_en: str
    name_id: str
    description_en: str
    description_id: str
    example_en: str
    example_id: str

class EntryDistortion(Base):
    entry_id: UUID (FK)
    distortion_id: int (FK)
```

### 4.4 `Settings` (single row)
```python
class Settings(Base):
    id: int (PK, always 1)
    language: str  # 'en' | 'id'
    pin_hash: str | None  # optional app lock
    daily_reminder_time: time | None
    theme: str  # 'light' | 'dark' | 'auto'
```

---

## 5. API Endpoints

All endpoints prefixed with `/api/v1`.

### Entries
- `POST /entries` — create new entry (returns ID; entry can be saved incomplete)
- `GET /entries` — list entries (query: `?from=&to=&distortion=&emotion=&search=`)
- `GET /entries/{id}` — fetch full entry
- `PATCH /entries/{id}` — update entry (used heavily during the multi-step flow)
- `DELETE /entries/{id}` — soft delete (move to trash, recoverable for 30 days)
- `POST /entries/{id}/complete` — mark entry as complete

### Distortions & Emotions
- `GET /distortions` — list all seven (with translations)
- `GET /emotions` — list seeded emotions

### Analytics
- `GET /analytics/distortion-frequency?from=&to=` — count of each distortion across entries in the range
- `GET /analytics/emotion-trend?from=&to=&granularity=day|week|month` — emotion intensity averages over time
- `GET /analytics/streak` — current journaling streak (consecutive days)
- `GET /analytics/summary` — total entries, completed entries, top 3 distortions, top 3 emotions, average intensity

### Settings
- `GET /settings`
- `PATCH /settings`

---

## 6. Frontend Routes & Screens

### 6.1 Routes
- `/` — Dashboard (recent entries + streak + quick stats)
- `/new` — New entry (multi-step ABC flow)
- `/entries` — History list with filters
- `/entries/:id` — Single entry detail (read + edit)
- `/insights` — Analytics & charts
- `/settings` — Language, PIN, reminder, theme

### 6.2 New Entry Flow (the heart of the app)
A **stepper-style multi-page form** matching the source diagram's numbered flow (note that the diagram numbers the circle as ① and the triangle as ②, meaning the therapist's intended teaching order is C → A → B → identify distortion → test → reframe; we follow this order).

**Step 1 — Consequences (Circle, red)** ①
- "How are you feeling right now?" → emotion multi-select + intensity slider
- "What did you do or want to do?" → behavior text
- *Rationale: the user usually opens the app *because* they're feeling something. Start there.*

**Step 2 — Activating Event (Triangle, purple)** ②
- "What happened?" → situation text
- Optional: location, people involved, date/time

**Step 3 — Belief (Square, blue)** ③
- "What automatic thought came up?" → automatic_thought text
- Tag the thought as automatic / irrational / unhelpful (visual chips, informational only)

**Step 4 — Identify Distortions** ④
- Show the seven distortions as cards with name + description + example
- Multi-select. User can pick "none" or skip.

**Step 5 — Test Your Thoughts** ⑤
- Sub-step 5a: Evidence For vs Against (two-column textarea)
- Sub-step 5b: Reality test prompt
- Sub-step 5c: Pragmatic check + alternative action
- Sub-step 5d: Write the reframed thought

**Final screen:** Summary card showing all sections + "Save & complete" or "Save as draft."

Every step has **Back / Next / Save & exit** buttons. Auto-save on every blur.

### 6.3 Visual Language
Honor the source diagram's geometry as a subtle motif:
- **Triangle** icon for "Event" sections (purple `#A855F7`)
- **Square** icon for "Belief" sections (blue `#3B82F6`)
- **Circle** icon for "Consequences" sections (red `#EF4444`)

Use these shapes as small inline icons in the entry detail view and dashboard. The shapes are a quiet nod to the therapist's whiteboard — keeps the human origin of this framework visible.

### 6.4 Insights Page (charts)
- **Distortion Frequency** — bar chart, sorted descending. "Which patterns show up most?"
- **Emotion Trend** — multi-line chart of average intensity per emotion over time
- **Calendar Heatmap** — entries-per-day for the last 90 days (GitHub-style)
- **Streak Card** — current streak + longest streak
- **Reframe Rate** — % of entries that reached the "reframed thought" stage (a healthy completion metric)

All charts respect the EN/ID language toggle.

---

## 7. Internationalization (EN/ID)

### 7.1 Approach
- All UI strings live in `frontend/src/locales/en.json` and `frontend/src/locales/id.json`.
- Distortions, emotions, and prompt templates are **stored bilingually in the DB**, not in i18n files (so the backend can return the right language based on `Settings.language`).
- The language toggle is **global and persistent** (top-right corner, also in Settings).
- User-written content (situation, thought, etc.) is stored as-is and **not auto-translated** — the user's voice stays the user's voice.

### 7.2 Mixed-language entries
Indonesian users often code-switch (Bahasa + English in one sentence). The app should never "correct" or flag this. Just store the raw text.

---

## 8. Project Structure

```
cognitia/
├── README.md
├── GUIDELINES.md           ← this file
├── backend/
│   ├── .venv/              ← project-specific venv (DO NOT share with Emitly/Compliya)
│   ├── pyproject.toml
│   ├── alembic.ini
│   ├── alembic/
│   │   └── versions/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models/
│   │   │   ├── entry.py
│   │   │   ├── distortion.py
│   │   │   ├── emotion.py
│   │   │   └── settings.py
│   │   ├── schemas/        ← Pydantic
│   │   ├── routers/
│   │   │   ├── entries.py
│   │   │   ├── distortions.py
│   │   │   ├── emotions.py
│   │   │   ├── analytics.py
│   │   │   └── settings.py
│   │   ├── services/
│   │   │   └── analytics.py
│   │   └── seed/
│   │       ├── distortions.py   ← the 7 distortions, bilingual
│   │       └── emotions.py      ← ~12 seeded emotions, bilingual
│   └── tests/
└── frontend/
    ├── package.json
    ├── vite.config.ts
    ├── tailwind.config.js
    ├── src/
    │   ├── main.tsx
    │   ├── App.tsx
    │   ├── locales/
    │   │   ├── en.json
    │   │   └── id.json
    │   ├── lib/
    │   │   ├── api.ts
    │   │   └── i18n.ts
    │   ├── components/
    │   │   ├── ui/                  ← shadcn primitives
    │   │   ├── shapes/              ← Triangle, Square, Circle SVG components
    │   │   ├── entry/
    │   │   │   ├── StepConsequences.tsx
    │   │   │   ├── StepActivating.tsx
    │   │   │   ├── StepBelief.tsx
    │   │   │   ├── StepDistortions.tsx
    │   │   │   ├── StepTesting.tsx
    │   │   │   └── EntryStepper.tsx
    │   │   └── insights/
    │   │       ├── DistortionChart.tsx
    │   │       ├── EmotionTrendChart.tsx
    │   │       └── CalendarHeatmap.tsx
    │   ├── pages/
    │   │   ├── Dashboard.tsx
    │   │   ├── NewEntry.tsx
    │   │   ├── EntryList.tsx
    │   │   ├── EntryDetail.tsx
    │   │   ├── Insights.tsx
    │   │   └── Settings.tsx
    │   ├── hooks/
    │   └── stores/
    └── tests/
```

---

## 9. Build Order (for Claude Code)

Build in this order so the app is testable end-to-end as early as possible.

**Phase 1 — Foundation**
1. Backend project scaffold (FastAPI + SQLAlchemy + Alembic).
2. DB models for Entry, Distortion, Emotion, EntryDistortion, EntryEmotion, Settings.
3. Seed scripts for the 7 distortions and ~12 emotions (bilingual).
4. Initial migration.

**Phase 2 — API**
5. CRUD endpoints for entries (`POST`, `GET`, `PATCH`, `DELETE`).
6. List endpoints for distortions and emotions.
7. Settings endpoints.

**Phase 3 — Frontend Foundation**
8. Vite + React + Tailwind + shadcn scaffold.
9. i18n setup with EN/ID JSON files and a language toggle.
10. API client (axios or fetch wrapper) + TanStack Query setup.
11. App shell: nav, language toggle, theme toggle, route skeleton.

**Phase 4 — The Core Flow**
12. New Entry stepper (5 steps as described in §6.2). Auto-save on blur.
13. Entry list page with filters.
14. Entry detail page (read + edit).

**Phase 5 — Analytics**
15. Backend analytics endpoints.
16. Insights page with the four charts.
17. Streak calculation.

**Phase 6 — Polish**
18. Settings page (language, theme, optional PIN, reminder time).
19. Soft delete & trash recovery.
20. Empty states, loading states, error boundaries.
21. Keyboard shortcuts (`N` for new entry, `/` for search).

---

## 10. Non-Negotiables (the "do not break these" list)

1. **No telemetry. No analytics SDKs. No third-party trackers.** This is a private mental health journal.
2. **All user-written content is stored verbatim** — no auto-correction, no auto-translation, no AI summarization unless explicitly requested in a future version.
3. **The seven distortions are fixed in this version.** No user-defined distortions in v1 (avoid scope creep).
4. **The app must work fully offline** once the frontend is loaded (assuming the local backend is running). No external API calls in the critical path.
5. **The visual triangle/square/circle motif must be preserved** — it's the bridge between the therapist's whiteboard and this app.
6. **Bilingual EN/ID is a first-class feature, not an afterthought.** Every label has both. Every distortion description has both.
7. **The flow is C → A → B → Distortion → Test → Reframe** (matching the numbered order on the source diagram). Do not rearrange to ABC alphabetical order.
8. **Backend port: 8003. Frontend port: 5173.** Each Lunavia project has its own venv and its own ports — never share.

---

## 11. Future Versions (not in v1, but worth noting)

- v2: Mood tracker (separate from entries — quick daily check-ins)
- v2: Custom distortions and emotions
- v2: Export to PDF (for sharing with therapist)
- v3: Voice-to-text for entries (mobile-first)
- v3: Optional encrypted cloud sync
- v3: Therapist-share mode (read-only link with PIN)

---

## 12. A Note from the Owner

This app exists because therapy works better when the homework is something you actually want to open. Make it feel like a friend, not a form. Soft edges. Patient prompts. No judgment. The user is healing — every interaction should feel like that's understood.