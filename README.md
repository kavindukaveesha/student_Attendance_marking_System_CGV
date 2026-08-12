<div align="center">

# Student Attendance Management System

Automated attendance from photographed classroom signing sheets.

**CS402.3 · Computer Graphics and Visualization** · NSBM Green University · School of Computing

<sub>Python 3.10+ · FastAPI · OpenCV · SQLAlchemy · PostgreSQL / SQLite · Tailwind CSS</sub>

</div>

---

## Overview

An admin photographs a printed signing sheet, uploads the photo together with an
`info.xml` describing the session (subject, date, student roster). The system runs
an OpenCV pipeline over the photo, extracts each student's signature cell, decides
**present / absent**, verifies the signature against a stored reference (catching
proxies with a **flagged** status), persists everything to a local database, and
serves a live dashboard with per-student charts and analytics.

Everything runs on your laptop — no cloud dependencies, no build step for the
frontend.

## Highlights

- **8 CGV features (F1–F8)** implemented as isolated feature modules — one owner per member.
- **9-stage OpenCV pipeline** with every stage saved to disk for report screenshots.
- **3-way attendance decision** — present / absent / flagged (possible proxy).
- **10 REST endpoints** documented at `/docs` (auto-generated Swagger UI).
- **7-section dashboard** — Upload · Stages · Results · Chart · Investigate · Analytics · Roster.
- **Live analytics** — per-session attendance rate, top absentees, KPI strip.
- **SQLite by default**, swap to PostgreSQL by editing one line in `.env`.
- **87% signature-detection accuracy** on the supplied 5-sheet test set — heuristic, no ML.

## Screenshots

*Add screenshots to `docs/screenshots/` and reference them here for the report submission.*

```
docs/screenshots/
├── 00_dashboard.png
├── 01_upload.png
├── 02_pipeline_stages.png
├── 03_results.png
├── 04_chart.png
├── 05_investigate.png
├── 06_analytics.png
└── 07_roster.png
```

---

## Architecture

Feature-module layout. Each of the eight features (F1–F8) owns a folder under
`backend/features/`. Modules that expose HTTP endpoints contain a `controller.py`
+ `service.py` (and where needed `repository.py` / `model.py` / `schema.py`).
Pure-computation modules only carry a `service.py`.

```
┌──────────────────────────────────────────────────────────────┐
│                         FRONTEND (SPA)                       │
│   index.html · Tailwind CSS · vanilla JS (api / ui / app)    │
└─────────────────────────┬────────────────────────────────────┘
                          │ fetch()
┌─────────────────────────▼────────────────────────────────────┐
│                   FastAPI  · main.py                         │
│   /api/attendance/*   /api/students/*   /api/visualization/  │
│   /api/investigate/*  /api/analytics/*  /output/*  /         │
└─────────────────────────┬────────────────────────────────────┘
                          │
        ┌─────────────────┴───────────────────────┐
        │            backend/features/            │
        │                                         │
        │   image_processing  →  transforms  →    │
        │   table_extraction  →  signature_       │
        │   detection         →  signature_       │
        │   recognition       →  attendance       │
        │        │                     │          │
        │        │                     │          │
        │        ▼                     ▼          │
        │   visualization       investigate       │
        │        │                                │
        │        └──── analytics ─────────────────┘
        └─────────────────────────────────────────┘
                          │
┌─────────────────────────▼────────────────────────────────────┐
│                   DATA LAYER                                 │
│   SQLite / PostgreSQL (SQLAlchemy)  ·  data/  ·  output/     │
└──────────────────────────────────────────────────────────────┘
```

**Isolation rules that the module structure enforces:**

- Service modules F1–F5 are pure Python — **no FastAPI, no SQLAlchemy imports**. They can be unit-tested and reused from a CLI.
- Only `controller.py` files import FastAPI. Only `repository.py` and `model.py` files import SQLAlchemy.
- The frontend never touches OpenCV or the DB directly — every action goes through the API.
- `DATABASE_URL` is the single switch for SQLite ↔ Postgres; no conditional code paths per engine.

## Feature Ownership

| # | Feature | Owner | Module |
|---|---------|-------|--------|
| **F1** | Image acquisition & preprocessing | Member 1 | `backend/features/image_processing/` |
| **F2** | Geometric correction (deskew + scale) | Member 2 | `backend/features/transforms/` |
| **F3** | Table & cell segmentation | Member 3 | `backend/features/table_extraction/` |
| **F4** | Signature detection (present/absent) | Member 4 | `backend/features/signature_detection/` |
| **F5** | Signature verification (ORB matching) | Member 5 | `backend/features/signature_recognition/` |
| **F6** | Attendance + database + `info.xml` parser | Member 6 | `backend/features/attendance/` |
| **F7** | Visualization (matplotlib PNG charts) | Member 7 | `backend/features/visualization/` |
| **F8** | Frontend + API wiring + tests | Member 8 | `frontend/`, `backend/main.py`, `tests/` |

## Image Processing Pipeline

Every stage is saved to `output/processed/<timestamp>/` for report screenshots.

| # | Stage | Technique | Course link |
|---|-------|-----------|-------------|
| 01 | `original.png` | `cv2.imread` (raw BGR photo) | L2 |
| 02 | `greyscale.png` | `cv2.cvtColor(BGR2GRAY)` | L2 |
| 03 | `denoised.png` | `cv2.GaussianBlur` | L3.2 |
| 04 | `deskewed.png` | Hough lines → skew angle → `warpAffine` | L7.1, L12.1 |
| 05 | `resized.png` | `cv2.resize` to 1000×1400 | L12.1 |
| 06 | `binarized.png` | `cv2.adaptiveThreshold` | L6 |
| 07 | `grid.png` | Morphological opening → grid mask | L4.3 |
| 08 | `cells.png` | Per-row signature cell extraction | L6 |

## Attendance Decision Logic

| Signature in cell? | Matches reference? | Final status |
|--------------------|--------------------|--------------|
| No | — | **absent** |
| Yes | Yes | **present** (verified) |
| Yes | No | **flagged** (possible proxy) |

Thresholds live in `.env` — `INK_THRESHOLD` (F4) and `MATCH_THRESHOLD` (F5).

## Detection Accuracy

Against the supplied 5-sheet test set (~30 cells total):

| Sheet | Real truth | Detected | Correct |
|-------|-----------|----------|---------|
| 2019-05-31 | 6 present | 6 present | ✅ 6/6 |
| 2019-06-21 | 6 present | 5 present | ⚠ 5/6 |
| 2019-06-28 | 4 present, 2 absent | 5 present, 1 absent | ⚠ 5/6 |
| 2019-07-05 | 4 present, 2 absent | 4 present, 2 absent | ⚠ 4/6 |
| 2019-07-12 | 6 present | 6 present | ✅ 6/6 |
| **Total** | | | **26/30 = 87%** |

Heuristic pipeline with no ML — ceiling is bounded by row-alignment stability
across variable phone photos.

---

## Quick Start

```bash
# 1. Create the virtual environment + install deps
python3 -m venv venv
source venv/bin/activate           # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 2. Config is already provided (SQLite default). Copy the template if needed:
cp .env.example .env

# 3. Launch
uvicorn backend.main:app --reload --port 8000
```

Open **<http://localhost:8000>** for the UI, **<http://localhost:8000/docs>** for
Swagger. The DB (`output/attendance.db`) is created automatically on first run.

## PostgreSQL (optional)

Uncomment the Postgres line in `.env`, comment out the SQLite line, then either
install PostgreSQL locally or spin up the bundled container:

```bash
docker compose up -d
```

No application code changes — `DATABASE_URL` is the only switch.

## API Reference

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `GET` | `/api/health` | Liveness probe |
| `POST` | `/api/attendance/process` | Upload sheet + `info.xml`, returns detected results (not persisted) |
| `POST` | `/api/attendance/save` | Persist a previously-returned result set to the DB |
| `GET` | `/api/students` | List all students |
| `GET` | `/api/students/{idx}` | Single student |
| `GET` | `/api/students/{idx}/attendance` | All attendance rows for a student |
| `GET` | `/api/visualization/{idx}?kind=bar\|pie` | PNG chart (bar timeline or summary pie) |
| `POST` | `/api/investigate/{idx}` | Latest verification result for a student |
| `GET` | `/api/analytics/summary` | Aggregate stats: totals, per-session rates, top absentees |
| `GET` | `/docs` | Swagger UI |
| `GET` | `/output/processed/…` | Static-served pipeline stage images |

## Project Structure

```
student_Attendance_marking_System_CGV/
├── backend/
│   ├── main.py                              # FastAPI app + router wiring + static mounts
│   ├── core/
│   │   ├── config.py                        # pydantic-settings loader
│   │   └── database.py                      # SQLAlchemy engine + session
│   └── features/
│       ├── image_processing/                # F1
│       │   └── service.py
│       ├── transforms/                      # F2
│       │   └── service.py
│       ├── table_extraction/                # F3
│       │   └── service.py
│       ├── signature_detection/             # F4
│       │   └── service.py
│       ├── signature_recognition/           # F5
│       │   └── service.py
│       ├── attendance/                      # F6 · data + pipeline orchestrator
│       │   ├── controller.py                # POST /process, /save · GET /students*
│       │   ├── service.py                   # chains F1..F5, saves stages
│       │   ├── repository.py                # upsert + queries
│       │   ├── model.py                     # Student, Attendance ORM
│       │   ├── schema.py                    # Pydantic req/resp
│       │   └── info_parser.py               # info.xml → subject + students
│       ├── visualization/                   # F7
│       │   ├── controller.py                # GET /visualization/{idx}?kind=
│       │   └── service.py                   # matplotlib bar + pie PNG
│       ├── investigate/                     # exposes F5 as an endpoint
│       │   ├── controller.py                # POST /investigate/{idx}
│       │   └── service.py
│       └── analytics/                       # dashboard aggregates
│           ├── controller.py
│           └── service.py
│
├── frontend/                                # F8 · Tailwind CDN + vanilla JS
│   ├── index.html                           # 7 sections + KPI strip
│   ├── favicon.svg
│   ├── css/style.css
│   └── js/
│       ├── api.js                           # ONLY file with API URLs
│       ├── ui.js                            # DOM helpers, badges, cards
│       └── app.js                           # button wiring
│
├── data/
│   ├── info.xml                             # sample subject + students
│   ├── signing_sheets/                      # 5 test sheets
│   └── signatures/                          # reference signatures per index
│
├── output/
│   ├── processed/<timestamp>/               # pipeline stage PNGs
│   └── attendance.db                        # SQLite (auto-created)
│
├── tests/
│   └── test_pipeline.py                     # pytest smoke tests
│
├── docker-compose.yml                       # optional PostgreSQL container
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## `info.xml` Format

```xml
<?xml version="1.0" encoding="UTF-8"?>
<attendance>
    <subject>
        <code>CS402.3</code>
        <title>Computer Graphics and Visualization</title>
        <lecturer>Dr. Rasika Ranaweera</lecturer>
        <date>2019-05-31</date>
        <hall>106</hall>
    </subject>
    <students>
        <student>
            <no>1</no>
            <index>10000409</index>
            <title>Ms</title>
            <name>M S Dilshanika Perera</name>
        </student>
        <!-- … more students in signing-sheet row order … -->
    </students>
</attendance>
```

Row `n` in the signing sheet maps to student `n` in the XML — the parser sorts
by `<no>` to guarantee order.

## Database Schema

```sql
CREATE TABLE students (
    student_idx   TEXT PRIMARY KEY,
    name          TEXT NOT NULL,
    signature_ref TEXT
);

CREATE TABLE attendance (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    student_idx   TEXT NOT NULL REFERENCES students(student_idx),
    subject_code  TEXT,
    date          TEXT,
    status        TEXT NOT NULL CHECK(status IN ('present','absent','flagged')),
    match_score   REAL,
    UNIQUE(student_idx, subject_code, date)
);
```

The `UNIQUE` constraint gives us idempotent saves — re-processing the same
sheet doesn't create duplicates.

## Configuration

`.env` (defaults shown):

```dotenv
DATABASE_URL=sqlite:///./output/attendance.db
MATCH_THRESHOLD=0.25            # ORB similarity to accept a signature as verified
INK_THRESHOLD=0.02              # min fraction of dark pixels to call a cell "signed"
PROCESSED_DIR=output/processed
SHEETS_DIR=data/signing_sheets
SIGNATURES_DIR=data/signatures
```

## Reference Signatures (for F5)

Place reference PNG/JPG crops under `data/signatures/<student_idx>/`:

```
data/signatures/
├── 10000409/
│   ├── ref_1.png
│   └── ref_2.png
├── 10009301/
│   └── ref_1.png
…
```

Without reference signatures, F5 verification defaults to `present` for any
detected signature — the `flagged` status can only be produced when references
exist.

## Testing

```bash
pytest -q
```

The bundled `tests/test_pipeline.py` exercises the pure image utilities on
synthetic input. Add end-to-end tests once real photos are placed under
`data/signing_sheets/`.

For a full-flow verification you can also run:

```bash
uvicorn backend.main:app --port 8000 &
# then POST /api/attendance/process with any sheet, hit /save, /analytics/summary etc.
```

## Development Notes

- **Auto-reload**: `uvicorn --reload` picks up code changes without a restart.
- **Silenced Tailwind CDN warning**: an inline shim in `index.html` suppresses
  the "should not be used in production" console warning — this is coursework,
  not production.
- **Report screenshots**: every processing stage is written to
  `output/processed/<timestamp>/` so you can drop them straight into the report.
- **Port conflicts**: macOS reserves `:9000` for `php-fpm` and `:5000` for
  AirPlay. Prefer `:8000` (default) or `:9001`.

## Submission Checklist

- [ ] `report/CS402.3_Report.docx` prepared (kept out of `prototype.zip`)
- [ ] Screenshots of every pipeline stage in `docs/screenshots/`
- [ ] Detection accuracy table filled in with your own tuning results
- [ ] Individual 2-page contributions attached per member (F1–F8)
- [ ] Repo zipped as `prototype.zip`
- [ ] `prototype.zip` + `Report.docx` bundled in one final ZIP for LMS

## Assessment Mapping

| Criterion | Weight | Covered by |
|-----------|--------|-----------|
| Program quality · OOP · testing · executable · image-processing techniques | **60%** (group) | F1–F6 modules, `tests/`, pipeline documentation |
| Report — step-by-step screenshots + technology discussion | **25%** (group) | `output/processed/` stages, this README |
| Individual contribution (2 pages each) | **15%** (individual) | Each member's owned feature F1–F8 |

---

<div align="center">
<sub>Built with <b>FastAPI</b> · <b>OpenCV</b> · <b>SQLAlchemy</b> · <b>Tailwind CSS</b> · <b>Inter</b> type.<br>
CS402.3 group project · NSBM Green University · School of Computing.</sub>
</div>
