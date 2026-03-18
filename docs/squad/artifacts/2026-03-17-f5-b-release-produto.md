# F5-B Preparar release de produto

## Task Brief

- Request: executar a `F5-B Preparar release de produto` no worktree atual, fechando responsividade, acessibilidade, polish visual e narrativa de demo/venda do MVP LegalTech.
- Risk level: `high-risk cross-cutting`
- Affected areas: `web`, `backend/tests/support`, `docs`, `qa`, `memory`, `release`
- Required roles: `implementation-manager`, `tech-lead`, `frontend-engineer`, `qa-backend`, `qa-frontend`, `documentation-engineer`
- Architecture review required: `yes`
- Required artifacts: task brief, architecture review, backend QA review, frontend QA review, E2E QA review, documentation update note
- Key requirements:
  - fechar a jornada E2E principal com quatro specs novas
  - revisar responsividade critica nas telas de contracts, dashboard e navegacao movel
  - corrigir gaps criticos de acessibilidade com foco visivel, skip link, live regions e estados ARIA
  - adicionar loading skeletons, empty state do dashboard e refinamentos visuais para demo
  - documentar o roteiro de demo e enriquecer o seed do dashboard sem quebrar textos travados em E2E
  - garantir que `make release-verify` volte a ser executavel no runtime local
- Blocking concerns known at entry:
  - a suite Playwright continua serializada por compartilhar um unico SQLite local
  - worktrees nao herdam `backend/.venv` nem `web/node_modules` automaticamente
- Notes marked `a confirmar`:
  - sincronizacao externa do card/board neste harness

## Architecture Review

- A entrega nao moveu fronteiras de dominio nem alterou contratos de API.
- O backend permaneceu restrito ao seed de dashboard e ao bootstrap do `Makefile`.
- O frontend preservou o padrao existente de CSS Modules por componente e screens client-side.
- O ajuste estrutural mais relevante foi tornar `make release-verify` shell-agnostic para usar o venv local em Unix e o venv/Scripts em Windows, eliminando o hardcode quebrado para um path externo de Windows.
- O trabalho de a11y foi tratado na superficie correta: utilitarios globais em `globals.css`, navegacao no `AppShell` e feedback dinâmico nas screens.

## Backend QA Review

- `backend/tests/support/dashboard_seed.py` foi enriquecido com `parties` e `financial_terms` nos contratos seeded sem alterar os literais usados pelos E2Es existentes.
- O seed continuou preservando `finance@example.com`, `Atrasado ha 5 dias` e `Dentro da janela de alerta (30 dias)` nos caminhos observados pelo Playwright.
- `make release-verify` passou a usar `.venv/bin/python` em Unix e `.venv/Scripts/python.exe` em Windows por default, restaurando a executabilidade do alvo oficial de release.
- Evidencia fresca:
  - `cd /home/dvdev/projeto-yuann/.worktrees/f5-b-release-produto && make release-verify`
  - backend slice: `55 passed in 1.18s`

## Frontend QA Review

- A navegacao ganhou `skip link`, `id="main-content"`, foco visivel global e refinamento do menu mobile com animacao e target minimo.
- `ContractsScreen`, `ContractDetailScreen` e `DashboardScreen` passaram a expor live regions SR-only e skeletons reutilizaveis para estados de carregamento.
- `EventsTimeline` agora expõe `aria-pressed`, contagem por filtro e sinal visual de atraso; `NotificationHistory` e menu mobile respeitam target minimo.
- A landing recebeu badge de workspace pronto e CTA final direto para `/contracts`.
- Evidencia fresca:
  - `cd /home/dvdev/projeto-yuann/.worktrees/f5-b-release-produto && make release-verify`
  - frontend unit slice: `19` arquivos e `81` testes passando
  - `npx tsc --noEmit` -> pass
  - `npm run lint` -> pass
  - `npm run build` -> pass

## E2E QA Review

- Novos cenarios adicionados:
  - `web/tests/e2e/full-happy-path.spec.ts`
  - `web/tests/e2e/notifications-flow.spec.ts`
  - `web/tests/e2e/upload-validation.spec.ts`
  - `web/tests/e2e/navigation.spec.ts`
- O spec existente `web/tests/e2e/dashboard-alerts.spec.ts` foi ajustado para tolerar os novos labels com contagem nos filtros.
- A validacao fresca do alvo oficial fechou com `9 passed (22.9s)`.

## Documentation Update Note

- Updated docs:
  - `docs/demo-script.md`
  - `docs/squad/artifacts/2026-03-17-f5-b-release-produto.md`
  - `./.codex-memory/current-state.md`
  - `./.codex-memory/session-log.md`

## Final Verification Timestamp

- 2026-03-17 22:38:51 -0300
