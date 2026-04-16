# LegalBoard — Design de Melhorias (3 Frentes)

> Data: 2026-04-16
> Fontes: `melhorias_aplicacao.md` (9 itens), 9 documentos jurídicos de análise de cláusulas, estado atual do repo

---

## Decisões tomadas

| Decisão | Escolha | Motivo |
|---|---|---|
| Estratégia de release | Faseado (3 frentes sequenciais) | Validação entre frentes, menor risco |
| Política de análise no LLM | Prompt completo (9 docs ~10K tokens) | Cabe no contexto, mais simples e preciso que RAG para 9 docs |
| Busca semântica | pgvector (embeddings de findings + summary) | Valor real para queries cross-contrato |
| Migração de banco | SQLite → PostgreSQL + pgvector | Necessário para produção + habilita vector search |
| Navegação de comparação | Stepper por cláusula | Uma cláusula por vez, anterior/próximo |
| Substituição de Pontos Críticos | Tabela de vencimentos com semáforo | Vermelho < 30d, amarelo < 90d, verde > 90d |
| Tipo "Contrato de terceiro" | Novo valor no enum `ContractSource` | Mantém arquitetura existente |
| RAG para policy | Infra pronta, ativar quando escalar | 9 docs não justifica retrieval; preparado para crescimento |

---

## Frente 1 — UX e Interface

### 1.1 Dashboard objetivo

**Remover:**
- Timeline de eventos do dashboard (mantida apenas no detalhe do contrato `/contracts/[id]`)
- "Achados Críticos" stat card

**Substituir "Achados Críticos" por "Contratos Próximos do Vencimento":**
- Tabela ordenada por `days_remaining ASC`
- Colunas: Nome do contrato, Unidade (parties.locatario), Tipo (source label), Vencimento (end_date), Urgência
- Semáforo de urgência:
  - Vermelho: < 30 dias
  - Amarelo: 30-90 dias
  - Verde: > 90 dias
- Limite: 10 contratos na tabela, link "Ver todos" para acervo com filtro

**Manter no dashboard:**
- Stats resumidos: contratos ativos, contratos vencendo (< 90d), notificações pendentes
- Histórico de notificações recentes (seção compacta)

**Backend:**
- `GET /api/dashboard` — novo campo `expiring_contracts: [{id, title, unit, source_label, end_date, days_remaining, urgency_level}]`
- Query otimizada: `WHERE is_active = true AND end_date IS NOT NULL ORDER BY end_date ASC LIMIT 10`

### 1.2 Painel de Comparação — Stepper por cláusula

**Remover:**
- `version-diff-panel.tsx` (comparação de texto diff bruto)
- Resumo executivo do diff
- Exibição do texto lado a lado

**Implementar — `ClauseStepper`:**
- Navegação: `[< Anterior] Cláusula 3 de 12 [Próximo >]`
- Cada cláusula exibe:
  - Nome da cláusula
  - Status: crítico / atenção / conforme (badge colorido)
  - Texto atual (current_summary do finding)
  - Regra da policy (policy_rule)
  - Explicação do risco (risk_explanation)
  - Direção sugerida (suggested_adjustment_direction)
- Total de cláusulas e contagem por status no topo (ex: "3 críticos, 5 atenção, 4 conforme")

**Regra de negócio:** toda análise comparativa = uma cláusula por vez. Validação no backend e frontend.

### 1.3 Remoções

| Componente/Página | Ação |
|---|---|
| `version-history-panel.tsx` | Remover — histórico de versão sai da UI |
| Timeline no dashboard | Remover de `dashboard-screen.tsx` |
| Text diff bruto | Remover de `version-diff-panel.tsx` |
| Endpoint `/api/contracts/{id}/compare` | Manter, mas retornar findings por cláusula em vez de text diff |

### 1.4 Acervo vs Histórico

**Acervo (`/acervo`):**
- Conteúdo documental cru — sem sugestões automáticas
- Mostra: título, partes, datas, tipo, status, findings resumidos (apenas status badge)
- Não exibe: direção sugerida, risco explicado, recomendações

**Histórico (`/historico`):**
- Camada analítica habilitada
- Mostra: situação atual, evolução histórica (últimas análises), direção sugerida
- Sugestões visíveis aqui

---

## Frente 2 — Regras de Negócio

### 2.1 Migração SQLite → PostgreSQL + pgvector

**Por que:**
- SQLite não suporta concurrent access em produção
- pgvector habilita busca semântica em contratos
- Postgres já está no `docker-compose.yml`

**Mudanças:**
- `DATABASE_URL` default → `postgresql+psycopg://...`
- Alembic migrations rodadas contra Postgres
- `app/db/session.py` — engine atualizada
- Remover `aiosqlite` das dependencies (manter como dev-only para tests unitários)
- `pyproject.toml` — adicionar `psycopg[binary]` (já existe), remover `aiosqlite` de producao
- Variável `DATABASE_URL` obrigatória em `.env`

### 2.2 Checklist por cláusula (9 cláusulas canônicas)

**Estrutura derivada dos 9 documentos jurídicos:**

| # | Cláusula | Classificação AI |
|---|---|---|
| 1 | Objeto e Viabilidade | adequada / risco_médio / ausente / conflitante |
| 2 | Exclusividade | adequada / risco_médio / ausente / conflitante |
| 3 | Obras e Adaptações | adequada / risco_médio / ausente / conflitante |
| 4 | Cessão e Sublocação | adequada / risco_médio / ausente / conflitante |
| 5 | Prazo e Renovação | adequada / risco_médio / ausente / conflitante |
| 6 | Comunicação e Penalidades | adequada / risco_médio / ausente / conflitante |
| 7 | Obrigação de Não Fazer (pós-contrato) | adequada / risco_médio / ausente / conflitante |
| 8 | Vistoria e Acesso | adequada / risco_médio / ausente / conflitante |
| 9 | Assinatura e Forma | adequada / risco_médio / ausente / conflitante |

**Prompt LLM reescrito:**
1. Ler por lógica de negócio, não por palavras-chave isoladas
2. Eixo central: viabilidade do ponto para lavanderia self-service
3. Ordem obrigatória de análise: objeto → viabilidade → exclusividade → obras → cessão → estabilidade temporal → comunicação/penalidades → proteção pós-contrato → assinatura
4. Veredito final: o contrato proporciona segurança jurídico-econômica equivalente ao padrão?

**Resultado por cláusula (Finding):**
- `clause_name`: exatamente um dos 9 nomes canônicos
- `classification`: adequada | risco_médio | ausente | conflitante
- `current_summary`: o que o contrato diz sobre essa cláusula
- `policy_rule`: o que a policy exige
- `risk_explanation`: por que há risco (se houver)
- `suggested_adjustment_direction`: para onde ir

### 2.3 Novo tipo de contrato: `third_party_contract`

**Backend:**
- Adicionar `third_party_contract = "third_party_contract"` ao enum `ContractSource`
- Atualizar labels: `third_party_draft` → "Minuta de terceiro", `signed_contract` → "Contrato assinado", `third_party_contract` → "Contrato de terceiro"

**Frontend:**
- Dropdowns de tipo/source atualizados
- Filtros de lista atualizados
- Labels traduzidos

### 2.4 Contrato assinado → Acervo automático

**Regra:** quando `source = signed_contract` e análise completa (`analysis.status = completed`), setar `contract.is_active = true`.

**Implementação:**
- Após completar análise, verificar se `source == signed_contract`
- Se sim, update `is_active = true, activated_at = now()`
- Frontend: contrato aparece no Acervo sem ação manual

### 2.5 Busca semântica com pgvector

**Tabela `contract_embeddings`:**
```sql
CREATE TABLE contract_embeddings (
    id UUID PRIMARY KEY,
    contract_id UUID REFERENCES contracts(id) ON DELETE CASCADE,
    chunk_type VARCHAR(50), -- 'finding_summary', 'contract_summary', 'metadata'
    chunk_text TEXT,
    embedding vector(1536),
    metadata_json JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

**Indexação:**
- Ao completar análise: gerar embeddings de cada finding (current_summary + risk_explanation)
- Ao gerar summary: embedding do summary completo
- Embeddings via OpenAI `text-embedding-3-small` (1536 dim)

**Endpoint:**
- `POST /api/search` — `{ query: string, filters?: { source?, is_active? }, limit?: number }`
- Query → embedding → cosine similarity → resultados ranqueados
- Retorna: contract_id, title, matching_chunk, similarity_score

**Infra de RAG para policy (preparada, não ativada):**
- Tabela `policy_chunks` criada (schema pronto)
- Seed script preparado
- Ativação quando policy > 50 cláusulas ou > 50K tokens

---

## Frente 3 — Performance

### 3.1 Backend

| Otimização | Detalhe |
|---|---|
| Índices | `contracts(end_date)`, `contracts(is_active)`, `contracts(status)`, `contract_events(event_date)`, `contract_embeddings USING hnsw (embedding vector_cosine_ops)` |
| Dashboard query | Query única preparada, LIMIT 10, index scan em end_date |
| Connection pool | SQLAlchemy pool_size=10, max_overflow=20 em produção |
| Cache | Dashboard snapshot cacheado 5 min (in-memory LRU ou Redis se disponível) |

### 3.2 Frontend

| Otimização | Detalhe |
|---|---|
| Remoção de componentes pesados | version-diff-panel, version-history-panel, timeline no dashboard |
| Lazy loading | `React.lazy` para telas de acervo, histórico, detalhe |
| React.memo | Em itens de lista (contract cards, findings) |
| Query invalidation | TanStack Query — invalidar apenas cache afetado, não global |

---

## Ordem de implementação

```
Frente 1 (UX)          Frente 2 (Negócio)       Frente 3 (Perf)
─────────────────      ──────────────────       ────────────────
1.1 Dashboard          2.1 SQLite → Postgres     3.1 Índices + pool
1.2 Stepper cláusula   2.2 Checklist 9 cláus    3.2 Frontend lazy
1.3 Remoções           2.3 Tipo terceiro
1.4 Acervo/Histórico   2.4 Assinado → Acervo
                       2.5 Busca semântica
```

**Dependências:**
- 2.1 (Postgres) deve vir antes de 2.5 (pgvector)
- 2.2 (checklist) deve vir antes de 1.2 (stepper — stepper depende dos findings por cláusula)
- 1.3 (remoções) pode ser paralelo com tudo

**Ordem sugerida:**
1. **2.1** — Migração Postgres (base para tudo)
2. **2.2** — Checklist 9 cláusulas + prompt reescrito (base para stepper)
3. **2.3** — Tipo terceiro (simples, quick win)
4. **2.4** — Assinado → Acervo automático
5. **1.1** — Dashboard objetivo (substituir Pontos Críticos)
6. **1.2** — Stepper por cláusula (depende de 2.2)
7. **1.3** — Remoções (version-history, diff bruto, timeline)
8. **1.4** — Acervo sem sugestões / Histórico com sugestões
9. **2.5** — Busca semântica pgvector
10. **3.1 + 3.2** — Performance (índices, lazy loading, memo)

---

## Critérios de aceite

| ID | Critério | Como verificar |
|---|---|---|
| AC1 | Dashboard não tem timeline de eventos | `/dashboard` não renderiza `events-timeline` |
| AC2 | "Achados Críticos" substituído por tabela de vencimentos | Ver semáforo vermelho/amarelo/verde + dados corretos |
| AC3 | Comparação mostra uma cláusula por vez | Stepper com Anterior/Próximo, badge de status |
| AC4 | Text diff bruto removido | `version-diff-panel` não existe mais |
| AC5 | Histórico de versão removido | `version-history-panel` não existe mais |
| AC6 | Acervo não mostra sugestões | `/acervo` — sem `suggested_adjustment_direction` |
| AC7 | Histórico mostra sugestões | `/historico` — com situação atual + direção sugerida |
| AC8 | Tipo "Contrato de terceiro" disponível | Dropdown + filtro + API retornam novo tipo |
| AC9 | Contrato assinado vai pro acervo automático | Upload signed → análise → `is_active=true` sem ação manual |
| AC10 | Análise produz 9 findings canônicos | Cada finding.clause_name ∈ lista de 9 cláusulas |
| AC11 | Postgres como banco principal | `DATABASE_URL` aponta para Postgres, sem SQLite em prod |
| AC12 | Busca semântica funciona | `POST /api/search` retorna contratos por similaridade |
| AC13 | Performance melhorada | Dashboard < 500ms, listas < 300ms |

---

## Riscos

| Risco | Mitigação |
|---|---|
| Migração SQLite → Postgres pode quebrar testes | Testes unitários continuam com SQLite (dev dependency); testes de integração usam Postgres via `DATABASE_URL` |
| Prompt reescrito pode produzir formato inesperado | Schema Pydantic strict + fallback para análise determinística |
| Embeddings custam $ (OpenAI) | `text-embedding-3-small` custa $0.02/1M tokens; ~1K contratos = ~$0.01 |
| pgvector requer Postgres 16+ | Imagem `postgres:16` já está no docker-compose |

---

**Fim do spec**