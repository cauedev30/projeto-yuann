# Review: LegalBoard Modernization Spec

> Reviewer: Senior Code Reviewer (Claude Opus 4.6)
> Date: 2026-03-21
> Spec: `2026-03-21-legalboard-modernization-design.md`

---

## CRITICAL Issues

### 1. API Key Leaked in Spec (CRITICAL)
**Section 8** contains a real `GOOGLE_API_KEY` value (`AIzaSyBud1Wju8IjlegIxBAGMm48Al3bbRWUZro`) directly in the spec document. This is a credential leak. If this doc is committed to git, the key is exposed in history forever.

**Fix:** Remove the real key immediately. Replace with placeholder `your-google-ai-studio-key`. Rotate the exposed key in Google AI Studio.

### 2. Sync Routes with SSE Streaming (CRITICAL)
**Section 5/6.5** specifies `POST /contracts/{id}/analyze-stream` as SSE, but the existing backend uses synchronous SQLAlchemy sessions (`Session = Depends(get_session)`). FastAPI SSE with `StreamingResponse` requires `async def` endpoints. The current codebase uses sync `def` handlers throughout.

**Fix:** Either (a) make the SSE endpoint async with `AsyncSession`, or (b) explicitly document that the SSE endpoint will use `run_in_executor` for the sync DB calls. This is an architectural decision that needs to be specified.

### 3. Database Migration Strategy Missing (CRITICAL)
The spec replaces `Policy`/`PolicyRule` with hardcoded `PLAYBOOK_CLAUSES` but does not address:
- What happens to existing `policy` table data and foreign keys?
- Are there Alembic migrations needed to drop/modify tables?
- The `policies.py` routes file still exists -- should it be removed?
- Existing `ContractAnalysis.findings` likely reference policy rules -- how are these migrated?

**Fix:** Add a section on database migration plan: which tables to drop, which FKs to update, and a migration script outline.

---

## IMPORTANT Issues

### 4. Env Var Naming Inconsistency (Important)
The spec says the Gemini key uses `GOOGLE_API_KEY`, but the existing `.env.example` uses `OPENAI_API_KEY`. The spec does not mention updating `backend/app/core/config.py` (which likely reads `OPENAI_API_KEY`) or updating `docker-compose.yml` environment.

**Fix:** Add explicit instructions to update `config.py` and `.env.example` with the new env var name. Document the transition path.

### 5. Missing PyMuPDF Dependency (Important)
**Section 5** specifies "PyMuPDF extrai texto com metadata de pagina" but PyMuPDF (`pymupdf` or `fitz`) is NOT in `pyproject.toml` dependencies. The existing `pdf_text.py` may use a different library.

**Fix:** Add `pymupdf` to the dependencies list in Section 8. Clarify if this is a new dependency or if the existing PDF extraction approach is being changed.

### 6. No Rate Limiting / Token Budget (Important)
The spec mentions "retry 1x with backoff" for Gemini failures but does not address:
- Max token budget per request (Gemini 2.5 Flash has limits)
- Rate limiting on the API endpoints to prevent abuse
- Cost controls (e.g., max analyses per day)

**Fix:** Add a subsection on resource limits and cost guardrails.

### 7. Corrected Contract Storage Not Specified (Important)
**Section 5, Etapa 3** generates a corrected contract but the spec does not clarify:
- Is the corrected contract stored in the database?
- Is it stored in MinIO/S3 (which is already in docker-compose)?
- What is the data model? New table? New field on `ContractAnalysis`?

**Fix:** Add data model for corrected contracts -- table schema or storage strategy.

### 8. Frontend SSE Reconnection Strategy Incomplete (Important)
**Section 9** says "frontend reconecta, busca estado via GET" but there is no `GET` endpoint specified for fetching analysis progress/state. The existing `GET /{id}` returns the contract, not the streaming state.

**Fix:** Add a `GET /contracts/{id}/analysis-status` endpoint spec, or clarify how the frontend recovers state after SSE disconnect.

---

## Minor Issues / Suggestions

### 9. Existing `services/` Layer Not Addressed (Minor)
The codebase has a `backend/app/services/` directory with `policy_analysis.py`, `rule_evaluator.py`, `pdf_text.py`, etc. The spec creates new files in `infrastructure/` but does not mention what happens to the parallel `services/` layer. This risks duplicated logic.

**Fix:** Clarify which `services/` files are deprecated/removed vs kept.

### 10. No Rollback Plan for LLM Migration (Minor)
Removing OpenAI entirely is a one-way door. If Gemini 2.5 Flash quality proves insufficient for Portuguese legal text, there is no fallback.

**Fix:** Consider keeping an `LLMClient` interface/protocol so the implementation can be swapped. This also makes testing easier.

### 11. `aiosqlite` Dependency Unused or Misplaced (Minor)
`pyproject.toml` lists `aiosqlite` but the codebase uses sync SQLAlchemy with PostgreSQL (per docker-compose). The SSE feature would benefit from async, but the spec does not address this mismatch.

### 12. Test Strategy Lacks Detail (Minor)
Section 10 lists test categories but does not specify:
- Mock strategy for Gemini SDK (VCR cassettes? Manual mocks?)
- Fixture files for contract PDFs
- Whether existing tests in `tests/services/test_policy_analysis.py` and `test_rule_evaluator.py` should be updated or removed

### 13. Rebranding Scope Incomplete (Minor)
The spec says to rename to "LegalBoard" but does not mention:
- `docker-compose.yml` still uses `POSTGRES_DB: legaltech`
- The `.env.example` uses `APP_NAME=legaltech-mvp`
- API prefix is `/api/contracts` -- does this stay?

---

## Summary

| Severity | Count |
|----------|-------|
| Critical | 3     |
| Important| 5     |
| Minor    | 5     |

The spec is well-structured and covers the major feature areas. The three critical issues (leaked API key, sync/async mismatch for SSE, missing DB migration plan) must be resolved before implementation begins. The important issues around missing dependencies, storage strategy, and env var consistency should be addressed in a spec revision.
