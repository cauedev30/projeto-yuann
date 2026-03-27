# Release Candidate Runbook

## Goal
Verify the LegalTech MVP release with one reproducible local verification flow for the current `main` checkout.

## Baseline
- Python: `3.13`
- Backend runtime: SQLite (`backend/legaltech.db`) plus filesystem uploads (`backend/uploads/`)
- Frontend runtime: local Node.js install with dependencies in `web/node_modules`
- E2E mode: serialized Playwright execution from the checked-in config

## Preconditions
- `main` or the release branch is clean before verification starts.
- Backend virtualenv is active, or the shell can call the intended interpreter directly with `python`.
- Backend and web dependencies are installed.
- Optional infrastructure from `docker-compose.yml` can be started with `make up`, but it is not required for the verified release baseline.
- Local manual smoke commands:
  - `cd backend && python -m uvicorn app.main:app --host 127.0.0.1 --port 8000`
  - `cd web && NEXT_PUBLIC_API_URL="http://127.0.0.1:8000" npm run dev -- --hostname 127.0.0.1 --port 3000`
- Demo assets available in the repo:
  - `web/tests/fixtures/third-party-draft.pdf`
  - `web/tests/fixtures/unreadable-upload.pdf`
- Dashboard demo commands:
  - `cd backend && python -m tests.support.seed_dashboard_runtime clear`
  - `cd backend && python -m tests.support.seed_dashboard_runtime seed`

## Verification order
1. `cd backend && python -m pytest -q`
2. `cd web && npm run test`
3. `cd web && npx tsc --noEmit`
4. `cd web && npm run lint`
5. `cd web && npm run build`
6. `cd web && npm run e2e`

## Expected outcome
- Backend suite green.
- Vitest green.
- TypeScript exits with no output.
- ESLint exits cleanly.
- Next.js build completes successfully.
- Playwright suite completes green under the serialized config.

## Manual smoke
1. Start the backend with `cd backend && python -m uvicorn app.main:app --host 127.0.0.1 --port 8000`.
2. Start the frontend with `cd web && NEXT_PUBLIC_API_URL="http://127.0.0.1:8000" npm run dev -- --hostname 127.0.0.1 --port 3000`.
3. Open `http://127.0.0.1:3000/contracts` and verify the upload form renders.
4. Upload `web/tests/fixtures/third-party-draft.pdf` and confirm the triage result renders.
5. Upload `web/tests/fixtures/unreadable-upload.pdf` and confirm the friendly error copy renders.
6. Run `cd backend && python -m tests.support.seed_dashboard_runtime clear`, then open `http://127.0.0.1:3000/dashboard` and confirm the unavailable state.
7. Run `cd backend && python -m tests.support.seed_dashboard_runtime seed`, then refresh `http://127.0.0.1:3000/dashboard` and confirm the populated dashboard renders.

## Contract retention operation
- Purpose: expurgo seguro de contratos inativos cujo `last_analyzed_at` venceu ha 30 dias ou mais, sempre em UTC.
- Preservation rules:
  - never remove active contracts
  - never remove contracts without `last_analyzed_at`
  - never remove inactive contracts still inside the 30-day window
- Dry-run inspection:
  - `cd backend && python -m app.tasks.retention --dry-run`
- Real execution:
  - `cd backend && python -m app.tasks.retention`
- Runtime config:
  - the task uses the normal backend configuration, including `DATABASE_URL` and `UPLOAD_DIR`
  - scheduling remains external to the app
- Expected behavior:
  - eligible contracts are deleted from the database
  - related versions, analyses, findings, events, and notifications are removed by cascade
  - physical version files are deleted only after a successful database commit
  - the CLI prints mode, counts, and contract references for auditability
  - exit code is non-zero if the database phase fails or if post-commit file cleanup reports failures

## Known non-blocking risks
- `web/src/app/globals.css` still emits the known autoprefixer warning for `end`.
- Old `.worktrees/`, `tmp/`, `backend/uploads/`, and the local SQLite database may remain on disk after verification; they are operational cleanup, not part of this release gate.

## Out of scope
- Production deployment or hosting changes.
- Refactoring the E2E suite for isolated per-worker runtimes.
- Destructive cleanup of legacy worktrees or ignored runtime artifacts.
