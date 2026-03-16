# LegalTech MVP

Monorepo for the first sellable version of the contract governance platform for franchise expansion teams.

## Product scope
- ingest draft and signed contracts
- compare draft clauses against a franchisor policy playbook
- extract dates and critical milestones from signed contracts
- surface risk, timeline, and notifications for the operator team

## Current architecture

### Backend
- `backend/app/main.py`: exports the FastAPI composition root only.
- `backend/app/core/app_factory.py`: wires middleware, routes, SQLite runtime state, storage, and OCR defaults.
- `backend/app/api/`: HTTP routes, dependencies, and request or response boundaries.
- `backend/app/application/`: orchestration use cases for uploads, analysis persistence, and alerts.
- `backend/app/domain/`: pure contract-analysis, metadata, event, and notification rules.
- `backend/app/infrastructure/`: concrete storage, OCR, PDF text extraction, and notification adapters.
- `backend/app/db/`: ORM models, session wiring, and persistence concerns.

### Frontend
- `web/src/app/`: Next.js routes acting as composition roots.
- `web/src/features/`: operator-facing screens, components, and test fixtures.
- `web/src/entities/`: UI-facing models and transport-to-UI mappers.
- `web/src/lib/api/`: transport-only clients and runtime data access.

## Runtime notes
- The current local backend runtime defaults to SQLite (`legaltech.db`) plus filesystem uploads under `backend/uploads/`.
- Dashboard fixture data no longer sits in the runtime path. When no live snapshot exists, the UI shows an explicit unavailable state.
- `docker-compose.yml` is still available for local infrastructure experiments, but the verified MVP test flow runs without requiring those services.

## Local setup
1. Create a Python virtual environment and install backend dependencies inside `backend/`.
2. Install web dependencies with `npm install` inside `web/`.
3. Copy `.env.example` to `.env` only if you need optional local infrastructure variables.
4. Start the API with `C:/Users/win/AppData/Local/Programs/Python/Python313/python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000` inside `backend/`.
5. Start the frontend with `npm run dev -- --hostname 127.0.0.1 --port 3000` inside `web/`.

## Verification
- Backend: `cd backend && C:/Users/win/AppData/Local/Programs/Python/Python313/python.exe -m pytest -v`
- Web tests: `cd web && npm run test`
- End to end: `cd web && npx playwright test`
