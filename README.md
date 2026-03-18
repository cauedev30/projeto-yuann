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
- Docker and `docker-compose.yml` remain available for optional local infrastructure experiments via `make up`, but the verified MVP test flow runs without requiring those services.
- The release-candidate baseline for this repository is `Python 3.13` plus the local Node.js runtime used by `web/`.

## Local setup
1. Create and activate a backend virtualenv with Python 3.13:
   - POSIX: `cd backend && python3.13 -m venv .venv && source .venv/bin/activate`
   - Windows PowerShell: `cd backend; py -3.13 -m venv .venv; .\.venv\Scripts\Activate.ps1`
2. Install backend dependencies with `cd backend && python -m pip install -e ".[dev]"`.
3. Install web dependencies with `cd web && npm install`.
4. Run `make up` if you want the optional Docker services from `docker-compose.yml`; otherwise skip it for the verified SQLite release flow.
5. Copy `.env.example` to `.env` only if you need optional local infrastructure variables.
6. Start the API with `cd backend && python -m uvicorn app.main:app --host 127.0.0.1 --port 8000`.
7. Start the frontend with `cd web && NEXT_PUBLIC_API_URL="http://127.0.0.1:8000" npm run dev -- --hostname 127.0.0.1 --port 3000`.
   - Windows PowerShell: `cd web; $env:NEXT_PUBLIC_API_URL="http://127.0.0.1:8000"; npm run dev -- --hostname 127.0.0.1 --port 3000`

## Verification
- Optional Docker infra: `make up` and `make down`
- Backend: `cd backend && python -m pytest -q`
- Root shortcut: `make backend-test`
- Web tests: `cd web && npm run test`
- Typecheck: `cd web && npx tsc --noEmit`
- Lint: `cd web && npm run lint`
- Build: `cd web && npm run build`
- End to end: `cd web && npm run e2e`

## Release candidate
- Use the verification order above as the official `F5-A` baseline.
- The Playwright suite is intentionally serialized in the checked-in config because the local backend runtime shares one SQLite database during E2E verification.
- Seed the dashboard demo state with `cd backend && python -m tests.support.seed_dashboard_runtime seed`.
- Clear the dashboard demo state with `cd backend && python -m tests.support.seed_dashboard_runtime clear`.
- The root `Makefile` exposes the same demo helpers as `release-seed-dashboard` and `release-clear-dashboard` when `make` is available in the shell.
- The minimum demo fixtures are `web/tests/fixtures/third-party-draft.pdf` and `web/tests/fixtures/unreadable-upload.pdf`.
- Cleanup of `.worktrees/`, `tmp/`, legacy uploads, and other ignored runtime artifacts is outside the `F5-A` release scope.
- See `docs/release-candidate-runbook.md` for the full checklist and known non-blocking risks.
