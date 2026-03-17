# F3-A Ajustar extracao de contrato assinado e motor de eventos

## Task Brief

- Request: executar o card `F3-A Ajustar extracao de contrato assinado e motor de eventos` para persistir snapshot por versao, recalcular a agenda canonica e endurecer a cobertura backend sem expandir a API publica.
- Risk level: `medium-risk feature`
- Affected areas: `backend`, `docs`, `memory`
- Required roles: `implementation-manager`, `tech-lead`, `backend-engineer`, `qa-backend`, `documentation-engineer`
- Architecture review required: `yes`
- Required artifacts: task brief, architecture review, implementation handoff, backend QA review, documentation update note
- Key requirements:
  - persistir snapshot estruturado da extracao do `signed_contract` em `contract_versions.extraction_metadata`
  - manter `contracts` como snapshot canonico operacional do contrato
  - recalcular `renewal`, `expiration`, `readjustment` e `grace_period_end` a partir da versao assinada mais recente
  - nao mudar `POST /api/uploads/contracts` nem `GET /api/contracts/*` nesta task
- Blocking concerns known at entry:
  - `contract_versions.extraction_metadata` ja alimentava o `used_ocr`, entao o novo snapshot nao podia quebrar esse contrato interno
- Notes marked `a confirmar`:
  - nome exato do proximo card funcional da fase 3 no Trello

## Architecture Review

- Reviewer: `tech-lead`
- Scope reviewed:
  - extracao de metadados de `signed_contract`
  - persistencia do snapshot por versao
  - reconstrucao da agenda canonica em `contract.events`
- Boundaries checked:
  - `application/contract_upload.py` segue apenas orquestrando upload + ingestao + archive
  - `tasks/archive.py` continua como fronteira de atualizacao do snapshot canonico do contrato
  - confianca e contexto de parse ficam em `contract_versions.extraction_metadata`, nao em `contracts`
  - API publica permanece intacta
- Result: `pass`
- Constraints or required changes:
  - preservar `ocr_attempted` e metadados de OCR no topo de `extraction_metadata`
  - anexar o snapshot estruturado em chave dedicada de versao
  - registrar nos eventos a origem da derivacao e a `contract_version` responsavel
  - nao abrir migracao nem endpoint novo nesta task
- Evidence:
  - `backend/app/domain/contract_metadata.py`
  - `backend/app/domain/events.py`
  - `backend/app/tasks/archive.py`
  - `backend/tests/application/test_contract_upload.py`
- Durable decision recorded: `yes`
- Notes marked `a confirmar`:
  - nenhuma

## Implementation Handoff

- Implementing role: `backend-engineer`
- Changed files:
  - `backend/app/domain/contract_metadata.py`
  - `backend/app/domain/events.py`
  - `backend/app/schemas/metadata.py`
  - `backend/app/tasks/archive.py`
  - `backend/tests/application/test_contract_upload.py`
  - `backend/tests/services/test_contract_metadata.py`
  - `backend/tests/services/test_event_scheduler.py`
  - `backend/tests/support/pdf_factory.py`
- Behavior summary:
  - o parser de contrato assinado agora aceita variantes razoaveis de rotulos para assinatura, inicio de vigencia, prazo, locataria, carencia e reajuste anual
  - `ContractMetadataResult` agora carrega `field_confidence`, `match_labels` e `ready_for_event_generation`
  - `contract_versions.extraction_metadata` preserva os metadados de OCR e ganha `signed_contract_snapshot` com campos normalizados e confianca por versao
  - `contract.events` continua sendo a agenda canonica atual do contrato, mas agora cada evento registra `derived_from` e `source_contract_version_id`
  - um novo `signed_contract` para a mesma `external_reference` substitui integralmente a agenda anterior
- Verification run:
  - `cd backend && C:/Users/win/AppData/Local/Programs/Python/Python313/python.exe -m pytest tests/services/test_contract_metadata.py tests/services/test_event_scheduler.py tests/application/test_contract_upload.py -q`
  - resultado: `8 passed in 1.21s`
  - `cd backend && C:/Users/win/AppData/Local/Programs/Python/Python313/python.exe -m pytest -q`
  - resultado: `30 passed in 2.89s`
- Residual risks:
  - a extracao continua baseada em regex e limitada ao nucleo atual de campos; enriquecimento financeiro ou societario mais profundo continua fora de escopo
- Follow-up items:
  - escolher a estrategia de integracao da branch `feature/f3-a-signed-contract-events`
  - retomar o proximo card funcional da fase 3 depois da integracao; nome exato no Trello permanece `a confirmar`
- Notes marked `a confirmar`:
  - nenhuma adicional

## Backend QA Review

- Status: `pass`
- Evidence:
  - cobertura nova para variantes de labels, snapshot estruturado, metadados de derivacao de eventos e substituicao da agenda com nova versao assinada
  - suite focada da `F3-A` verde com `8 passed`
  - suite backend completa verde com `30 passed`
- Non-blocking notes:
  - a API de contratos ainda nao expoe os eventos ou a confianca de extracao; isso permanece para cards posteriores

## Documentation Update Note

- Updated docs:
  - `backend/README.md`
  - `docs/squad/artifacts/2026-03-16-f3-a-signed-contract-events.md`
  - `.codex-memory/decisions.md`
  - `.codex-memory/patterns.md`
  - `.codex-memory/current-state.md`
  - `.codex-memory/session-log.md`
- Notes marked `a confirmar`:
  - nome exato do proximo card funcional da fase 3 no Trello
