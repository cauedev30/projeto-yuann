# F4-B Finalizar dashboard e timeline operacional

## Task Brief

- Request: executar o card `F4-B Finalizar dashboard e timeline operacional` para fechar KPIs do dashboard, timeline com filtros, historico visual de alertas e estados honestos de loading, erro e vazio.
- Risk level: `high-risk cross-cutting`
- Affected areas: `backend`, `web`, `setup`, `docs`, `memory`
- Required roles: `implementation-manager`, `tech-lead`, `backend-engineer`, `frontend-engineer`, `qa-backend`, `qa-frontend`, `documentation-engineer`
- Architecture review required: `yes`
- Required artifacts: task brief, architecture review, implementation handoff, backend QA review, frontend QA review, documentation update note
- Key requirements:
  - criar uma fonte real de dashboard no backend sem fan-out no frontend
  - construir KPIs operacionais do portfolio
  - integrar timeline com filtros operacionais
  - exibir historico visual de alertas
  - resolver estados de loading, erro e vazio sem reintroduzir dados demo como fonte runtime
- Blocking concerns known at entry:
  - `web/src/lib/api/dashboard.ts` retornava `null` fixo e o dashboard nao tinha contrato real de dados
  - `web/playwright.config.ts` ainda usava bootstrap Unix-only para o backend
- Notes marked `a confirmar`:
  - nome exato do proximo card funcional depois da `F4-B`

## Architecture Review

- Reviewer: `tech-lead`
- Scope reviewed:
  - novo `GET /api/dashboard`
  - agregacao de KPIs, eventos e notificacoes
  - migracao do dashboard para leitura client-side com estados explicitos
  - bootstrap Playwright compatível com Windows
- Boundaries checked:
  - o backend concentra a agregacao em `application/dashboard.py`
  - `backend/app/api/routes/dashboard.py` permanece fino
  - `web/src/app/(app)/dashboard/page.tsx` segue como composition root
  - `DashboardScreen` assume loading, erro, vazio, refresh e composicao da UI
  - nenhuma migracao ou tabela nova foi aberta nesta task
- Result: `pass`
- Constraints or required changes:
  - nao reintroduzir fixture como fonte runtime default
  - manter `GET /api/dashboard` como payload unico e canonico para a tela
  - preservar o estado honesto de indisponibilidade quando nao houver snapshot operacional util
  - limitar a timeline ao horizonte operacional ja acordado sem inventar nova persistencia
- Evidence:
  - `backend/app/application/dashboard.py`
  - `backend/app/api/routes/dashboard.py`
  - `web/src/lib/api/dashboard.ts`
  - `web/src/features/dashboard/screens/dashboard-screen.tsx`
- Durable decision recorded: `yes`
- Notes marked `a confirmar`:
  - nenhuma

## Implementation Handoff

- Implementing role: `backend-engineer` + `frontend-engineer`
- Changed files:
  - `backend/app/api/routes/dashboard.py`
  - `backend/app/application/dashboard.py`
  - `backend/app/core/app_factory.py`
  - `backend/app/schemas/dashboard.py`
  - `backend/tests/api/test_dashboard_api.py`
  - `backend/tests/application/test_dashboard_snapshot.py`
  - `web/playwright.config.ts`
  - `web/src/app/(app)/dashboard/page.tsx`
  - `web/src/entities/dashboard/model.ts`
  - `web/src/entities/dashboard/model.test.ts`
  - `web/src/features/dashboard/components/events-timeline.tsx`
  - `web/src/features/dashboard/components/events-timeline.module.css`
  - `web/src/features/dashboard/components/events-timeline.test.tsx`
  - `web/src/features/dashboard/fixtures/dashboard-snapshot.ts`
  - `web/src/features/dashboard/screens/dashboard-screen.tsx`
  - `web/src/features/dashboard/screens/dashboard-screen.module.css`
  - `web/src/features/dashboard/screens/dashboard-screen.test.tsx`
  - `web/src/features/notifications/components/notification-history.tsx`
  - `web/src/features/notifications/components/notification-history.module.css`
  - `web/src/features/notifications/components/notification-history.test.tsx`
  - `web/src/lib/api/dashboard.ts`
  - `web/src/lib/api/dashboard.test.ts`
- Behavior summary:
  - o backend agora expoe `GET /api/dashboard` com `summary`, `events` e `notifications`
  - o dashboard usa dados reais de runtime e traduz snapshot completamente vazio para o estado honesto de indisponibilidade
  - `DashboardScreen` passou a ter loading, erro, vazio, refresh e renderizacao preenchida
  - a timeline agora oferece filtros operacionais e contexto de contrato por evento
  - o historico de notificacoes agora exibe contrato, referencia, evento, status, canal e horario
  - o Playwright agora consegue subir o backend em Windows mesmo sem `.venv`
- Verification run:
  - `cd backend && C:/Users/win/AppData/Local/Programs/Python/Python313/python.exe -m pytest -q`
  - resultado: `34 passed in 2.30s`
  - `cd web && npm.cmd run test`
  - resultado: `49 passed in 6.12s`
  - `cd web && npm.cmd run build`
  - resultado: build Next.js verde
  - `cd web && npx.cmd playwright test tests/e2e/dashboard-alerts.spec.ts`
  - resultado: `1 passed`
- Residual risks:
  - `active_contracts` ainda depende de regra provisoria baseada em status diferente de `draft`
  - o build ainda emite warning de autoprefixer em `web/src/app/globals.css`
- Follow-up items:
  - escolher a estrategia de integracao da branch `feature/f4-b-dashboard-ops`
  - sincronizar o card no Trello apos integrar a branch
  - retomar o proximo card funcional, cujo nome exato permanece `a confirmar`
- Notes marked `a confirmar`:
  - nome exato do proximo card funcional depois da `F4-B`

## Backend QA Review

- Status: `pass`
- Evidence:
  - agregacao nova coberta por teste de aplicacao do snapshot
  - rota `GET /api/dashboard` coberta por teste de API
  - suite backend completa verde com `34 passed`
- Non-blocking notes:
  - o critério de contrato ativo ainda depende da taxonomia frouxa de `status`

## Frontend QA Review

- Status: `pass`
- Evidence:
  - novos testes de mapeamento, cliente HTTP, timeline, historico e tela do dashboard
  - suite frontend completa verde com `49 passed`
  - build Next.js verde
  - spec Playwright do dashboard verde em Windows
- Non-blocking notes:
  - a spec E2E do dashboard ainda valida o empty state, porque o runtime local continua sem dados operacionais seeded por padrao

## Documentation Update Note

- Updated docs:
  - `docs/squad/artifacts/2026-03-17-f4-b-dashboard-timeline-operational.md`
  - `.codex-memory/decisions.md`
  - `.codex-memory/source-of-truth.md`
  - `.codex-memory/current-state.md`
  - `.codex-memory/session-log.md`
- Notes marked `a confirmar`:
  - nome exato do proximo card funcional depois da `F4-B`
