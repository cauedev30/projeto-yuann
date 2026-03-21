# Análise Comparativa: VectorHire vs Projeto Yuann
_Gerado em 2026-03-21_

---

## 1. O que é o VectorHire

VectorHire é um ATS (Applicant Tracking System) B2B que analisa currículos semanticamente contra uma descrição de vaga usando um pipeline RAG Two-Step:

**Tech Stack:**
- Backend: FastAPI + PostgreSQL + `pgvector`
- Embeddings: `sentence-transformers/all-MiniLM-L6-v2` (local, ~80MB)
- LLM: Google Gemini 2.5 Flash via `google-generativeai`
- PDF: PyMuPDF (`fitz`)
- ORM: SQLAlchemy 2.x com Repository Pattern
- Output estruturado: Pydantic schema forçado via `response_schema` do Gemini
- Streaming: Server-Sent Events (SSE) via `StreamingResponse` do FastAPI

**Pipeline:**
1. PDF → texto bruto (PyMuPDF)
2. Texto → chunks semânticos por seção em UPPERCASE
3. Chunks → embeddings vetoriais locais (sentence-transformers)
4. Embeddings → upsert no PostgreSQL/pgvector
5. Job description → embedding → cosine distance search → top-N chunks relevantes
6. Chunks relevantes → Gemini com schema Pydantic → JSON estruturado com veredito

---

## 2. Comparação com Projeto Yuann

| Aspecto | Projeto Yuann | VectorHire |
|---|---|---|
| LLM | OpenAI GPT-4o-mini | Gemini 2.5 Flash |
| Output estruturado | `response_format: json_object` (sem schema) | `response_schema=PydanticModel` (schema forçado) |
| Embeddings | Nenhum (texto direto para LLM) | `all-MiniLM-L6-v2` local |
| Banco vetorial | Nenhum (SQLite) | PostgreSQL + pgvector |
| Chunking | Nenhum (texto bruto completo para o LLM) | Chunking por seções (headers UPPERCASE) |
| Streaming | Nenhum | SSE em tempo real |
| Busca semântica | Nenhum | Cosine similarity via pgvector |
| PDF | PyMuPDF com fallback OCR | PyMuPDF simples |
| Comparação política | Regras + LLM ad hoc | N/A (domínio diferente) |
| Arquitetura | DDD (domain/application/infrastructure) | Simples (src/extraction/processing/vector_db/llm) |

---

## 3. Gaps Críticos no Projeto Yuann (o que VectorHire resolve)

### Gap 1: Sem chunking de contratos
**Problema atual:** O projeto yuann envia o texto bruto completo do contrato para o GPT-4o-mini em uma única chamada. Para contratos longos (> 20 páginas), isso:
- Ultrapassa o context window facilmente
- Aumenta custo de tokens desnecessariamente
- Reduz precisão da análise por falta de foco

**Solução do VectorHire:** Chunking por seções semânticas, onde cada chunk preserva o contexto da seção (ex: `CLÁUSULA DE VIGÊNCIA:\n[conteúdo]`). Para contratos de franquia, adaptar para chunks por cláusula numerada.

**Implementação recomendada para Yuann:**
```python
# infrastructure/contract_chunker.py
def chunk_contract_by_clause(text: str, contract_id: str) -> list[ContractChunk]:
    """Fatia contrato por cláusulas numeradas (ex: CLÁUSULA 1., Art. 1º)"""
    import re
    pattern = r'(CLÁUSULA\s+\d+|Art(?:igo)?\.?\s+\d+)[ºª\.]'
    chunks = re.split(pattern, text, flags=re.IGNORECASE)
    # ...retorna lista de ContractChunk com section_id, text_content
```

### Gap 2: Sem busca semântica por política
**Problema atual:** Para comparar cláusulas contra o playbook de políticas, o projeto busca TODAS as regras da política e as envia para o LLM. Com políticas extensas, isso é ineficiente.

**Solução do VectorHire:** Vetorizar as cláusulas do contrato, vetorizar as regras da política, fazer busca por cosine similarity para encontrar apenas as regras mais relevantes para cada cláusula — reduzindo tokens e aumentando precisão.

**Implementação recomendada:**
```python
# Em pyproject.toml, adicionar:
# sentence-transformers>=3.0.0
# pgvector>=0.3.0  (ou sqlite-vec para manter SQLite)

# Alternativa sem mudar banco: usar sqlite-vec (extensão vetorial para SQLite)
# pip install sqlite-vec
```

> **Nota:** Para manter SQLite (MVP), usar `sqlite-vec` em vez de pgvector. Para produção, migrar para PostgreSQL + pgvector como o VectorHire.

### Gap 3: Sem output estruturado com schema Pydantic forçado
**Problema atual:** O projeto usa `response_format={"type": "json_object"}` que apenas pede JSON genérico. O LLM pode retornar campos errados, tipos errados, ou JSON inválido.

**Solução do VectorHire com Gemini:** Usa `response_schema=CandidateEvaluation` que força o modelo a respeitar o schema Pydantic exatamente.

**Solução equivalente para OpenAI (Structured Outputs):**
```python
# openai_client.py — substituir response_format por:
response = client.beta.chat.completions.parse(
    model="gpt-4o-mini",
    messages=[...],
    response_format=ContractAnalysisResult,  # Pydantic model direto
    temperature=0.1,
)
result = response.choices[0].message.parsed  # já é ContractAnalysisResult validado
```
Isso elimina o `json.loads()` manual e garante que campos ausentes falham em parse-time, não em runtime.

### Gap 4: Sem streaming de progresso na análise
**Problema atual:** A análise de contratos é síncrona — o usuário não vê progresso durante o processamento, que pode levar 10-30 segundos.

**Solução do VectorHire:** SSE (Server-Sent Events) com `StreamingResponse` + `async def event_generator()` que emite updates de progresso em tempo real.

**Implementação recomendada:**
```python
# routes/contracts.py
from fastapi.responses import StreamingResponse
import json

@router.post("/{contract_id}/analyze-stream")
async def analyze_contract_stream(contract_id: str, ...):
    async def generator():
        yield f"data: {json.dumps({'step': 'extracting', 'pct': 10})}\n\n"
        # ... pipeline steps
        yield f"data: {json.dumps({'step': 'done', 'result': result})}\n\n"
    return StreamingResponse(generator(), media_type="text/event-stream")
```

No frontend Next.js, consumir com `EventSource` ou `fetch` + `ReadableStream`.

### Gap 5: PDF extraction sem page-level metadata
**Problema atual:** O `pdf_text.py` extrai todo o texto como string única, perdendo informação de qual página cada trecho estava.

**Solução do VectorHire:** Preserva page boundaries com `chr(12)` (form feed) entre páginas.

**Melhoria rápida:**
```python
# pdf_text.py — modificar extract_contract_text para retornar por página:
pages_text = []
with fitz.open(pdf_path) as doc:
    for i, page in enumerate(doc):
        pages_text.append({"page": i+1, "text": page.get_text("text")})
```

---

## 4. Recomendações Priorizadas

### Prioridade Alta (impacto imediato, baixo esforço)

1. **OpenAI Structured Outputs** — Trocar `response_format={"type": "json_object"}` por `client.beta.chat.completions.parse(response_format=ContractAnalysisResult)`. Elimina falhas silenciosas de JSON. Mudança em `openai_client.py`, ~10 linhas.

2. **Chunking por cláusula** — Adicionar `infrastructure/contract_chunker.py` com split por regex de cláusulas numeradas. Não requer mudança de banco. Reduz tokens e melhora foco do LLM.

3. **Page metadata no PDF** — Modificar `pdf_text.py` para retornar lista de `{page, text}` em vez de string única. Permite futuras citações de página nos findings.

### Prioridade Média (próximo sprint)

4. **SSE para análise assíncrona** — Adicionar endpoint `/contracts/{id}/analyze-stream` que emite progresso via Server-Sent Events. No frontend, mostrar progress bar real.

5. **Embeddings locais para busca de política** — Adicionar `sentence-transformers` e `sqlite-vec` (mantém SQLite) para vetorizar regras de política e fazer busca semântica antes de chamar o LLM. Reduz tokens em 60-80% para políticas extensas.

### Prioridade Baixa (roadmap)

6. **Migrar para PostgreSQL + pgvector** — Para escala, seguir o modelo exato do VectorHire: `pgvector.sqlalchemy.Vector` no modelo ORM + `session.merge()` para upsert idempotente de chunks.

7. **Considerar Gemini como alternativa ao GPT-4o-mini** — Gemini 2.5 Flash tem custo menor e suporta `response_schema` nativo. VectorHire demonstra que é viável para análise jurídica estruturada.

---

## 5. Padrões de Código Diretamente Aproveitáveis do VectorHire

| Arquivo VectorHire | Padrão | Onde aplicar no Yuann |
|---|---|---|
| `src/vector_db/repository.py` | `session.merge()` para upsert idempotente de chunks | `infrastructure/` ao adicionar chunks vetoriais |
| `src/vector_db/repository.py` | `.cosine_distance(embedding)` com pgvector | `db/models/` se migrar para Postgres |
| `src/llm/matching_service.py` | `response_schema=PydanticModel` no Gemini | `openai_client.py` com equivalente OpenAI |
| `src/api/app.py` | `StreamingResponse` + `event_generator()` assíncrono | `api/routes/contracts.py` |
| `src/processing/text_chunker.py` | Chunking preservando seção como prefixo do chunk | `infrastructure/contract_chunker.py` |
| `src/extraction/pdf_extractor.py` | `chr(12)` como separador de páginas | `infrastructure/pdf_text.py` |

---

## 6. O que o Projeto Yuann faz MELHOR que o VectorHire

- **Arquitetura DDD** — Domain/Application/Infrastructure/API com separação clara de responsabilidades. VectorHire é flat e acoplado.
- **Alembic migrations** — Yuann tem 6 migrations versionadas. VectorHire recria schema no startup.
- **JWT Auth** — Yuann tem autenticação completa. VectorHire não tem auth.
- **Testes** — Yuann tem suite de testes (pytest + Playwright). VectorHire não tem testes.
- **Domínio específico** — Extração de metadados contratuais (datas, partes, termos financeiros), eventos, notificações e risk scoring são funcionalidades muito mais ricas.
- **OCR fallback** — Yuann detecta PDFs sem texto embarcado e aciona OCR. VectorHire não tem esse fallback.

---

_Fonte: análise de https://github.com/jsaraivx/vectorhire (main branch) vs /home/dvdev/projeto-yuann (local)_
