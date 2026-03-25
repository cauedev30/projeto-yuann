# LegalBoard Contract Lifecycle OpenAI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver `Acervo`, `Historico`, versionamento por contrato, comparacao entre versoes, analise juridica OpenAI-only e base de conhecimento obrigatoria sem travar a evolucao futura para Postgres/Supabase.

**Architecture:** Expand the backend contract lifecycle model first, then bind analyses to versions, then expose version/history endpoints, then update the Next.js workspace to separate active contracts from historical analyses. Replace Gemini entirely with a single OpenAI adapter, move the legal reasoning to a deterministic-plus-LLM pipeline, and keep the Supabase decision as a bounded infrastructure spike rather than a blocker.

**Tech Stack:** FastAPI, SQLAlchemy, SQLite-compatible schema with Postgres-safe direction, Next.js 15, React 19, TypeScript, OpenAI Python SDK, Vitest, Playwright, pytest

---

## Task 1: Backend Lifecycle Foundation

**Files:**
- Modify: `backend/app/db/models/contract.py`
- Modify: `backend/app/schemas/contract.py`
- Modify: `backend/app/api/serializers/contracts.py`
- Modify: `backend/app/api/routes/contracts.py`
- Modify: `backend/tests/api/test_contracts_api.py`
- Modify: `web/src/entities/contracts/model.ts`
- Modify: `web/src/lib/api/contracts.ts`

- [ ] **Step 1: Add failing backend tests for active/history fields**
Run or extend tests to assert contract payloads now expose:
`is_active`, `activated_at`, `last_accessed_at`, `last_analyzed_at`.

- [ ] **Step 2: Add lifecycle fields to persistence**
Add lifecycle columns on `Contract` for active state and operational timestamps.

- [ ] **Step 3: Expose lifecycle fields in schemas and serializers**
Extend list/detail schemas and serializers so frontend can render `Acervo` and `Historico`.

- [ ] **Step 4: Add filtering contract list API**
Support a scope such as `active`, `history`, and `all`, while keeping current pagination behavior.

- [ ] **Step 5: Add mutation for activate/deactivate**
Allow the UI to mark a contract as active or inactive without rewriting unrelated fields.

- [ ] **Step 6: Verify backend contract tests**
Run: `cd backend && python -m pytest tests/api/test_contracts_api.py -q`

- [ ] **Step 7: Update frontend entities and transport**
Map the new lifecycle fields in `web/src/entities/contracts/model.ts` and transport readers.

- [ ] **Step 8: Verify frontend mapping tests**
Run: `cd web && npm run test -- src/lib/api/contracts.test.ts src/entities/contracts/model.test.ts`

## Task 2: OpenAI-Only Analysis Adapter

**Files:**
- Modify: `backend/pyproject.toml`
- Modify: `backend/app/core/app_factory.py`
- Modify: `backend/app/infrastructure/openai_client.py`
- Delete: `backend/app/infrastructure/gemini_client.py`
- Delete: `backend/app/infrastructure/gemini_models.py`
- Modify: `backend/app/infrastructure/prompts.py`
- Modify: `.env.example`
- Modify: `README.md`
- Modify: `backend/tests/infrastructure/test_prompts.py`

- [ ] **Step 1: Remove Gemini dependencies and config**
Drop `google-genai`, `GOOGLE_API_KEY`, and Gemini fallback wiring from runtime/config/docs.

- [ ] **Step 2: Standardize one OpenAI adapter**
Keep a single OpenAI client for:
`analyze_contract`, `summarize_contract`, `generate_corrected_contract`, and future version diff analysis.

- [ ] **Step 3: Set default model to `gpt-5-mini`**
Use `gpt-5-mini` as the default configured analysis model and make it overrideable by env var.

- [ ] **Step 4: Rewrite prompts for stricter legal output**
Prompts must require:
- PT-BR only
- clause presence/absence
- explicit mention of prazo, aluguel/valor, reajuste, exclusividade, cessao, fiador, vistorias, obras
- justification of score-driving items

- [ ] **Step 5: Verify prompt and client tests**
Run: `cd backend && python -m pytest tests/infrastructure/test_prompts.py tests/infrastructure/test_gemini_client.py -q`
Expected follow-up change: rename or replace Gemini-specific tests with OpenAI-specific ones.

## Task 3: Knowledge Base and Score Rework

**Files:**
- Modify: `backend/app/domain/playbook.py`
- Modify: `backend/app/domain/contract_analysis.py`
- Modify: `backend/app/services/policy_analysis.py`
- Modify: `backend/app/schemas/analysis.py`
- Modify: `backend/tests/domain/test_contract_analysis.py`
- Modify: `backend/tests/services/test_policy_analysis.py`
- Create: `backend/tests/fixtures/knowledge_base/` as needed

- [ ] **Step 1: Expand the playbook with all mandatory clauses**
Bring the local `.docx` obligations into the canonical playbook, including exclusividade, prazo, vistorias, obras, cessao, fiador, obrigacao de nao fazer, assinaturas and infrastructure constraints.

- [ ] **Step 2: Encode law-derived checks from Lei 8.245**
Add deterministic checks for:
- cessao/sublocacao consent
- garantia locaticia
- benfeitorias/infraestrutura
- renovacao logic for non-residential leases

- [ ] **Step 3: Rework score calculation**
Replace the current `max(llm, deterministic)` pattern with weighted category scoring plus explicit caps.

- [ ] **Step 4: Enrich findings payload**
Ensure findings can state:
- clause essentiality
- present/missing/deviating
- severity
- rationale
- suggested correction

- [ ] **Step 5: Verify legal analysis tests**
Run: `cd backend && python -m pytest tests/domain/test_contract_analysis.py tests/services/test_policy_analysis.py -q`

## Task 4: Version-Bound Analyses and Version History API

**Files:**
- Modify: `backend/app/db/models/analysis.py`
- Modify: `backend/app/db/models/contract.py`
- Modify: `backend/app/application/contract_upload.py`
- Modify: `backend/app/application/contract_pipeline.py`
- Modify: `backend/app/api/routes/uploads.py`
- Modify: `backend/app/api/routes/contracts.py`
- Modify: `backend/app/api/serializers/contracts.py`
- Modify: `backend/app/schemas/contract.py`
- Modify: `backend/tests/application/test_contract_upload.py`
- Modify: `backend/tests/api/test_contracts_api.py`

- [ ] **Step 1: Add failing tests for analysis-per-version behavior**
Assert each analysis now records the exact `contract_version_id`.

- [ ] **Step 2: Add explicit version numbering**
Persist version sequence per contract and expose it in the API.

- [ ] **Step 3: Bind analysis creation to the uploaded version**
Every new upload under the same contract must create:
- a new `ContractVersion`
- a new `ContractAnalysis` tied to that version

- [ ] **Step 4: Expose version history endpoints**
Add endpoints to:
- list versions for a contract
- fetch one version detail
- upload a new version for an existing contract

- [ ] **Step 5: Update last analyzed timestamp**
Whenever a version analysis completes, update `contract.last_analyzed_at`.

- [ ] **Step 6: Verify upload and contract API tests**
Run: `cd backend && python -m pytest tests/application/test_contract_upload.py tests/api/test_contracts_api.py -q`

## Task 5: Version Diff and Analysis Diff

**Files:**
- Modify: `backend/app/infrastructure/openai_client.py`
- Create: `backend/app/application/version_diff.py`
- Modify: `backend/app/api/routes/contracts.py`
- Modify: `backend/app/schemas/contract.py`
- Create: `backend/tests/application/test_version_diff.py`
- Modify: `web/src/entities/contracts/model.ts`
- Modify: `web/src/lib/api/contracts.ts`

- [ ] **Step 1: Add diff response schema**
Define payloads for:
- textual changes between two versions
- finding deltas between two analyses
- high-level executive summary of what changed

- [ ] **Step 2: Implement backend diff service**
Combine deterministic signals plus OpenAI summarization to identify changes in:
- prazo
- aluguel/valor
- reajuste
- exclusividade
- partes
- clausulas essenciais

- [ ] **Step 3: Add compare endpoint**
Expose endpoint to compare a selected version against the previous or any chosen baseline.

- [ ] **Step 4: Add transport and entity mapping**
Map version list and diff payloads to frontend-safe structures.

- [ ] **Step 5: Verify targeted tests**
Run: `cd backend && python -m pytest tests/application/test_version_diff.py -q`

## Task 6: Frontend Workspace Split (`Acervo` and `Historico`)

**Files:**
- Modify: `web/src/components/navigation/app-shell.tsx`
- Create: `web/src/app/(app)/acervo/page.tsx`
- Create: `web/src/app/(app)/historico/page.tsx`
- Create: `web/src/features/contracts/screens/acervo-screen.tsx`
- Create: `web/src/features/contracts/screens/historico-screen.tsx`
- Modify: `web/src/features/dashboard/components/manage-contracts-panel.tsx`
- Modify: `web/src/features/dashboard/screens/dashboard-screen.tsx`
- Modify: `web/src/features/dashboard/components/empty-dashboard-state.tsx`
- Modify: `web/src/features/contracts/components/contracts-list-panel.tsx`
- Modify: `web/src/features/contracts/screens/contracts-screen.tsx`

- [ ] **Step 1: Add navigation entries**
Expose `Acervo` and `Historico` in desktop and mobile navigation.

- [ ] **Step 2: Build `Acervo` screen**
Show only active contracts and allow toggling active state from the UI.

- [ ] **Step 3: Build `Historico` screen**
Show recently analyzed inactive contracts with:
- ultima analise
- ultimo acesso
- status
- score
- remaining retention window

- [ ] **Step 4: Rename and clean copy**
Replace `portfolio`, `portifolio`, and English terms with consistent PT-BR wording.

- [ ] **Step 5: Verify frontend screen tests**
Run: `cd web && npm run test -- src/components/navigation/app-shell.test.tsx src/features/dashboard/screens/dashboard-screen.test.tsx src/features/contracts/screens/contracts-screen.test.tsx`

## Task 7: Contract Detail, Timeline and Version UX

**Files:**
- Modify: `web/src/features/contracts/screens/contract-detail-screen.tsx`
- Modify: `web/src/features/contracts/components/metadata-section.tsx`
- Modify: `web/src/features/contracts/components/event-timeline.tsx`
- Modify: `web/src/features/contracts/components/findings-section.tsx`
- Create: `web/src/features/contracts/components/version-history-panel.tsx`
- Create: `web/src/features/contracts/components/version-diff-panel.tsx`
- Modify: `web/src/features/contracts/screens/contract-detail-screen.test.tsx`
- Modify: `web/src/features/contracts/components/metadata-section.test.tsx`
- Modify: `web/src/features/contracts/components/event-timeline.test.tsx`

- [ ] **Step 1: Fix terminology in contract detail**
Change:
- `Minuta de terceiro` -> `Contrato padrao`
- `monthly` -> `aluguel`

- [ ] **Step 2: Improve metadata presentation**
Render `locador`, `locatario` and `fiador` explicitly when present.

- [ ] **Step 3: Enrich findings and key points**
Highlight:
- prazo
- aluguel/valor
- reajuste monetario
- exclusividade
- presenca ou ausencia de clausulas essenciais

- [ ] **Step 4: Add version history panel**
Allow opening any previous version and selecting comparison targets.

- [ ] **Step 5: Add diff panel**
Show what changed in text and in legal analysis between versions.

- [ ] **Step 6: Add reajuste monetario to the timeline**
Ensure timeline surfaces readjustment clearly in both detail and dashboard contexts.

- [ ] **Step 7: Verify UI tests**
Run: `cd web && npm run test -- src/features/contracts/screens/contract-detail-screen.test.tsx src/features/contracts/components/metadata-section.test.tsx src/features/contracts/components/event-timeline.test.tsx`

## Task 8: Retention Job and Safe Expurgo

**Files:**
- Create: `backend/app/tasks/retention.py`
- Modify: `backend/app/api/routes/contracts.py` if manual trigger/debug endpoint is needed
- Modify: `backend/app/infrastructure/storage.py`
- Create: `backend/tests/tasks/test_retention_task.py`
- Modify: `README.md`
- Modify: `docs/release-candidate-runbook.md`

- [ ] **Step 1: Add failing retention tests**
Assert the job removes only contracts that:
- are not active
- have `last_analyzed_at <= now - 30 days`

- [ ] **Step 2: Delete contract graph safely**
Ensure expurgo removes:
- contract
- versions
- analyses
- findings
- stored files

- [ ] **Step 3: Preserve active contracts**
Explicit test: active contracts survive even if older than 30 days.

- [ ] **Step 4: Add operational entrypoint**
Expose a callable job or CLI path that can later be scheduled by cron/worker.

- [ ] **Step 5: Verify retention tests**
Run: `cd backend && python -m pytest tests/tasks/test_retention_task.py -q`

## Task 9: Supabase Spike

**Files:**
- Create: `docs/superpowers/specs/2026-03-25-supabase-spike-notes.md`
- Create: `docs/superpowers/plans/2026-03-25-supabase-migration-spike.md`
- Modify: `backend/app/db/models/*.py` only if portability gaps must be documented in-code

- [ ] **Step 1: Audit SQLite-specific coupling**
Document all uses of SQLite-only dialect imports and runtime assumptions.

- [ ] **Step 2: Define Postgres-safe target shape**
Specify model, migration, storage and scheduling changes required for Supabase.

- [ ] **Step 3: Compare Railway current state vs Supabase**
Evaluate:
- retention scheduling
- operational simplicity
- database backups
- file storage split
- migration risk

- [ ] **Step 4: Produce go/no-go recommendation**
Result must end in one of:
- migrate now
- prepare and migrate later
- stay on current stack for this phase

## Task 10: Full Verification and Release Gate

**Files:**
- Modify: `README.md`
- Modify: `docs/release-candidate-runbook.md`
- Modify: `web/tests/e2e/*.spec.ts` as needed
- Modify: `backend/tests/support/dashboard_seed.py`
- Modify: `web/tests/fixtures/*` as needed

- [ ] **Step 1: Update fixtures and seeds**
Ensure fixtures cover:
- active contract
- inactive historical contract
- multiple versions of one contract
- missing essential clause
- readjustment event

- [ ] **Step 2: Add regression coverage**
Cover the known issues:
- prazo 12 vs 60
- score inflation
- English labels
- missing exclusividade details

- [ ] **Step 3: Run backend suite**
Run: `cd backend && python -m pytest -q`

- [ ] **Step 4: Run web unit suite**
Run: `cd web && npm run test`

- [ ] **Step 5: Run typecheck, lint and build**
Run:
- `cd web && npx tsc --noEmit`
- `cd web && npm run lint`
- `cd web && npm run build`

- [ ] **Step 6: Run E2E**
Run: `cd web && npm run e2e`

- [ ] **Step 7: Record evidence in docs**
Update release and operational docs with the new flows, retention behavior and OpenAI-only configuration.
