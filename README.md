# EduVerse Backend (Prototype)

FastAPI backend implementing the two-branch diagnostic quiz and the
confidence-aware recommendation engine.

## Setup

```bash
pip install -r requirements.txt
```

## Run

```bash
uvicorn app.main:app --reload
```

The API will be live at `http://localhost:8000`.
Interactive docs (auto-generated, useful for testing without the frontend
built yet) are at `http://localhost:8000/docs`.

A SQLite database file (`eduverse.db`) is created automatically on first
run, seeded with two demo topics: **Thermodynamics** and **Data
Structures**, each with sample content (video/PDF/question bank) and quiz
questions. Delete `eduverse.db` and restart to reset to a clean seeded
state.

## How the core logic works

- **`app/recommendation.py`** — the two pieces that matter most for your
  pitch:
  - `confidence_flag()` — classifies each quiz answer as `confident`,
    `shaky`, or `guess` based on response time and whether the student
    switched their answer, not just correctness.
  - `score_content()` — ranks candidate content against a student's
    detected weak subtopics + format/difficulty preference, and returns a
    plain-language reason for every recommendation (the "Recommended
    because..." line).
- **`app/seed_data.py`** — swap this out for real YouTube Data API results
  later; the `Content` table shape stays the same either way.

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| POST | `/students` | Create a student profile |
| GET | `/students/{id}` | Fetch a student |
| GET | `/topics` | List available topics |
| POST | `/topics/start` | Branch: `prior_knowledge` = `never_studied` (returns beginner content directly) or `studied_before` (returns quiz questions + disclaimer text) |
| POST | `/quiz/submit` | Submit quiz responses (with per-question timing + initial/final answer); returns detected weak subtopics + ranked recommendations |
| POST | `/feedback` | Record thumbs up/down on a piece of content |

## Connecting the Lovable frontend

Point the frontend's quiz screen at `/topics/start` and `/quiz/submit`.
The frontend is already tracking `time_taken_seconds` and the
initial-vs-final answer per question (per the earlier prompt) — send those
exact fields in the `/quiz/submit` request body and the confidence logic
above does the rest.

CORS is wide open (`allow_origins=["*"]`) for the demo — tighten this
before any real deployment.
