# F2-B Contracts Real API

## Task Brief

- Request: conectar a listagem e o detalhe de contratos do frontend ao contrato HTTP real publicado pela `F2-A`.
- Risk level: `medium-risk feature`
- Affected areas: `web`, `docs`, `memory`
- Required roles: `implementation-manager`, `tech-lead`, `frontend-engineer`, `qa-frontend`, `documentation-engineer`
- Architecture review required: `yes`
- Required artifacts: task brief, implementation handoff, frontend QA review, documentation update note
- Key requirements:
  - consumir `GET /api/contracts` e `GET /api/contracts/{contract_id}` sem reabrir a `F2-A`
  - tratar `loading`, `empty`, `error` e `refresh` na lista
  - substituir o placeholder do detalhe por uma tela real com `404` e estados parciais
  - refrescar a lista apos upload bem-sucedido e validar a navegacao lista -> detalhe
- Blocking concerns known at entry:
  - `main` local estava atrasado em relacao a `origin/main`, entao o contrato canonico da `F2-A` precisava ser confirmado antes da implementacao
- Notes marked `a confirmar`:
  - nome exato do proximo card da fase 2 sem acesso ao Trello na abertura da tarefa

## Implementation Handoff

- Implementing role: `frontend-engineer`
- Changed files:
  - `web/src/features/contracts/screens/contract-detail-screen.tsx`
  - `web/src/features/contracts/screens/contract-detail-screen.test.tsx`
  - `web/tests/e2e/contracts-list-detail.spec.ts`
  - `docs/squad/artifacts/2026-03-16-f2-b-contracts-real-api.md`
  - `./.codex-memory/current-state.md`
  - `./.codex-memory/session-log.md`
- Behavior summary:
  - `/contracts` segue consumindo a lista real do backend, com estados explicitos de `loading`, `empty`, `error` e `refresh`, sem fabricar itens locais apos upload.
  - `/contracts/[contractId]` agora fecha tambem o gap remanescente da `F2-B`: erro generico na carga inicial ou apos refresh expoe CTA `Tentar novamente` na propria UI, preservando `404` como estado dedicado.
  - a regressao do detalhe cobre retry apos falha inicial e recuperacao apos refresh quebrado.
  - o E2E `contracts-list-detail` passou a usar identificadores unicos para nao depender de banco SQLite vazio ao validar lista -> detalhe.
- Verification run:
  - `cd web && npm.cmd run test -- "src/lib/api/contracts.test.ts" "src/features/contracts/screens/contracts-screen.test.tsx" "src/features/contracts/screens/contract-detail-screen.test.tsx" --reporter=dot`
  - resultado: `3` arquivos de teste, `24` testes verdes
  - `cd web && npm.cmd run build`
  - resultado: build Next.js verde
  - boot controlado de backend + frontend locais e `cd web && npx.cmd playwright test tests/e2e/contracts-list-detail.spec.ts --workers=1`
  - resultado: `1 passed (13.2s)`
- Residual risks:
  - `web/playwright.config.ts` ainda depende de `reuseExistingServer`; no ambiente Windows atual a verificacao E2E exigiu limpar processos stale em `3100/8100` e subir o backend com Python do sistema porque `./.venv/bin/python` nao existe aqui
- Follow-up items:
  - executar `F2-G Gate da fase 2: analise + QA + docs`
- Notes marked `a confirmar`:
  - nenhuma

## Frontend QA Review

- Status: `pass`
- Evidence:
  - `ContractsScreen` segue coberto para load, erro, refresh, upload com refetch e navegacao canonica
  - `ContractDetailScreen` agora fica coberto para payload completo, `404`, estados parciais, retry apos falha inicial e recuperacao apos refresh com erro generico
  - E2E real cobrindo upload -> lista persistida -> detalhe real
- Non-blocking notes:
  - vale padronizar o bootstrap do Playwright para reduzir dependencia de setup manual em worktrees Windows

## Documentation Update Note

- Updated docs:
  - `docs/squad/artifacts/2026-03-16-f2-b-contracts-real-api.md`
  - `./.codex-memory/current-state.md`
  - `./.codex-memory/session-log.md`
- External sync:
  - card `F2-B Conectar lista e detalhe de contratos a API real` sincronizado no Trello com checklist completo e movido para `Concluido`
- Notes marked `a confirmar`:
  - nenhuma
