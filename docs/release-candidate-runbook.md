# Release Candidate Runbook

## Goal
Close `F5-A Preparar release tecnico` with one reproducible local verification flow for the current `main` checkout.

## Baseline
- Python: `3.13`
- Backend runtime: SQLite (`backend/legaltech.db`) plus filesystem uploads (`backend/uploads/`)
- Frontend runtime: local Node.js install with dependencies in `web/node_modules`
- E2E mode: serialized Playwright execution from the checked-in config

## Preconditions
- `main` or the release branch is clean before verification starts.
- Backend and web dependencies are installed.
- Optional infrastructure from `docker-compose.yml` is not required for the release baseline.
- Demo assets available in the repo:
  - `web/tests/fixtures/third-party-draft.pdf`
  - `web/tests/fixtures/unreadable-upload.pdf`
- Dashboard demo commands:
  - `cd backend && py -3.13 -m tests.support.seed_dashboard_runtime clear`
  - `cd backend && py -3.13 -m tests.support.seed_dashboard_runtime seed`

## Verification order
1. `cd backend && py -3.13 -m pytest -q`
2. `cd web && npm run test`
3. `cd web && npx tsc --noEmit`
4. `cd web && npm run lint`
5. `cd web && npm run build`
6. `cd web && npx playwright test`

## Expected outcome
- Backend suite green.
- Vitest green.
- TypeScript exits with no output.
- ESLint exits cleanly.
- Next.js build completes successfully.
- Playwright suite completes green under the serialized config.

## Manual smoke
1. Start the backend locally.
2. Start the frontend locally.
3. Open `/contracts` and verify the upload form renders.
4. Upload `web/tests/fixtures/third-party-draft.pdf` and confirm the triage result renders.
5. Upload `web/tests/fixtures/unreadable-upload.pdf` and confirm the friendly error copy renders.
6. Run `cd backend && py -3.13 -m tests.support.seed_dashboard_runtime clear`, then open `/dashboard` and confirm the unavailable state.
7. Run `cd backend && py -3.13 -m tests.support.seed_dashboard_runtime seed`, then refresh `/dashboard` and confirm the populated dashboard renders.

## Known non-blocking risks
- `web/src/app/globals.css` still emits the known autoprefixer warning for `end`.
- Old `.worktrees/`, `tmp/`, `backend/uploads/`, and the local SQLite database may remain on disk after verification; they are operational cleanup, not part of this release gate.

## Out of scope
- Production deployment or hosting changes.
- Refactoring the E2E suite for isolated per-worker runtimes.
- Destructive cleanup of legacy worktrees or ignored runtime artifacts.
