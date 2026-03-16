# F1-A Backend Upload

## Task Brief

- Request: corrigir a falha backend do upload ponta a ponta para arquivos PDF invalidos ou nao parseaveis.
- Risk level: `low-risk single-area`
- Affected areas: `backend`, `docs`, `memory`
- Required roles: `implementation-manager`, `backend-engineer`, `qa-backend`, `documentation-engineer`
- Architecture review required: `no`
- Required artifacts: task brief, implementation handoff, backend QA review, documentation update note
- Key requirements:
  - upload invalido nao pode derrubar a API com erro generico
  - upload invalido nao pode persistir `Contract` ou `ContractVersion` parciais
  - rota deve retornar payload de erro tratavel
  - fluxo feliz existente deve continuar verde
- Blocking concerns known at entry:
  - falha reproduzida apenas com PDF nao parseavel; causa raiz precisava de evidencia objetiva
- Notes marked `a confirmar`:
  - se o frontend vai exibir `detail` bruto ou mapear mensagem propria: a confirmar

## Implementation Handoff

- Implementing role: `backend-engineer`
- Changed files:
  - `backend/app/api/routes/uploads.py`
  - `backend/app/application/contract_upload.py`
  - `backend/app/infrastructure/pdf_text.py`
  - `backend/app/infrastructure/storage.py`
  - `backend/app/tasks/ingestion.py`
  - `backend/app/tasks/archive.py`
  - `backend/tests/api/test_uploads_api.py`
  - `backend/tests/application/test_contract_upload.py`
- Behavior summary:
  - falha de parsing de PDF agora vira erro controlado de upload
  - `/api/uploads/contracts` responde `422` com `{"detail":"Uploaded file is not a readable PDF"}`
  - caso de uso de upload agora controla `commit` no fim e faz rollback + limpeza de arquivo em falhas
- Verification run:
  - `cd backend && C:/Users/win/AppData/Local/Programs/Python/Python313/python.exe -m pytest -q`
  - resultado: `21 passed in 2.44s`
- Residual risks:
  - outros tipos de falha inesperada no pipeline continuam retornando `500`, embora agora sem persistencia parcial
- Follow-up items:
  - nenhum
- Notes marked `a confirmar`:
  - nenhum adicional

## Backend QA Review

- Status: `pass`
- Evidence:
  - regressao adicionada para PDF invalido na API e no caso de uso
  - fluxo feliz de upload mantido
  - suite backend completa verde com `21 passed in 2.44s`
- Non-blocking notes:
  - seria util cobrir futuramente falhas de OCR ou storage com a mesma disciplina transacional

## Documentation Update Note

- Updated docs:
  - `backend/README.md`
  - `docs/squad/artifacts/2026-03-16-f1-a-backend-upload.md`
  - `.codex-memory/patterns.md`
  - `.codex-memory/current-state.md`
  - `.codex-memory/session-log.md`
- Notes marked `a confirmar`:
  - nenhum
