# F1-A Frontend Upload

## Task Brief

- Request: consumir no frontend o `422` do upload invalido e exibir mensagem amigavel ao operador.
- Risk level: `low-risk single-area`
- Affected areas: `web`, `docs`, `memory`
- Required roles: `implementation-manager`, `frontend-engineer`, `qa-frontend`, `documentation-engineer`
- Architecture review required: `no`
- Required artifacts: task brief, implementation handoff, frontend QA review, documentation update note
- Key requirements:
  - nao esconder o `detail` conhecido do backend atras de mensagem generica
  - traduzir o erro conhecido para portugues no boundary de transporte
  - manter o fluxo feliz de upload
  - validar o caso invalido por unit test, screen test e E2E com arquivo em disco
- Blocking concerns known at entry:
  - o cliente HTTP descartava qualquer `detail` do backend
- Notes marked `a confirmar`:
  - nenhum

## Implementation Handoff

- Implementing role: `frontend-engineer`
- Changed files:
  - `web/src/lib/api/contracts.ts`
  - `web/src/lib/api/contracts.test.ts`
  - `web/src/features/contracts/screens/contracts-screen.test.tsx`
  - `web/tests/e2e/contract-analysis.spec.ts`
  - `web/tests/fixtures/unreadable-upload.pdf`
  - `docs/superpowers/specs/2026-03-16-contract-upload-error-propagation-design.md`
  - `docs/superpowers/plans/2026-03-16-contract-upload-error-propagation.md`
- Behavior summary:
  - `web/src/lib/api/contracts.ts` agora le `detail` do backend em respostas nao-`ok`
  - o erro conhecido `Uploaded file is not a readable PDF` e traduzido para `O arquivo enviado nao e um PDF legivel.`
  - erros sem payload utilizavel continuam com fallback generico
- Verification run:
  - `cd web && npm run test`
  - resultado: `10 passed`, `14 passed`
  - `cd web && npx playwright test tests/e2e/contract-analysis.spec.ts`
  - resultado: `2 passed`
- Residual risks:
  - consumo de outros erros backend alem do caso conhecido continua simples, sem taxonomia dedicada
- Follow-up items:
  - decidir na `F1-G` se vale documentar mais contratos de erro HTTP alem do upload ilegivel
- Notes marked `a confirmar`:
  - nenhum adicional

## Frontend QA Review

- Status: `pass`
- Evidence:
  - unit test para traducao do `detail` conhecido
  - screen test para alerta renderizado ao operador
  - E2E com arquivo `.pdf` ilegivel em disco
  - suite web e spec de contratos verdes
- Non-blocking notes:
  - se novos erros operator-facing surgirem, pode valer extrair um mapeador compartilhado de mensagens HTTP

## Documentation Update Note

- Updated docs:
  - `docs/squad/artifacts/2026-03-16-f1-a-frontend-upload.md`
  - `docs/superpowers/specs/2026-03-16-contract-upload-error-propagation-design.md`
  - `docs/superpowers/plans/2026-03-16-contract-upload-error-propagation.md`
  - `.codex-memory/patterns.md`
  - `.codex-memory/current-state.md`
  - `.codex-memory/session-log.md`
- Notes marked `a confirmar`:
  - nenhum adicional
