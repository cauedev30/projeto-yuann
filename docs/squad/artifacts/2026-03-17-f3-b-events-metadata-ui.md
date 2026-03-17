# Artifact F3-B

## Task Brief

- Request: registrar o fechamento do card `F3-B` com evidencia consolidada para a visualizacao de metadados e eventos na tela de detalhe de contratos.
- Risk level: `medium-risk feature`
- Affected areas: `web`, `backend contract`, `docs`, `memory`
- Required roles: `implementation-manager`, `tech-lead`, `frontend-engineer`, `qa-frontend`, `documentation-engineer`
- Architecture review required: `yes`
- Required artifacts: task brief, implementation handoff, frontend QA review, documentation update note
- Key requirements:
  - exibir `field_confidence`, partes, datas e termos financeiros com apresentacao legivel na UI
  - exibir a timeline de eventos do contrato usando o payload canonico de `GET /api/contracts/{contract_id}`
  - manter estados honestos para ausencia de eventos, ausencia de metadados e falhas de carregamento
  - validar a integracao entre serializer backend, mapper frontend e tela de detalhe sem reabrir a `F3-A`
- Blocking concerns known at entry:
  - o artifact da `F3-B` nao existia em `docs/squad/artifacts/`, apesar de os commits funcionais ja estarem em `main`
- Notes marked `a confirmar`:
  - nenhuma

## Implementation Handoff

- Implementing role: `frontend-engineer`
- Changed files:
  - `web/src/features/contracts/components/metadata-section.tsx`
  - `web/src/features/contracts/components/metadata-section.module.css`
  - `web/src/features/contracts/components/metadata-section.test.tsx`
  - `web/src/features/contracts/components/event-timeline.tsx`
  - `web/src/features/contracts/components/event-timeline.module.css`
  - `web/src/features/contracts/components/event-timeline.test.tsx`
  - `web/src/features/contracts/screens/contract-detail-screen.tsx`
  - `web/src/features/contracts/screens/contract-detail-screen.test.tsx`
  - `web/src/entities/contracts/model.ts`
  - `web/src/entities/contracts/model.test.ts`
  - `web/src/lib/api/contracts.test.ts`
  - `backend/app/api/serializers/contracts.py`
  - `backend/app/schemas/contract.py`
  - `backend/app/tasks/archive.py`
  - `backend/tests/api/test_contracts_api.py`
  - `backend/tests/tasks/test_archive_task.py`
  - `backend/tests/application/test_contract_upload.py`
- Behavior summary:
  - `MetadataSection` passou a renderizar datas, partes, termos financeiros e badges de confianca em vez de JSON bruto.
  - `EventTimeline` passou a consumir `events` do contrato, classificar urgencia e exibir estado vazio honesto quando a agenda estiver ausente.
  - `ContractDetailScreen` passou a integrar os dois componentes no fluxo principal e a manter estados parciais e de erro consistentes.
  - O backend passou a expor `field_confidence` e `events` no detalhe do contrato para sustentar a UI sem payload ad hoc.
- Verification run:
  - evidencia historica dos commits `8b962df`, `dfcf418`, `b54494e` e `5c5f984`
  - validacao atual do frontend nesta sessao: `npm run test` -> `69 passed`, `npx tsc --noEmit` -> `pass`, `npm run lint` -> `pass`
- Residual risks:
  - a validacao E2E em navegador da tela de detalhe permanece fora deste artifact e continua `a confirmar`
- Follow-up items:
  - fechar o gate `F3-G` com QA formal e memoria atualizada
- Notes marked `a confirmar`:
  - nenhuma

## Frontend QA Review

- Status: `pass`
- Evidence:
  - `npm run test` -> `69 passed`
  - suites diretamente ligadas ao card: `contract-detail-screen.test.tsx` (`11` testes), `metadata-section.test.tsx` (`12` testes) e `event-timeline.test.tsx` (`11` testes)
  - `npx tsc --noEmit` executado sem erros nesta sessao
  - `npm run lint` executado com ESLint CLI e sem warnings nesta sessao
- Non-blocking notes:
  - a validacao E2E por Playwright nao fez parte deste fechamento retroativo e permanece `a confirmar`

## Documentation Update Note

- Updated docs:
  - `docs/squad/artifacts/2026-03-17-f3-b-events-metadata-ui.md`
- Notes marked `a confirmar`:
  - nenhuma
