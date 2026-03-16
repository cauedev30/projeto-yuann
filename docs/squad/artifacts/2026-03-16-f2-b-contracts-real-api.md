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
  - sincronizacao remota do card `F2-B` no board `Legal-Tech`
  - nome exato do proximo card da fase 2 sem acesso ao Trello

## Implementation Handoff

- Implementing role: `frontend-engineer`
- Changed files:
  - `web/src/entities/contracts/model.ts`
  - `web/src/entities/contracts/model.test.ts`
  - `web/src/lib/api/contracts.ts`
  - `web/src/lib/api/contracts.test.ts`
  - `web/src/features/contracts/components/contracts-list-panel.tsx`
  - `web/src/features/contracts/screens/contracts-screen.tsx`
  - `web/src/features/contracts/screens/contracts-screen.test.tsx`
  - `web/src/features/contracts/screens/contracts-screen.module.css`
  - `web/src/features/contracts/screens/contract-detail-screen.tsx`
  - `web/src/features/contracts/screens/contract-detail-screen.test.tsx`
  - `web/src/features/contracts/screens/contract-detail-screen.module.css`
  - `web/src/app/(app)/contracts/[contractId]/page.tsx`
  - `web/src/app/(app)/contracts/[contractId]/page.test.tsx`
  - `web/tests/e2e/contracts-list-detail.spec.ts`
- Behavior summary:
  - `web/src/lib/api/contracts.ts` agora expoe `listContracts` e `getContractDetail`, mapeando o payload canonico da `F2-A` via `entities/contracts`
  - `/contracts` carrega contratos persistidos no mount, mostra estados explicitos de lista, refresca apos upload e navega pela rota canonica do App Router
  - `/contracts/[contractId]` renderiza o detalhe real do contrato, com refresh, `404`, `latest_version = null` e `latest_analysis = null`
  - a regressao de navegacao foi coberta por teste do `ContractsScreen` com fallback de `router.push`
- Verification run:
  - `cd web && npm.cmd run test -- "src/entities/contracts/model.test.ts" "src/lib/api/contracts.test.ts" "src/features/contracts/screens/contracts-screen.test.tsx" "src/features/contracts/screens/contract-detail-screen.test.tsx" "src/app/(app)/contracts/[contractId]/page.test.tsx"`
  - resultado: `5` arquivos de teste, `26` testes verdes
  - boot controlado de backend + frontend locais e `cd web && npx.cmd playwright test tests/e2e/contracts-list-detail.spec.ts --workers=1`
  - resultado: `1 passed (8.8s)`
- Residual risks:
  - `web/playwright.config.ts` ainda depende de `reuseExistingServer`; no worktree Windows atual o backend precisou subir com Python do sistema porque `./.venv/bin/python` nao existe ali
  - a entrega esta verificada no branch `feature/f2-b-contracts-real-api`, mas ainda nao integrada em `main`
- Follow-up items:
  - alinhar o bootstrap E2E local para worktrees Windows ou padronizar a presenca de `.venv` no backend
  - decidir a estrategia de integracao da branch e depois retomar o proximo card da fase 2
- Notes marked `a confirmar`:
  - sincronizacao remota do board `Legal-Tech`
  - proximo card exato da fase 2

## Frontend QA Review

- Status: `pass`
- Evidence:
  - mapeamentos de lista e detalhe cobertos em unit tests
  - `ContractsScreen` coberto para load, erro, refresh, upload com refetch e navegacao canonica
  - `ContractDetailScreen` coberto para payload completo, `404` e estados parciais
  - E2E real cobrindo upload -> lista persistida -> detalhe real
- Non-blocking notes:
  - vale padronizar o bootstrap do Playwright para reduzir dependencia de setup manual em worktrees Windows

## Documentation Update Note

- Updated docs:
  - `docs/squad/artifacts/2026-03-16-f2-b-contracts-real-api.md`
  - `C:/Users/win/Documents/CODEX_MEMORY/projects/Projeto_yuann/current-state.md`
  - `C:/Users/win/Documents/CODEX_MEMORY/projects/Projeto_yuann/session-log.md`
- Notes marked `a confirmar`:
  - sincronizacao remota do board `Legal-Tech`
  - nome exato do proximo card da fase 2
