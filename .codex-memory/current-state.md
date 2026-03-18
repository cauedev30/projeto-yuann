# Current State

## Projeto
- Monorepo `projeto-yuann` do MVP `LegalTech` para ingestao, analise e governanca de contratos.
- Raiz verificada: `/home/dvdev/projeto-yuann`
- Interface canonica de memoria compartilhada: `./.codex-memory/`

## Snapshot verificado
- Checkout principal publicado: `main` alinhada com `origin/main`, mantendo `F5-A Preparar release tecnico` como ultimo card publicado no topo verificado.
- Worktree ativo desta sessao: `/home/dvdev/projeto-yuann/.worktrees/f5-b-release-produto`
- Branch ativa desta sessao: `feature/f5-b-release-produto`
- `F5-B Preparar release de produto` foi implementada e verificada localmente neste worktree.
- Entregas fechadas na branch:
  - novos specs Playwright `full-happy-path`, `notifications-flow`, `upload-validation` e `navigation`
  - responsividade e acessibilidade reforcadas em `AppShell`, `ContractsScreen`, `ContractDetailScreen`, `DashboardScreen`, `EventsTimeline` e `NotificationHistory`
  - `LoadingSkeleton` reutilizavel, polimento visual do dashboard/contracts e CTA final da landing para `/contracts`
  - `docs/demo-script.md` criado para a narrativa comercial da demo
  - `backend/tests/support/dashboard_seed.py` enriquecido com `parties` e `financial_terms`
  - `Makefile` corrigido para usar o venv local e `npm`/`npm.cmd` por plataforma no alvo oficial `release-verify`
- QA fresca confirmada nesta branch:
  - `cd /home/dvdev/projeto-yuann/.worktrees/f5-b-release-produto && make release-verify`
  - backend: `55 passed in 1.18s`
  - frontend unit: `19 files, 81 tests passed`
  - TypeScript: pass
  - lint: pass
  - build Next.js: pass
  - Playwright: `9 passed (22.9s)`
- Artefatos desta entrega:
  - `docs/demo-script.md`
  - `docs/squad/artifacts/2026-03-17-f5-b-release-produto.md`

## Worktrees agora
- O checkout principal em `main` permanece limpo e alinhado com `origin/main`.
- O worktree `/home/dvdev/projeto-yuann/.worktrees/f5-b-release-produto` concentra a `F5-B` pronta para revisao/integracao.
- O worktree `/home/dvdev/projeto-yuann/.worktrees/f5-a-release-tecnico` permanece em `fd46992` e pode ser removido quando nao for mais necessario.
- O worktree `/home/dvdev/projeto-yuann/.worktrees/f3-g-gate-fase-3` permanece como sobra historica e pode ser removido em cleanup futuro.
- O worktree `/home/dvdev/projeto-yuann/.worktrees/f4-a-notifications` permanece como sobra historica e pode ser removido em cleanup futuro.

## Riscos / pendencias
- `backend/pyproject.toml` ainda declara `requires-python = ">=3.13"`, mas a validacao local desta sessao continuou usando `Python 3.12.3`.
- Worktrees novos nao herdam `backend/.venv` nem `web/node_modules`; o bootstrap ou o fallback para ambientes compartilhados continua necessario antes de rodar QA completa fora do checkout principal.
- A suite Playwright oficial permanece serializada porque o runtime local ainda compartilha um unico SQLite durante o E2E.
- `docker-compose.yml` segue opcional; o baseline verificado do release candidate continua sendo SQLite + filesystem local.
- A `F5-B` ainda nao foi integrada nem publicada em `main`/`origin/main` neste harness.

## Proximo passo recomendado
- Escolher a estrategia de integracao da branch `feature/f5-b-release-produto`; depois disso, publicar o closeout correspondente e decidir entre `F5-G` ou o proximo card funcional do board.

## Ultima atualizacao
- 2026-03-17 22:38:51 -0300
