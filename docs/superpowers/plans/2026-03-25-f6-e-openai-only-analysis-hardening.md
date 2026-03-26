# F6-E OpenAI-Only Analysis Hardening Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove Gemini from the backend runtime, standardize contract analysis on OpenAI with `gpt-5-mini` as the default model, and harden prompts plus scoring for stronger PT-BR legal analysis.

**Architecture:** Keep one OpenAI adapter as the only LLM boundary, preserve deterministic fallback when no API key is configured, and move score composition out of the current `max(llm, deterministic)` shortcut. Extend the canonical playbook and prompt layer so the backend produces auditable PT-BR findings grounded in franchise clauses and core lease-law checks.

**Tech Stack:** FastAPI, SQLAlchemy, Pydantic, OpenAI Python SDK, pytest

---

### Task 1: Remove Gemini runtime and config

**Files:**
- Modify: `backend/pyproject.toml`
- Modify: `backend/requirements.txt`
- Modify: `backend/app/core/app_factory.py`
- Modify: `backend/tests/core/test_app_factory.py`
- Modify: `.env.example`
- Modify: `README.md`
- Delete: `backend/app/infrastructure/gemini_client.py`
- Delete: `backend/app/infrastructure/gemini_models.py`

- [ ] **Step 1: Write failing runtime/config tests**
Add or extend tests to assert the app factory no longer reads `GOOGLE_API_KEY` and wires the LLM client only from `OPENAI_API_KEY`.

- [ ] **Step 2: Run the focused app-factory tests and verify RED**
Run: `cd backend && py -3.13 -m pytest tests/core/test_app_factory.py -q`

- [ ] **Step 3: Remove Gemini dependency and runtime wiring**
Drop `google-genai`, delete Gemini modules, and simplify app boot to either OpenAI or deterministic fallback.

- [ ] **Step 4: Update env and README contract**
Replace Gemini env/config references with `OPENAI_API_KEY` and `OPENAI_MODEL`.

- [ ] **Step 5: Re-run focused app-factory tests and verify GREEN**
Run: `cd backend && py -3.13 -m pytest tests/core/test_app_factory.py -q`

### Task 2: Standardize the OpenAI adapter

**Files:**
- Modify: `backend/app/infrastructure/openai_client.py`
- Modify: `backend/tests/infrastructure/test_prompts.py`
- Create: `backend/tests/infrastructure/test_openai_client.py`
- Modify: `backend/app/infrastructure/docx_generator.py`
- Modify: `backend/tests/infrastructure/test_docx_generator.py`
- Modify: `backend/app/api/routes/contracts.py`
- Modify: `backend/app/application/contract_pipeline.py`

- [ ] **Step 1: Write failing OpenAI adapter tests**
Cover default model selection, typed fallback behavior, summary flow, correction flow, and imports no longer depending on Gemini-specific models.

- [ ] **Step 2: Run focused infrastructure tests and verify RED**
Run: `cd backend && py -3.13 -m pytest tests/infrastructure/test_openai_client.py tests/infrastructure/test_docx_generator.py -q`

- [ ] **Step 3: Make OpenAI the only typed adapter**
Set default model to `gpt-5-mini`, allow `OPENAI_MODEL` override, and move shared response models under an OpenAI-neutral module or existing schemas.

- [ ] **Step 4: Re-run focused infrastructure tests and verify GREEN**
Run: `cd backend && py -3.13 -m pytest tests/infrastructure/test_openai_client.py tests/infrastructure/test_docx_generator.py -q`

### Task 3: Strengthen prompts and playbook coverage

**Files:**
- Modify: `backend/app/infrastructure/prompts.py`
- Modify: `backend/app/domain/playbook.py`
- Modify: `backend/tests/infrastructure/test_prompts.py`

- [ ] **Step 1: Write failing prompt/playbook tests**
Assert PT-BR-only instructions, explicit legal checks, score justification requirements, and coverage for exclusividade, prazo, aluguel/valor, reajuste, cessao/sublocacao, fiador, vistorias, obras, infraestrutura, garantias, renovacao and assinaturas.

- [ ] **Step 2: Run prompt tests and verify RED**
Run: `cd backend && py -3.13 -m pytest tests/infrastructure/test_prompts.py -q`

- [ ] **Step 3: Expand prompts and playbook minimally**
Update prompts and canonical clauses using the versioned repo/spec requirements as the verified source baseline.

- [ ] **Step 4: Re-run prompt tests and verify GREEN**
Run: `cd backend && py -3.13 -m pytest tests/infrastructure/test_prompts.py -q`

### Task 4: Rework scoring and policy analysis

**Files:**
- Modify: `backend/app/domain/contract_analysis.py`
- Modify: `backend/app/services/policy_analysis.py`
- Modify: `backend/tests/domain/test_contract_analysis.py`
- Modify: `backend/tests/services/test_policy_analysis.py`

- [ ] **Step 1: Write failing scoring tests**
Add tests for weighted final scoring, essential-clause penalties, and the removal of the pure `max(llm, deterministic)` rule.

- [ ] **Step 2: Run domain/service tests and verify RED**
Run: `cd backend && py -3.13 -m pytest tests/domain/test_contract_analysis.py tests/services/test_policy_analysis.py -q`

- [ ] **Step 3: Implement weighted score composition**
Compute deterministic severity by category, merge with LLM findings, and cap final score predictably.

- [ ] **Step 4: Re-run domain/service tests and verify GREEN**
Run: `cd backend && py -3.13 -m pytest tests/domain/test_contract_analysis.py tests/services/test_policy_analysis.py -q`

### Task 5: Regression verification and closeout docs

**Files:**
- Modify: `README.md`
- Modify: `.env.example`
- Modify: `.codex-memory/current-state.md`
- Modify: `.codex-memory/session-log.md`

- [ ] **Step 1: Run targeted backend regression suite**
Run: `cd backend && py -3.13 -m pytest tests/core/test_app_factory.py tests/infrastructure/test_prompts.py tests/infrastructure/test_openai_client.py tests/infrastructure/test_docx_generator.py tests/domain/test_contract_analysis.py tests/services/test_policy_analysis.py -q`

- [ ] **Step 2: Update operational docs and memory**
Record OpenAI-only runtime, model default, score strategy, and any benchmark limitation due to missing verified API execution.

- [ ] **Step 3: Report evidence**
Summarize exact commands, pass counts, residual risks, and whether benchmark remained documentation-only.
