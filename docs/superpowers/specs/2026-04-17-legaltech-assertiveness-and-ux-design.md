# Spec: LegalTech — Assertividade da LLM, UX e Notificações

**Data:** 2026-04-17  
**Status:** Draft  
**Abordagem:** Prompt Profundo + RAG complementar

---

## 1. Problema

A aplicação LegalTech tem 3 problemas estruturais:

1. **LLM pouco assertiva** — O prompt de análise tem ~73 linhas genéricas. Cada cláusula é descrita em 1 linha. Os 9 DOCXs de análise jurídica detalham regras de decisão específicas que a LLM nunca vê. Resultado: achados rasos, genéricos, que não agregam valor decisório ao usuário.

2. **UX incompleta** — O ClauseStepper (uma cláusula por vez) foi prometido como regra de negócio mas nunca existiu. Os findings são uma tabela plana. O dashboard mostra tabela de vencimentos vazia. O histórico não exibe sugestões. Version history/diff panels ainda existem.

3. **Notificações inexistentes** — Zero notificações em produção. O sistema existe no código mas não tem scheduler, não puxa email do usuário, e expiring_soon conta events ao invés de contratos vencendo.

---

## 2. Soluções

### 2.1 Prompt Profundo (Abordagem A — Prioridade 1)

Transformar os 9 DOCXs em regras de decisão estruturadas no `SYSTEM_PROMPT`. Cada cláusula canônica recebe:

- **Regras de verificação** — lista explícita do que a LLM deve checar
- **Classificação objetiva** — critérios claros para adequada/risco_medio/ausente/conflitante
- **Exemplos de achado** — o que constitui um achado forte vs. raso
- **Peso no score** — quais cláusulas têm peso maior

**Estrutura de cada cláusula no prompt:**

```
1. OBJETO_E_VIABILIDADE
   Regras de verificação:
   - Verificar se existe cláusula de inviabilidade com prazo definido para aferição
   - Verificar se o locador declara ciência da infraestrutura mínima (art. 22 Lei 8.245)
   - Verificar se há declaração de inexistência de restrição condominial
   - Verificar se há procedimento de comprovação da inviabilidade (laudo, negativa administrativa)
   - Verificar se há regra sobre investimentos prévios em caso de resolução
   
   Classificação:
   - ADEQUADA: inviabilidade com prazo + ciência do locador + declaração condominial
   - RISCO_MEDIO: inviabilidade sem prazo, sem procedimento de comprovação, ou sem declaração do locador
   - AUSENTE: sem cláusula de inviabilidade ou sem menção a infraestrutura
   - CONFLITANTE: inviabilidade contradita por outra cláusula
```

Isso se repete para todas as 9 cláusulas, com profundidade retirada dos DOCXs.

**Impacto estimado:** A assertividade da análise salta de ~30% para ~80% sem mudar infraestrutura.

### 2.2 RAG Complementar (Prioridade 2)

Indexar os 9 DOCXs como chunks no `contract_embeddings`. Quando a LLM for analisar um contrato:

1. Gerar embedding da query (ex: "exclusividade cessão sublocação franqueado")
2. Buscar trechos relevantes dos DOCXs
3. Injetar como contexto complementar no prompt

**O que vai no RAG:**
- Distinções jurídicas (cessão vs sublocação vs exploração operacional)
- Base legal específica (artigos, jurisprudência)
- Exemplos de classificação forte/incompleta/fraca
- Trechos que NÃO cabem no prompt fixo (muito longos)

**O que NÃO vai no RAG (fica no SYSTEM_PROMPT):**
- Regras de decisão (sempre necessárias)
- Classificações por cláusula (sempre necessárias)
- Pesos do score (sempre necessários)

**Requisito:** Habilitar pgvector no PostgreSQL do Railway.

### 2.3 ClauseStepper (Prioridade 1)

Componente React que exibe **uma cláusula por vez** com:

- Barra de navegação (Anterior / Próximo) com indicador de posição (3/9)
- Badge de severidade por cláusula (adequada=green, risco_medio=yellow, ausente=red, conflitante=red+bold)
- Nome da cláusula canônica em destaque
- Descrição do achado (current_summary)
- Sugestão de correção (suggested_adjustment_direction)
- Botão "Próximo" desabilitado até o usuário ler (scroll check)

**Fluxo:** Ao final das 9 cláusulas, exibir veredito final com risk_score.

### 2.4 Correções de UX (Prioridade 1)

| Item | Problema | Solução |
|------|----------|---------|
| Dashboard - ExpiringContracts | Sempre vazio (filtra > 365 dias) | Remover filtro de 365 dias, mostrar todos com urgência |
| Dashboard - Timeline | Deve ser removida da visão geral | Remover `events` do dashboard, manter só expiring_contracts + summary + notifications |
| Dashboard - Summary | `active_contracts: 10` conta todos | Corrigir para contar só `is_active=True` |
| Dashboard - `expiring_soon` | Conta events, não contratos | Contar contratos vencendo em 365 dias |
| Acervo | Não mostra sugestões (OK) | Manter como está |
| Histórico | Deve mostrar sugestões | Adicionar findings resumidos na listagem |
| Version history/diff panels | Deviam ter sido removidos | Remover arquivos e rotas |

### 2.5 Notificações (Prioridade 2)

| Item | Problema | Solução |
|------|----------|----------|
| Recipient | Hardcoded `alerts@example.com` | Puxar email do usuário autenticado |
| Scheduler | Nenhum | Adicionar cron job no Railway (chamar `/api/notifications/process-due` diariamente) |
| SMTP | Provavelmente desabilitado em prod | Configurar `SMTP_ENABLED=true` no Railway com credenciais reais |
| Template | Plain text | Criar template HTML com branding LegalBoard |
| In-app | Enum existe mas sem UI | Implementar badge de notificação nunca lidas no header + polling |
| `lead_time_days` | Fixo em 30 | Criar sequência: 90 dias (alerta), 30 dias (urgente), 7 dias (crítico) |

### 2.6 Bugs de Produção (Prioridade 1)

| Bug | Causa | Solução |
|-----|-------|---------|
| `POST /api/search` retorna 500 | pgvector não habilitado no Railway | Habilitar extensão `vector` no Postgres do Railway |
| Backend tests quebram | `ContractEmbedding` usa `PgJSONB` incompatível com SQLite | Usar `JSON` com fallback condicional por dialect |
| `expiring_contracts: []` | Filtro `days_remaining > 365` remove todos | Mostrar todos os contratos ativos com `end_date`, classificar por urgência |

---

## 3. Arquitetura

### 3.1 Fluxo de Análise (antes)

```
Contrato → Prompt genérico (73 linhas) → OpenAI → Findings rasos
```

### 3.2 Fluxo de Análise (depois)

```
Contrato → SYSTEM_PROMPT (regras detalhadas por cláusula) 
         → RAG context (trechos jurídicos relevantes dos DOCXs)
         → Playbook das cláusulas do contrato padrão
         → OpenAI 
         → Findings assertivos com classificação objetiva
         → Indexar findings como embeddings (RAG futuro)
```

### 3.2 Fluxo de Notificações

```
Cron diário (Railway) → POST /api/notifications/process-due
                      → process_due_events()
                      → Para cada ContractEvent due:
                          → Buscar recipient (email do usuário dono do contrato)
                          → build_email_notification()
                          → dispatch_email_notification()
                          → Criar Notification record
                      → Commit

Usuário faz login → GET /api/notifications?dismissed=false
                  → Badge no header com count de não lidas
                  → NotificationHistory no dashboard
```

---

## 4. Detalhamento por Cláusula Canônica

Cada cláusula do prompt será reescrita com as regras de decisão dos DOCXs. Exemplo completo para OBJETO_E_VIABILIDADE:

### 4.1 OBJETO_E_VIABILIDADE

**Regras de verificação:**
- Verificar se existe cláusula de inviabilidade com resolução sem penalidade
- Verificar se há prazo definido para aferição da inviabilidade
- Verificar se o locador declara ciência da infraestrutura mínima (água, esgoto, energia trifásica, alvarás, CNAE) conforme art. 22 da Lei 8.245
- Verificar se há declaração de inexistência de restrição condominial
- Verificar se há procedimento de comprovação (laudo técnico, negativa administrativa)
- Verificar se há regra sobre investimentos já realizados em caso de resolução

**Classificação:**
- ADEQUADA: inviabilidade com prazo + ciência do locador + declaração condominial + procedimento de comprovação
- RISCO_MEDIO: inviabilidade sem prazo definido, sem procedimento de comprovação, ou sem declaração do locador
- AUSENTE: sem cláusula de inviabilidade ou sem menção a infraestrutura
- CONFLITANTE: inviabilidade contradita por outra cláusula (ex: proíbe obras mas exige viabilidade)

### 4.2 EXCLUSIVIDADE

**Regras de verificação:**
- Verificar se há proibição geral de cessão, sublocação ou empréstimo
- Verificar se há exceção expressa para franqueados
- Verificar se a exceção especifica: (a) se o franqueado pode ocupar integralmente o ponto, (b) se deve comunicar qual franqueado operará, (c) se pode constar em licenças
- Verificar se a destinação do ponto está preservada (não pode mudar atividade)
- Verificar se a locatária permanece responsável (parágrafo terceiro)
- Verificar se há vedação de exploração indireta (mesmo grupo, interpostos)
- Verificar se a garantia locatícia tem disciplina clara sobre substituição de fiador
- Verificar se há cobertura para lavanderia, passadoria, tinturaria, higienização, locker, vending

**Classificação:**
- ADEQUADA: proibição geral + exceção para franqueados + manutenção de responsabilidade + destinação preservada + disciplina de garantia
- RISCO_MEDIO: autoriza franqueados mas sem detalhar forma, sem cobertura indireta, ou com ambiguidade entre cessão/sublocação/exploração
- AUSENTE: sem cláusula de exclusividade ou com autorização ampla a terceiros
- CONFLITANTE: proíbe cessão mas não preserva destinação, ou não mantém responsabilidade da locatária

*(As demais 7 cláusulas seguem o mesmo formato, extraído dos DOCXs. Serão detalhadas no prompt final.)*

### 4.3 OBRAS_E_ADAPTACOES
- Autorização prévia para obras essenciais
- Lista de obras pré-aprovadas (elétrica trifásica, hidráulica, ventilação, fachada, piso, submedição)
- Exigência de responsável técnico (ART/RRT)
- Aprovação formal para obras sensíveis
- Regra sobre reversibilidade e indenização de benfeitorias
- Autorização do locador ≠ autorização legal

### 4.4 CESSAO_E_SUBLOCACAO
- Proibição geral + exceção para franqueados
- Manutenção da responsabilidade da locatária
- Preservação da destinação do ponto
- Disciplina sobre garantia locatícia e substituição de fiador
- Comunicação ao locador sobre identificação do franqueado
- Distinção entre cessão, sublocação e exploração operacional

### 4.5 PRAZO_E_RENOVACAO
- Prazo adequado para amortização
- Renovação automática vs prazo indeterminado
- Disciplina do reajuste no renovado
- Formalização de aditivo
- Manutenção das garantias

### 4.6 COMUNICACAO_E_PENALIDADES
- Comunicações por escrito como requisito
- Multas proporcionais e enforcáveis
- Prazo de cura para infrações
- Tutela específica prevista
- Multa não substitui obrigação de não fazer

### 4.7 OBRIGACAO_DE_NAO_FAZER
- Proibição pós-contratual de realocar para atividade concorrente
- Prazo fixo (24 meses)
- Cobertura direta E indireta (mesmo grupo, interpostos)
- Multa não exime obrigação
- Tutela específica prevista
- Distinção entre distrato consensual e não renovação unilateral

### 4.8 VISTORIA_E_ACESSO
- Vistoria acompanhada pelo locatário ou representante
- Aviso prévio obrigatório
- Horário comercial ou previamente ajustado
- Exceção de emergência com comunicação imediata
- Registro compartilhado (laudo/fotos)

### 4.9 ASSINATURA_E_FORMA
- E-assinatura válida
- Dispensa de firma reconhecida
- Coerência entre forma contratada e prática
- Cláusula acessória de baixa criticidade material
- Reforço físico contingente se questionado

---

## 5. Componentes Frontend

### 5.1 ClauseStepper

**Localização:** `web/src/features/analysis/components/clause-stepper.tsx`

**Props:**
```typescript
interface ClauseStepperProps {
  findings: ContractFinding[];
  currentIndex: number;
  onNext: () => void;
  onPrevious: () => void;
}
```

**Comportamento:**
- Exibe 1 cláusula por vez
- Barra de progresso (3/9)
- Badge de severidade colorido
- Botões Anterior/Próximo
- Ao completar as 9, transiciona para veredito final

### 5.2 Histórico com Sugestões

Adicionar aos cards do `HistoricoScreen`:
- Badge com número de findings críticos
- Indicação de situação atual (analisado, enviado, draft)
- Link "Ver sugestões" que navega para o detail com findings expandidos

### 5.3 In-app Notification Badge

Adicionar ao `AppShell` (header):
- Badge com count de notificações não lidas
- Dropdown com lista de notificações recentes
- Link para dismiss individual ou bulk

---

## 6. Correções de Infra

### 6.1 Habilitar pgvector no Railway

```sql
-- Conectar ao Postgres do Railway como superuser e executar:
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
```

### 6.2 Corrigir ContractEmbedding para SQLite

```python
# Antes:
metadata_json: Mapped[dict[str, Any] | None] = mapped_column(PgJSONB)

# Depois:
metadata_json: Mapped[dict[str, Any] | None] = mapped_column(
    PgJSONB.with_variant(JSON, "sqlite")
)
```

### 6.3 Corrigir Dashboard

```python
# Antes (filtra > 365 dias, removendo tudo):
if days_remaining > 365:
    continue

# Depois (mostra todos, classifica por urgência):
# Remover o filtro de 365 dias
if days_remaining < 30:
    urgency = "red"
elif days_remaining < 90:
    urgency = "yellow"
elif days_remaining < 365:
    urgency = "green"
else:
    urgency = "blue"  # Contratos longos, informação ainda útil
```

### 6.4 Notificações — Recipient do Usuário

```python
# Antes:
def _recipient_for_event(event: ContractEvent) -> str:
    if event.metadata_json and isinstance(event.metadata_json.get("notification_recipient"), str):
        return event.metadata_json["notification_recipient"]
    return "alerts@example.com"

# Depois:
def _recipient_for_event(event: ContractEvent, user_email: str | None = None) -> str:
    if event.metadata_json and isinstance(event.metadata_json.get("notification_recipient"), str):
        return event.metadata_json["notification_recipient"]
    return user_email or "alerts@legalboard.com.br"
```

---

## 7. Sequência de Notificações

Criar 3 sequências de alerta por evento de vencimento:

| Sequência | Dias antes | Tipo | Urgência |
|-----------|-----------|------|----------|
| 1 | 90 | `expiration` | Informação |
| 2 | 30 | `expiration` | Urgente |
| 3 | 7 | `expiration` | Crítico |

Cada contrato com `end_date` gera 3 `ContractEvent` com `lead_time_days` diferentes.

---

## 8. Critérios de Aceite

1. **Assertividade da LLM** — Análise de um contrato real deve produzir findings com classificação objetiva por cláusula, citação de artigos da Lei 8.245, e sugestões de correção específicas (não genéricas)
2. **ClauseStepper funcional** — Exibe 1 cláusula por vez com navegação e badges de severidade
3. **Dashboard com dados** — Tabela de vencimentos com pelo menos 2 contrados preenchidos
4. **Notificações rodando** — Cron dispara diariamente, gera notificações para eventos vencendo em 90/30/7 dias, envia email para o usuário dono do contrato
5. **RAG funcional** — `POST /api/search` retorna resultados relevantes sem erro 500
6. **Backend tests passando** — Todos os testes passam com SQLite e PostgreSQL
7. **Histórico com sugestões** — Tela de histórico mostra indicação de findings críticos

---

## 9. Fora de Escopo

- HTML email templates com branding (futuro)
- Notificações push em tempo real via WebSocket (futuro)
- Página dedicada de notificações com filtros avançados (futuro)
- Migration de SQLite para PostgreSQL para testes (manter SQLite para testes, PG para prod)
- Apagamento automático de contratos inativos (retention job já existe)