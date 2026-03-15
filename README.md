# LegalTech MVP

Monorepo for the first sellable version of the contract governance platform for franchise expansion teams.

## Planned scope
- ingest draft and signed contracts
- compare draft clauses against a franchisor policy playbook
- extract dates and critical milestones from signed contracts
- surface risk, timeline, and notifications for the operator team

## Stack
- `web/`: Next.js operator app
- `backend/`: FastAPI API and background worker
- `docker-compose.yml`: local Postgres, Redis, MinIO, and Mailpit

## Local setup
1. Copy `.env.example` to `.env`.
2. Start local services with `docker compose up -d`.
3. Create a Python virtual environment and install backend dependencies.
4. Install web dependencies with `npm install`.
5. Start the API with `C:/Users/win/AppData/Local/Programs/Python/Python313/python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000` inside `backend/`.
6. Start the frontend with `npm run dev -- --hostname 127.0.0.1 --port 3000` inside `web/`.

## Verification
- Backend: `pytest`
- Web tests: `npm run test`
- Web build: `npm run build`
- End to end: `npm run e2e`
