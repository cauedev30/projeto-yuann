# F6-F Contract Detail, Timeline and PT-BR Copy Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Improve the contract detail flow so it presents richer PT-BR copy, clearer parties and metadata, stronger executive key points, and explicit monetary readjustment in the timeline.

**Architecture:** Keep the existing contract detail route, API surface, and versioning flow intact. Make only the minimum backend changes needed to enrich `parties` extraction and summary prompt coverage, then adapt the frontend detail screen and supporting components to consume the richer payload honestly without inventing missing data.

**Tech Stack:** FastAPI, Pydantic, OpenAI Python SDK, pytest, Next.js App Router, React, TypeScript, Vitest, React Testing Library

---

## Chunk 1: Backend Support

### Task 1: Enrich contract metadata parties extraction

**Files:**
- Modify: `backend/app/domain/contract_metadata.py`
- Modify: `backend/tests/services/test_contract_metadata.py`

- [ ] **Step 1: Write the failing metadata tests**

Add focused tests covering:
- extraction of `locador`, `locatario` and `fiador` when the contract text exposes those roles clearly
- fallback preservation of `entities` when role-specific parsing is partial
- honest absence when a role is not present in the text

- [ ] **Step 2: Run the focused metadata tests and verify RED**

Run: `cd backend && .\.venv\Scripts\python -m pytest tests/services/test_contract_metadata.py -q --basetemp=.pytest-tmp`

Expected: FAIL because the richer `parties` structure does not exist yet.

- [ ] **Step 3: Implement the minimal parser changes**

Update `extract_contract_metadata` so `parties` becomes a richer dict while staying backward compatible. Preserve `entities`, then add role-specific keys only when there is enough evidence in the text:

```python
{
    "entities": [...],
    "landlord": "...",
    "tenant": "...",
    "guarantor": "...",
}
```

Do not invent data. If a role is missing, omit it or leave it empty.

- [ ] **Step 4: Re-run the metadata tests and verify GREEN**

Run: `cd backend && .\.venv\Scripts\python -m pytest tests/services/test_contract_metadata.py -q --basetemp=.pytest-tmp`

Expected: PASS.

### Task 2: Harden the contract summary prompt for F6-F coverage

**Files:**
- Modify: `backend/app/infrastructure/prompts.py`
- Modify: `backend/tests/infrastructure/test_prompts.py`

- [ ] **Step 1: Write the failing prompt tests**

Add tests asserting that the summary prompt explicitly asks for:
- prazo
- aluguel/valor
- reajuste monetario
- exclusividade
- cessao/sublocacao
- garantias/fiador
- vistorias
- obras/infraestrutura
- explicit treatment of absent information as `Nao identificado` or equivalent

- [ ] **Step 2: Run the focused prompt tests and verify RED**

Run: `cd backend && .\.venv\Scripts\python -m pytest tests/infrastructure/test_prompts.py -q --basetemp=.pytest-tmp`

Expected: FAIL because the current summary instructions are too generic.

- [ ] **Step 3: Update the summary prompt minimally**

Strengthen `SUMMARY_SYSTEM_PROMPT` and `build_summary_user_prompt` so the LLM produces executive PT-BR output with clause coverage aligned to F6-F, without changing the route or response schema.

- [ ] **Step 4: Re-run the prompt tests and verify GREEN**

Run: `cd backend && .\.venv\Scripts\python -m pytest tests/infrastructure/test_prompts.py -q --basetemp=.pytest-tmp`

Expected: PASS.

## Chunk 2: Frontend Components

### Task 3: Improve metadata and timeline components

**Files:**
- Modify: `web/src/features/contracts/components/metadata-section.tsx`
- Modify: `web/src/features/contracts/components/metadata-section.test.tsx`
- Modify: `web/src/features/contracts/components/event-timeline.tsx`
- Modify: `web/src/features/contracts/components/event-timeline.test.tsx`
- Modify: `web/src/entities/contracts/model.ts`

- [ ] **Step 1: Write the failing component tests**

Add or update tests to cover:
- `MetadataSection` grouping parties into clear roles when available
- fallback rendering when only generic entities are present
- explicit rendering of aluguel, reajuste, carencia and multa
- timeline label `Reajuste monetario` for `readjustment`

- [ ] **Step 2: Run the focused frontend tests and verify RED**

Run: `cd web && npm.cmd run test -- src/features/contracts/components/metadata-section.test.tsx src/features/contracts/components/event-timeline.test.tsx`

Expected: FAIL because the current rendering is still generic.

- [ ] **Step 3: Implement the minimal component changes**

Update `MetadataSection` to render:
- `Partes`
- `Datas`
- `Condicoes financeiras`

Render role-specific values first, then generic entities as fallback. Keep honest empty states.

Update `EventTimeline` label mapping:

```ts
readjustment: "Reajuste monetario"
```

If needed, adjust `model.ts` mapping so the richer `parties` payload remains typed and backward compatible.

- [ ] **Step 4: Re-run the focused frontend tests and verify GREEN**

Run: `cd web && npm.cmd run test -- src/features/contracts/components/metadata-section.test.tsx src/features/contracts/components/event-timeline.test.tsx`

Expected: PASS.

### Task 4: Improve contract detail and summary presentation

**Files:**
- Modify: `web/src/features/contracts/screens/contract-detail-screen.tsx`
- Modify: `web/src/features/contracts/screens/contract-detail-screen.module.css`
- Modify: `web/src/features/contracts/screens/contract-detail-screen.test.tsx`
- Modify: `web/src/features/contracts/components/contract-summary-panel.tsx`
- Modify: `web/src/features/contracts/components/contracts-list-panel.tsx`
- Modify: `web/src/features/contracts/components/upload-summary-cards.tsx`
- Modify: `web/src/features/contracts/components/upload-form.tsx`
- Modify: `web/src/features/contracts/components/upload-form.test.tsx`

- [ ] **Step 1: Write the failing detail-screen tests**

Extend the detail tests to cover:
- revised PT-BR copy for source labels
- display of ultimo acesso and ultima analise in the header/detail summary
- richer presentation of summary and key points
- continuity of historical version flow and existing recovery states

- [ ] **Step 2: Run the focused detail tests and verify RED**

Run: `cd web && npm.cmd run test -- src/features/contracts/screens/contract-detail-screen.test.tsx src/features/contracts/components/upload-form.test.tsx`

Expected: FAIL because the current copy and detail presentation do not reflect F6-F.

- [ ] **Step 3: Implement the minimal UI changes**

In `contract-detail-screen.tsx`:
- replace impacted source label copy from `Minuta de terceiro` to `Contrato padrao`
- surface `ultimo acesso` and `ultima analise` in the visible detail summary
- keep the current loading, error, diff and version behavior intact

In `contract-summary-panel.tsx`:
- keep the executive summary short
- present `Principais Pontos` as a more useful checklist-style block
- avoid vague fallback wording

Update other touched frontend components only where F6-F still leaves residual inconsistent copy.

- [ ] **Step 4: Re-run the focused detail tests and verify GREEN**

Run: `cd web && npm.cmd run test -- src/features/contracts/screens/contract-detail-screen.test.tsx src/features/contracts/components/upload-form.test.tsx`

Expected: PASS.

## Chunk 3: Full Verification and Closeout

### Task 5: Run regression suites and update task memory

**Files:**
- Modify: `.codex-memory/current-state.md`
- Modify: `.codex-memory/session-log.md`

- [ ] **Step 1: Run the backend regression suite**

Run: `cd backend && .\.venv\Scripts\python -m pytest -q --basetemp=.pytest-tmp`

- [ ] **Step 2: Run the frontend regression suite**

Run: `cd web && npm.cmd run test`

- [ ] **Step 3: Update project memory**

Record:
- F6-F scope actually implemented
- exact commands run
- pass counts
- any residual risks or intentionally deferred items

- [ ] **Step 4: Prepare implementation handoff**

Summarize:
- changed files
- behavior outcomes
- verification evidence
- remaining risks
