# LegalBoard — Spec de Modernização Completa

> Data: 2026-03-21
> Status: Aprovado pelo usuário

## 1. Visão Geral

Modernização completa do projeto (ex-LegalTech/Yuann) agora rebatizado **LegalBoard**.
Plataforma de governança contratual para franquias (Lavanderia 60 Minutos) que:

1. Recebe contratos de locação (PDF)
2. Analisa contra um playbook de cláusulas obrigatórias da franquia
3. Avalia risco jurídico com nota por cláusula
4. Gera contrato corrigido completo + resumo das alterações

## 2. Rebranding

- **Nome**: LegalBoard (substituir todas as referências a LegalTech, Yuann, legaltech)
- **Logo**: `/web/public/logo.png` (balança neon ciano/verde sobre fundo escuro)
- **Aplicar em**: navbar, login, `<title>`, favicon, API title, package.json, pyproject.toml

## 3. Migração de LLM: Gemini 2.5 Flash

### Motivação
| Aspecto | Gemini 2.5 Flash | GPT-4o-mini |
|---|---|---|
| Custo | ~$0.075/1M tokens | ~$0.15/1M tokens |
| Structured output | `response_schema` Pydantic nativo | `beta.parse()` |
| Contexto | 1M tokens | 128k tokens |
| Qualidade PT-BR jurídico | Excelente | Muito boa |

### Implementação
- Novo: `backend/app/infrastructure/gemini_client.py`
- SDK: `google-genai`
- API key via env var `GOOGLE_API_KEY` (arquivo `.env`, gitignored)
- Modelos Pydantic de resposta: `ContractAnalysisResult`, `ContractSummaryResult`, `CorrectedContractResult`
- Remover dependência do `openai` do pyproject.toml
- Remover `backend/app/infrastructure/openai_client.py`

## 4. Playbook Fixo

Cláusulas da Lavanderia 60 Minutos hardcoded em `backend/app/domain/playbook.py`:

```python
PLAYBOOK_CLAUSES = [
    PlaybookClause(code="EXCLUSIVIDADE", title="Da Exclusividade", ...),
    PlaybookClause(code="PRAZO", title="Do Prazo", ...),
    PlaybookClause(code="VISTORIAS", title="Das Vistorias", ...),
    PlaybookClause(code="OBRAS", title="Das Obras", ...),
    PlaybookClause(code="CESSAO", title="Da Cessão", ...),
    PlaybookClause(code="DISPOSICOES_GERAIS", title="Das Disposições Gerais", ...),
    PlaybookClause(code="OBRIGACAO_NAO_FAZER", title="Da Obrigação de Não Fazer", ...),
    PlaybookClause(code="ASSINATURAS", title="Das Assinaturas", ...),
]
```

- Substitui o sistema `Policy` + `PolicyRule` do banco
- Cada cláusula tem: `code`, `title`, `full_text`, `category`

## 5. Pipeline de Análise (3 Etapas)

### Etapa 1 — Análise de Risco
```
Upload PDF
  → PyMuPDF extrai texto com metadata de página
  → ContractChunker divide por cláusula (regex)
  → SSE inicia streaming de progresso
  → Para cada chunk:
      → Gemini analisa contra playbook → Pydantic validado
      → SSE emite "Analisando cláusula 3/8..."
  → Merge findings Gemini + avaliação determinística
  → Salva análise + findings no banco
  → SSE emite "completed"
```

### Etapa 2 — Relatório
- Nota geral de risco (0-100)
- Nota por cláusula com severidade (critical/attention/conforme)
- Explicação do risco em linguagem clara
- Cláusulas com nota baixa destacadas visualmente

### Etapa 3 — Geração de Contrato Corrigido (NOVO)
- Botão "Gerar contrato corrigido" disponível após análise
- Gemini recebe: contrato original + findings + playbook
- Gera contrato completo corrigido
- Resumo de alterações: para cada cláusula alterada, explica o que mudou e por quê
- Download como DOCX (usando python-docx)

## 6. Componentes Backend

### 6.1 `infrastructure/gemini_client.py`
- `GeminiAnalysisClient(api_key, model="gemini-2.5-flash")`
- `analyze_contract(chunks: list[str], playbook: list[PlaybookClause]) -> ContractAnalysisResult`
- `summarize_contract(text: str) -> ContractSummaryResult`
- `generate_corrected_contract(original: str, findings: list, playbook: list) -> CorrectedContractResult`
- Retry 1x com backoff em caso de falha
- Nunca retorna `{}` silencioso — sempre `status=failed` com mensagem

### 6.2 `infrastructure/contract_chunker.py`
- Regex: `CLÁUSULA\s+\w+`, `Art\.\s*\d+`, `Parágrafo\s+\w+`
- Cada chunk preserva header: `"CLÁUSULA TERCEIRA: [conteúdo]"`
- Fallback: chunks de ~2000 tokens com overlap 200 se nenhum padrão encontrado

### 6.3 `infrastructure/pdf_text.py` (modificação)
- Retorna `list[PageText]` em vez de `str`
- `PageText(page: int, text: str)`
- Habilita citação de página nos findings

### 6.4 `infrastructure/docx_generator.py` (NOVO)
- Recebe contrato corrigido (texto) + alterações
- Gera .docx formatado com cabeçalho LegalBoard + logo
- Seção de alterações no final do documento

### 6.5 `api/routes/contracts.py` (modificação)
- Novo endpoint: `POST /contracts/{id}/analyze-stream` (SSE)
- Novo endpoint: `POST /contracts/{id}/generate-corrected`
- Paginação em `GET /contracts` (`?page=1&per_page=20`)

### 6.6 `domain/playbook.py` (NOVO)
- `PlaybookClause` dataclass
- `PLAYBOOK_CLAUSES` constante com todas as cláusulas do docx

### 6.7 `infrastructure/prompts.py` (reescrita)
- System prompt em PT-BR para análise jurídica de contratos de locação
- Prompt para geração de contrato corrigido
- Instruções claras para o Gemini avaliar cada cláusula contra o playbook

## 7. Componentes Frontend

### 7.1 React Query (TanStack Query)
- `QueryClientProvider` no layout root
- Hooks: `useContracts()`, `useContract(id)`, `useDashboard()`
- Mutations: `useUploadContract()`, `useAnalyzeContract()`, `useGenerateCorrected()`
- Invalidação automática de cache após mutations

### 7.2 SSE Hook
- `useAnalysisStream(contractId)`
- Expõe: `{ stage, progress, message, isComplete, error }`
- Componente `AnalysisProgress` com barra de progresso
- Ao completar, invalida query cache

### 7.3 Tela de Contrato Corrigido (NOVO)
- Exibe contrato gerado + resumo de alterações lado a lado
- Para cada alteração: cláusula original vs corrigida + justificativa
- Botão de download DOCX

### 7.4 Error Boundaries
- Wrapper nos componentes principais
- Fallback visual + toast para erros de API

### 7.5 Rebranding Visual
- Logo no header/navbar
- Nome "LegalBoard" em toda a interface
- Paleta: fundo escuro + ciano/verde neon (matching a logo)

## 8. Configuração e Deploy

### `.env.local` (gitignored — desenvolvimento local)
```
GOOGLE_API_KEY=<sua-key-aqui>
JWT_SECRET=dev-secret-change-in-production
```

### `.env.example` (versionado — template para deploy)
```
GOOGLE_API_KEY=
JWT_SECRET=
```

### Deploy (Railway/Render/Vercel)
- Configurar `GOOGLE_API_KEY` e `JWT_SECRET` como Environment Variables no painel da plataforma
- O código usa `python-dotenv` para carregar `.env.local` em dev
- Em produção, `os.environ` lê direto das env vars da plataforma

### Dependências novas
- Backend: `google-genai`, `python-docx`, `python-dotenv`
- Frontend: `@tanstack/react-query`

### Dependências removidas
- Backend: `openai`

### Migrações de banco (Alembic)
- Remover tabelas `policies` e `policy_rules` (substituídas pelo playbook fixo)
- Adicionar coluna `corrected_text` em `contract_analyses` para armazenar contrato corrigido
- Adicionar coluna `corrections_summary` (JSON) para resumo das alterações

### Endpoint de status para SSE reconnection
- `GET /contracts/{id}/analysis-status` — retorna estado atual da análise (pending/analyzing/completed/failed + progresso)

## 9. Tratamento de Erros
- Gemini timeout/falha: retry 1x com backoff, depois `status=failed` com mensagem
- PDF sem texto: OCR fallback existente, se falhar retorna erro claro
- Chunker sem padrões: fallback para chunks por tamanho
- SSE desconecta: frontend reconecta, busca estado via GET

## 10. Testes
- Unit: `GeminiAnalysisClient` (mock SDK), `ContractChunker` (fixtures), `playbook.py`
- Integration: pipeline completo upload → chunk → análise → findings → geração
- Frontend: Vitest para hooks, Playwright para E2E
- Testes existentes adaptados — nenhum teste removido sem substituição
