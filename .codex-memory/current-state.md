# Current State

## Projeto
- Monorepo do MVP vendavel de uma plataforma LegalTech de governanca de contratos para times de expansao de franquias.

## Estado atual
- Existe um `backend/` em FastAPI organizado com `api/`, `application/`, `domain/`, `infrastructure/` e composition root em `app/core/app_factory.py`.
- Existe um `web/` em Next.js organizado com pages como composition roots, screens em `features/`, modelos em `entities/` e clientes de transporte em `lib/api/`.
- Existe um sistema operacional de squad implementado em `docs/squad/`, com roteamento, regras de bloqueio, arquivos de papeis e templates de artefatos.
- O vault operacional `./.codex-memory/` agora esta versionado no proprio repositorio e segue a mesma `main` do codigo.
- O repositorio ja contem testes de backend, frontend e E2E.
- O runtime local verificado continua usando SQLite e filesystem; `docker-compose.yml` segue como opcional para evolucoes de infraestrutura.
- A `F4-B Finalizar dashboard e timeline operacional` agora esta integrada em `main` e `origin/main` no merge `29bd91b`, adicionando `GET /api/dashboard`, consumo real do snapshot no frontend e leitura operacional do dashboard.
- A `F5-A Preparar release tecnico` agora esta integrada em `main` no commit `c248a0a`, oficializando `Python 3.13` como baseline documental do release candidate, adicionando `docs/release-candidate-runbook.md` e serializando a suite Playwright no config versionado.

## Em andamento
- A fase 1 esta fechada no repositorio: `F1-A` e `F1-B` seguem validadas em `main`, e a `F1-G` consolidou o gate operacional.
- A fase 2 esta fechada no repositorio: `F2-A` e `F2-B` seguem validadas em `main`, e a `F2-G` consolidou o gate operacional.
- A `F3-A Ajustar extracao de contrato assinado e motor de eventos` agora esta integrada em `main` no commit `b3d242e`, endurecendo a extracao de `signed_contract`, persistindo snapshot estruturado por versao e recalculando a agenda canonica de eventos.
- `origin/main` ja recebeu a `F3-A Ajustar extracao de contrato assinado e motor de eventos`, o commit documental `29afd05`, o merge `29bd91b` da `F4-B`, o gate documental da fase 4 no commit `0eac567`, a integracao da `F5-A` e a sincronizacao versionada da memoria; o branch local `main` voltou a ficar alinhado com o remoto apos o push final.
- A fase 4 esta fechada no repositorio: `F4-B` foi publicada, `F4-G Gate da fase 4: dashboard/alertas + QA + docs` ja tem artefato em `docs/squad/artifacts/2026-03-17-f4-g-gate-fase-4.md`, e o roadmap pode seguir para a fase 5.
- A fase 5 avancou com a `F5-A Preparar release tecnico` ja integrada em `main` e `origin/main`, com verificacao fresca verde na propria `main` e artefato em `docs/squad/artifacts/2026-03-17-f5-a-release-tecnico.md`.

## Ultimas mudancas relevantes
- O backend ganhou `GET /api/dashboard`, com agregacao de KPIs, timeline operacional e historico de alertas em `backend/app/application/dashboard.py`.
- O frontend passou a consumir o snapshot real em `web/src/lib/api/dashboard.ts`, mantendo `web/src/app/(app)/dashboard/page.tsx` fino e movendo loading, erro, vazio e refresh para `DashboardScreen`.
- A timeline do dashboard agora oferece filtros operacionais (`Todos`, `Vencidos`, `Na janela`, `Futuros`) e contextualiza cada evento com contrato, referencia e janela de vencimento.
- O historico de notificacoes agora mostra contrato, referencia, evento, canal, status e horario em leitura operacional.
- O bootstrap Playwright no Windows deixou de depender de `./.venv/bin/python` e agora faz fallback para o Python local do sistema quando necessario.
- A verificacao fresca da `main` apos o merge `29bd91b` fechou com `55` testes backend verdes, `75` testes frontend verdes, `npm run build` verde e `2` cenarios Playwright do dashboard verdes.
- O gate `F4-G` foi formalizado em `docs/squad/artifacts/2026-03-17-f4-g-gate-fase-4.md`, liberando a transicao da fase 4 para a fase 5.
- A memoria operacional (`current-state`, `session-log`, `decisions`, `patterns`, `source-of-truth`) agora segue versionada e publicada na propria `main`.
- O `README.md` agora concentra o baseline oficial do release candidate, e `docs/release-candidate-runbook.md` descreve precondicoes, ordem de verificacao, smoke manual e riscos conhecidos.
- O frontend ganhou `web/tests/playwright-config.test.ts`, travando via Vitest que o config versionado do Playwright roda a suite E2E em `1` worker.
- O release candidate agora tambem versiona `web/tests/fixtures/third-party-draft.pdf`, documenta o seed do dashboard com comandos Python diretos e trava esses assets em `web/tests/release-candidate-assets.test.ts`.
- A revisao final da branch `feature/f5-a-release-tecnico` corrigiu a documentacao de boot local para usar `py -3.13 -m uvicorn ...` e `NEXT_PUBLIC_API_URL="http://127.0.0.1:8000"` no frontend, travando esse contrato em `web/tests/release-candidate-assets.test.ts`.
- A verificacao fresca da branch `feature/f5-a-release-tecnico` fechou com `55` testes backend verdes, `80` testes frontend verdes, `npx tsc --noEmit` verde, `npm run lint` verde, `npm run build` verde, os comandos diretos de `clear/seed` do dashboard verdes, `5` cenarios Playwright verdes e smoke manual verde em `http://127.0.0.1:8000` + `http://127.0.0.1:3000`.
- A integracao local em `main` foi revalidada com `55` testes backend verdes, `80` testes frontend verdes, `npx tsc --noEmit` verde, `npm run lint` verde, `npm run build` verde e `5` cenarios Playwright verdes.
- A `main` foi publicada em `origin/main`, e a branch local `feature/f5-a-release-tecnico` deixou de ser necessaria para a continuidade do roadmap.
- Uma auditoria local apos a publicacao da `F5-A` nao encontrou branch, plano ou artifact local para um proximo card alem do que ja foi entregue; a confirmacao do roadmap segue dependente do board externo.

## Arquivos alterados nesta tarefa
- `Makefile`
- `README.md`
- `docs/release-candidate-runbook.md`
- `docs/squad/artifacts/2026-03-17-f5-a-release-tecnico.md`
- `web/playwright.config.ts`
- `web/tests/e2e/contract-analysis.spec.ts`
- `web/tests/e2e/contracts-list-detail.spec.ts`
- `web/tests/fixtures/third-party-draft.pdf`
- `web/tests/release-candidate-assets.test.ts`
- `web/tests/playwright-config.test.ts`
- `./.codex-memory/current-state.md`
- `./.codex-memory/session-log.md`

## Arquivos importantes
- `Makefile`
- `README.md`
- `docs/release-candidate-runbook.md`
- `docs/squad/README.md`
- `docs/squad/routing-matrix.md`
- `docs/squad/blocking-rules.md`
- `web/playwright.config.ts`
- `backend/tests/support/seed_dashboard_runtime.py`
- `web/tests/fixtures/third-party-draft.pdf`
- `web/tests/release-candidate-assets.test.ts`
- `web/tests/playwright-config.test.ts`
- `backend/pyproject.toml`

## Problemas / riscos / pendencias
- Fonte padrao de banco entre `docker-compose` e runtime atual do backend: ainda precisa de alinhamento se o projeto sair do SQLite local.
- A suite Playwright oficial do release candidate agora e deliberadamente serializada; paralelismo por worker continua fora do baseline ate existir isolamento real de runtime.
- O build frontend segue emitindo um warning de autoprefixer em `web/src/app/globals.css` por uso de `end`; nao bloqueou a entrega da `F5-A`.
- O shell Windows do harness nao expoe `make`; a documentacao do fluxo de demo usa comandos Python diretos e deixa os targets do `Makefile` como conveniencia opcional.
- `.worktrees/`, `tmp/`, `backend/uploads/` e `backend/legaltech.db` seguem presentes no diretório de trabalho; cleanup ficou fora desta tarefa por ser operacional e potencialmente destrutivo.
- O proximo card do roadmap permanece `a confirmar`: a auditoria local em 2026-03-17 nao encontrou referencia repo-local equivalente a `F5-B`, entao a confirmacao depende de board/artefatos externos ainda indisponiveis neste harness.

## Proximo passo
- Sincronizar board/artefatos externos com acesso adequado e confirmar o proximo card do roadmap (`a confirmar` no repositorio).

## Ultima atualizacao
- 2026-03-17 16:23:12 -03:00
