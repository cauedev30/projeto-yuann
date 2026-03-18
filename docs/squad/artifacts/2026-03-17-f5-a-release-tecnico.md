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
  - `docs/release-candidate-runbook.md` concentra checklist, precondicoes, comandos concretos de boot local, smoke manual, fixture paths e comandos concretos de seed
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
  - `cd /home/dvdev/projeto-yuann/.worktrees/f5-a-release-tecnico/backend && /home/dvdev/projeto-yuann/backend/.venv/bin/python -m pytest -v`

```text
55 passed in 1.26s
```

- Non-blocking notes:
  - o runtime local de release continua acoplado a SQLite e filesystem; isso segue intencional para o baseline atual

## Seeds Validation

- Status: `pass`
- Evidence:
  - `cd /home/dvdev/projeto-yuann/.worktrees/f5-a-release-tecnico/backend && /home/dvdev/projeto-yuann/backend/.venv/bin/python tests/support/seed_dashboard_runtime.py clear`
  - `cd /home/dvdev/projeto-yuann/.worktrees/f5-a-release-tecnico/backend && /home/dvdev/projeto-yuann/backend/.venv/bin/python tests/support/seed_dashboard_runtime.py seed`
  - fixture check: `cd /home/dvdev/projeto-yuann/.worktrees/f5-a-release-tecnico/web && ls -la tests/fixtures`
  - SQLite counts confirmed after seeding:

```text
contracts: 3 rows
contract_analyses: 3 rows
contract_analysis_findings: 3 rows
contract_events: 3 rows
notifications: 3 rows
```

- Notes:
  - os nomes canonicos de tabela do schema atual sao `contract_analyses` e `contract_analysis_findings`; a validacao funcional foi registrada com esses nomes reais
  - fixtures presentes: `web/tests/fixtures/third-party-draft.pdf` e `web/tests/fixtures/unreadable-upload.pdf`

## Frontend QA Review

- Status: `pass`
- Evidence:
  - `cd web && npm run test`

```text
Test Files  19 passed (19)
     Tests  80 passed (80)
   Duration  2.53s
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

- Non-blocking notes:
  - a suite falhou na primeira tentativa porque `web/tests/release-candidate-assets.test.ts` ainda validava o README antigo; o teste foi alinhado com a documentacao shell-agnostic antes da reexecucao
  - o worktree nao tinha `web/node_modules` nem `eslint`; foi necessario executar `npm install` no worktree antes da evidência final

## E2E QA Review

- Status: `pass`
- Evidence:
  - `cd /home/dvdev/projeto-yuann/.worktrees/f5-a-release-tecnico/web && npx playwright test`

```text
Running 5 tests using 1 worker
  5 passed (16.0s)
```

- Browser: `Chromium`
- Specs executadas:
  - `tests/e2e/contract-analysis.spec.ts`
  - `tests/e2e/contracts-list-detail.spec.ts`
  - `tests/e2e/dashboard-alerts.spec.ts`
- Non-blocking notes:
  - o Playwright precisou de fallback explicito para o venv compartilhado do backend, porque o worktree novo nao tinha `backend/.venv`
  - `dashboard-alerts.spec.ts` tambem precisou usar esse mesmo fallback para os comandos `clear` e `seed`

## Documentation Update Note

- Updated docs:
  - `README.md`
  - `docs/release-candidate-runbook.md`
  - `docs/squad/artifacts/2026-03-17-f5-a-release-tecnico.md`
  - `web/playwright.config.ts`
  - `web/tests/e2e/dashboard-alerts.spec.ts`
  - `web/tests/release-candidate-assets.test.ts`

## Final Verification Timestamp

- `2026-03-17 21:49:45 -0300`
