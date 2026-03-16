# F2-A Contract Detail API Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Padronizar a API de listagem, analise e detalhe de contrato para fechar o contrato HTTP que a UI vai consumir nas proximas fases.

**Architecture:** Manter a responsabilidade HTTP em `backend/app/api/routes/contracts.py`, mas extrair a serializacao de listagem e detalhe para schemas e helpers dedicados, evitando montar payload ad-hoc dentro da rota. O backend continua sendo a fonte canonica de score, findings, status e metadados, com o detalhe montado a partir dos modelos persistidos de contrato, versao e analise.

**Tech Stack:** FastAPI, SQLAlchemy, Pydantic, Pytest, SQLite in-memory tests

---

## Workflow Notes
- Executar em worktree isolado.
- Seguir `@superpowers:test-driven-development` para qualquer mudanca de comportamento.
- Como o card toca contrato HTTP do backend, tratar como rota `implementation-manager -> tech-lead -> backend-engineer -> qa-backend -> documentation-engineer`.
- Nao conectar telas do frontend neste card.
- Atualizar o checklist do Trello somente apos verificacao real de cada marco.

## Planned File Structure
- Modify: `backend/app/schemas/contract.py`
  - ampliar os schemas de listagem e criar o contrato de detalhe do contrato.
- Modify: `backend/app/api/routes/contracts.py`
  - enriquecer `GET /api/contracts` e adicionar `GET /api/contracts/{contract_id}`.
- Create: `backend/app/api/serializers/contracts.py`
  - encapsular a serializacao de contrato, versao e analise para listagem e detalhe.
- Modify: `backend/tests/api/test_contracts_api.py`
  - cobrir listagem padronizada, detalhe com analise, detalhe sem analise e `404`.
- Create: `docs/squad/artifacts/2026-03-16-f2-a-contract-detail-api.md`
  - documentar o payload final de listagem e detalhe como artefato do card.
- Modify: `.codex-memory/current-state.md`
  - registrar o estado final verificado do projeto.
- Modify: `.codex-memory/session-log.md`
  - registrar o resumo da sessao.

## Chunk 1: Contract HTTP Design In Code

### Task 1: Expand the API tests to define the final list and detail payloads

**Files:**
- Modify: `backend/tests/api/test_contracts_api.py`

- [ ] **Step 1: Write the failing tests for list and detail payloads**

Add tests that:
- keep the current empty list assertion
- persist a contract, version, and analysis, then assert `GET /api/contracts` returns the enriched list item
- assert `GET /api/contracts/{contract_id}` returns `contract`, `latest_version`, and `latest_analysis`
- assert detail returns `latest_analysis: null` when no analysis exists
- assert unknown contract id returns `404`

- [ ] **Step 2: Run the targeted contracts API tests to verify they fail**

Run: `cd backend && ./.venv/bin/pytest tests/api/test_contracts_api.py -v`
Expected: FAIL because the list response is still minimal and no detail route exists.

### Task 2: Define the canonical Pydantic schemas

**Files:**
- Modify: `backend/app/schemas/contract.py`

- [ ] **Step 1: Implement the minimal schemas required by the failing tests**

Add schemas for:
- enriched list item
- latest version summary
- normalized finding summary
- latest analysis summary
- contract detail block
- top-level detail response

Use existing persisted names where possible and keep field names consistent with the approved spec.

- [ ] **Step 2: Do not touch route logic yet**

Keep this task limited to schema definition so the next failure points at route/serialization gaps, not missing types.

## Chunk 2: Route And Serialization Behavior

### Task 3: Add focused serializers for list and detail payload assembly

**Files:**
- Create: `backend/app/api/serializers/contracts.py`

- [ ] **Step 1: Write the minimal serialization helpers**

Create helpers that:
- derive `latest_version` from the newest `ContractVersion`
- derive `latest_analysis` from the newest `ContractAnalysis`
- normalize `used_ocr` from `extraction_metadata`
- normalize findings from `ContractAnalysisFinding`
- assemble the enriched list item and the full detail payload

- [ ] **Step 2: Keep serializer responsibility narrow**

Do not add database access here; accept ORM objects that the route already loaded.

### Task 4: Implement the list/detail routes against the schemas and serializers

**Files:**
- Modify: `backend/app/api/routes/contracts.py`

- [ ] **Step 1: Implement the minimal route changes to satisfy the tests**

Update `GET /api/contracts` to:
- load contracts ordered by `created_at desc`
- include relationships needed for latest version and latest analysis
- return the enriched list payload

Add `GET /api/contracts/{contract_id}` to:
- load the contract by id
- return `404` when not found
- return the canonical detail payload

- [ ] **Step 2: Run the targeted contracts API tests to verify they pass**

Run: `cd backend && ./.venv/bin/pytest tests/api/test_contracts_api.py -v`
Expected: PASS

- [ ] **Step 3: Commit the backend contract API milestone**

```bash
git add backend/app/schemas/contract.py backend/app/api/serializers/contracts.py backend/app/api/routes/contracts.py backend/tests/api/test_contracts_api.py
git commit -m "feat: add canonical contract detail API"
```

## Chunk 3: Documentation And Full Verification

### Task 5: Document the final payload for downstream UI work

**Files:**
- Create: `docs/squad/artifacts/2026-03-16-f2-a-contract-detail-api.md`

- [ ] **Step 1: Write the payload artifact**

Document:
- endpoint list
- final list payload
- final detail payload
- notes about nullable blocks (`latest_version`, `latest_analysis`)
- notes about `used_ocr` derivation and findings normalization

- [ ] **Step 2: Keep the artifact concise and implementation-facing**

Do not duplicate the whole spec; only capture what future implementers and QA need.

### Task 6: Run backend verification and update project memory

**Files:**
- Modify: `.codex-memory/current-state.md`
- Modify: `.codex-memory/session-log.md`

- [ ] **Step 1: Run the backend verification commands**

Run:
- `cd backend && ./.venv/bin/pytest`

Expected: PASS with the updated contracts API coverage included.

- [ ] **Step 2: Update the Trello checklist only after verification**

Mark complete only after evidence exists for:
- `Definir e normalizar resposta de detalhe do contrato`
- `Fechar score, findings, status e metadados`
- `Garantir API de listagem e detalhe consistente`
- `Cobrir contrato HTTP com testes`
- `Documentar payload final`

- [ ] **Step 3: Update persistent memory**

Record:
- final backend API state
- changed files
- verification evidence
- remaining risks (`pyproject` Python mismatch, frontend still not connected, etc.)

- [ ] **Step 4: Commit docs and memory updates**

```bash
git add docs/squad/artifacts/2026-03-16-f2-a-contract-detail-api.md .codex-memory/current-state.md .codex-memory/session-log.md
git commit -m "docs: record F2-A contract API payload"
```
