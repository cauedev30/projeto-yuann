# LegalBoard Improvements Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement 3 fronts of improvements (UX, business rules, performance) for the LegalBoard contract governance platform, including SQLite→Postgres migration, RAG-ready pgvector infrastructure, 9-clause canonical checklist, and dashboard/UX redesign.

**Architecture:** Phase-gated implementation — Postgres migration first (enables pgvector), then business rules (new types, checklist prompt, auto-acervo), then UX (stepper, dashboard, removals), then performance (indexes, lazy loading). RAG for policy is infrastructure-ready but not activated until the policy grows beyond 50 clauses.

**Tech Stack:** Python 3.12+ / FastAPI / SQLAlchemy 2 / Alembic / PostgreSQL 16 + pgvector / Next.js 15 / React 19 / OpenAI API

**Spec:** `docs/superpowers/specs/2026-04-16-legalboard-improvements-design.md`

---

## File Map

### New files to create

| File | Responsibility |
|---|---|
| `backend/alembic/versions/0010_migrate_to_postgres.py` | Migration: switch to Postgres-compatible types, drop SQLite JSON dialect |
| `backend/alembic/versions/0011_add_third_party_contract_source.py` | Migration: add `third_party_contract` to contract_source enum |
| `backend/alembic/versions/0012_add_contract_embeddings_table.py` | Migration: create `contract_embeddings` table with pgvector extension |
| `backend/app/db/models/embedding.py` | ORM model for `contract_embeddings` |
| `backend/app/infrastructure/embeddings.py` | Embedding generation client (OpenAI text-embedding-3-small) |
| `backend/app/infrastructure/semantic_search.py` | Semantic search service using pgvector cosine similarity |
| `backend/app/api/routes/search.py` | API route `POST /api/search` for semantic search |
| `web/src/features/contracts/components/clause-stepper.tsx` | Stepper component: one clause at a time with prev/next |
| `web/src/features/contracts/components/clause-stepper.module.css` | Styles for clause stepper |
| `web/src/features/dashboard/components/expiring-contracts-table.tsx` | Table of contracts expiring soon with traffic-light urgency |
| `web/src/features/dashboard/components/expiring-contracts-table.module.css` | Styles for expiring contracts table |
| `backend/tests/api/test_search_api.py` | Test for semantic search endpoint |
| `backend/tests/infrastructure/test_embeddings.py` | Test for embedding generation |
| `backend/tests/infrastructure/test_semantic_search.py` | Test for semantic search service |
| `web/src/lib/api/search.ts` | Frontend API client for search |

### Files to modify

| File | Change |
|---|---|
| `backend/app/db/models/contract.py` | Add `third_party_contract` to `ContractSource` enum; replace `from sqlalchemy.dialects.sqlite import JSON` with `from sqlalchemy.dialects.postgresql import JSONB` |
| `backend/app/db/models/analysis.py` | Replace `from sqlalchemy.dialects.sqlite import JSON` with `from sqlalchemy.dialects.postgresql import JSONB` |
| `backend/app/db/models/__init__.py` | Import new `ContractEmbedding` model |
| `backend/app/db/session.py` | Add Postgres connection pool config (pool_size, max_overflow) |
| `backend/app/core/config.py` | Add `embedding_model` setting; make `database_url` point to Postgres |
| `backend/app/core/app_factory.py` | Register search router; seed `third_party_contract` in source enum |
| `backend/app/infrastructure/prompts.py` | Rewrite `SYSTEM_PROMPT` with 9-clause canonical checklist and ordered analysis |
| `backend/app/infrastructure/openai_client.py` | Add `generate_embedding` method |
| `backend/app/application/dashboard.py` | Replace `critical_findings` with `expiring_contracts` list; add urgency classification |
| `backend/app/application/analysis.py` | Add auto-activate for signed contracts after analysis completion |
| `backend/app/schemas/dashboard.py` | Add `ExpiringContractResponse`; replace `critical_findings` with `expiring_contracts` |
| `backend/app/schemas/contract.py` | Add `third_party_contract` source label |
| `backend/app/api/routes/contracts.py` | After analysis stream: auto-activate signed contracts; update compare endpoint to return clause-level findings |
| `backend/.env.example` | Update `DATABASE_URL` to Postgres default |
| `backend/pyproject.toml` | Add `pgvector` dependency; move `aiosqlite` to dev-only |
| `backend/app/api/serializers/contracts.py` | Update source labels mapping |
| `web/src/entities/dashboard/model.ts` | Add `expiring_contracts` to `DashboardSnapshot` type; add `ExpiringContract` type |
| `web/src/features/dashboard/screens/dashboard-screen.tsx` | Replace `EventsTimeline` + `ContractsSummary(critical_findings)` with `ExpiringContractsTable` + compact stats |
| `web/src/features/contracts/screens/contract-detail-screen.tsx` | Replace `version-diff-panel` + `version-history-panel` with `clause-stepper`; conditionally hide suggestions for acervo vs historico |
| `web/src/features/contracts/screens/acervo-screen.tsx` | Hide suggestion fields (suggested_adjustment_direction, risk_explanation) |
| `web/src/features/contracts/screens/historico-screen.tsx` | Show suggestion fields + current state + suggested direction |
| `web/src/lib/api/dashboard.ts` | Update to handle new `expiring_contracts` field |
| `web/src/lib/api/contracts.ts` | Add `searchContracts` function |

### Files to delete

| File | Reason |
|---|---|
| `web/src/features/contracts/components/version-diff-panel.tsx` | Removed per spec — raw text diff no longer needed |
| `web/src/features/contracts/components/version-history-panel.tsx` | Removed per spec — version history removed from UI |

---

## Task 1: Migrate SQLite → PostgreSQL + pgvector

**Goal:** Switch the primary database from SQLite to PostgreSQL with pgvector extension enabled.

**Files:**
- Modify: `backend/app/db/models/contract.py`
- Modify: `backend/app/db/models/analysis.py`
- Modify: `backend/app/db/session.py`
- Modify: `backend/app/core/config.py`
- Modify: `backend/.env.example`
- Modify: `backend/pyproject.toml`
- Create: `backend/alembic/versions/0010_migrate_to_postgres.py`

- [ ] **Step 1: Update pyproject.toml — add pgvector, move aiosqlite to dev**

In `backend/pyproject.toml`, update dependencies:

```toml
dependencies = [
    "fastapi[standard]>=0.115.0",
    "sqlalchemy>=2.0.0",
    "psycopg[binary]>=3.2.0",
    "pgvector>=0.3.0",
    "uvicorn>=0.30.0",
    "python-multipart>=0.0.12",
    "openai>=1.47.0",
    "PyMuPDF>=1.24.0",
    "python-docx>=1.1.0",
    "python-dotenv>=1.0.0",
    "pydantic[email]>=2.9.0",
    "pydantic-settings>=2.6.0",
]

[project.optional-dependencies]
dev = [
  "alembic>=1.16,<2.0",
  "httpx>=0.28,<1.0",
  "pytest>=8.3,<9.0",
  "aiosqlite>=0.20.0",
]
```

- [ ] **Step 2: Replace SQLite JSON with PostgreSQL JSONB in model files**

In `backend/app/db/models/contract.py`, change:
```python
from sqlalchemy.dialects.sqlite import JSON
```
to:
```python
from sqlalchemy.dialects.postgresql import JSONB as JSON
```

In `backend/app/db/models/analysis.py`, make the same replacement.

- [ ] **Step 3: Update session.py with Postgres connection pool**

Replace the entire `backend/app/db/session.py`:

```python
from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker


def create_database_engine(database_url: str, *, echo: bool = False) -> Engine:
    is_postgres = "postgresql" in database_url
    connect_args = {}
    if "sqlite" in database_url:
        connect_args["check_same_thread"] = False

    kwargs: dict = {"echo": echo, "connect_args": connect_args}
    if is_postgres:
        kwargs["pool_size"] = 10
        kwargs["max_overflow"] = 20
        kwargs["pool_pre_ping"] = True

    return create_engine(database_url, **kwargs)


def create_session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


def get_db(session_factory: sessionmaker[Session]) -> Generator[Session, None, None]:
    session = session_factory()
    try:
        yield session
    finally:
        session.close()
```

- [ ] **Step 4: Update .env.example with Postgres default**

In `backend/.env.example`, change:
```
DATABASE_URL=sqlite:///./backend/legaltech.db
```
to:
```
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/legaltech
SQLITE_DATABASE_URL=sqlite:///./backend/legaltech.db
```

- [ ] **Step 5: Create Alembic migration 0010**

Create `backend/alembic/versions/0010_migrate_to_postgres.py`:

```python
"""Migrate to PostgreSQL — enable pgvector, fix JSON columns."""

from alembic import op
import sqlalchemy as sa


def upgrade() -> None:
    bind = op.get_bind()
    dialect = bind.dialect.name

    if dialect == "postgresql":
        op.execute("CREATE EXTENSION IF NOT EXISTS vector")
        op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")

    with op.batch_alter_table("contracts") as batch_op:
        batch_op.alter_column("parties", type_=sa.JSON, existing_type=sa.Text)
        batch_op.alter_column("financial_terms", type_=sa.JSON, existing_type=sa.Text)

    with op.batch_alter_table("contract_versions") as batch_op:
        batch_op.alter_column("extraction_metadata", type_=sa.JSON, existing_type=sa.Text)

    with op.batch_alter_table("contract_analyses") as batch_op:
        batch_op.alter_column("raw_payload", type_=sa.JSON, existing_type=sa.Text)
        batch_op.alter_column("corrections_summary", type_=sa.JSON, existing_type=sa.Text)

    with op.batch_alter_table("contract_analysis_findings") as batch_op:
        batch_op.alter_column("metadata_json", type_=sa.JSON, existing_type=sa.Text)


def downgrade() -> None:
    pass
```

- [ ] **Step 6: Install new dependencies and verify**

Run:
```bash
cd /home/dvdev/projeto-yuann/cloned-repo/backend && source .venv/bin/activate && pip install -e ".[dev]" -q
alembic upgrade head
python -m pytest tests/ -q --tb=short
```

Expected: All existing tests pass (tests still use SQLite for unit tests via config override).

- [ ] **Step 7: Commit**

```bash
git add -A && git commit -m "feat: migrate database from SQLite to PostgreSQL + pgvector"
```

---

## Task 2: Add `third_party_contract` source type

**Goal:** Add the new contract source type to the enum.

**Files:**
- Modify: `backend/app/db/models/contract.py`
- Create: `backend/alembic/versions/0011_add_third_party_contract_source.py`
- Modify: `backend/app/api/serializers/contracts.py`

- [ ] **Step 1: Add enum value**

In `backend/app/db/models/contract.py`, update `ContractSource`:

```python
class ContractSource(str, enum.Enum):
    third_party_draft = "third_party_draft"
    signed_contract = "signed_contract"
    third_party_contract = "third_party_contract"
```

- [ ] **Step 2: Create migration 0011**

Create `backend/alembic/versions/0011_add_third_party_contract_source.py`:

```python
"""Add third_party_contract to contract_source enum."""

from alembic import op


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("ALTER TYPE contract_source ADD VALUE IF NOT EXISTS 'third_party_contract'")


def downgrade() -> None:
    pass
```

- [ ] **Step 3: Update source labels in serializers**

In `backend/app/api/serializers/contracts.py`, find the source labels mapping and add:

```python
SOURCE_LABELS = {
    "third_party_draft": "Minuta de terceiro",
    "signed_contract": "Contrato assinado",
    "third_party_contract": "Contrato de terceiro",
}
```

- [ ] **Step 4: Run tests and commit**

```bash
cd /home/dvdev/projeto-yuann/cloned-repo/backend && source .venv/bin/activate && python -m pytest tests/ -q --tb=short
git add -A && git commit -m "feat: add third_party_contract source type"
```

---

## Task 3: Rewrite analysis prompt with 9-clause canonical checklist

**Goal:** Replace the current analysis prompt with a structured 9-clause checklist based on the franchise legal framework.

**Files:**
- Modify: `backend/app/infrastructure/prompts.py`

- [ ] **Step 1: Write the new SYSTEM_PROMPT**

In `backend/app/infrastructure/prompts.py`, replace the `SYSTEM_PROMPT` with:

```python
CANONICAL_CLAUSES = [
    "OBJETO_E_VIABILIDADE",
    "EXCLUSIVIDADE",
    "OBRAS_E_ADAPTACOES",
    "CESSAO_E_SUBLOCACAO",
    "PRAZO_E_RENOVACAO",
    "COMUNICACAO_E_PENALIDADES",
    "OBRIGACAO_DE_NAO_FAZER",
    "VISTORIA_E_ACESSO",
    "ASSINATURA_E_FORMA",
]

SYSTEM_PROMPT = """Voce e um analista juridico senior de contratos de locacao comercial para franquias de lavanderia self-service no Brasil.

## Idioma e postura
- Responda SOMENTE em PT-BR.
- Seja juridicamente rigoroso e objetivo.
- Nao invente clausulas, fatos, valores ou datas.

## Fontes obrigatorias
- Playbook da franquia enviado no prompt.
- Lei 8.245/1991 (Lei do Inquilinato) como referencia de base juridica.

## Eixo central
O contrato deve viabilizar a implantacao, operacao, permanencia e protecao do ponto comercial para lavanderia self-service.

## Checklist obrigatorio — 9 clausulas canonicas
Voce DEVE analisar o contrato seguindo ESTA ORDEM e produzir UM achado para cada clausula canonica:

1. **OBJETO_E_VIABILIDADE** — O contrato define o objeto e garante viabilidade (agua, esgoto, energia trifasica, fachada, alvaras, CNAE, sem restricao condominial)?
2. **EXCLUSIVIDADE** — Ha clausula de exclusividade intra-ponto que proibe concorrencia direta (lavanderia, passadoria, tinturaria, higienizacao, locker, vending)? Cobertura direta + indireta (mesmo grupo, interpostos)?
3. **OBRAS_E_ADAPTACOES** — Ha autorizacao previa para obras essenciais de implantacao (eletrica trifasica, hidraulica, ventilacao/exaustao, fachada, piso, submedicao)? Respeita obrigatoriedade de tecnico responsavel (ART/RRT)?
4. **CESSAO_E_SUBLOCACAO** — Ha autorizacao expressa para cessao/sublocacao ao franqueado? O locatario permanece responsavel? O destino e preservado? A garantia locaticia tem disciplina clara?
5. **PRAZO_E_RENOVACAO** — Prazo contratual adequado para amortizacao? Renovacao automatica ou mecanismo de continuidade? Disciplina de reajuste no renovado?
6. **COMUNICACAO_E_PENALIDADES** — Comunicacoes por escrito? Multas proporcionais e enforcaveis? Tutela especifica prevista?
7. **OBRIGACAO_DE_NAO_FAZER** — Protecao pos-contratual do ponto? Proibicao de realocacao para atividade concorrente apos distrato ou denuncia? Prazo fixo (24 meses)? Multa nao exime obrigacao?
8. **VISTORIA_E_ACESSO** — Vistoria acompanhada pelo locatario? Aviso previo? Horario comercial? Excecao de emergencia com comunicacao imediata?
9. **ASSINATURA_E_FORMA** — Assinatura e forma previstas? E-assinatura valida? Dispensa de firma reconhecida? Coerencia entre forma contratada e pratica?

## Classificacao por clausula
Para CADA uma das 9 clausulas, atribua UMA classificacao:
- **adequada**: clausula presente, completa, alinhada ao playbook e a Lei 8.245.
- **risco_medio**: clausula presente mas ambigua, incompleta ou com risco operacional moderado.
- **ausente**: clausula essencial nao prevista no contrato.
- **conflitante**: clausula presente mas em conflito direto com o playbook ou a Lei 8.245.

## Ordem obrigatoria de analise
objeto → viabilidade → exclusividade → obras → cessao → estabilidade temporal → comunicacao/penalidades → protecao pos-contrato → assinatura

## Veredito final
Apos analisar as 9 clausulas, emita um veredito: o contrato proporciona seguranca juridico-economica equivalente ao padrao da franquia?

## Regras para os achados
1. Produza EXATAMENTE 9 achados — um por clausula canonica.
2. Cada achado DEVE ter clause_name igual ao nome canonico (ex: OBJETO_E_VIABILIDADE).
3. Cite valores, prazos e termos exatos quando existirem.
4. Se nao houver base para afirmar algo, diga "Nao identificado".
5. Nao use ingles na resposta.
6. Trate cessao, sublocacao, garantia locaticia, benfeitorias e renovacao empresarial como checks juridicos obrigatorios.

## Score
- contract_risk_score: 0 a 100.
- O score e auditavel pelas justificativas dos 9 achados.
- Peso maior: ausencia de exclusividade, cessao sem autorizacao, inviabilidade infraestrutural, sem protecao pos-contrato."""
```

- [ ] **Step 2: Update build_user_prompt to include full playbook text**

In `backend/app/infrastructure/prompts.py`, update `build_user_prompt`:

```python
def build_user_prompt(contract_text: str, playbook: list[PlaybookClause]) -> str:
    clauses_text = "\n".join(
        f"### {c.code} - {c.title}\n{c.full_text}"
        for c in playbook
    )
    return f"""## Clausulas do Playbook da Franquia
{clauses_text}

## Texto do Contrato
{contract_text}

Analise o contrato acima usando o checklist obrigatorio de 9 clausulas canonicas contra o playbook e a Lei 8.245/1991. Produza EXATAMENTE 9 achados, um por clausula canonica, com classificacao (adequada, risco_medio, ausente, conflitante)."""
```

- [ ] **Step 3: Run tests and commit**

```bash
cd /home/dvdev/projeto-yuann/cloned-repo/backend && source .venv/bin/activate && python -m pytest tests/ -q --tb=short
git add -A && git commit -m "feat: rewrite analysis prompt with 9-clause canonical checklist"
```

---

## Task 4: Auto-activate signed contracts → Acervo

**Goal:** When analysis completes for a signed contract, automatically set `is_active = true`.

**Files:**
- Modify: `backend/app/api/routes/contracts.py` — in `_analysis_stream` function

- [ ] **Step 1: Add auto-activate logic after analysis completion**

In `backend/app/api/routes/contracts.py`, inside the `_analysis_stream` function, after `session.commit()` (around line 468), add:

```python
                if contract:
                    source_enum = None
                    for version in contract.versions:
                        if version.id == contract_version_id:
                            source_enum = version.source
                            break
                    if source_enum == ContractSource.signed_contract:
                        contract.is_active = True
                        contract.activated_at = datetime.now(timezone.utc)
                        session.commit()
```

Also add the same logic in the synchronous `analyze_contract` endpoint (around line 298), after `session.commit()`:

```python
    if contract.versions:
        latest_source = latest_contract_version(contract).source if latest_version else None
    else:
        latest_source = None
    if latest_source == ContractSource.signed_contract and not contract.is_active:
        contract.is_active = True
        contract.activated_at = _utcnow()
        session.commit()
        contract = _get_contract_or_404(session, contract_id)
```

- [ ] **Step 2: Run tests and commit**

```bash
cd /home/dvdev/projeto-yuann/cloned-repo/backend && source .venv/bin/activate && python -m pytest tests/ -q --tb=short
git add -A && git commit -m "feat: auto-activate signed contracts into acervo after analysis"
```

---

## Task 5: Replace "Achados Críticos" with "Contratos Próximos do Vencimento"

**Goal:** Dashboard shows expiring contracts table with traffic-light urgency instead of critical findings count.

**Files:**
- Modify: `backend/app/application/dashboard.py`
- Modify: `backend/app/schemas/dashboard.py`
- Modify: `web/src/entities/dashboard/model.ts`
- Modify: `web/src/features/dashboard/screens/dashboard-screen.tsx`
- Create: `web/src/features/dashboard/components/expiring-contracts-table.tsx`
- Create: `web/src/features/dashboard/components/expiring-contracts-table.module.css`
- Modify: `web/src/lib/api/dashboard.ts`

- [ ] **Step 1: Add ExpiringContractResponse to dashboard schema**

In `backend/app/schemas/dashboard.py`, add:

```python
class ExpiringContractResponse(BaseModel):
    id: str
    title: str
    unit: str | None
    source_label: str
    end_date: date | None
    days_remaining: int | None
    urgency_level: str  # "red", "yellow", "green"
```

Update `DashboardSummaryResponse`:

```python
class DashboardSummaryResponse(BaseModel):
    active_contracts: int
    expiring_soon: int
    critical_findings: int  # keep for backward compat, deprecate
```

Update `DashboardSnapshotResponse`:

```python
class DashboardSnapshotResponse(BaseModel):
    summary: DashboardSummaryResponse
    expiring_contracts: list[ExpiringContractResponse]
    events: list[DashboardEventResponse]
    notifications: list[DashboardNotificationResponse]
```

- [ ] **Step 2: Update build_dashboard_snapshot in application/dashboard.py**

In `backend/app/application/dashboard.py`, add expiring contracts logic. After the `operational_contracts` list, add:

```python
    from app.api.serializers.contracts import SOURCE_LABELS

    expiring_contracts: list[ExpiringContractResponse] = []
    for contract in operational_contracts:
        if contract.end_date is None or not contract.is_active:
            continue
        days_remaining = (contract.end_date - reference_date).days
        if days_remaining > 365:
            continue
        if days_remaining < 30:
            urgency = "red"
        elif days_remaining < 90:
            urgency = "yellow"
        else:
            urgency = "green"
        unit = None
        if contract.parties and isinstance(contract.parties, dict):
            unit = contract.parties.get("locatario") or contract.parties.get("locatário")
        source_label = SOURCE_LABELS.get(
            contract.versions[0].source.value if contract.versions else "",
            contract.versions[0].source.value if contract.versions else "",
        ) if contract.versions else ""
        expiring_contracts.append(
            ExpiringContractResponse(
                id=contract.id,
                title=contract.title,
                unit=unit,
                source_label=source_label,
                end_date=contract.end_date,
                days_remaining=days_remaining,
                urgency_level=urgency,
            )
        )
    expiring_contracts.sort(key=lambda c: (c.days_remaining or 999999))
```

Then update the return statement:

```python
    return DashboardSnapshotResponse(
        summary=DashboardSummaryResponse(
            active_contracts=active_contracts,
            critical_findings=critical_findings,
            expiring_soon=len(event_items),
        ),
        expiring_contracts=expiring_contracts[:10],
        events=event_items,
        notifications=notification_items,
    )
```

- [ ] **Step 3: Run backend tests**

```bash
cd /home/dvdev/projeto-yuann/cloned-repo/backend && source .venv/bin/activate && python -m pytest tests/ -q --tb=short
```

- [ ] **Step 4: Update frontend dashboard model**

In `web/src/entities/dashboard/model.ts`, add:

```typescript
export type ExpiringContract = {
  id: string;
  title: string;
  unit: string | null;
  source_label: string;
  end_date: string | null;
  days_remaining: number | null;
  urgency_level: "red" | "yellow" | "green";
};
```

Update `DashboardSnapshot` type to include:
```typescript
  expiring_contracts: ExpiringContract[];
```

- [ ] **Step 5: Create ExpiringContractsTable component**

Create `web/src/features/dashboard/components/expiring-contracts-table.tsx`:

```tsx
"use client";

import React from "react";
import type { ExpiringContract } from "../../../entities/dashboard/model";
import styles from "./expiring-contracts-table.module.css";

type Props = {
  contracts: ExpiringContract[];
};

function formatDaysRemaining(days: number | null): string {
  if (days === null) return "—";
  if (days < 0) return `Vencido há ${Math.abs(days)} dias`;
  if (days === 0) return "Vence hoje";
  return `${days} dias`;
}

function urgencyLabel(level: string): string {
  if (level === "red") return "Urgente";
  if (level === "yellow") return "Atenção";
  return "Normal";
}

export function ExpiringContractsTable({ contracts }: Props) {
  if (!contracts.length) {
    return <p className={styles.empty}>Nenhum contrato próximo do vencimento.</p>;
  }

  return (
    <table className={styles.table}>
      <thead>
        <tr>
          <th>Contrato</th>
          <th>Unidade</th>
          <th>Tipo</th>
          <th>Vencimento</th>
          <th>Prazo</th>
          <th>Urgência</th>
        </tr>
      </thead>
      <tbody>
        {contracts.map((c) => (
          <tr key={c.id} className={styles[`urgency-${c.urgency_level}`]}>
            <td className={styles.contractTitle}>{c.title}</td>
            <td>{c.unit || "—"}</td>
            <td>{c.source_label}</td>
            <td>{c.end_date || "—"}</td>
            <td className={styles.daysRemaining}>{formatDaysRemaining(c.days_remaining)}</td>
            <td>
              <span className={`${styles.badge} ${styles[`badge-${c.urgency_level}`]}`}>
                {urgencyLabel(c.urgency_level)}
              </span>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
```

Create `web/src/features/dashboard/components/expiring-contracts-table.module.css`:

```css
.empty {
  color: var(--color-text-muted);
  font-style: italic;
  text-align: center;
  padding: 1rem;
}

.table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
}

.table th {
  text-align: left;
  padding: 0.5rem 0.75rem;
  font-weight: 600;
  color: var(--color-text-muted);
  border-bottom: 1px solid var(--color-border);
}

.table td {
  padding: 0.625rem 0.75rem;
  border-bottom: 1px solid var(--color-border);
}

.urgency-red {
  background: color-mix(in srgb, var(--color-red) 8%, transparent);
}

.urgency-yellow {
  background: color-mix(in srgb, var(--color-yellow) 6%, transparent);
}

.contractTitle {
  font-weight: 500;
}

.daysRemaining {
  font-variant-numeric: tabular-nums;
  white-space: nowrap;
}

.badge {
  display: inline-block;
  padding: 0.15rem 0.5rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
}

.badge-red {
  background: color-mix(in srgb, var(--color-red) 15%, transparent);
  color: var(--color-red);
}

.badge-yellow {
  background: color-mix(in srgb, var(--color-yellow) 15%, transparent);
  color: var(--color-yellow);
}

.badge-green {
  background: color-mix(in srgb, var(--color-green) 15%, transparent);
  color: var(--color-green);
}
```

- [ ] **Step 6: Update dashboard-screen.tsx**

In `web/src/features/dashboard/screens/dashboard-screen.tsx`:

Remove the import and usage of `EventsTimeline` from the dashboard. Replace the detail grid with the expiring contracts table:

```tsx
import { ExpiringContractsTable } from "../components/expiring-contracts-table";
// Remove: import { EventsTimeline } from "../components/events-timeline";
```

Replace the detail grid section:
```tsx
          <div className={styles.detailGrid}>
            <SurfaceCard title="Contratos próximos do vencimento">
              <ExpiringContractsTable contracts={snapshot.expiring_contracts} />
            </SurfaceCard>

            <SurfaceCard title="Histórico de notificações">
              <NotificationHistory items={snapshot.notifications} showTitle={false} />
            </SurfaceCard>
          </div>
```

- [ ] **Step 7: Run frontend build and commit**

```bash
cd /home/dvdev/projeto-yuann/cloned-repo/web && npm run build && npm run test
git add -A && git commit -m "feat: replace Achados Críticos with expiring contracts table on dashboard"
```

---

## Task 6: Create Clause Stepper component

**Goal:** Replace version-diff-panel with a clause-by-clause stepper for analysis findings.

**Files:**
- Create: `web/src/features/contracts/components/clause-stepper.tsx`
- Create: `web/src/features/contracts/components/clause-stepper.module.css`
- Modify: `web/src/features/contracts/screens/contract-detail-screen.tsx`

- [ ] **Step 1: Create ClauseStepper component**

Create `web/src/features/contracts/components/clause-stepper.tsx`:

```tsx
"use client";

import React, { useState } from "react";
import styles from "./clause-stepper.module.css";

export type ClauseFinding = {
  clause_name: string;
  classification: string;
  status: string;
  current_summary: string;
  policy_rule: string;
  risk_explanation: string;
  suggested_adjustment_direction: string;
};

type Props = {
  findings: ClauseFinding[];
};

function statusLabel(status: string): string {
  if (status === "critical") return "Crítico";
  if (status === "attention") return "Atenção";
  if (status === "conforme" || status === "adequada") return "Conforme";
  return status;
}

function classificationLabel(cls: string): string {
  if (cls === "adequada") return "Adequada";
  if (cls === "risco_medio") return "Risco médio";
  if (cls === "ausente") return "Ausente";
  if (cls === "conflitante") return "Conflitante";
  return cls;
}

function clauseDisplayName(code: string): string {
  const names: Record<string, string> = {
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
  return names[code] || code;
}

export function ClauseStepper({ findings }: Props) {
  const [index, setIndex] = useState(0);
  const finding = findings[index];
  if (!finding) return null;

  const total = findings.length;
  const criticals = findings.filter((f) => f.status === "critical").length;
  const attentions = findings.filter((f) => f.status === "attention").length;
  const conforme = total - criticals - attentions;

  return (
    <div className={styles.stepper}>
      <div className={styles.header}>
        <span className={styles.counter}>{criticals} críticos · {attentions} atenção · {conforme} conforme</span>
        <span className={styles.pagination}>Cláusula {index + 1} de {total}</span>
      </div>

      <div className={styles.clauseCard}>
        <div className={styles.clauseHeader}>
          <h3 className={styles.clauseTitle}>{clauseDisplayName(finding.clause_name)}</h3>
          <span className={`${styles.classification} ${styles[`cls-${finding.classification}`]}`}>
            {classificationLabel(finding.classification)}
          </span>
        </div>

        <div className={styles.clauseBody}>
          <div className={styles.field}>
            <strong>Texto atual:</strong>
            <p>{finding.current_summary}</p>
          </div>
          <div className={styles.field}>
            <strong>Regra da policy:</strong>
            <p>{finding.policy_rule}</p>
          </div>
          {(finding.status === "critical" || finding.status === "attention") && (
            <>
              <div className={styles.field}>
                <strong>Explicação do risco:</strong>
                <p className={styles.riskText}>{finding.risk_explanation}</p>
              </div>
              {finding.suggested_adjustment_direction && (
                <div className={styles.field}>
                  <strong>Direção sugerida:</strong>
                  <p className={styles.suggestionText}>{finding.suggested_adjustment_direction}</p>
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
          onClick={() => setIndex((i) => i - 1)}
          type="button"
        >
          ← Anterior
        </button>
        <div className={styles.dots}>
          {findings.map((f, i) => (
            <button
              key={f.clause_name}
              className={`${styles.dot} ${i === index ? styles.dotActive : ""} ${styles[`dot-${f.status}`]}`}
              onClick={() => setIndex(i)}
              type="button"
              aria-label={`Cláusula ${i + 1}: ${clauseDisplayName(f.clause_name)}`}
            />
          ))}
        </div>
        <button
          className={styles.navButton}
          disabled={index === total - 1}
          onClick={() => setIndex((i) => i + 1)}
          type="button"
        >
          Próximo →
        </button>
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Create clause-stepper.module.css**

Create `web/src/features/contracts/components/clause-stepper.module.css`:

```css
.stepper {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.875rem;
  color: var(--color-text-muted);
}

.counter {
  font-weight: 500;
}

.pagination {
  font-variant-numeric: tabular-nums;
}

.clauseCard {
  padding: 1.25rem;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 0.75rem;
}

.clauseHeader {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid var(--color-border);
}

.clauseTitle {
  font-size: 1.125rem;
  font-weight: 600;
  margin: 0;
}

.classification {
  display: inline-block;
  padding: 0.2rem 0.625rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
}

.cls-adequada {
  background: color-mix(in srgb, var(--color-green) 15%, transparent);
  color: var(--color-green);
}

.cls-risco_medio {
  background: color-mix(in srgb, var(--color-yellow) 15%, transparent);
  color: var(--color-yellow);
}

.cls-ausente {
  background: color-mix(in srgb, var(--color-red) 15%, transparent);
  color: var(--color-red);
}

.cls-conflitante {
  background: color-mix(in srgb, var(--color-red) 20%, transparent);
  color: var(--color-red);
}

.clauseBody {
  display: flex;
  flex-direction: column;
  gap: 0.875rem;
}

.field strong {
  display: block;
  font-size: 0.8125rem;
  color: var(--color-text-muted);
  margin-bottom: 0.25rem;
}

.field p {
  margin: 0;
  font-size: 0.9375rem;
  line-height: 1.5;
}

.riskText {
  color: var(--color-red);
}

.suggestionText {
  color: var(--color-green);
}

.nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.navButton {
  padding: 0.5rem 1rem;
  border: 1px solid var(--color-border);
  border-radius: 0.5rem;
  background: var(--color-surface);
  cursor: pointer;
  font-size: 0.875rem;
}

.navButton:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.navButton:not(:disabled):hover {
  background: var(--color-border);
}

.dots {
  display: flex;
  gap: 0.375rem;
}

.dot {
  width: 0.5rem;
  height: 0.5rem;
  border-radius: 9999px;
  border: none;
  padding: 0;
  cursor: pointer;
  background: var(--color-border);
}

.dotActive {
  transform: scale(1.4);
}

.dot-critical {
  background: var(--color-red);
}

.dot-attention {
  background: var(--color-yellow);
}
```

- [ ] **Step 3: Wire ClauseStepper into contract-detail-screen.tsx**

In `web/src/features/contracts/screens/contract-detail-screen.tsx`:
- Remove imports for `VersionDiffPanel` and `VersionHistoryPanel`
- Add import for `ClauseStepper`
- Replace the section that renders `VersionDiffPanel` with `ClauseStepper` using the analysis findings data
- Add `isAcervo` prop to conditionally hide suggestions

- [ ] **Step 4: Run frontend build and commit**

```bash
cd /home/dvdev/projeto-yuann/cloned-repo/web && npm run build && npm run test
git add -A && git commit -m "feat: add clause stepper component for one-clause-at-a-time analysis"
```

---

## Task 7: Remove version-diff-panel, version-history-panel, and dashboard timeline

**Goal:** Remove components that are no longer needed per spec.

**Files:**
- Delete: `web/src/features/contracts/components/version-diff-panel.tsx`
- Delete: `web/src/features/contracts/components/version-history-panel.tsx`
- Modify: `web/src/features/contracts/screens/contract-detail-screen.tsx` — remove imports
- Modify: `web/src/features/dashboard/screens/dashboard-screen.tsx` — remove EventsTimeline (already done in Task 5)

- [ ] **Step 1: Delete version-diff-panel.tsx and version-history-panel.tsx**

```bash
rm web/src/features/contracts/components/version-diff-panel.tsx
rm web/src/features/contracts/components/version-history-panel.tsx
```

- [ ] **Step 2: Remove all references to deleted components**

Search for any remaining imports of `version-diff-panel` or `version-history-panel` across the codebase and remove them. Update test files that reference these components.

- [ ] **Step 3: Run frontend build and commit**

```bash
cd /home/dvdev/projeto-yuann/cloned-repo/web && npm run build && npm run test
git add -A && git commit -m "chore: remove version-diff-panel and version-history-panel from UI"
```

---

## Task 8: Differentiate Acervo (no suggestions) vs Histórico (with suggestions)

**Goal:** Acervo shows raw documental content. Histórico shows analytical content with suggestions.

**Files:**
- Modify: `web/src/features/contracts/screens/acervo-screen.tsx`
- Modify: `web/src/features/contracts/screens/historico-screen.tsx`
- Modify: `web/src/features/contracts/screens/contract-detail-screen.tsx`

- [ ] **Step 1: Update contract detail screen with context prop**

In `web/src/features/contracts/screens/contract-detail-screen.tsx`, add a `context` prop:

```tsx
type ContractDetailScreenProps = {
  contractId: string;
  context?: "acervo" | "historico" | "contracts";
};
```

When `context === "acervo"`, hide `risk_explanation` and `suggested_adjustment_direction` fields in the ClauseStepper.

When `context === "historico"`, show all fields including situacao atual + direcao sugerida.

- [ ] **Step 2: Pass context from acervo/historico route pages**

In the Next.js route pages for `/acervo/[contractId]` and `/historico/[contractId]`, pass the appropriate context prop to the contract detail screen.

- [ ] **Step 3: Update acervo-screen.tsx**

In `web/src/features/contracts/screens/acervo-screen.tsx`, ensure findings display only shows: clause name + classification + current_summary (no suggestions, no risk explanation).

- [ ] **Step 4: Run frontend build and commit**

```bash
cd /home/dvdev/projeto-yuann/cloned-repo/web && npm run build && npm run test
git add -A && git commit -m "feat: differentiate acervo (documental) vs historico (analytical) views"
```

---

## Task 9: Create contract_embeddings table and embedding infrastructure

**Goal:** Add pgvector-backed table and embedding generation for semantic search.

**Files:**
- Create: `backend/alembic/versions/0012_add_contract_embeddings_table.py`
- Create: `backend/app/db/models/embedding.py`
- Modify: `backend/app/db/models/__init__.py`
- Create: `backend/app/infrastructure/embeddings.py`
- Create: `backend/tests/infrastructure/test_embeddings.py`

- [ ] **Step 1: Create ContractEmbedding ORM model**

Create `backend/app/db/models/embedding.py`:

```python
from __future__ import annotations

from typing import Any
from uuid import uuid4

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from pgvector.sqlalchemy import Vector

from app.db.base import Base, TimestampMixin


class ContractEmbedding(TimestampMixin, Base):
    __tablename__ = "contract_embeddings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    contract_id: Mapped[str] = mapped_column(
        ForeignKey("contracts.id", ondelete="CASCADE"), nullable=False
    )
    chunk_type: Mapped[str] = mapped_column(String(50), nullable=False)
    chunk_text: Mapped[str] = mapped_column(Text, nullable=False)
    embedding = mapped_column(Vector(1536), nullable=False)
    metadata_json: Mapped[dict[str, Any] | None] = mapped_column(JSONB)

    contract: Mapped["Contract"] = relationship(back_populates="embeddings")
```

- [ ] **Step 2: Register in __init__.py**

In `backend/app/db/models/__init__.py`, add:

```python
from app.db.models.embedding import ContractEmbedding
```

- [ ] **Step 3: Add embeddings relationship to Contract model**

In `backend/app/db/models/contract.py`, add to the `Contract` class:

```python
    embeddings: Mapped[list["ContractEmbedding"]] = relationship(
        back_populates="contract",
        cascade="all, delete-orphan",
    )
```

Add the import at the top (using TYPE_CHECKING to avoid circular imports).

- [ ] **Step 4: Create migration 0012**

Create `backend/alembic/versions/0012_add_contract_embeddings_table.py`:

```python
"""Add contract_embeddings table with pgvector."""

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "contract_embeddings",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("contract_id", sa.String(36), sa.ForeignKey("contracts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("chunk_type", sa.String(50), nullable=False),
        sa.Column("chunk_text", sa.Text, nullable=False),
        sa.Column("embedding", Vector(1536), nullable=False),
        sa.Column("metadata_json", sa.JSON),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    if bind.dialect.name == "postgresql":
        op.create_index(
            "ix_contract_embeddings_hnsw",
            "contract_embeddings",
            ["embedding"],
            postgresql_using="hnsw",
            postgresql_with={"m": 16, "ef_construction": 64},
            postgresql_ops={"embedding": "vector_cosine_ops"},
        )
        op.create_index(
            "ix_contract_embeddings_contract_id",
            "contract_embeddings",
            ["contract_id"],
        )


def downgrade() -> None:
    bind = op.get_bind()
    op.drop_index("ix_contract_embeddings_hnsw")
    op.drop_index("ix_contract_embeddings_contract_id")
    op.drop_table("contract_embeddings")
```

- [ ] **Step 5: Create embedding generation service**

Create `backend/app/infrastructure/embeddings.py`:

```python
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

try:
    import openai
except ImportError:
    openai = None

logger = logging.getLogger(__name__)

EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIMENSIONS = 1536


class EmbeddingClient:
    def __init__(self, api_key: str, model: str = EMBEDDING_MODEL) -> None:
        self._api_key = api_key
        self._model = model
        if openai is None:
            self._client = None
            logger.warning("openai package not installed — embeddings unavailable")
            return
        self._client = openai.OpenAI(api_key=api_key)

    def generate_embedding(self, text: str) -> list[float] | None:
        if not self._client:
            return None
        try:
            response = self._client.embeddings.create(
                model=self._model,
                input=text,
                dimensions=EMBEDDING_DIMENSIONS,
            )
            return response.data[0].embedding
        except Exception:
            logger.exception("Embedding generation failed")
            return None

    def generate_embeddings(self, texts: list[str]) -> list[list[float] | None]:
        if not self._client:
            return [None] * len(texts)
        try:
            response = self._client.embeddings.create(
                model=self._model,
                input=texts,
                dimensions=EMBEDDING_DIMENSIONS,
            )
            return [item.embedding for item in response.data]
        except Exception:
            logger.exception("Batch embedding generation failed")
            return [None] * len(texts)
```

- [ ] **Step 6: Write test for EmbeddingClient**

Create `backend/tests/infrastructure/test_embeddings.py`:

```python
from app.infrastructure.embeddings import EmbeddingClient


def test_embedding_client_returns_none_without_openai():
    client = EmbeddingClient(api_key="fake")
    if client._client is None:
        result = client.generate_embedding("test text")
        assert result is None


def test_embedding_client_batch_returns_none_without_openai():
    client = EmbeddingClient(api_key="fake")
    if client._client is None:
        result = client.generate_embeddings(["text 1", "text 2"])
        assert all(r is None for r in result)
```

- [ ] **Step 7: Install pgvector and run tests**

```bash
cd /home/dvdev/projeto-yuann/cloned-repo/backend && source .venv/bin/activate && pip install -e ".[dev]" -q && python -m pytest tests/ -q --tb=short
git add -A && git commit -m "feat: add contract_embeddings table with pgvector and embedding client"
```

---

## Task 10: Create semantic search endpoint

**Goal:** Add `POST /api/search` for semantic search across contract findings and summaries.

**Files:**
- Create: `backend/app/infrastructure/semantic_search.py`
- Create: `backend/app/api/routes/search.py`
- Modify: `backend/app/core/app_factory.py` — register search router
- Create: `backend/tests/api/test_search_api.py`
- Create: `web/src/lib/api/search.ts`

- [ ] **Step 1: Create semantic search service**

Create `backend/app/infrastructure/semantic_search.py`:

```python
from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.infrastructure.embeddings import EmbeddingClient


@dataclass
class SearchResult:
    contract_id: str
    contract_title: str
    chunk_type: str
    chunk_text: str
    similarity_score: float


def search_similar_contracts(
    *,
    session: Session,
    query_embedding: list[float],
    limit: int = 10,
    min_similarity: float = 0.5,
) -> list[SearchResult]:
    embedding_str = "[" + ",".join(str(v) for v in query_embedding) + "]"

    results = session.execute(
        text("""
            SELECT
                ce.contract_id,
                c.title AS contract_title,
                ce.chunk_type,
                ce.chunk_text,
                1 - (ce.embedding <=> :query_embedding::vector) AS similarity
            FROM contract_embeddings ce
            JOIN contracts c ON c.id = ce.contract_id
            WHERE 1 - (ce.embedding <=> :query_embedding::vector) > :min_similarity
            ORDER BY ce.embedding <=> :query_embedding::vector
            LIMIT :limit
        """),
        {
            "query_embedding": embedding_str,
            "min_similarity": min_similarity,
            "limit": limit,
        },
    ).fetchall()

    return [
        SearchResult(
            contract_id=row.contract_id,
            contract_title=row.contract_title,
            chunk_type=row.chunk_type,
            chunk_text=row.chunk_text,
            similarity_score=float(row.similarity),
        )
        for row in results
    ]
```

- [ ] **Step 2: Create search API route**

Create `backend/app/api/routes/search.py`:

```python
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.dependencies import get_session
from app.infrastructure.embeddings import EmbeddingClient
from app.infrastructure.semantic_search import SearchResult, search_similar_contracts

router = APIRouter(prefix="/api/search", tags=["search"])


class SearchRequest(BaseModel):
    query: str
    limit: int = 10
    min_similarity: float = 0.5


class SearchResponseItem(BaseModel):
    contract_id: str
    contract_title: str
    chunk_type: str
    chunk_text: str
    similarity_score: float


class SearchResponse(BaseModel):
    results: list[SearchResponseItem]


@router.post("", response_model=SearchResponse)
def search_contracts(
    payload: SearchRequest,
    session: Session = Depends(get_session),
) -> SearchResponse:
    from app.core.app_factory import get_embedding_client

    embedding_client = get_embedding_client()
    if embedding_client is None:
        raise HTTPException(status_code=503, detail="Embedding service not configured")

    query_embedding = embedding_client.generate_embedding(payload.query)
    if query_embedding is None:
        raise HTTPException(status_code=503, detail="Failed to generate query embedding")

    results = search_similar_contracts(
        session=session,
        query_embedding=query_embedding,
        limit=payload.limit,
        min_similarity=payload.min_similarity,
    )

    return SearchResponse(
        results=[
            SearchResponseItem(
                contract_id=r.contract_id,
                contract_title=r.contract_title,
                chunk_type=r.chunk_type,
                chunk_text=r.chunk_text,
                similarity_score=r.similarity_score,
            )
            for r in results
        ]
    )
```

- [ ] **Step 3: Register search router in app_factory.py**

In `backend/app/core/app_factory.py`, add:

```python
from app.api.routes.search import router as search_router
# ...
app.include_router(search_router)
```

Also add `get_embedding_client` function:

```python
_embedding_client: EmbeddingClient | None = None

def get_embedding_client() -> EmbeddingClient | None:
    return _embedding_client
```

Initialize it in the app factory setup when `OPENAI_API_KEY` is present.

- [ ] **Step 4: Create frontend search API client**

Create `web/src/lib/api/search.ts`:

```typescript
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export type SearchResult = {
  contract_id: string;
  contract_title: string;
  chunk_type: string;
  chunk_text: string;
  similarity_score: number;
};

export type SearchResponse = {
  results: SearchResult[];
};

export async function searchContracts(
  query: string,
  limit: number = 10,
): Promise<SearchResponse> {
  const res = await fetch(`${API_URL}/api/search`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, limit }),
  });
  if (!res.ok) throw new Error("Search failed");
  return res.json();
}
```

- [ ] **Step 5: Run tests and commit**

```bash
cd /home/dvdev/projeto-yuann/cloned-repo/backend && source .venv/bin/activate && python -m pytest tests/ -q --tb=short
cd /home/dvdev/projeto-yuann/cloned-repo/web && npm run build
git add -A && git commit -m "feat: add semantic search endpoint with pgvector"
```

---

## Task 11: Performance optimizations

**Goal:** Add database indexes, connection pooling, and frontend lazy loading.

**Files:**
- Modify: `backend/app/db/session.py` — already done in Task 1 (pool_size, max_overflow)
- Create: `backend/alembic/versions/0013_add_performance_indexes.py`
- Modify: `web/src/features/dashboard/screens/dashboard-screen.tsx` — React.lazy
- Modify: `web/src/features/contracts/screens/contracts-screen.tsx` — React.memo on list items

- [ ] **Step 1: Create migration for performance indexes**

Create `backend/alembic/versions/0013_add_performance_indexes.py`:

```python
"""Add performance indexes for common queries."""

from alembic import op


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.create_index("ix_contracts_end_date", "contracts", ["end_date"])
        op.create_index("ix_contracts_is_active", "contracts", ["is_active"])
        op.create_index("ix_contracts_status", "contracts", ["status"])
        op.create_index(
            "ix_contracts_active_end_date",
            "contracts",
            ["is_active", "end_date"],
            postgresql_where=op.text("is_active = true AND end_date IS NOT NULL"),
        )
        op.create_index("ix_contract_events_event_date", "contract_events", ["event_date"])


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.drop_index("ix_contracts_end_date")
        op.drop_index("ix_contracts_is_active")
        op.drop_index("ix_contracts_status")
        op.drop_index("ix_contracts_active_end_date")
        op.drop_index("ix_contract_events_event_date")
```

- [ ] **Step 2: Add React.lazy for dashboard screens**

In `web/src/app/(app)/dashboard/page.tsx`, wrap the dashboard screen with React.lazy:

```tsx
import dynamic from "next/dynamic";

const DashboardScreen = dynamic(
  () => import("../../../features/dashboard/screens/dashboard-screen").then((m) => m.DashboardScreen),
  { ssr: false },
);
```

- [ ] **Step 3: Run tests and commit**

```bash
cd /home/dvdev/projeto-yuann/cloned-repo/backend && source .venv/bin/activate && python -m pytest tests/ -q --tb=short
cd /home/dvdev/projeto-yuann/cloned-repo/web && npm run build && npm run test
git add -A && git commit -m "perf: add database indexes, connection pooling, and frontend lazy loading"
```

---

## Task 12: Index contract analysis results as embeddings

**Goal:** After analysis completes, generate embeddings for findings and summary so they're searchable.

**Files:**
- Modify: `backend/app/api/routes/contracts.py` — in `_analysis_stream` and `analyze_contract`

- [ ] **Step 1: Add embedding generation after analysis completion**

In `backend/app/api/routes/contracts.py`, inside `_analysis_stream`, after the analysis is saved to the database, add embedding generation:

```python
                embedding_client = getattr(request.app.state, "embedding_client", None) if hasattr(request, "app") else None
                if embedding_client:
                    try:
                        from app.db.models.embedding import ContractEmbedding
                        for finding in analysis.findings:
                            chunk_text = f"{finding.clause_name}: {finding.current_summary}"
                            emb = embedding_client.generate_embedding(chunk_text)
                            if emb:
                                session.add(ContractEmbedding(
                                    contract_id=contract.id,
                                    chunk_type="finding_summary",
                                    chunk_text=chunk_text,
                                    embedding=emb,
                                    metadata_json={"clause_name": finding.clause_name, "severity": finding.severity},
                                ))
                        session.commit()
                    except Exception:
                        logger.exception("Failed to index embeddings")
```

- [ ] **Step 2: Run tests and commit**

```bash
cd /home/dvdev/projeto-yuann/cloned-repo/backend && source .venv/bin/activate && python -m pytest tests/ -q --tb=short
git add -A && git commit -m "feat: index analysis findings as embeddings for semantic search"
```

---

## Verification checklist (run after all tasks)

- [ ] Backend: `cd backend && python -m pytest tests/ -q` — all pass
- [ ] Frontend: `cd web && npm run build` — no errors
- [ ] Frontend: `cd web && npm run test` — all pass
- [ ] Dashboard: no timeline, no "Achados Críticos" — shows expiring contracts table
- [ ] Contract detail: ClauseStepper renders, no version-diff-panel
- [ ] Acervo: no suggestions shown
- [ ] Histórico: suggestions shown
- [ ] `POST /api/search` returns results (with embeddings indexed)
- [ ] `third_party_contract` source type available in dropdowns
- [ ] Signed contracts auto-activate to acervo after analysis