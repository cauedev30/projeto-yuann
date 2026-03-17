# F5-A Preparar release tecnico

## Task Brief

- Request: preparar o release candidate tecnico do MVP LegalTech no checkout atual, fechando o baseline oficial de runtime, verificacao e documentacao operacional.
- Risk level: `high-risk cross-cutting`
- Affected areas: `web`, `setup`, `docs`, `memory`, `qa`, `release`
- Required roles: `implementation-manager`, `tech-lead`, `frontend-engineer`, `qa-backend`, `qa-frontend`, `documentation-engineer`
- Architecture review required: `yes`
- Required artifacts: task brief, architecture review, backend QA review, frontend QA review, documentation update note
- Key requirements:
  - criar seeds e fixtures minimos para o fluxo de demo
  - documentar boot local e fluxo de demo com comandos explicitos
  - oficializar `Python 3.13` como baseline do release candidate
  - consolidar o `README.md` como referencia unica de bootstrap e verificacao
  - adicionar um runbook/checklist de release em `docs/`
  - tornar o Playwright deterministico via configuracao serializada versionada
  - atualizar `./.codex-memory/` para refletir a entrega pronta na branch
- Blocking concerns known at entry:
  - a revisao literal do diretorio mostrou grande volume em `.worktrees/`, `web/node_modules/` e `web/.next/`, mas isso ficou fora do escopo de cleanup do card
  - a suite Playwright completa era intermitente em paralelo por compartilhar o mesmo `backend/legaltech.db` local
- Notes marked `a confirmar`:
  - sincronizacao externa do card/board neste harness

## Architecture Review

- Reviewer: `tech-lead`
- Scope reviewed:
  - contrato operacional do release candidate
  - configuracao do Playwright para o baseline E2E
  - documentacao oficial de bootstrap e verificacao
- Boundaries checked:
  - `Makefile` agora expoe `release-clear-dashboard` e `release-seed-dashboard` para o fluxo minimo de demo
  - `web/tests/fixtures/third-party-draft.pdf` passa a existir como fixture valida e reutilizavel do fluxo de demo
  - `web/playwright.config.ts` agora fixa `workers: 1` para alinhar a suite E2E ao runtime local compartilhado
  - `web/tests/playwright-config.test.ts` trava essa decisao como comportamento versionado
  - `web/tests/release-candidate-assets.test.ts` trava a presenca do fixture PDF, dos targets de seed e da documentacao de demo
  - `web/tests/e2e/contract-analysis.spec.ts` e `web/tests/e2e/contracts-list-detail.spec.ts` agora usam a fixture PDF versionada
  - `README.md` passa a explicitar `Python 3.13`, a ordem oficial de verificacao e o escopo do `F5-A`
  - `docs/release-candidate-runbook.md` concentra checklist, precondicoes, smoke manual, fixture paths e comandos concretos de seed
- Result: `pass`
- Constraints or required changes:
  - nenhuma mudanca de API HTTP, schema ou persistencia foi introduzida
  - o baseline oficial continua sendo SQLite + filesystem local
  - a serializacao do Playwright e uma decisao deliberada de release, nao um workaround manual fora do repo
  - cleanup destrutivo de `.worktrees/`, `tmp/`, `backend/uploads/` e do banco SQLite permanece fora deste card
- Evidence:
  - `Makefile`
  - `README.md`
  - `docs/release-candidate-runbook.md`
  - `backend/tests/support/seed_dashboard_runtime.py`
  - `web/playwright.config.ts`
  - `web/tests/playwright-config.test.ts`
  - `web/tests/release-candidate-assets.test.ts`
  - `web/tests/fixtures/third-party-draft.pdf`
  - `web/tests/e2e/contract-analysis.spec.ts`
  - `web/tests/e2e/contracts-list-detail.spec.ts`
- Durable decision recorded: `no`
- Notes marked `a confirmar`:
  - nenhuma

## Backend QA Review

- Status: `pass`
- Evidence:
  - `cd backend && py -3.13 -m pytest -q`

```text
55 passed in 2.24s
```

- Non-blocking notes:
  - o runtime local de release continua acoplado a SQLite e filesystem; isso segue intencional para o baseline atual

## Frontend QA Review

- Status: `pass`
- Evidence:
  - `cd web && npm run test`

```text
Test Files  19 passed (19)
     Tests  80 passed (80)
```

  - `cd web && npx tsc --noEmit`

```text
TypeScript completed with no output.
```

  - `cd web && npm run lint`

```text
> legaltech-web@0.1.0 lint
> eslint .
```

  - `cd web && npm run build`

```text
Next.js build completed successfully.
```

  - `cd web && npx playwright test`

```text
Running 5 tests using 1 worker
  5 passed
```

- Non-blocking notes:
  - o warning conhecido do autoprefixer em `web/src/app/globals.css` continua aparecendo no bootstrap do build, sem bloquear a verificacao
  - o shell Windows do harness nao expoe `make`; por isso o fluxo de demo ficou documentado com os comandos Python diretos, mantendo os targets do `Makefile` apenas como conveniencia quando o utilitario estiver disponivel

## Documentation Update Note

- Updated docs:
  - `Makefile`
  - `README.md`
  - `docs/release-candidate-runbook.md`
  - `docs/squad/artifacts/2026-03-17-f5-a-release-tecnico.md`
  - `./.codex-memory/current-state.md`
  - `./.codex-memory/session-log.md`
- External sync:
  - `a confirmar` neste harness
- Notes marked `a confirmar`:
  - proximo card do roadmap apos a integracao da branch em `main`
