# LegalTech MVP Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the first sellable MVP for franchise expansion teams: contract intake, policy-based analysis, signed-contract archive, critical date monitoring, and operator alerts.

**Architecture:** Use a small monorepo with a Next.js operator web app, a Python FastAPI backend, and a Python worker for OCR, extraction, and notifications. Keep the intelligence pipeline split into deterministic stages: file ingestion, text extraction, structured AI output, deterministic validation, event calculation, and alert delivery.

**Tech Stack:** Next.js App Router, TypeScript, Tailwind CSS, Python 3.12, FastAPI, SQLAlchemy, Alembic, PostgreSQL, Redis, Celery, MinIO/S3-compatible storage, OpenAI structured responses, Tesseract OCR, PyMuPDF, pytest, Vitest, React Testing Library, Playwright, Docker Compose

---

## Delivery Strategy
Build the MVP in this order:
1. Local platform and repo foundation
2. Domain model and persistence
3. Upload, OCR, and policy analysis pipeline
4. Signed contract extraction and event scheduling
5. Alerts and audit trail
6. Operator web flows
7. End-to-end verification and deployment docs

## Proposed Repository Structure

```text
Projeto_yuann/
  README.md
  .env.example
  Makefile
  docker-compose.yml
  web/
    package.json
    src/
      app/
      components/
      features/
      lib/
    tests/
    playwright.config.ts
  backend/
    pyproject.toml
    alembic.ini
    alembic/
    app/
      main.py
      core/
      api/
      db/
      schemas/
      services/
      tasks/
    tests/
```

## Assumptions Locked For Implementation
- Single tenant in MVP: one franchisor organization per deployment.
- Auth is postponed to a later hardening pass; MVP starts as an internal operator tool behind environment-level protection.
- Alerts for MVP use in-app records plus e-mail; WhatsApp stays out of scope.
- File storage uses S3-compatible APIs so MinIO works locally and cloud storage can replace it later.
- AI output must always be revalidated by typed schemas and deterministic business rules before persistence.

## Chunk 1: Foundation

### Task 1: Scaffold the monorepo and local development stack

**Files:**
- Create: `README.md`
- Create: `.env.example`
- Create: `Makefile`
- Create: `docker-compose.yml`
- Create: `web/package.json`
- Create: `web/tsconfig.json`
- Create: `web/next.config.ts`
- Create: `backend/pyproject.toml`
- Create: `backend/app/main.py`
- Test: `backend/tests/test_healthcheck.py`

- [ ] **Step 1: Write the failing backend healthcheck test**

```python
from fastapi.testclient import TestClient

from app.main import app


def test_healthcheck_returns_ok():
    client = TestClient(app)
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && pytest tests/test_healthcheck.py -v`
Expected: FAIL because `app.main` or `/health` does not exist yet.

- [ ] **Step 3: Implement the minimal backend app and local tooling**

```python
from fastapi import FastAPI

app = FastAPI()


@app.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}
```

Add Docker services for `postgres`, `redis`, `minio`, and `mailpit`. Add a root `Makefile` with `up`, `down`, `backend-test`, `web-test`, and `e2e` targets. Add `.env.example` with every variable referenced by backend and web.

- [ ] **Step 4: Run the test suite and boot local services**

Run: `docker compose up -d`
Run: `cd backend && pytest tests/test_healthcheck.py -v`
Expected: Compose services start and the healthcheck test passes.

- [ ] **Step 5: Commit**

```bash
git add README.md .env.example Makefile docker-compose.yml web backend
git commit -m "chore: bootstrap legaltech monorepo"
```

### Task 2: Define configuration loading and environment contracts

**Files:**
- Create: `backend/app/core/config.py`
- Create: `backend/app/core/logging.py`
- Create: `web/src/lib/env.ts`
- Test: `backend/tests/core/test_config.py`
- Test: `web/tests/env.test.ts`

- [ ] **Step 1: Write failing tests for required environment loading**

```python
from pydantic import ValidationError
import pytest

from app.core.config import Settings


def test_settings_require_database_url():
    with pytest.raises(ValidationError):
        Settings(
            openai_api_key="x",
            redis_url="redis://localhost:6379/0",
            s3_bucket="contracts",
        )
```

```ts
import { describe, expect, it } from "vitest";
import { loadClientEnv } from "@/lib/env";

describe("loadClientEnv", () => {
  it("requires NEXT_PUBLIC_API_URL", () => {
    expect(() => loadClientEnv({})).toThrow("NEXT_PUBLIC_API_URL");
  });
});
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd backend && pytest tests/core/test_config.py -v`
Run: `cd web && npm run test -- tests/env.test.ts`
Expected: FAIL because the settings modules do not exist.

- [ ] **Step 3: Implement typed environment parsing**

Create typed settings for backend with `pydantic-settings` and a small client-side env helper in the web app. Add structured JSON logging for API and worker processes.

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd backend && pytest tests/core/test_config.py -v`
Run: `cd web && npm run test -- tests/env.test.ts`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/app/core web/src/lib/env.ts backend/tests/core web/tests
git commit -m "chore: add typed configuration contracts"
```

## Chunk 2: Domain and Persistence

### Task 3: Model policies, contracts, analyses, and critical events

**Files:**
- Create: `backend/app/db/base.py`
- Create: `backend/app/db/session.py`
- Create: `backend/app/db/models/policy.py`
- Create: `backend/app/db/models/contract.py`
- Create: `backend/app/db/models/analysis.py`
- Create: `backend/app/db/models/event.py`
- Create: `backend/alembic/versions/0001_initial_schema.py`
- Test: `backend/tests/db/test_contract_models.py`

- [ ] **Step 1: Write failing tests for the core contract graph**

```python
from app.db.models.contract import Contract
from app.db.models.analysis import ContractAnalysis
from app.db.models.event import ContractEvent


def test_contract_relations_expose_analysis_and_events():
    contract = Contract(title="Loja Centro", external_reference="LOC-001")

    contract.analyses.append(ContractAnalysis(policy_version="v1"))
    contract.events.append(ContractEvent(event_type="renewal", lead_time_days=180))

    assert contract.analyses[0].policy_version == "v1"
    assert contract.events[0].event_type == "renewal"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && pytest tests/db/test_contract_models.py -v`
Expected: FAIL because the SQLAlchemy models do not exist.

- [ ] **Step 3: Implement the initial schema**

Include these tables at minimum:
- `policies`
- `policy_rules`
- `contracts`
- `contract_versions`
- `contract_analyses`
- `contract_events`
- `notifications`

Use enums for contract source, analysis status, event type, and notification channel. Store raw AI payloads in JSON columns for auditability.

- [ ] **Step 4: Run tests and migration checks**

Run: `cd backend && pytest tests/db/test_contract_models.py -v`
Run: `cd backend && alembic upgrade head`
Expected: PASS and migration applies cleanly.

- [ ] **Step 5: Commit**

```bash
git add backend/app/db backend/alembic backend/tests/db
git commit -m "feat: add legaltech core persistence models"
```

### Task 4: Expose CRUD endpoints for policies and contracts

**Files:**
- Create: `backend/app/schemas/policy.py`
- Create: `backend/app/schemas/contract.py`
- Create: `backend/app/api/routes/policies.py`
- Create: `backend/app/api/routes/contracts.py`
- Modify: `backend/app/main.py`
- Test: `backend/tests/api/test_policies_api.py`
- Test: `backend/tests/api/test_contracts_api.py`

- [ ] **Step 1: Write failing API tests for policy creation and contract listing**

```python
def test_create_policy_returns_201(client):
    payload = {
        "name": "Padrao Franquia",
        "version": "2026.03",
        "rules": [
            {"code": "MIN_TERM_MONTHS", "value": 60},
            {"code": "MAX_FINE_MONTHS", "value": 3},
        ],
    }

    response = client.post("/api/policies", json=payload)

    assert response.status_code == 201
    assert response.json()["version"] == "2026.03"
```

```python
def test_list_contracts_returns_empty_collection(client):
    response = client.get("/api/contracts")

    assert response.status_code == 200
    assert response.json() == {"items": []}
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd backend && pytest tests/api/test_policies_api.py tests/api/test_contracts_api.py -v`
Expected: FAIL because routes and schemas are missing.

- [ ] **Step 3: Implement typed schemas and routes**

Provide:
- policy creation with nested rules
- contract listing with pagination stubs
- contract detail endpoint with analyses and events placeholders

Mount routes under `/api`.

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd backend && pytest tests/api/test_policies_api.py tests/api/test_contracts_api.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/app/api backend/app/schemas backend/tests/api backend/app/main.py
git commit -m "feat: add policies and contracts api surface"
```

## Chunk 3: Ingestion and Analysis

### Task 5: Implement contract upload, storage registration, and text extraction

**Files:**
- Create: `backend/app/services/storage.py`
- Create: `backend/app/services/pdf_text.py`
- Create: `backend/app/services/ocr.py`
- Create: `backend/app/api/routes/uploads.py`
- Create: `backend/app/tasks/ingestion.py`
- Test: `backend/tests/services/test_pdf_text.py`
- Test: `backend/tests/api/test_uploads_api.py`

- [ ] **Step 1: Write failing tests for direct-text PDFs and OCR fallback**

```python
def test_extract_text_prefers_embedded_text(tmp_path):
    pdf_path = tmp_path / "contract.pdf"
    pdf_path.write_bytes(build_pdf_with_text("Prazo de vigencia 60 meses"))

    result = extract_contract_text(pdf_path)

    assert result.text == "Prazo de vigencia 60 meses"
    assert result.used_ocr is False
```

```python
def test_extract_text_falls_back_to_ocr_when_pdf_has_no_text(tmp_path):
    pdf_path = tmp_path / "scan.pdf"
    pdf_path.write_bytes(build_image_only_pdf())

    result = extract_contract_text(pdf_path, ocr_client=FakeOcrClient("Contrato assinado"))

    assert result.text == "Contrato assinado"
    assert result.used_ocr is True
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd backend && pytest tests/services/test_pdf_text.py tests/api/test_uploads_api.py -v`
Expected: FAIL because extraction services and upload route do not exist.

- [ ] **Step 3: Implement upload and extraction pipeline**

On upload:
- store original file in S3-compatible storage
- create `contract_versions` row with source `third_party_draft` or `signed_contract`
- enqueue ingestion task

In ingestion:
- extract embedded text with PyMuPDF first
- run OCR only when extracted text confidence is too low
- persist normalized text and extraction metadata

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd backend && pytest tests/services/test_pdf_text.py tests/api/test_uploads_api.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/app/services backend/app/tasks backend/app/api/routes/uploads.py backend/tests
git commit -m "feat: add contract upload and extraction pipeline"
```

### Task 6: Implement policy analysis with structured AI output and deterministic validation

**Files:**
- Create: `backend/app/schemas/analysis.py`
- Create: `backend/app/services/policy_analysis.py`
- Create: `backend/app/services/rule_evaluator.py`
- Create: `backend/app/tasks/analysis.py`
- Test: `backend/tests/services/test_policy_analysis.py`
- Test: `backend/tests/services/test_rule_evaluator.py`

- [ ] **Step 1: Write the failing tests for policy mismatch detection**

```python
def test_rule_evaluator_marks_short_term_as_critical():
    rules = [
        {"code": "MIN_TERM_MONTHS", "value": 60},
    ]
    extracted = {"term_months": 36}

    result = evaluate_rules(rules, extracted)

    assert result.items[0].status == "critical"
    assert result.items[0].clause_name == "Prazo de vigencia"
```

```python
def test_policy_analysis_returns_structured_items(openai_stub):
    result = analyze_contract_against_policy(
        contract_text="Prazo de 36 meses e multa de 6 alugueis",
        policy_rules=[{"code": "MIN_TERM_MONTHS", "value": 60}],
        llm_client=openai_stub,
    )

    assert result.contract_risk_score > 0
    assert result.items[0].suggested_adjustment_direction
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd backend && pytest tests/services/test_rule_evaluator.py tests/services/test_policy_analysis.py -v`
Expected: FAIL because analysis services do not exist.

- [ ] **Step 3: Implement the analysis pipeline**

Requirements:
- send a structured prompt to the LLM with contract text and policy JSON
- validate the response with typed schemas
- enrich the output with deterministic checks for date ranges, term length, and penalty caps
- compute a normalized `contract_risk_score`
- persist analysis rows and per-item findings

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd backend && pytest tests/services/test_rule_evaluator.py tests/services/test_policy_analysis.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/app/services/policy_analysis.py backend/app/services/rule_evaluator.py backend/app/schemas/analysis.py backend/tests/services
git commit -m "feat: add policy-based contract analysis"
```

## Chunk 4: Archive, Events, and Alerts

### Task 7: Extract signed-contract metadata and calculate critical events

**Files:**
- Create: `backend/app/schemas/metadata.py`
- Create: `backend/app/services/contract_metadata.py`
- Create: `backend/app/services/event_scheduler.py`
- Create: `backend/app/tasks/archive.py`
- Test: `backend/tests/services/test_contract_metadata.py`
- Test: `backend/tests/services/test_event_scheduler.py`

- [ ] **Step 1: Write failing tests for metadata extraction and event calculation**

```python
def test_event_scheduler_creates_renewal_and_expiration_events():
    metadata = {
        "signature_date": "2026-03-01",
        "start_date": "2026-04-01",
        "term_months": 60,
        "critical_events": [],
    }

    events = build_contract_events(metadata, default_lead_times={"renewal": 180, "expiration": 30})

    event_types = [event.event_type for event in events]
    assert "renewal" in event_types
    assert "expiration" in event_types
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd backend && pytest tests/services/test_contract_metadata.py tests/services/test_event_scheduler.py -v`
Expected: FAIL because metadata extraction and scheduling services do not exist.

- [ ] **Step 3: Implement signed-contract archive processing**

Requirements:
- parse structured metadata from signed contracts
- mark field-level confidence
- persist contract dates, parties, and financial triggers
- calculate derived events for renewal, expiration, readjustment, and grace-period end

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd backend && pytest tests/services/test_contract_metadata.py tests/services/test_event_scheduler.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/app/services/contract_metadata.py backend/app/services/event_scheduler.py backend/app/tasks/archive.py backend/tests/services
git commit -m "feat: add signed contract archive processing"
```

### Task 8: Implement alert dispatch and notification audit trail

**Files:**
- Create: `backend/app/services/notifications.py`
- Create: `backend/app/tasks/alerts.py`
- Create: `backend/app/api/routes/notifications.py`
- Test: `backend/tests/services/test_notifications.py`
- Test: `backend/tests/tasks/test_alerts_task.py`

- [ ] **Step 1: Write failing tests for alert generation**

```python
def test_alert_worker_creates_email_notification_for_due_event(session):
    due_event = make_contract_event(days_until_due=30, event_type="expiration")

    result = process_due_events(session=session, today="2026-04-01")

    assert result.sent == 1
    assert result.skipped == 0
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd backend && pytest tests/services/test_notifications.py tests/tasks/test_alerts_task.py -v`
Expected: FAIL because the worker and notification service do not exist.

- [ ] **Step 3: Implement alert delivery**

Requirements:
- scan due events daily
- create notification records before attempting send
- send e-mail via transactional provider abstraction
- expose notification history on the API
- keep idempotency keys so the same event window is not re-sent accidentally

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd backend && pytest tests/services/test_notifications.py tests/tasks/test_alerts_task.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/app/services/notifications.py backend/app/tasks/alerts.py backend/app/api/routes/notifications.py backend/tests
git commit -m "feat: add contract alerting and notification audit trail"
```

## Chunk 5: Web App

### Task 9: Build the contract intake and analysis review flow in the web app

**Files:**
- Create: `web/src/app/(app)/contracts/page.tsx`
- Create: `web/src/app/(app)/contracts/[contractId]/page.tsx`
- Create: `web/src/features/contracts/components/upload-form.tsx`
- Create: `web/src/features/analysis/components/risk-score-card.tsx`
- Create: `web/src/features/analysis/components/findings-table.tsx`
- Create: `web/src/lib/api/contracts.ts`
- Test: `web/src/features/contracts/components/upload-form.test.tsx`
- Test: `web/src/features/analysis/components/findings-table.test.tsx`

- [ ] **Step 1: Write failing component tests**

```tsx
it("renders critical findings with the expected badge", () => {
  render(
    <FindingsTable
      items={[
        {
          clauseName: "Prazo de vigencia",
          status: "critical",
          riskExplanation: "Prazo abaixo do minimo permitido",
        },
      ]}
    />,
  );

  expect(screen.getByText("critical")).toBeInTheDocument();
  expect(screen.getByText("Prazo de vigencia")).toBeInTheDocument();
});
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd web && npm run test -- src/features/contracts/components/upload-form.test.tsx src/features/analysis/components/findings-table.test.tsx`
Expected: FAIL because components do not exist.

- [ ] **Step 3: Implement the operator flow**

Requirements:
- contracts list page with upload CTA
- upload form posting multipart files to backend
- contract detail page showing score, status badges, findings, and source document metadata
- strong loading, empty, and error states

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd web && npm run test -- src/features/contracts/components/upload-form.test.tsx src/features/analysis/components/findings-table.test.tsx`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add web/src/app web/src/features web/src/lib/api web/tests
git commit -m "feat: add contract intake and analysis review ui"
```

### Task 10: Build the portfolio dashboard and notification timeline

**Files:**
- Create: `web/src/app/(app)/dashboard/page.tsx`
- Create: `web/src/features/dashboard/components/contracts-summary.tsx`
- Create: `web/src/features/dashboard/components/events-timeline.tsx`
- Create: `web/src/features/notifications/components/notification-history.tsx`
- Create: `web/src/lib/api/dashboard.ts`
- Test: `web/src/features/dashboard/components/events-timeline.test.tsx`
- Test: `web/src/features/notifications/components/notification-history.test.tsx`

- [ ] **Step 1: Write failing tests for timeline rendering**

```tsx
it("shows renewal and expiration events in chronological order", () => {
  render(
    <EventsTimeline
      events={[
        { id: "2", eventType: "expiration", eventDate: "2031-03-31" },
        { id: "1", eventType: "renewal", eventDate: "2030-09-30" },
      ]}
    />,
  );

  const items = screen.getAllByRole("listitem");
  expect(items[0]).toHaveTextContent("renewal");
  expect(items[1]).toHaveTextContent("expiration");
});
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd web && npm run test -- src/features/dashboard/components/events-timeline.test.tsx src/features/notifications/components/notification-history.test.tsx`
Expected: FAIL because dashboard components do not exist.

- [ ] **Step 3: Implement the dashboard**

Requirements:
- KPI cards for active contracts, critical findings, and contracts expiring in 12 months
- timeline grouped by month
- notification history panel from backend API
- filters by contract status and event type

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd web && npm run test -- src/features/dashboard/components/events-timeline.test.tsx src/features/notifications/components/notification-history.test.tsx`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add web/src/app/(app)/dashboard web/src/features/dashboard web/src/features/notifications web/src/lib/api/dashboard.ts
git commit -m "feat: add portfolio dashboard and notification timeline"
```

## Chunk 6: Release Readiness

### Task 11: Add end-to-end tests for the MVP operator journey

**Files:**
- Create: `web/playwright.config.ts`
- Create: `web/tests/e2e/contract-analysis.spec.ts`
- Create: `web/tests/e2e/dashboard-alerts.spec.ts`
- Modify: `README.md`

- [ ] **Step 1: Write the failing end-to-end happy path**

```ts
test("operator uploads a contract and reviews the findings", async ({ page }) => {
  await page.goto("/contracts");
  await page.getByLabel("Contrato PDF").setInputFiles("tests/fixtures/third-party-draft.pdf");
  await page.getByRole("button", { name: "Enviar contrato" }).click();

  await expect(page.getByText("Prazo de vigencia")).toBeVisible();
  await expect(page.getByText("critical")).toBeVisible();
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd web && npx playwright test tests/e2e/contract-analysis.spec.ts`
Expected: FAIL because the UI and seeded backend flow are not fully wired yet.

- [ ] **Step 3: Implement test fixtures and local run instructions**

Requirements:
- provide backend seed command with one sample policy
- add test fixtures for a draft contract and a signed contract
- document full local boot flow in `README.md`

- [ ] **Step 4: Run verification commands**

Run: `cd backend && pytest -v`
Run: `cd web && npm run test`
Run: `cd web && npx playwright test`
Expected: PASS across backend, frontend, and e2e suites.

- [ ] **Step 5: Commit**

```bash
git add README.md web/tests/e2e web/playwright.config.ts
git commit -m "test: cover legaltech mvp operator flow end to end"
```

## Acceptance Checklist
- Uploading a third-party draft stores the original file and normalized text.
- Policy analysis produces structured findings with a contract-level risk score.
- Signed contracts generate derived events and appear in the portfolio timeline.
- Alert worker creates in-app and e-mail notifications without duplicate sends.
- Web app supports the full operator flow from upload to contract review to dashboard follow-up.
- Local setup is reproducible with one documented boot sequence.

## Commands Summary
- `docker compose up -d`
- `cd backend && alembic upgrade head`
- `cd backend && pytest -v`
- `cd web && npm install`
- `cd web && npm run test`
- `cd web && npx playwright test`

## Out of Scope For This Plan
- Multi-tenant isolation
- Fine-grained auth and RBAC
- WhatsApp notification delivery
- Automatic contract generation
- Counterparty collaboration portal
