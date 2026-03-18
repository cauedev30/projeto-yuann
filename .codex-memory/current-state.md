# Current State

## Projeto
- Monorepo `projeto-yuann` do MVP `LegalTech` para ingestao, analise e governanca de contratos.
- Raiz verificada: `/home/dvdev/projeto-yuann`
- Interface canonica de memoria compartilhada: `./.codex-memory/`

## Snapshot verificado
- Branch atual do checkout principal: `main`
- `HEAD` do checkout principal: `fd469928ec17c8756d5654496d7a200898c0858f`
- `origin/main`: `fd469928ec17c8756d5654496d7a200898c0858f`
- `F5-A Preparar release tecnico` foi fechada operacionalmente e publicada em `main` e `origin/main` via `fd46992 feat: validate and close f5-a release tecnico [F5-A]`.
- O artefato oficial da entrega foi atualizado com evidencia fresca em `docs/squad/artifacts/2026-03-17-f5-a-release-tecnico.md`.
- O card Trello `F5-A Preparar release tecnico` (`69b79d6556fa3b7d415cdd24`) foi sincronizado nesta sessao:
  - checklist final: `5/5 complete`
  - lista final: `Concluido` (`69b79d22642552e28cb23dd3`)
- QA fresca confirmada para o closeout:
  - `cd /home/dvdev/projeto-yuann/.worktrees/f5-a-release-tecnico/backend && /home/dvdev/projeto-yuann/backend/.venv/bin/python -m pytest -v` -> `55 passed in 1.26s`
  - `cd /home/dvdev/projeto-yuann/.worktrees/f5-a-release-tecnico/web && npm run test` -> `19 files, 80 tests passed`
  - `cd /home/dvdev/projeto-yuann/.worktrees/f5-a-release-tecnico/web && npx tsc --noEmit` -> pass
  - `cd /home/dvdev/projeto-yuann/.worktrees/f5-a-release-tecnico/web && npm run lint` -> pass
  - `cd /home/dvdev/projeto-yuann/.worktrees/f5-a-release-tecnico/web && npx playwright test` -> `5 passed (16.0s)`
- Seeds e fixtures foram validados no worktree da `F5-A`:
  - `tests/support/seed_dashboard_runtime.py clear` e `seed` passaram sem erro
  - `backend/legaltech.db` ficou com `3` registros em `contracts`, `contract_analyses`, `contract_analysis_findings`, `contract_events` e `notifications`
  - fixtures confirmadas: `web/tests/fixtures/third-party-draft.pdf` e `web/tests/fixtures/unreadable-upload.pdf`
- Ajustes finais publicados no closeout:
  - `README.md` e `docs/release-candidate-runbook.md` agora documentam bootstrap shell-agnostic, `make up` opcional e comandos reais de seed/E2E
  - `web/playwright.config.ts` e `web/tests/e2e/dashboard-alerts.spec.ts` agora fazem fallback para o venv compartilhado do backend quando o worktree nao tem `.venv` local
  - `web/tests/release-candidate-assets.test.ts` agora trava o contrato documental atualizado

## Worktrees agora
- O checkout principal em `main` permanece limpo e alinhado com `origin/main`.
- O worktree `/home/dvdev/projeto-yuann/.worktrees/f5-a-release-tecnico` permanece em `fd46992` e pode ser removido quando nao for mais necessario.
- O worktree `/home/dvdev/projeto-yuann/.worktrees/f3-g-gate-fase-3` permanece como sobra historica e pode ser removido em cleanup futuro.
- O worktree `/home/dvdev/projeto-yuann/.worktrees/f4-a-notifications` permanece como sobra historica e pode ser removido em cleanup futuro.

## Riscos / pendencias
- `backend/pyproject.toml` ainda declara `requires-python = ">=3.13"`, mas a validacao local desta sessao continuou usando `Python 3.12.3`.
- Worktrees novos nao herdam `backend/.venv` nem `web/node_modules`; o bootstrap ou o fallback para ambientes compartilhados continua necessario antes de rodar QA completa fora do checkout principal.
- A suite Playwright oficial permanece serializada porque o runtime local ainda compartilha um unico SQLite durante o E2E.
- `docker-compose.yml` segue opcional; o baseline verificado do release candidate continua sendo SQLite + filesystem local.

## Proximo passo recomendado
- Iniciar `F5-B` ou `F5-G`, agora que a `F5-A` esta publicada e o card correspondente foi movido para `Concluido`.

## Ultima atualizacao
- 2026-03-17 21:52:59 -0300
