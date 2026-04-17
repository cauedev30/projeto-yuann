# LegalTech — Assertividade da LLM, UX e Notificações — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Resolver 3 problemas estruturais — LLM pouco assertiva, UX incompleta, notificações inexistentes — através de prompt profundo com 9 cláusulas canônicas, ClauseStepper no frontend, dashboard objetivo, remoção de componentes obsoletos, diferenciação Acervo/Histórico, notificações em 3 sequências, e correção de bugs de produção.

**Architecture:** Prompt Profundo primeiro (sem RAG, 9 DOCXs ~10K tokens cabem no contexto), depois UX (stepper, dashboard, remoções), depois notificações (sequências 90/30/7, email do usuário). Bugs de produção corrigidos no meio quando bloqueiam.

**Tech Stack:** Python 3.12+ / FastAPI / SQLAlchemy 2 / PostgreSQL (Railway) / OpenAI gpt-5-mini / Next.js 15 / React 19

**Spec:** `docs/superpowers/specs/2026-04-17-legaltech-assertiveness-and-ux-design.md`

---

## File Map

### New files to create

| File | Responsibility |
|---|---|
| `web/src/features/contracts/components/clause-stepper.tsx` | Stepper: 1 cláusula por vez com Anterior/Próximo |
| `web/src/features/contracts/components/clause-stepper.module.css` | Estilos do stepper |
| `web/src/app/(app)/notifications/page.tsx` | Página de notificações |
| `web/src/features/notifications/components/notification-badge.tsx` | Badge de notificações não lidas no header |
| `web/src/features/notifications/components/notification-badge.module.css` | Estilos do badge |
| `web/src/lib/api/notifications.ts` | Cliente API de notificações |
| `web/tests/e2e/clause-stepper.spec.ts` | E2E do stepper |

### Files to modify

| File | Change |
|---|---|
| `backend/app/infrastructure/prompts.py` | Reescrever `SYSTEM_PROMPT` com checklist profundo de 9 cláusulas + regras de decisão por cláusula |
| `backend/app/infrastructure/llm_models.py` | Adicionar campo `classification` em `AnalysisFindingItem` (adequada/risco_medio/ausente/conflitante) e mapear para `status` existente |
| `backend/app/domain/contract_analysis.py` | Atualizar `evaluate_rules` para mapear classificação canônica para status existente |
| `backend/app/application/dashboard.py` | Remover `events` do retorno (timeline sai do dashboard), corrigir `expiring_soon` para contar contratos (não events) |
| `backend/app/schemas/dashboard.py` | Remover `events` de `DashboardSnapshotResponse` |
| `web/src/entities/dashboard/model.ts` | Remover `DashboardEvent` e `events` de `DashboardSnapshot` |
| `web/src/features/dashboard/screens/dashboard-screen.tsx` | Remover `EventsTimeline`, usar `ExpiringContractsTable` |
| `web/src/features/contracts/screens/contract-detail-screen.tsx` | Substituir `VersionDiffPanel` por `ClauseStepper`, adicionar `context` prop ("acervo"/"historico"/"contracts") |
| `web/src/features/contracts/screens/acervo-screen.tsx` | Passar `context="acervo"` ao navegar para detalhe |
| `web/src/features/contracts/screens/historico-screen.tsx` | Passar `context="historico"` ao navegar; adicionar badge de findings críticos nos cards |
| `web/src/components/navigation/app-shell.tsx` | Adicionar `NotificationBadge` no header |
| `backend/app/api/routes/notifications.py` | Adicionar `GET /api/notifications?dismissed=false` e `PATCH /api/notifications/{id}/dismiss` |
| `backend/app/domain/notifications.py` | Atualizar `_recipient_for_event` para aceitar email do usuário; criar sequência 90/30/7 |
| `backend/app/domain/events.py` | Criar 3 eventos de notificação por contrato vencendo (90, 30, 7 dias) |

### Files to delete

| File | Reason |
|---|---|
| `web/src/features/contracts/components/version-diff-panel.tsx` | Removido — diff bruto substituído pelo ClauseStepper |
| `web/src/features/contracts/components/version-diff-panel.module.css` | Estilos do diff removido |
| `web/src/features/contracts/components/version-history-panel.tsx` | Removido — histórico de versão sai da UI |
| `web/src/features/contracts/components/version-history-panel.module.css` | Estilos do history removido |
| `web/src/features/dashboard/components/events-timeline.tsx` | Removido — timeline sai do dashboard |
| `web/src/features/dashboard/components/events-timeline.module.css` | Estilos da timeline |
| `web/src/features/dashboard/components/events-timeline.test.tsx` | Testes da timeline removida |

---

## Task 1: Reescrever prompt de análise com checklist profundo de 9 cláusulas

**Goal:** Transformar o `SYSTEM_PROMPT` genérico (~73 linhas) em um prompt estruturado com regras de decisão detalhadas por cláusula, retiradas dos 9 DOCXs jurídicos. Atualizar `AnalysisFindingItem` para suportar `classification`.

**Files:**
- Modify: `backend/app/infrastructure/prompts.py`
- Modify: `backend/app/infrastructure/llm_models.py`
- Modify: `backend/app/domain/contract_analysis.py`

- [ ] **Step 1: Adicionar campo `classification` em `AnalysisFindingItem`**

Em `backend/app/infrastructure/llm_models.py`, adicionar campo `classification` em `AnalysisFindingItem`:

```python
class AnalysisFindingItem(BaseModel):
    clause_code: str = Field(description="Codigo interno da clausula analisada.")
    clause_title: str = Field(description="Nome amigavel da clausula em portugues.")
    classification: Literal["adequada", "risco_medio", "ausente", "conflitante"] = Field(
        description="Classificacao canonica: adequada, risco_medio, ausente ou conflitante."
    )
    severity: Literal["critical", "attention"] = Field(
        description="Severidade do achado: critical ou attention."
    )
    risk_score: int = Field(ge=0, le=100, description="Score de risco do achado.")
    explanation: str = Field(description="Explicacao objetiva do problema encontrado.")
    suggested_correction: str = Field(
        default="",
        description="Correcao sugerida para resolver o achado.",
    )
    page_reference: str | None = Field(
        default=None,
        description="Referencia de pagina quando disponivel.",
    )
```

- [ ] **Step 2: Atualizar `evaluate_rules` para mapear classificação → status**

Em `backend/app/domain/contract_analysis.py`, adicionar função de mapeamento:

```python
CLASSIFICATION_TO_STATUS = {
    "adequada": "conforme",
    "risco_medio": "attention",
    "ausente": "critical",
    "conflitante": "critical",
}
```

Atualizar a lógica de `merge_analysis_items` para:
1. Se o finding da LLM tem `classification`, mapear para `status` via `CLASSIFICATION_TO_STATUS`
2. Persistir `classification` no campo `metadata_json` do `ContractAnalysisFinding`
3. Mapear `explanation` → `risk_explanation` e `suggested_correction` → `suggested_adjustment_direction` na persistência

No `ContractAnalysisFinding` ORM, adicionar `classification` ao `metadata_json`:

```python
# Ao persistir finding:
metadata_json = {
    "classification": item.classification,
    **(item.metadata or {}),
}
finding = ContractAnalysisFinding(
    clause_name=item.clause_code,
    status=CLASSIFICATION_TO_STATUS.get(item.classification, item.severity),
    severity=item.severity,
    current_summary="",  # preenchido pelo merge
    policy_rule="",       # preenchido pelo merge
    risk_explanation=item.explanation,
    suggested_adjustment_direction=item.suggested_correction,
    metadata_json=metadata_json,
)
```

- [ ] **Step 3: Reescrever `SYSTEM_PROMPT` com regras de decisão por cláusula**

Em `backend/app/infrastructure/prompts.py`, substituir o `SYSTEM_PROMPT` existente pelo prompt profundo. Cada cláusula recebe regras de verificação, classificação objetiva e exemplos. O prompt mantém a estrutura de 9 cláusulas canônicas existente mas adiciona profundidade jurídica. O mapeamento classification→status fica explícito:

```
## Mapeamento de classificação para severidade
- adequada → status "conforme", não gera achado negativo
- risco_medio → status "attention", severity "medium"  
- ausente → status "critical", severity "critical"
- conflitante → status "critical", severity "critical"
```

- [ ] **Step 4: Atualizar `build_user_prompt` para reforçar classificação canônica**

Em `backend/app/infrastructure/prompts.py`, adicionar instrução final no `build_user_prompt`:

```python
    ...existing code...

    return f"""## Clausulas do Playbook da Franquia
{clauses_text}

## Texto do Contrato
{contract_text}

Analise o contrato acima usando o checklist obrigatorio de 9 clausulas canonicas contra o playbook e a Lei 8.245/1991. Produza EXATAMENTE 9 achados, um por clausula canonica. Para CADA achado, forneça:
- clause_code: o código canônico (ex: OBJETO_E_VIABILIDADE)
- classification: adequada | risco_medio | ausente | conflitante
- severity: critical | attention (mapeado da classification)
- explanation: justificativa objetiva baseada nas regras de verificação
- suggested_correction: direção sugerida para adequação (vazio se adequada)"""
```

- [ ] **Step 5: Atualizar testes de prompts e análise**

Em `backend/tests/infrastructure/test_prompts.py`, atualizar testes para verificar que o novo prompt produz 9 achados com `classification` no formato esperado.

Em `backend/tests/domain/test_contract_analysis.py`, adicionar testes para `CLASSIFICATION_TO_STATUS` mapeamento.

- [ ] **Step 6: Rodar testes e commitar**

```bash
cd /home/dvdev/projeto-yuann/cloned-repo/backend && source .venv/bin/activate && python -m pytest tests/infrastructure/test_prompts.py tests/domain/test_contract_analysis.py tests/infrastructure/test_openai_client.py -q --tb=short
git add -A && git commit -m "feat: rewrite analysis prompt with deep 9-clause canonical checklist and classification mapping"
```

---

## Task 2: Corrigir bugs de produção

**Goal:** Corrigir os 3 bugs de produção listados na spec: dashboard `expiring_soon` contando events, `ContractEmbedding` incompatível com SQLite, e `POST /api/search` retornando 500 sem pgvector.

**Files:**
- Modify: `backend/app/application/dashboard.py` — corrigir `expiring_soon`
- Modify: `backend/app/db/models/embedding.py` — compatibilidade SQLite
- Modify: `backend/app/infrastructure/semantic_search.py` — fallback quando pgvector não disponível
- Modify: `backend/app/api/routes/search.py` — tratamento robusto de erro

- [ ] **Step 1: Corrigir `expiring_soon` no dashboard**

Em `backend/app/application/dashboard.py`, a linha atual conta `len(event_items)`. Corrigir para contar contratos vencendo:

```python
expiring_soon_count = len(expiring_contracts)
```

E usar `expiring_soon_count` no retorno:

```python
summary=DashboardSummaryResponse(
    active_contracts=active_contracts,
    critical_findings=critical_findings,
    expiring_soon=expiring_soon_count,
),
```

- [ ] **Step 1b: Corrigir `active_contracts` para contar só `is_active=True`**

Em `backend/app/application/dashboard.py`, a função `_is_operational_contract` atualmente usa `contract.status != "draft"`. Corrigir para contar apenas contratos realmente ativos:

```python
def _is_operational_contract(contract: Contract) -> bool:
    return contract.is_active
```

E atualizar `active_contracts`:

```python
active_contracts = sum(1 for c in contracts if c.is_active)
```

- [ ] **Step 1c: Remover filtro `days_remaining > 365` e adicionar nível "blue"**

Em `backend/app/application/dashboard.py`, remover `if days_remaining > 365: continue` que esvazia a tabela. Adicionar nível "blue" para contratos de longo prazo:

```python
if days_remaining < 30:
    urgency = "red"
elif days_remaining < 90:
    urgency = "yellow"
elif days_remaining < 365:
    urgency = "green"
else:
    urgency = "blue"  # Contratos longos, informação ainda útil
```

Atualizar `ExpiringContractResponse.urgency_level` no schema para aceitar `"blue"` como valor válido.

- [ ] **Step 2: Corrigir `ContractEmbedding` para compatibilidade SQLite**

Em `backend/app/db/models/embedding.py`, adicionar fallback condicional:

```python
from sqlalchemy import JSON
from sqlalchemy.dialects.postgresql import JSONB as PgJSONB

# Use JSONB on PostgreSQL, JSON on SQLite
JSONB = PgJSONB.with_variant(JSON, "sqlite")
```

E usar `JSONB` em vez de importar `JSONB` diretamente do `sqlalchemy.dialects.postgresql`.

- [ ] **Step 3: Tratar erro de pgvector ausente no search endpoint**

Em `backend/app/api/routes/search.py`, envolver a busca em try/except e retornar 503 com mensagem clara se pgvector não estiver disponível:

```python
from sqlalchemy.exc import OperationalError

@router.post("", response_model=SearchResponse)
def search_contracts(payload: SearchRequest, session: Session = Depends(get_session)):
    # ... existing code ...
    try:
        results = search_similar_contracts(...)
    except OperationalError:
        raise HTTPException(status_code=503, detail="Embedding service not configured. pgvector extension not available.")
```

- [ ] **Step 4: Rodar testes e commitar**

```bash
cd /home/dvdev/projeto-yuann/cloned-repo/backend && source .venv/bin/activate && python -m pytest tests/ -q --tb=short
git add -A && git commit -m "fix: correct expiring_soon, active_contracts, remove 365 filter, SQLite/pgvector compat"
```

---

## Task 3: Remover EventsTimeline do dashboard e events da API

**Goal:** Remover a timeline de eventos do dashboard (mantida apenas no detalhe do contrato) e o campo `events` de `DashboardSnapshotResponse`. O dashboard passa a mostrar apenas `ExpiringContractsTable`, `ContractsSummary` e `NotificationHistory`.

**Files:**
- Modify: `backend/app/schemas/dashboard.py` — remover `events` de `DashboardSnapshotResponse`
- Modify: `backend/app/application/dashboard.py` — não popular `events`
- Modify: `web/src/entities/dashboard/model.ts` — remover tipos de evento do dashboard
- Modify: `web/src/features/dashboard/screens/dashboard-screen.tsx` — remover `EventsTimeline`
- Delete: `web/src/features/dashboard/components/events-timeline.tsx`
- Delete: `web/src/features/dashboard/components/events-timeline.module.css`
- Delete: `web/src/features/dashboard/components/events-timeline.test.tsx`

- [ ] **Step 1: Remover `events` do schema do dashboard no backend**

Em `backend/app/schemas/dashboard.py`, remover `events: list[DashboardEventResponse]` de `DashboardSnapshotResponse`. Manter `DashboardEventResponse` pois é usado no detalhe do contrato.

Em `backend/app/application/dashboard.py`, parar de popular `event_items` e remover a lógica de construção de `events`. O retorno fica:

```python
return DashboardSnapshotResponse(
    summary=DashboardSummaryResponse(...),
    expiring_contracts=expiring_contracts[:10],
    events=[],  # Removido do dashboard, mas tipo ainda existe
    notifications=notification_items,
)
```

Na verdade, como `events` sai do schema, remover `events=[]` também:

```python
return DashboardSnapshotResponse(
    summary=DashboardSummaryResponse(...),
    expiring_contracts=expiring_contracts[:10],
    notifications=notification_items,
)
```

- [ ] **Step 2: Remover `events` do frontend dashboard**

Em `web/src/entities/dashboard/model.ts`, remover `DashboardEvent` de `DashboardSnapshot` e os tipos de payload de evento do dashboard. Manter `ContractEventSummary` em `contracts/model.ts`.

Em `web/src/features/dashboard/screens/dashboard-screen.tsx`, remover import e renderização de `EventsTimeline`.

- [ ] **Step 3: Deletar componentes obsoletos da timeline do dashboard**

Deletar `web/src/features/dashboard/components/events-timeline.tsx`, `events-timeline.module.css` e `events-timeline.test.tsx`.

- [ ] **Step 4: Atualizar testes e commitar**

```bash
cd /home/dvdev/projeto-yuann/cloned-repo/backend && source .venv/bin/activate && python -m pytest tests/ -q --tb=short
cd /home/dvdev/projeto-yuann/cloned-repo/web && npm run build && npm run test
git add -A && git commit -m "feat: remove EventsTimeline from dashboard, keep only ExpiringContractsTable and notifications"
```

---

## Task 4: Criar ClauseStepper no frontend

**Goal:** Criar o componente `ClauseStepper` que exibe uma cláusula por vez com navegação Anterior/Próximo, badges de severidade, e indicador de posição (3/9). Substituir `VersionDiffPanel` e `VersionHistoryPanel` no detalhe do contrato.

**Files:**
- Create: `web/src/features/contracts/components/clause-stepper.tsx`
- Create: `web/src/features/contracts/components/clause-stepper.module.css`
- Modify: `web/src/features/contracts/screens/contract-detail-screen.tsx`
- Delete: `web/src/features/contracts/components/version-diff-panel.tsx`
- Delete: `web/src/features/contracts/components/version-diff-panel.module.css`
- Delete: `web/src/features/contracts/components/version-history-panel.tsx`
- Delete: `web/src/features/contracts/components/version-history-panel.module.css`

- [ ] **Step 1: Criar `ClauseStepper` component**

Criar `web/src/features/contracts/components/clause-stepper.tsx`:

```tsx
"use client";

import React, { useState } from "react";
import styles from "./clause-stepper.module.css";

export type ClauseFinding = {
  clauseName: string;
  classification: string;
  status: string;
  currentSummary: string;
  policyRule: string;
  riskExplanation: string;
  suggestedAdjustmentDirection: string;
};

type Props = {
  findings: ClauseFinding[];
  context?: "acervo" | "historico" | "contracts";
  riskScore?: number | null;
};

const CANONICAL_NAMES: Record<string, string> = {
  OBJETO_E_VIABILIDADE: "Objeto e Viabilidade",
  EXCLUSIVIDADE: "Exclusividade",
  OBRAS_E_ADAPTACOES: "Obras e Adaptações",
  CESSAO_E_SUBLOCACAO: "Cessão e Sublocação",
  PRAZO_E_RENOVACAO: "Prazo e Renovação",
  COMUNICACAO_E_PENALIDADES: "Comunicação e Penalidades",
  OBRIGACAO_DE_NAO_FAZER: "Obrigação de Não Fazer",
  VISTORIA_E_ACESSO: "Vistoria e Acesso",
  ASSINATURA_E_FORMA: "Assinatura e Forma",
};

function classificationLabel(cls: string): string {
  const labels: Record<string, string> = {
    adequada: "Adequada",
    risco_medio: "Risco médio",
    ausente: "Ausente",
    conflitante: "Conflitante",
  };
  return labels[cls] || cls;
}

function statusLabel(status: string): string {
  if (status === "critical") return "Crítico";
  if (status === "attention") return "Atenção";
  if (status === "conforme" || status === "adequada") return "Conforme";
  return status;
}

function VerdictPanel({ findings, riskScore }: { findings: ClauseFinding[]; riskScore: number | null }) {
  const criticals = findings.filter((f) => f.status === "critical").length;
  const attentions = findings.filter((f) => f.status === "attention").length;
  const conforme = findings.length - criticals - attentions;

  return (
    <div className={styles.verdictPanel}>
      <h3 className={styles.verdictTitle}>Veredito Final</h3>
      {riskScore !== null && (
        <p className={styles.verdictScore}>Score de risco: {riskScore}/100</p>
      )}
      <p>{criticals} críticos · {attentions} atenção · {conforme} conforme</p>
      {criticals === 0 && attentions === 0 ? (
        <p className={styles.verdictConforme}>O contrato está em conformidade com o padrão da franquia.</p>
      ) : (
        <p className={styles.verdictAtencao}>O contrato apresenta pontos que requerem atenção.</p>
      )}
    </div>
  );
}

export function ClauseStepper({ findings, context = "contracts", riskScore }: Props & { riskScore?: number | null }) {
  const [index, setIndex] = useState(0);
  const [hasReadClause, setHasReadClause] = useState(false);
  const clauseBodyRef = useRef<HTMLDivElement>(null);
  const finding = findings[index];
  const showVerdict = index >= findings.length;

  if (showVerdict) {
    return <VerdictPanel findings={findings} riskScore={riskScore ?? null} />;
  }

  if (!finding) return null;

  const total = findings.length;
  const criticals = findings.filter((f) => f.status === "critical").length;
  const attentions = findings.filter((f) => f.status === "attention").length;
  const conforme = total - criticals - attentions;
  const hideSuggestions = context === "acervo";

  const handleScroll = () => {
    if (!clauseBodyRef.current) return;
    const { scrollTop, scrollHeight, clientHeight } = clauseBodyRef.current;
    if (scrollHeight - scrollTop - clientHeight < 20) {
      setHasReadClause(true);
    }
  };

  const handleNext = () => {
    setIndex((i) => i + 1);
    setHasReadClause(false);
  };

  const handlePrevious = () => {
    setIndex((i) => Math.max(0, i - 1));
    setHasReadClause(false);
  };

  const handleDotClick = (dotIndex: number) => {
    setIndex(dotIndex);
    setHasReadClause(false);
  };

  return (
    <div className={styles.stepper}>
      <div className={styles.header}>
        <span className={styles.counter}>
          {criticals} críticos · {attentions} atenção · {conforme} conforme
        </span>
        <span className={styles.pagination}>
          Cláusula {index + 1} de {total}
        </span>
      </div>

      <div className={styles.clauseCard}>
        <div className={styles.clauseHeader}>
          <h3 className={styles.clauseTitle}>
            {CANONICAL_NAMES[finding.clauseName] || finding.clauseName}
          </h3>
          <span className={`${styles.classification} ${styles[`cls-${finding.classification}`]}`}>
            {classificationLabel(finding.classification)}
          </span>
        </div>

      <div className={styles.clauseBody} ref={clauseBodyRef} onScroll={handleScroll}>
            <div className={styles.field}>
            <strong>Texto atual:</strong>
            <p>{finding.currentSummary}</p>
          </div>
          <div className={styles.field}>
            <strong>Regra da policy:</strong>
            <p>{finding.policyRule}</p>
          </div>
          {!hideSuggestions && (finding.status === "critical" || finding.status === "attention") && (
            <>
              <div className={styles.field}>
                <strong>Explicação do risco:</strong>
                <p className={styles.riskText}>{finding.riskExplanation}</p>
              </div>
              {finding.suggestedAdjustmentDirection && (
                <div className={styles.field}>
                  <strong>Direção sugerida:</strong>
                  <p className={styles.suggestionText}>{finding.suggestedAdjustmentDirection}</p>
                </div>
              )}
            </>
          )}
        </div>
      </div>

      <div className={styles.nav}>
        <button
          className={styles.navButton}
          disabled={index === 0}
          onClick={handlePrevious}
          type="button"
        >
          ← Anterior
        </button>
        <div className={styles.dots}>
          {findings.map((f, i) => (
            <button
              key={f.clauseName}
              className={`${styles.dot} ${i === index ? styles.dotActive : ""} ${styles[`dot-${f.status}`]}`}
              onClick={() => handleDotClick(i)}
              type="button"
              aria-label={`Cláusula ${i + 1}: ${CANONICAL_NAMES[f.clauseName] || f.clauseName}`}
            />
          ))}
          <button
            className={`${styles.dot} ${styles.dotVerdict}`}
            onClick={() => { setIndex(findings.length); setHasReadClause(false); }}
            type="button"
            aria-label="Veredito final"
          >
            ✓
          </button>
        </div>
        <button
          className={styles.navButton}
          disabled={index === total - 1 && !hasReadClause}
          onClick={handleNext}
          type="button"
        >
          Próximo →
        </button>
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Criar `clause-stepper.module.css`**

Criar `web/src/features/contracts/components/clause-stepper.module.css` com os estilos do stepper (glassmorphism alinhado ao design system existente, badges coloridos por classification, navegação com dots).

- [ ] **Step 3: Integrar ClauseStepper no contract-detail-screen**

Em `web/src/features/contracts/screens/contract-detail-screen.tsx`:
- Remover imports de `VersionDiffPanel` e `VersionHistoryPanel`
- Adicionar import de `ClauseStepper`
- Adicionar prop `context` ao componente: `"acervo" | "historico" | "contracts"`
- Substituir a seção que renderiza `VersionDiffPanel` por `ClauseStepper` usando os findings da análise
- Mapear findings existentes para `ClauseFinding` incluindo campo `classification` (fallback para mapear `status` → `classification`)

- [ ] **Step 4: Deletar `version-diff-panel` e `version-history-panel`**

```bash
rm web/src/features/contracts/components/version-diff-panel.tsx
rm web/src/features/contracts/components/version-diff-panel.module.css
rm web/src/features/contracts/components/version-history-panel.tsx
rm web/src/features/contracts/components/version-history-panel.module.css
```

Remover imports e referências em `contract-detail-screen.tsx`. Atualizar testes que referenciam esses componentes.

- [ ] **Step 5: Escrever testes do ClauseStepper**

Criar `web/src/features/contracts/components/clause-stepper.test.tsx` com testes para:
- Renderiza 1 cláusula por vez
- Navegação Anterior/Próximo funciona
- Dots de posição refletem severidade
- Context `"acervo"` oculta sugestões
- Context `"historico"` mostra sugestões

- [ ] **Step 6: Atualizar testes do contract-detail-screen**

Remover testes de `VersionDiffPanel` e `VersionHistoryPanel`. Adicionar testes para `ClauseStepper`.

- [ ] **Step 7: Build, testes e commit**

```bash
cd /home/dvdev/projeto-yuann/cloned-repo/web && npm run build && npm run test
git add -A && git commit -m "feat: add ClauseStepper component, remove version-diff-panel and version-history-panel"
```

---

## Task 5: Diferenciar Acervo (sem sugestões) de Histórico (com sugestões)

**Goal:** Acervo mostra conteúdo documental cru — sem sugestões automáticas. Histórico mostra camada analítica habilitada com sugestões e situação atual.

**Files:**
- Modify: `web/src/features/contracts/screens/acervo-screen.tsx`
- Modify: `web/src/features/contracts/screens/historico-screen.tsx`
- Modify: `web/src/features/contracts/screens/contract-detail-screen.tsx`
- Modify: `web/src/app/(app)/acervo/[contractId]/page.tsx` (ou equivalente)
- Modify: `web/src/app/(app)/historico/[contractId]/page.tsx` (ou equivalente)

- [ ] **Step 1: Adicionar prop `context` ao ContractDetailScreen**

Em `web/src/features/contracts/screens/contract-detail-screen.tsx`, adicionar:

```tsx
type ContractDetailScreenProps = {
  contractId: string;
  versionId?: string | null;
  context?: "acervo" | "historico" | "contracts";
  // ...existing props
};
```

Passar `context` para o `ClauseStepper`. Quando `context === "acervo"`, ocultar `riskExplanation` e `suggestedAdjustmentDirection`.

- [ ] **Step 2: Criar rotas para detalhe do contrato com contexto**

Verificar se as rotas `/acervo/[contractId]` e `/historico/[contractId]` existem. Se não, criar páginas que passam o `context` correto para `ContractDetailScreen`.

- [ ] **Step 3: Adicionar badge de findings críticos no Histórico**

Em `web/src/features/contracts/screens/historico-screen.tsx`, adicionar `renderExtraMeta` que mostra:
- Badge com número de findings críticos (se disponível no `ContractListItemSummary`)
- Indicação de situação atual (analisado, enviado, draft)
- Texto "Ver sugestões" que navega para o detalhe

- [ ] **Step 4: Atualizar testes e commitar**

```bash
cd /home/dvdev/projeto-yuann/cloned-repo/web && npm run build && npm run test
git add -A && git commit -m "feat: differentiate acervo (no suggestions) vs historico (with suggestions)"
```

---

## Task 6: Notificações — Sequência 12/9/7 meses e email do usuário

**Goal:** Criar 3 sequências de alerta por contrato vencendo (12, 9, 7 meses antes), usar email do usuário autenticado como destinatário, e adicionar endpoints para listar e dismiss notificações.

**Files:**
- Modify: `backend/app/domain/events.py` — criar 3 eventos de notificação por contrato vencendo
- Modify: `backend/app/domain/notifications.py` — aceitar email do usuário como destinatário
- Modify: `backend/app/api/routes/notifications.py` — adicionar `GET /api/notifications` e `PATCH /api/notifications/{id}/dismiss`

- [ ] **Step 1: Criar sequência de notificação 12/9/7 meses em `events.py`**

Em `backend/app/domain/events.py`, adicionar lógica para gerar 3 `ContractEvent` por contrato com `end_date`:
- 12 meses antes: `event_type=expiration`, `lead_time_days=365`
- 9 meses antes: `event_type=expiration`, `lead_time_days=270`
- 7 meses antes: `event_type=expiration`, `lead_time_days=210`

| Sequência | Meses antes | Tipo | Urgência |
|-----------|------------|------|----------|
| 1 | 12 | `expiration` | Informação |
| 2 | 9 | `expiration` | Urgente |
| 3 | 7 | `expiration` | Crítico |

Atualizar `build_contract_events` para gerar essas notificações automaticamente quando `end_date` existe.

- [ ] **Step 2: Atualizar destinatário de email para usar o email do usuário**

Em `backend/app/domain/notifications.py`, atualizar `_recipient_for_event`:

```python
def _recipient_for_event(event: ContractEvent, user_email: str | None = None) -> str:
    if event.metadata_json and isinstance(event.metadata_json.get("notification_recipient"), str):
        return event.metadata_json["notification_recipient"]
    return user_email or "alerts@legalboard.com.br"
```

Atualizar `process_due_notifications` para receber `user_email` opcional e propagá-lo.

- [ ] **Step 3: Adicionar endpoints de notificação**

Em `backend/app/api/routes/notifications.py`, adicionar:

```python
@router.get("", response_model=list[NotificationResponse])
def list_notifications(
    dismissed: bool = False,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    # Lista notificações do usuário, filtrando por dismissed

@router.patch("/{notification_id}/dismiss", response_model=NotificationResponse)
def dismiss_notification(
    notification_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    # Marca notificação como lida
```

- [ ] **Step 4: Criar schema de resposta de notificação**

Em `backend/app/schemas/notification.py`, adicionar `NotificationResponse`.

- [ ] **Step 5: Escrever testes e commitar**

```bash
cd /home/dvdev/projeto-yuann/cloned-repo/backend && source .venv/bin/activate && python -m pytest tests/ -q --tb=short
git add -A && git commit -m "feat: add notification sequences 12/9/7 months, user email recipient, list/dismiss endpoints"
```

---

## Task 7: Notification Badge no header do frontend

**Goal:** Adicionar badge de notificações não lidas no `AppShell` e página de notificações.

**Files:**
- Create: `web/src/lib/api/notifications.ts`
- Create: `web/src/features/notifications/components/notification-badge.tsx`
- Create: `web/src/features/notifications/components/notification-badge.module.css`
- Create: `web/src/app/(app)/notifications/page.tsx`
- Modify: `web/src/components/navigation/app-shell.tsx`

- [ ] **Step 1: Criar cliente API de notificações**

Criar `web/src/lib/api/notifications.ts` com funções:
- `listNotifications(dismissed?: boolean)` → `GET /api/notifications`
- `dismissNotification(id: string)` → `PATCH /api/notifications/{id}/dismiss`
- `getUnreadCount()` → `GET /api/notifications?dismissed=false` (contar items)

- [ ] **Step 2: Criar `NotificationBadge` component**

Criar `web/src/features/notifications/components/notification-badge.tsx` com:
- Badge com count de notificações não lidas
- Dropdown com lista de notificações recentes
- Link para dismiss individual
- Polling a cada 60 segundos para atualizar o count

- [ ] **Step 3: Integrar `NotificationBadge` no `AppShell`**

Em `web/src/components/navigation/app-shell.tsx`, adicionar `NotificationBadge` no header, após o logo e antes do botão de logout.

- [ ] **Step 4: Criar página de notificações**

Criar `web/src/app/(app)/notifications/page.tsx` com lista completa de notificações com filtros (todas/não lidas).

- [ ] **Step 5: Testes e commit**

```bash
cd /home/dvdev/projeto-yuann/cloned-repo/web && npm run build && npm run test
git add -A && git commit -m "feat: add notification badge in header and notifications page"
```

---

## Task 8: Auto-activate contracts signed → Acervo

**Goal:** Quando a análise completa para um contrato `signed_contract`, automaticamente setar `is_active = true`. Contratos assinados entram no acervo sem ação manual.

**Note:** `ContractSource.signed_contract` já existe no enum (confirmado em `contract.py:32`).

**Files:**
- Modify: `backend/app/api/routes/contracts.py` — adicionar auto-activate após análise completa
- Modify: `backend/app/application/analysis.py` — adicionar hook de auto-ativação

- [ ] **Step 1: Adicionar auto-ativação em `analysis.py`**

Em `backend/app/application/analysis.py`, adicionar função:

```python
def auto_activate_signed_contract(contract: Contract, session: Session) -> None:
    """Auto-activate signed contracts after analysis completion."""
    if not contract.is_active:
        for version in contract.versions:
            if version.source == ContractSource.signed_contract:
                contract.is_active = True
                contract.activated_at = datetime.now(timezone.utc)
                session.commit()
                return
```

- [ ] **Step 2: Chamar auto-ativação após análise no endpoint stream**

Em `backend/app/api/routes/contracts.py`, após `mark_contract_analysis_completed` no fluxo de análise, chamar `auto_activate_signed_contract`.

- [ ] **Step 3: Escrever teste e commitar**

```bash
cd /home/dvdev/projeto-yuann/cloned-repo/backend && source .venv/bin/activate && python -m pytest tests/ -q --tb=short
git add -A && git commit -m "feat: auto-activate signed contracts into acervo after analysis"
```

---

## Task 9: Integração final e testes E2E

**Goal:** Garantir que todas as peças funcionam juntas — prompt profundo produz findings com classification, ClauseStepper renderiza corretamente, dashboard sem timeline, notificações com sequência 90/30/7.

**Files:**
- Verify: todos os testes existentes passam
- Add: testes de integração para o fluxo completo

- [ ] **Step 1: Rodar suite completa do backend**

```bash
cd /home/dvdev/projeto-yuann/cloned-repo/backend && source .venv/bin/activate && python -m pytest tests/ -q --tb=short
```

- [ ] **Step 2: Rodar suite completa do frontend**

```bash
cd /home/dvdev/projeto-yuann/cloned-repo/web && npm run build && npm run test
```

- [ ] **Step 3: Verificar TypeScript sem erros**

```bash
cd /home/dvdev/projeto-yuann/cloned-repo/web && npx tsc --noEmit
```

- [ ] **Step 4: Verificar consistência do Schema**

Garantir que:
- `AnalysisFindingItem.classification` é produzido pela LLM e mapeado para `status` existente
- `ContractAnalysisFinding` persiste `classification` no `metadata_json`
- Frontend `ClauseFinding` suporta `classification` com fallback
- Dashboard não retorna `events`

- [ ] **Step 5: Commit final**

```bash
git add -A && git commit -m "chore: integration verification for assertiveness, UX, and notifications"
```

---

## Out of Scope (declarado)

Os seguintes items da spec foram explicitamente marcados como fora de escopo (spec §9) ou operacionais:

| Item | Status | Motivo |
|---|---|---|
| HTML email templates com branding LegalBoard | Deferido | Spec §9 marca como "futuro"; notificações usam plain text |
| RAG complementar (pgvector para policy) | Deferido | Spec §2.2 é Prioridade 2; infra pronta mas não ativada |
| Notificações push em tempo real (WebSocket) | Deferido | Spec §9 |
| Página dedicada de notificações com filtros avançados | Deferido | Spec §9 |
| Apagamento automático de contratos inativos | Deferido | Retention job já existe |
| Cron job Railway para `POST /api/notifications/process-due` | Operacional | Já existe o endpoint; configurar cron no Railway é infra, não código |
| Habilitar pgvector no Postgres do Railway | Operacional | `CREATE EXTENSION IF NOT EXISTS vector;` já está na migration 0012; necessário acesso superuser no Railway |
| Configurar `SMTP_ENABLED=true` com credenciais reais | Operacional | Configuração de ambiente no Railway, não código |

Para os items operacionais, adicionar ao `DEPLOY_GUIDE.md` como passos de configuração pós-deploy.

---

```
Task 1 (Prompt Profundo)  → base para tudo
Task 2 (Bugs de Produção) → pode ser paralelo com T1
Task 3 (Remover Timeline) → depende de T2 parcialmente
Task 4 (ClauseStepper)     → depende de T1 (classification field)
Task 5 (Acervo/Histórico) → depende de T4 (ClauseStepper)
Task 6 (Notificações)      → independente de T1-T5
Task 7 (Badge UI)          → depende de T6
Task 8 (Auto-activate)    → independente
Task 9 (Integração)        → depende de todos
```