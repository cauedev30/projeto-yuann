# F2-A Contract Detail API Design

## Objetivo
- Padronizar a API de listagem, analise e detalhe de contrato para que a UI tenha um contrato HTTP estavel antes da conexao real das telas.

## Contexto Atual
- `GET /api/contracts` existe, mas hoje retorna apenas `id`, `title`, `external_reference` e `status`.
- O frontend de `/contracts/[contractId]` ainda e placeholder e nao ha endpoint dedicado de detalhe.
- O upload ja persiste contrato, versao, texto extraido e analise no backend, mas esse dado ainda nao sai por uma resposta canonica de detalhe.
- A UI atual de analise trabalha conceitualmente com score, findings, texto e metadados; o `F2-A` deve fechar esse contrato no backend sem ainda conectar as telas.

## Fora de Escopo
- Conectar a tela de listagem a API real.
- Conectar a tela de detalhe a API real.
- Redesenhar UX de `/contracts` ou `/contracts/[contractId]`.
- Criar nova regra de analise ou mudar o fluxo de upload.

## Rota do Squad
- Classificacao: `medium-risk feature`
- Areas tocadas: `backend`, contrato HTTP, testes de API, documentacao
- Rota minima: `implementation-manager -> tech-lead -> backend-engineer -> qa-backend -> documentation-engineer`

## Direcao Escolhida

### 1. Padronizar vocabulario de contrato
- A API de listagem e a API de detalhe devem falar o mesmo idioma de dominio.
- Os campos basicos compartilhados passam a ser:
  - `id`
  - `title`
  - `external_reference`
  - `status`

### 2. Manter listagem leve, mas util para a UI
- `GET /api/contracts` continua retornando `items`, mas cada item deve ganhar os metadados minimos que a UI de lista vai precisar no `F2-B`, sem carregar o payload inteiro do detalhe.
- Campos alvo por item:
  - identidade basica
  - `signature_date`
  - `start_date`
  - `end_date`
  - `term_months`
  - `latest_analysis_status`
  - `latest_contract_risk_score`
  - `latest_version_source`

### 3. Introduzir endpoint canonico de detalhe
- Criar `GET /api/contracts/{contract_id}`.
- Resposta alvo:
  - `contract`: identidade e metadados persistidos do contrato
  - `latest_version`: versao mais recente com origem, nome do arquivo, `used_ocr`, `text`
  - `latest_analysis`: analise mais recente com `analysis_id`, `analysis_status`, `policy_version`, `contract_risk_score` e `findings`
- O detalhe deve funcionar mesmo sem analise ou sem versao recente, retornando `null` nas secoes derivadas em vez de quebrar o payload.

### 4. Findings e score devem sair normalizados
- `findings` devem ser montados a partir de `contract_analysis_findings`, nao do `raw_payload`.
- Cada finding deve expor:
  - `id`
  - `clause_name`
  - `status`
  - `severity`
  - `current_summary`
  - `policy_rule`
  - `risk_explanation`
  - `suggested_adjustment_direction`
  - `metadata`
- `contract_risk_score` e `analysis_status` devem sair explicitamente no bloco de analise.

### 5. Coerencia entre upload e detalhe
- Quando existir `latest_version`, ela deve expor os mesmos conceitos ja usados no upload:
  - `source`
  - `text`
  - `used_ocr`
- Como `used_ocr` hoje mora em `extraction_metadata`, a API de detalhe deve derivar esse campo a partir desse metadata persistido.

## Contrato Proposto

### `GET /api/contracts`
```json
{
  "items": [
    {
      "id": "ctr_123",
      "title": "Loja Centro",
      "external_reference": "LOC-001",
      "status": "draft",
      "signature_date": null,
      "start_date": null,
      "end_date": null,
      "term_months": 36,
      "latest_analysis_status": "completed",
      "latest_contract_risk_score": 80,
      "latest_version_source": "third_party_draft"
    }
  ]
}
```

### `GET /api/contracts/{contract_id}`
```json
{
  "contract": {
    "id": "ctr_123",
    "title": "Loja Centro",
    "external_reference": "LOC-001",
    "status": "draft",
    "signature_date": null,
    "start_date": null,
    "end_date": null,
    "term_months": 36,
    "parties": {},
    "financial_terms": {}
  },
  "latest_version": {
    "contract_version_id": "ver_123",
    "source": "third_party_draft",
    "original_filename": "contract.pdf",
    "used_ocr": false,
    "text": "Prazo de vigencia 36 meses"
  },
  "latest_analysis": {
    "analysis_id": "ana_123",
    "analysis_status": "completed",
    "policy_version": "v1",
    "contract_risk_score": 80,
    "findings": [
      {
        "id": "finding_1",
        "clause_name": "Prazo de vigencia",
        "status": "critical",
        "severity": "critical",
        "current_summary": "Prazo atual de 36 meses.",
        "policy_rule": "Prazo minimo exigido: 60 meses.",
        "risk_explanation": "Prazo abaixo do minimo permitido pela politica.",
        "suggested_adjustment_direction": "Solicitar prazo minimo de 60 meses.",
        "metadata": {}
      }
    ]
  }
}
```

## Testes Necessarios
- Teste de listagem vazia continua existindo.
- Novo teste de listagem com contrato persistido, validando os campos padronizados.
- Novo teste de detalhe retornando contrato com versao e analise.
- Novo teste de detalhe retornando contrato sem analise.
- Novo teste `404` para contrato inexistente.

## Documentacao Necessaria
- Atualizar docs operacionais ou artefato do card com o payload final da listagem e do detalhe.
- Registrar o novo endpoint e o contrato final antes de iniciar `F2-B`.

## Riscos
- Duplicar logica de montagem de resumo entre listagem e detalhe.
  - mitigacao: criar mapper/backend helper pequeno para serializacao.
- Inferir `used_ocr` de metadata inconsistente em registros antigos.
  - mitigacao: fallback seguro para `false` quando nao houver evidencia persistida.
- Acoplar demais a listagem ao detalhe.
  - mitigacao: manter listagem resumida e detalhe expandido, mas com vocabulario comum.
