# RailOpt AI

RailOpt AI is a decision-support prototype for coordinating railway maintenance block planning across Engineering, Traction, and S&T. It is being built as a single-developer Smart India Hackathon prototype.

## Phase 1 status

The foundation currently includes:

- React + TypeScript + Vite frontend at the repository root
- FastAPI backend under `backend/`
- `GET /api/health` liveness endpoint
- Pydantic environment configuration
- SQLAlchemy domain models, relationships, and session boundary
- Alembic migration for the core planning schema
- PostgreSQL Docker Compose service
- Backend health and database schema tests
- Deterministic synthetic railway data generator and database seeder
- Normalized TMS, SMMS, TDMS, COA, timetable, and goods ingestion adapters
- Transparent priority scoring and deterministic fallback risk engine
- Task compatibility checks with dynamic shared-block savings and hard train-conflict rejection
- Dedicated train movement conflict detector with corridor and interval safety checks
- OR-Tools CP-SAT optimizer for feasible task-to-block assignment
- Planning service and emergency replanning workflow with old-vs-new results
- Calculated before-vs-after analytics and prototype asset-availability metric
- FastAPI data, optimization, analytics, and emergency simulation endpoints
- React dashboard API client with live status, task queue, analytics, fallback demo mode, and safety disclaimer
- Interactive navigation for command center, planner, maintenance queue, corridor map, and reports

Optimizer, synthetic data, and railway planning APIs are intentionally reserved for later phases. This prevents mock screens from being mistaken for a working optimization system.

## Safety boundary

This is a decision-support prototype only. It never authorizes railway blocks, signaling, interlocking, traction isolation, or train movement. All authorization and safety procedures remain with authorized railway personnel. Phase 1 contains no real railway integration and no operational data.

## Prerequisites

- Node.js 22+
- Python 3.11+
- Docker Desktop (for PostgreSQL)

## Environment setup

Copy the backend environment template:

```powershell
Copy-Item backend/.env.example backend/.env
```

The frontend currently runs on `http://localhost:5173`. The backend defaults to `http://127.0.0.1:8000`.

## Start PostgreSQL

```powershell
docker compose up -d postgres
```

The database is exposed locally as `railopt:railopt@localhost:5432/railopt`. Migrations and domain tables are part of Phase 2.

## Start the backend

```powershell
Set-Location backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Verify:

```text
http://127.0.0.1:8000/api/health
http://127.0.0.1:8000/docs
```

Expected health response:

```json
{"status":"healthy","service":"railopt-ai"}
```

## Start the frontend

From the repository root:

```powershell
npm install
npm run dev
```

Open `http://localhost:5173/`.

## Verification

Frontend:

```powershell
npm run build
npm run lint
```

Backend:

```powershell
Set-Location backend
pytest
```

## Planned phases

1. Foundation and local services
2. SQLAlchemy models, Alembic, and PostgreSQL persistence (complete)
3. Meaningful deterministic synthetic railway data (complete)
4. TMS, SMMS, TDMS, COA, timetable, and goods adapters (complete)
5. Transparent priority and fallback risk engines (complete)
6. Compatibility and hard train-conflict checks (complete)
7. OR-Tools CP-SAT planning (complete)
8. Planning, explanations, analytics, and emergency replanning (planning and analytics complete)
9. FastAPI integration and React workflow pages (API integration complete)
10. Frontend API-connected dashboard slice (complete)
11. End-to-end integration flow (complete)
12. Frontend workflow pages and polish (interactive workspaces complete)
13. Final testing and SIH demo polish

## Generate and seed synthetic data

Phase 3 uses seed `42` and labels all generated records as synthetic. The dataset includes related assets, maintenance tasks, train movements, block windows, goods forecasts, and department resources. The C102 demo corridor includes intentionally overlapping Engineering, S&T, and Traction tasks for later compatibility and optimization phases.

From `backend/` with the virtual environment active:

```powershell
python scripts/generate_data.py --output ..\data\synthetic\synthetic_dataset.json
python scripts/seed_database.py --seed 42
```

Current generated counts:

```text
assets: 363
maintenance_tasks: 1203
trains: 2700
block_windows: 360
goods_forecasts: 360
resources: 6
```
