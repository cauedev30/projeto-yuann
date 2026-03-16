# F2-A Contract Detail API Artifact

## Objetivo
- Registrar o payload final da API de listagem e detalhe de contratos apos o fechamento do card `F2-A`.

## Endpoints
- `GET /api/contracts`
- `GET /api/contracts/{contract_id}`

## `GET /api/contracts`

### Shape
```json
{
  "items": [
    {
      "id": "ctr_123",
      "title": "Loja Centro",
      "external_reference": "LOC-001",
      "status": "uploaded",
      "signature_date": null,
      "start_date": null,
      "end_date": null,
      "term_months": 36,
      "latest_analysis_status": "completed",
      "latest_contract_risk_score": 80.0,
      "latest_version_source": "third_party_draft"
    }
  ]
}
```

### Notes
- A listagem continua resumida.
- `latest_analysis_status`, `latest_contract_risk_score` e `latest_version_source` sao derivados da versao e da analise mais recentes do contrato.
- Quando nao houver versao ou analise, esses campos retornam `null`.

## `GET /api/contracts/{contract_id}`

### Shape
```json
{
  "contract": {
    "id": "ctr_123",
    "title": "Loja Centro",
    "external_reference": "LOC-001",
    "status": "uploaded",
    "signature_date": null,
    "start_date": null,
    "end_date": null,
    "term_months": 36,
    "parties": {
      "tenant": "Loja Centro"
    },
    "financial_terms": {
      "monthly_rent": 12000
    }
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
    "contract_risk_score": 80.0,
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

### Notes
- `latest_version` pode ser `null` quando o contrato ainda nao tiver versoes persistidas.
- `latest_analysis` pode ser `null` quando o contrato ainda nao tiver analise persistida.
- `used_ocr` e derivado de `extraction_metadata.ocr_attempted` da versao mais recente.
- `findings` saem normalizados a partir de `contract_analysis_findings`, sem depender de `raw_payload`.

## Casos de erro
- `GET /api/contracts/{contract_id}` retorna `404` com:

```json
{
  "detail": "Contract not found"
}
```
