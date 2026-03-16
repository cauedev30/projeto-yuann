# MVP Architecture Reorganization Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reorganize the LegalTech MVP into clearer backend and frontend layers while preserving routes, core behavior, and local operability.

**Architecture:** Keep the monorepo structure, but separate HTTP, application orchestration, domain logic, and infrastructure on the backend; separate routing, features, entities, and transport clients on the frontend. Migrate incrementally so tests keep protecting behavior while the internal architecture becomes more intentional and professional.

**Tech Stack:** FastAPI, SQLAlchemy, Pydantic, PyMuPDF, Next.js App Router, React 19, TypeScript, Vitest, Playwright, Docker Compose

---

## Planned File Structure

### Backend
- `backend/app/main.py`
  - final responsibility: export `app = create_app()` only.
- `backend/app/core/app_factory.py`
  - new responsibility: create and configure the FastAPI app, middleware, routes, and app-state runtime dependencies.
- `backend/app/application/contract_upload.py`
  - new responsibility: orchestrate file upload, contract version persistence, ingestion, and optional signed-contract archive processing.
- `backend/app/application/analysis.py`
  - new responsibility: orchestrate policy analysis use cases around domain logic and persistence.
- `backend/app/application/alerts.py`
  - new responsibility: orchestrate due-event scanning and notification processing.
- `backend/app/domain/contract_analysis.py`
  - new responsibility: contract facts extraction, deterministic findings merge, and analysis-related pure rules.
- `backend/app/domain/events.py`
  - new responsibility: event scheduling and metadata-derived event rules.
- `backend/app/domain/notifications.py`
  - new responsibility: notification eligibility and idempotency rules.
- `backend/app/infrastructure/`
  - new responsibility: group concrete storage, OCR, notification, and integration-facing adapters without changing their current behavior.
- `backend/tests/core/test_app_factory.py`
  - new responsibility: protect composition-root behavior.
- `backend/tests/application/test_contract_upload.py`
  - new responsibility: protect the upload use case boundary.
- `backend/tests/domain/test_contract_analysis.py`
  - new responsibility: protect pure analysis rules in their new location.

### Frontend
- `web/src/app/(app)/contracts/page.tsx`
  - final responsibility: compose the contracts screen only.
- `web/src/app/(app)/dashboard/page.tsx`
  - final responsibility: compose the dashboard screen only.
- `web/src/features/contracts/screens/contracts-screen.tsx`
  - new responsibility: manage contracts page screen state and coordinate upload flow presentation.
- `web/src/features/dashboard/screens/dashboard-screen.tsx`
  - new responsibility: manage dashboard screen rendering states with explicit data boundary behavior.
- `web/src/entities/contracts/model.ts`
  - new responsibility: business-facing contract and finding types used by UI.
- `web/src/entities/dashboard/model.ts`
  - new responsibility: business-facing dashboard summary, event, and notification types used by UI.
- `web/src/lib/api/contracts.ts`
  - final responsibility: HTTP transport and payload mapping only.
- `web/src/lib/api/dashboard.ts`
  - final responsibility: HTTP transport and payload mapping only, with no demo snapshot as production runtime source.
- `web/src/features/dashboard/fixtures/dashboard-snapshot.ts`
  - new responsibility: keep test/demo snapshot data outside runtime transport code.
- `web/src/features/dashboard/components/empty-dashboard-state.tsx`
  - new responsibility: explicit empty/unavailable dashboard state.
- `web/src/features/contracts/components/upload-form.tsx`
  - responsibility unchanged: present upload UI only.
- `web/src/features/analysis/components/findings-table.tsx`
  - responsibility unchanged: present findings only, typed from entities instead of transport DTOs.

### Documentation
- `README.md`
  - update local architecture explanation to match the reorganized code.
- `docs/superpowers/specs/2026-03-16-mvp-architecture-reorganization-design.md`
  - reference document for plan execution.
- `C:/Users/win/Desktop/Projeto_yuann/.codex-memory/source-of-truth.md`
  - update architecture source-of-truth references if new folders become primary.
- `C:/Users/win/Desktop/Projeto_yuann/.codex-memory/decisions.md`
  - record durable architecture decisions introduced by the refactor.

## Chunk 1: Backend Architecture

### Task 1: Extract the FastAPI composition root out of `main.py`

**Files:**
- Create: `backend/app/core/app_factory.py`
- Modify: `backend/app/main.py`
- Modify: `backend/app/api/dependencies.py`
- Test: `backend/tests/core/test_app_factory.py`
- Test: `backend/tests/test_healthcheck.py`

- [ ] **Step 1: Write the failing app-factory test**

```python
from pathlib import Path

from fastapi.testclient import TestClient

from app.core.app_factory import create_app


def test_create_app_wires_runtime_dependencies(tmp_path: Path):
    app = create_app(
        database_url="sqlite://",
        storage_directory=tmp_path / "uploads",
    )

    assert callable(app.state.session_factory)
    assert app.state.storage_service is not None
    assert app.state.ocr_client is not None

    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd backend && pytest tests/core/test_app_factory.py tests/test_healthcheck.py -v`
Expected: FAIL because `app.core.app_factory` does not exist yet.

- [ ] **Step 3: Implement the composition root**

Create `app.core.app_factory.create_app()` so it:
- builds the FastAPI instance
- configures CORS middleware
- creates the engine and session factory when `database_url` is provided
- wires `storage_service` and `ocr_client` into `app.state`
- includes all existing routers

Reduce `backend/app/main.py` to:

```python
from app.core.app_factory import create_app

app = create_app()
```

Keep `app.api.dependencies.get_session()` compatible with `app.state.session_factory`.

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd backend && pytest tests/core/test_app_factory.py tests/test_healthcheck.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/app/core/app_factory.py backend/app/main.py backend/app/api/dependencies.py backend/tests/core/test_app_factory.py backend/tests/test_healthcheck.py
git commit -m "refactor: extract backend app composition root"
```

### Task 2: Introduce an application-layer upload workflow

**Files:**
- Create: `backend/app/application/__init__.py`
- Create: `backend/app/application/contract_upload.py`
- Modify: `backend/app/api/routes/uploads.py`
- Modify: `backend/app/tasks/ingestion.py`
- Modify: `backend/app/tasks/archive.py`
- Test: `backend/tests/application/test_contract_upload.py`
- Test: `backend/tests/api/test_uploads_api.py`

- [ ] **Step 1: Write the failing application workflow test**

```python
from app.application.contract_upload import upload_contract_file
from app.db.models.contract import ContractSource
from app.services.storage import LocalStorageService
from tests.support.pdf_factory import build_pdf_with_text


def test_upload_contract_file_persists_version_and_extraction(session, workspace_tmp_path):
    storage_service = LocalStorageService(workspace_tmp_path / "uploads")

    result = upload_contract_file(
        session=session,
        title="Loja Centro",
        external_reference="LOC-001",
        source=ContractSource.third_party_draft,
        filename="contract.pdf",
        content=build_pdf_with_text("Prazo de vigencia 60 meses"),
        storage_service=storage_service,
    )

    assert result.contract.title == "Loja Centro"
    assert result.contract_version.source == ContractSource.third_party_draft
    assert result.extraction.text == "Prazo de vigencia 60 meses"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd backend && pytest tests/application/test_contract_upload.py tests/api/test_uploads_api.py -v`
Expected: FAIL because `app.application.contract_upload` does not exist yet.

- [ ] **Step 3: Implement the upload use case**

Create `upload_contract_file()` so it owns:
- contract lookup or creation
- contract version creation
- storage persistence
- ingestion execution
- optional signed-contract archive execution

Update `api/routes/uploads.py` so the route only:
- validates transport inputs
- converts `source` to `ContractSource`
- calls the application use case
- maps the result to HTTP response

Leave `tasks/ingestion.py` and `tasks/archive.py` as lower-level helpers used by the application layer, not as direct route orchestrators.

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd backend && pytest tests/application/test_contract_upload.py tests/api/test_uploads_api.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/app/application backend/app/api/routes/uploads.py backend/app/tasks/ingestion.py backend/app/tasks/archive.py backend/tests/application/test_contract_upload.py backend/tests/api/test_uploads_api.py
git commit -m "refactor: add backend upload application workflow"
```

### Task 3: Move pure business rules into domain modules and keep orchestration in application/tasks

**Files:**
- Create: `backend/app/domain/__init__.py`
- Create: `backend/app/domain/contract_analysis.py`
- Create: `backend/app/domain/contract_metadata.py`
- Create: `backend/app/domain/events.py`
- Create: `backend/app/domain/notifications.py`
- Create: `backend/app/application/analysis.py`
- Create: `backend/app/application/alerts.py`
- Create: `backend/app/infrastructure/__init__.py`
- Create: `backend/app/infrastructure/storage.py`
- Create: `backend/app/infrastructure/ocr.py`
- Create: `backend/app/infrastructure/pdf_text.py`
- Create: `backend/app/infrastructure/notifications.py`
- Modify: `backend/app/services/policy_analysis.py`
- Modify: `backend/app/services/rule_evaluator.py`
- Modify: `backend/app/services/contract_metadata.py`
- Modify: `backend/app/services/event_scheduler.py`
- Modify: `backend/app/services/storage.py`
- Modify: `backend/app/services/ocr.py`
- Modify: `backend/app/services/pdf_text.py`
- Modify: `backend/app/services/notifications.py`
- Modify: `backend/app/tasks/analysis.py`
- Modify: `backend/app/tasks/alerts.py`
- Test: `backend/tests/domain/test_contract_analysis.py`
- Test: `backend/tests/services/test_contract_metadata.py`
- Test: `backend/tests/services/test_policy_analysis.py`
- Test: `backend/tests/services/test_rule_evaluator.py`
- Test: `backend/tests/services/test_event_scheduler.py`
- Test: `backend/tests/services/test_notifications.py`
- Test: `backend/tests/tasks/test_alerts_task.py`

- [ ] **Step 1: Write the failing domain-level test**

```python
from app.domain.contract_analysis import merge_analysis_items
from app.schemas.analysis import AnalysisItem


def test_merge_analysis_items_prefers_deterministic_result_for_same_clause():
    llm_items = [
        AnalysisItem(
            clause_name="Prazo de vigencia",
            status="attention",
            risk_explanation="LLM",
            current_summary="36 meses",
            policy_rule="60 meses",
            suggested_adjustment_direction="Revisar",
        )
    ]
    deterministic_items = [
        AnalysisItem(
            clause_name="Prazo de vigencia",
            status="critical",
            risk_explanation="Deterministico",
            current_summary="36 meses",
            policy_rule="60 meses",
            suggested_adjustment_direction="Solicitar prazo minimo",
        )
    ]

    merged = merge_analysis_items(llm_items, deterministic_items)

    assert merged[0].status == "critical"
    assert merged[0].risk_explanation == "Deterministico"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd backend && pytest tests/domain/test_contract_analysis.py tests/services/test_contract_metadata.py tests/services/test_policy_analysis.py tests/services/test_rule_evaluator.py tests/services/test_event_scheduler.py tests/services/test_notifications.py tests/tasks/test_alerts_task.py -v`
Expected: FAIL because `app.domain.contract_analysis` does not exist yet.

- [ ] **Step 3: Implement the domain/application split**

Move pure logic into domain modules:
- fact extraction and analysis-item merge
- metadata extraction interpretation
- deterministic event rules
- notification-eligibility logic

Create `app/infrastructure/` modules for concrete adapters now living under `services/`:
- storage
- OCR
- PDF text extraction
- notification delivery adapter

Keep legacy service modules as thin compatibility facades only if needed during transition, then switch imports toward `domain/` and `infrastructure/`.

Create application-layer functions that orchestrate:
- policy analysis persistence flow
- due-event notification processing

Update task modules so they delegate to application-layer orchestration instead of holding the orchestration themselves.

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd backend && pytest tests/domain/test_contract_analysis.py tests/services/test_contract_metadata.py tests/services/test_policy_analysis.py tests/services/test_rule_evaluator.py tests/services/test_event_scheduler.py tests/services/test_notifications.py tests/tasks/test_alerts_task.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/app/domain backend/app/infrastructure backend/app/application/analysis.py backend/app/application/alerts.py backend/app/services/policy_analysis.py backend/app/services/rule_evaluator.py backend/app/services/contract_metadata.py backend/app/services/event_scheduler.py backend/app/services/storage.py backend/app/services/ocr.py backend/app/services/pdf_text.py backend/app/services/notifications.py backend/app/tasks/analysis.py backend/app/tasks/alerts.py backend/tests/domain/test_contract_analysis.py backend/tests/services backend/tests/tasks/test_alerts_task.py
git commit -m "refactor: separate backend domain and application logic"
```

## Chunk 2: Frontend Architecture

### Task 4: Introduce entity boundaries between UI and transport DTOs

**Files:**
- Create: `web/src/entities/contracts/model.ts`
- Create: `web/src/entities/dashboard/model.ts`
- Modify: `web/src/lib/api/contracts.ts`
- Modify: `web/src/lib/api/dashboard.ts`
- Modify: `web/src/features/analysis/components/findings-table.tsx`
- Modify: `web/src/features/dashboard/components/contracts-summary.tsx`
- Modify: `web/src/features/dashboard/components/events-timeline.tsx`
- Modify: `web/src/features/notifications/components/notification-history.tsx`
- Test: `web/src/entities/contracts/model.test.ts`
- Test: `web/src/entities/dashboard/model.test.ts`
- Test: `web/src/features/analysis/components/findings-table.test.tsx`
- Test: `web/src/features/dashboard/components/events-timeline.test.tsx`

- [ ] **Step 1: Write the failing entity-mapping tests**

```ts
import { describe, expect, it } from "vitest";

import { mapUploadResponseToContractUploadResult } from "./model";

describe("contracts entity mapping", () => {
  it("maps snake_case upload payloads into UI-facing contract upload results", () => {
    const result = mapUploadResponseToContractUploadResult({
      contract_id: "ctr-1",
      contract_version_id: "ver-1",
      source: "third_party_draft",
      used_ocr: false,
      text: "Prazo de vigencia 60 meses",
    });

    expect(result.contractId).toBe("ctr-1");
    expect(result.usedOcr).toBe(false);
  });
});
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd web && npm run test -- src/entities/contracts/model.test.ts src/entities/dashboard/model.test.ts src/features/analysis/components/findings-table.test.tsx src/features/dashboard/components/events-timeline.test.tsx`
Expected: FAIL because the new entity modules do not exist yet.

- [ ] **Step 3: Implement entity models and transport-only API clients**

Create entity modules that own:
- UI-facing contract upload result and finding shapes
- dashboard summary, event, and notification shapes
- explicit mapper helpers from transport payloads into entity types

Update API modules so they only:
- perform HTTP calls
- parse transport payloads
- delegate shape conversion to entity mappers

Update components to import entity types instead of transport types.

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd web && npm run test -- src/entities/contracts/model.test.ts src/entities/dashboard/model.test.ts src/features/analysis/components/findings-table.test.tsx src/features/dashboard/components/events-timeline.test.tsx`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add web/src/entities web/src/lib/api/contracts.ts web/src/lib/api/dashboard.ts web/src/features/analysis/components/findings-table.tsx web/src/features/dashboard/components/contracts-summary.tsx web/src/features/dashboard/components/events-timeline.tsx web/src/features/notifications/components/notification-history.tsx web/src/features/analysis/components/findings-table.test.tsx web/src/features/dashboard/components/events-timeline.test.tsx
git commit -m "refactor: introduce frontend entity boundaries"
```

### Task 5: Turn pages into composition roots and remove demo data from the runtime path

**Files:**
- Create: `web/src/features/contracts/screens/contracts-screen.tsx`
- Create: `web/src/features/dashboard/screens/dashboard-screen.tsx`
- Create: `web/src/features/dashboard/components/empty-dashboard-state.tsx`
- Create: `web/src/features/dashboard/fixtures/dashboard-snapshot.ts`
- Modify: `web/src/app/(app)/contracts/page.tsx`
- Modify: `web/src/app/(app)/dashboard/page.tsx`
- Modify: `web/src/lib/api/dashboard.ts`
- Modify: `web/src/features/contracts/components/upload-form.tsx`
- Modify: `web/src/features/notifications/components/notification-history.tsx`
- Test: `web/src/features/dashboard/screens/dashboard-screen.test.tsx`
- Test: `web/src/features/contracts/screens/contracts-screen.test.tsx`
- Test: `web/tests/e2e/dashboard-alerts.spec.ts`

- [ ] **Step 1: Write the failing screen-state tests**

```tsx
import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { DashboardScreen } from "./dashboard-screen";

describe("DashboardScreen", () => {
  it("shows an explicit unavailable state when no runtime dashboard snapshot exists", () => {
    render(<DashboardScreen snapshot={null} />);

    expect(screen.getByText("Dashboard indisponivel no momento.")).toBeInTheDocument();
  });
});
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd web && npm run test -- src/features/dashboard/screens/dashboard-screen.test.tsx src/features/contracts/screens/contracts-screen.test.tsx`
Expected: FAIL because the new screen modules and explicit unavailable state do not exist yet.

- [ ] **Step 3: Implement composition-root pages and honest runtime states**

Create screen components so pages only compose them.

Change dashboard runtime behavior so:
- runtime data loading is explicit
- missing runtime data produces an honest empty or unavailable state
- snapshot/demo data lives only in `features/dashboard/fixtures/`
- tests can still use fixture data without pretending it is live backend data

Adjust E2E expectations so the dashboard verifies the professional state that should ship, not implicit demo content.

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd web && npm run test -- src/features/dashboard/screens/dashboard-screen.test.tsx src/features/contracts/screens/contracts-screen.test.tsx`
Run: `cd web && npx playwright test tests/e2e/dashboard-alerts.spec.ts`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add web/src/app/(app)/contracts/page.tsx web/src/app/(app)/dashboard/page.tsx web/src/features/contracts/screens/contracts-screen.tsx web/src/features/dashboard/screens/dashboard-screen.tsx web/src/features/dashboard/components/empty-dashboard-state.tsx web/src/features/dashboard/fixtures/dashboard-snapshot.ts web/src/lib/api/dashboard.ts web/src/features/contracts/components/upload-form.tsx web/src/features/notifications/components/notification-history.tsx web/src/features/dashboard/screens/dashboard-screen.test.tsx web/src/features/contracts/screens/contracts-screen.test.tsx web/tests/e2e/dashboard-alerts.spec.ts
git commit -m "refactor: make frontend pages composition roots"
```

## Chunk 3: Documentation and Verification

### Task 6: Align documentation and memory with the implemented architecture

**Files:**
- Modify: `README.md`
- Modify: `C:/Users/win/Desktop/Projeto_yuann/.codex-memory/source-of-truth.md`
- Modify: `C:/Users/win/Desktop/Projeto_yuann/.codex-memory/decisions.md`
- Modify: `C:/Users/win/Desktop/Projeto_yuann/.codex-memory/current-state.md`
- Modify: `C:/Users/win/Desktop/Projeto_yuann/.codex-memory/session-log.md`

- [ ] **Step 1: Write the failing documentation/structure checklist**

Create a temporary implementation checklist from the approved spec and verify these statements against the repo:
- `backend/app/main.py` is a composition root
- backend application modules exist for orchestration
- backend domain modules exist for pure rules
- frontend entity modules exist
- frontend pages act as composition roots
- dashboard demo data is not the default runtime source

Expected: at least one checklist item is still false before documentation updates.

- [ ] **Step 2: Run full verification before writing final docs**

Run: `cd backend && pytest -v`
Run: `cd web && npm run test`
Run: `cd web && npx playwright test`
Expected: PASS before claiming the reorganization is complete.

- [ ] **Step 3: Update docs and memory**

Update:
- `README.md` to describe the new backend/frontend architectural boundaries
- `source-of-truth.md` to point to the new primary architectural folders
- `decisions.md` to record the durable MVP architecture split
- `current-state.md` and `session-log.md` with the new state, changed files, and next steps

- [ ] **Step 4: Re-run the verification commands**

Run: `cd backend && pytest -v`
Run: `cd web && npm run test`
Run: `cd web && npx playwright test`
Expected: PASS again after the documentation changes.

- [ ] **Step 5: Commit**

```bash
git add README.md .codex-memory/source-of-truth.md .codex-memory/decisions.md .codex-memory/current-state.md .codex-memory/session-log.md
git commit -m "docs: align project architecture documentation"
```

## Acceptance Checklist
- `backend/app/main.py` is reduced to app composition.
- Backend use-case orchestration is visible under `app/application/`.
- Backend pure business rules are visible under `app/domain/`.
- Frontend UI components depend on entity-facing types rather than raw transport DTOs.
- Frontend pages are composition roots, not mixed transport-and-screen modules.
- Demo dashboard data is no longer the default runtime source for production-facing pages.
- README and memory documents describe the architecture the code actually uses.

## Commands Summary
- `cd backend && pytest tests/core/test_app_factory.py tests/test_healthcheck.py -v`
- `cd backend && pytest tests/application/test_contract_upload.py tests/api/test_uploads_api.py -v`
- `cd backend && pytest tests/domain/test_contract_analysis.py tests/services/test_policy_analysis.py tests/services/test_rule_evaluator.py tests/services/test_event_scheduler.py tests/services/test_notifications.py tests/tasks/test_alerts_task.py -v`
- `cd backend && pytest -v`
- `cd web && npm run test -- src/entities/contracts/model.test.ts src/entities/dashboard/model.test.ts src/features/analysis/components/findings-table.test.tsx src/features/dashboard/components/events-timeline.test.tsx`
- `cd web && npm run test -- src/features/dashboard/screens/dashboard-screen.test.tsx src/features/contracts/screens/contracts-screen.test.tsx`
- `cd web && npm run test`
- `cd web && npx playwright test tests/e2e/dashboard-alerts.spec.ts`
- `cd web && npx playwright test`

## Out of Scope For This Plan
- Replacing FastAPI, Next.js, SQLAlchemy, or the existing monorepo split
- Full DDD or ports-and-adapters formalization across every module
- Multi-tenant or auth hardening work
- Cloud deployment redesign
