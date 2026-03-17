# Current State

## Projeto
- Monorepo do MVP vendavel de uma plataforma LegalTech de governanca de contratos para times de expansao de franquias.

## Estado atual
- Existe um `backend/` em FastAPI organizado com `api/`, `application/`, `domain/`, `infrastructure/` e composition root em `app/core/app_factory.py`.
- Existe um `web/` em Next.js organizado com pages como composition roots, screens em `features/`, modelos em `entities/` e clientes de transporte em `lib/api/`.
- Existe um sistema operacional de squad implementado em `docs/squad/`, com roteamento, regras de bloqueio, arquivos de papeis e templates de artefatos.
- O repositorio ja contem testes de backend, frontend e E2E.
- O runtime local verificado continua usando SQLite e filesystem; `docker-compose.yml` segue como opcional para evolucoes de infraestrutura.
- A `F4-B Finalizar dashboard e timeline operacional` agora esta integrada em `main` e `origin/main` no merge `29bd91b`, adicionando `GET /api/dashboard`, consumo real do snapshot no frontend e leitura operacional do dashboard.

## Em andamento
- A fase 1 esta fechada no repositorio: `F1-A` e `F1-B` seguem validadas em `main`, e a `F1-G` consolidou o gate operacional.
- A fase 2 esta fechada no repositorio: `F2-A` e `F2-B` seguem validadas em `main`, e a `F2-G` consolidou o gate operacional.
- A `F3-A Ajustar extracao de contrato assinado e motor de eventos` agora esta integrada em `main` no commit `b3d242e`, endurecendo a extracao de `signed_contract`, persistindo snapshot estruturado por versao e recalculando a agenda canonica de eventos.
- `origin/main` ja recebeu a `F3-A Ajustar extracao de contrato assinado e motor de eventos`, o commit documental `29afd05` e o merge `29bd91b` da `F4-B`; o branch local `main` esta alinhado com o remoto.
- O card do Trello da `F4-B` foi movido para `Concluido`, com checklist completa e comentario final de entrega.

## Ultimas mudancas relevantes
- O backend ganhou `GET /api/dashboard`, com agregacao de KPIs, timeline operacional e historico de alertas em `backend/app/application/dashboard.py`.
- O frontend passou a consumir o snapshot real em `web/src/lib/api/dashboard.ts`, mantendo `web/src/app/(app)/dashboard/page.tsx` fino e movendo loading, erro, vazio e refresh para `DashboardScreen`.
- A timeline do dashboard agora oferece filtros operacionais (`Todos`, `Vencidos`, `Na janela`, `Futuros`) e contextualiza cada evento com contrato, referencia e janela de vencimento.
- O historico de notificacoes agora mostra contrato, referencia, evento, canal, status e horario em leitura operacional.
- O bootstrap Playwright no Windows deixou de depender de `./.venv/bin/python` e agora faz fallback para o Python local do sistema quando necessario.
- A verificacao fresca da `main` apos o merge `29bd91b` fechou com `55` testes backend verdes, `75` testes frontend verdes, `npm run build` verde e `2` cenarios Playwright do dashboard verdes.

## Arquivos alterados nesta tarefa
- `backend/app/api/routes/dashboard.py`
- `backend/app/application/dashboard.py`
- `backend/app/core/app_factory.py`
- `backend/app/schemas/dashboard.py`
- `backend/tests/api/test_dashboard_api.py`
- `backend/tests/application/test_dashboard_snapshot.py`
- `backend/tests/support/dashboard_seed.py`
- `backend/tests/support/seed_dashboard_runtime.py`
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
- `web/tests/e2e/dashboard-alerts.spec.ts`
- `docs/squad/artifacts/2026-03-17-f4-b-dashboard-timeline-operational.md`
- `./.codex-memory/source-of-truth.md`
- `./.codex-memory/decisions.md`
- `./.codex-memory/current-state.md`
- `./.codex-memory/session-log.md`

## Arquivos importantes
- `README.md`
- `docs/squad/README.md`
- `docs/squad/routing-matrix.md`
- `docs/squad/blocking-rules.md`
- `backend/app/main.py`
- `backend/app/core/app_factory.py`
- `backend/app/application/dashboard.py`
- `backend/app/api/routes/dashboard.py`
- `backend/app/schemas/dashboard.py`
- `web/src/app/(app)/dashboard/page.tsx`
- `web/src/features/dashboard/screens/dashboard-screen.tsx`
- `web/src/lib/api/dashboard.ts`

## Problemas / riscos / pendencias
- Fonte padrao de banco entre `docker-compose` e runtime atual do backend: ainda precisa de alinhamento se o projeto sair do SQLite local.
- O KPI `active_contracts` do dashboard trata contratos com status diferente de `draft` como ativos enquanto o projeto ainda nao formalizou uma taxonomia mais rica de status operacionais.
- O dashboard continua exibindo o estado honesto de indisponibilidade quando nao ha snapshot operacional util no runtime; isso e intencional, nao regressao.
- O build frontend segue emitindo um warning de autoprefixer em `web/src/app/globals.css` por uso de `end`; nao bloqueou a entrega da `F4-B`.

## Proximo passo
- Executar `F4-G Gate da fase 4: dashboard/alertas + QA + docs` para consolidar a fase 4 sobre a `main` ja publicada.

## Ultima atualizacao
- 2026-03-17 14:12:48 -03:00
