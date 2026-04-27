# LegalTech Consultiva + RBAC Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reescopar LegalTech de interpretativa (LLM) para consultiva (apenas extração de cláusulas + info do contrato), adicionando RBAC com admin e user.

**Architecture:** Hard remove de todos os módulos LLM/análise. Novo módulo de extração de cláusulas por regex sobre texto OCR. RBAC via campo `role` em `users`. Ownership via `contracts.owner_id`. Admin cria contas e vê tudo; user vê só seus contratos.

**Tech Stack:** Python (FastAPI, SQLAlchemy, Alembic), TypeScript (Next.js, React), PostgreSQL/SQLite

---

## File Structure

### Backend
- `app/db/models/user.py` — adiciona `role`
- `app/db/models/contract.py` — adiciona `owner_id`
- `app/db/models/analysis.py` — remove tabelas de análise
- `app/db/models/__init__.py` — atualiza exports
- `app/domain/clause_extraction.py` — novo: regex extraction de cláusulas
- `app/api/dependencies.py` — adiciona `require_admin`
- `app/api/routes/auth.py` — retorna `role`, register restrito a admin
- `app/api/routes/admin.py` — novo: gerenciamento de usuários
- `app/api/routes/contracts.py` — remove endpoints de análise/correção/diff, adiciona filtro owner
- `app/api/routes/dashboard.py` — adiciona filtro owner
- `app/application/contract_pipeline.py` — remove LLM, adiciona extração de cláusulas
- `app/application/dashboard.py` — remove métricas de análise, adiciona filtro owner
- `app/core/app_factory.py` — remove search router, LLM client, embedding client
- `alembic/versions/0014_consultative_rbac.py` — migração

### Frontend
- `src/lib/api/auth.ts` — adiciona `role` aos types
- `src/contexts/auth-context.tsx` — expõe `role`
- `src/components/navigation/app-shell.tsx` — menu condicional admin/user
- `src/features/contracts/screens/contract-detail-screen.tsx` — remove análise/score, adiciona cláusulas extraídas
- `src/features/admin/screens/admin-users-screen.tsx` — novo: tela admin
- `src/app/(app)/admin/usuarios/page.tsx` — nova rota

---

## Task 1: Database Migration — RBAC + Ownership + Drop Analysis

**Files:**
- Create: `backend/alembic/versions/0014_consultative_rbac.py`
- Modify: `backend/app/db/models/user.py`
- Modify: `backend/app/db/models/contract.py`
- Modify: `backend/app/db/models/analysis.py`
- Modify: `backend/app/db/models/__init__.py`

- [ ] **Step 1: Add role to User model**

```python
# backend/app/db/models/user.py
import enum
from sqlalchemy import String

class UserRole(str, enum.Enum):
    admin = "admin"
    user = "user"

class User(TimestampMixin, Base):
    __tablename__ = "users"
    # ... existing fields ...
    role: Mapped[str] = mapped_column(String(20), nullable=False, default=UserRole.user)
```

- [ ] **Step 2: Add owner_id to Contract model**

```python
# backend/app/db/models/contract.py
from sqlalchemy import ForeignKey

class Contract(TimestampMixin, Base):
    __tablename__ = "contracts"
    # ... existing fields ...
    owner_id: Mapped[str | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
```

- [ ] **Step 3: Remove analysis models**

```python
# backend/app/db/models/analysis.py
# Delete entire file content, keep empty file or remove imports from __init__.py
# Tables to drop: contract_analyses, contract_analysis_findings
```

- [ ] **Step 4: Update __init__.py exports**

```python
# backend/app/db/models/__init__.py
# Remove: AnalysisStatus, ContractAnalysis, ContractAnalysisFinding
__all__ = [
    "Contract",
    "ContractEmbedding",
    "ContractEvent",
    "ContractSource",
    "ContractVersion",
    "EventType",
    "Notification",
    "NotificationChannel",
    "Policy",
    "PolicyRule",
    "User",
]
```

- [ ] **Step 5: Write Alembic migration**

```python
# backend/alembic/versions/0014_consultative_rbac.py
from alembic import op
import sqlalchemy as sa

revision = "0014"
down_revision = "0013"

def upgrade():
    op.add_column("users", sa.Column("role", sa.String(20), nullable=False, server_default="user"))
    op.add_column("contracts", sa.Column("owner_id", sa.String(36), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True))
    op.create_index("idx_contracts_owner_id", "contracts", ["owner_id"])
    op.drop_table("contract_analysis_findings")
    op.drop_table("contract_analyses")

def downgrade():
    op.drop_column("contracts", "owner_id")
    op.drop_column("users", "role")
    # Recriar tabelas de análise se necessário (omissão aceitável para downgrade)
```

- [ ] **Step 6: Run migration**

```bash
cd backend && alembic upgrade head
```

- [ ] **Step 7: Commit**

```bash
git add backend/app/db/models/ backend/alembic/versions/
git commit -m "feat: add rbac role and contract ownership, drop analysis tables"
```

---

## Task 2: Clause Extraction Module

**Files:**
- Create: `backend/app/domain/clause_extraction.py`
- Create: `backend/tests/test_clause_extraction.py`

- [ ] **Step 1: Write failing test**

```python
# backend/tests/test_clause_extraction.py
from app.domain.clause_extraction import extract_clauses, ClauseItem

def test_extract_clauses_basic():
    text = """
    CLÁUSULA 1 - OBJETO
    O objeto do presente contrato é a locação do imóvel.
    CLÁUSULA 2 - PRAZO
    O prazo de vigência é de 60 meses.
    """
    clauses = extract_clauses(text)
    assert len(clauses) == 2
    assert clauses[0].title == "OBJETO"
    assert "locação" in clauses[0].content
    assert clauses[1].title == "PRAZO"
    assert "60 meses" in clauses[1].content
```

- [ ] **Step 2: Run test to verify failure**

```bash
cd backend && pytest tests/test_clause_extraction.py -v
```
Expected: FAIL — `extract_clauses` not defined

- [ ] **Step 3: Implement clause extraction**

```python
# backend/app/domain/clause_extraction.py
from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class ClauseItem:
    title: str
    content: str
    order_index: int


CLAUSE_PATTERNS = [
    re.compile(r"CLÁUSULA\s+(\d+)ª?\s*[-–—]\s*(.+)", re.IGNORECASE),
    re.compile(r"Art\.?\s*(\d+)º?\s*[-–—.]\s*(.+)", re.IGNORECASE),
    re.compile(r"^(\d+)\.\s+([A-Z][A-Z\s]+)$", re.MULTILINE),
    re.compile(r"^(CLÁUSULA|ARTIGO)\s+(.+)$", re.IGNORECASE | re.MULTILINE),
]


def extract_clauses(contract_text: str) -> list[ClauseItem]:
    text = contract_text.replace("\r\n", "\n").replace("\r", "\n")
    matches: list[tuple[int, str, int]] = []

    for pattern in CLAUSE_PATTERNS:
        for m in pattern.finditer(text):
            start = m.start()
            title = m.group(2).strip() if m.lastindex and m.lastindex >= 2 else m.group(1).strip()
            matches.append((start, title, start))

    if not matches:
        return []

    matches.sort(key=lambda x: x[0])
    clauses: list[ClauseItem] = []
    for i, (start, title, _) in enumerate(matches):
        end = matches[i + 1][0] if i + 1 < len(matches) else len(text)
        content = text[start:end].strip()
        clauses.append(ClauseItem(title=title, content=content, order_index=i))

    return clauses
```

- [ ] **Step 4: Run test to verify pass**

```bash
cd backend && pytest tests/test_clause_extraction.py -v
```
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/app/domain/clause_extraction.py backend/tests/test_clause_extraction.py
git commit -m "feat: add clause extraction module"
```

---

## Task 3: RBAC Middleware

**Files:**
- Modify: `backend/app/api/dependencies.py`
- Modify: `backend/app/api/routes/auth.py`
- Modify: `backend/app/schemas/auth.py` (ou criar)

- [ ] **Step 1: Add require_admin dependency**

```python
# backend/app/api/dependencies.py
from fastapi import HTTPException, status

def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user
```

- [ ] **Step 2: Update auth endpoints to return role and restrict register**

```python
# backend/app/api/routes/auth.py
from app.api.dependencies import require_admin

class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    email: str
    full_name: str
    role: str

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    is_active: bool
    role: str

class RegisterInput(BaseModel):
    email: str
    password: str
    full_name: str
    role: str = "user"

@router.post("/register", response_model=AuthResponse, status_code=201)
def register(
    payload: RegisterInput,
    request: Request,
    session: Session = Depends(get_session),
    _admin: User = Depends(require_admin),
) -> AuthResponse:
    # ... existing logic ...
    return AuthResponse(
        access_token=token,
        user_id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
    )

@router.post("/login", response_model=AuthResponse)
def login(...) -> AuthResponse:
    # ... existing logic ...
    return AuthResponse(..., role=user.role)

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)) -> UserResponse:
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        is_active=current_user.is_active,
        role=current_user.role,
    )
```

- [ ] **Step 3: Commit**

```bash
git add backend/app/api/dependencies.py backend/app/api/routes/auth.py
git commit -m "feat: add rbac middleware and restrict registration to admin"
```

---

## Task 4: Admin API

**Files:**
- Create: `backend/app/api/routes/admin.py`
- Modify: `backend/app/core/app_factory.py`

- [ ] **Step 1: Create admin router**

```python
# backend/app/api/routes/admin.py
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import get_session, require_admin, get_current_user
from app.db.models.user import User
from app.domain.auth import hash_password

router = APIRouter(prefix="/api/admin", tags=["admin"])

class UserCreateInput(BaseModel):
    email: str
    password: str
    full_name: str
    role: str = "user"

class UserListResponse(BaseModel):
    id: str
    email: str
    full_name: str
    role: str
    is_active: bool

class AssignContractInput(BaseModel):
    contract_id: str
    user_id: str

@router.get("/users", response_model=list[UserListResponse])
def list_users(
    session: Session = Depends(get_session),
    _admin: User = Depends(require_admin),
) -> list[UserListResponse]:
    users = session.scalars(select(User)).all()
    return [
        UserListResponse(
            id=u.id, email=u.email, full_name=u.full_name, role=u.role, is_active=u.is_active
        )
        for u in users
    ]

@router.post("/users", response_model=UserListResponse, status_code=201)
def create_user(
    payload: UserCreateInput,
    session: Session = Depends(get_session),
    _admin: User = Depends(require_admin),
) -> UserListResponse:
    existing = session.scalar(select(User).where(User.email == payload.email))
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")
    user = User(
        email=payload.email,
        hashed_password=hash_password(payload.password),
        full_name=payload.full_name,
        role=payload.role,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return UserListResponse(
        id=user.id, email=user.email, full_name=user.full_name, role=user.role, is_active=user.is_active
    )

@router.patch("/users/{user_id}")
def update_user(
    user_id: str,
    payload: dict,
    session: Session = Depends(get_session),
    _admin: User = Depends(require_admin),
) -> dict:
    user = session.scalar(select(User).where(User.id == user_id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if "role" in payload:
        user.role = payload["role"]
    if "is_active" in payload:
        user.is_active = payload["is_active"]
    session.commit()
    return {"id": user.id, "role": user.role, "is_active": user.is_active}

@router.post("/assign-contract")
def assign_contract(
    payload: AssignContractInput,
    session: Session = Depends(get_session),
    _admin: User = Depends(require_admin),
) -> dict:
    from app.db.models.contract import Contract
    contract = session.scalar(select(Contract).where(Contract.id == payload.contract_id))
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    user = session.scalar(select(User).where(User.id == payload.user_id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    contract.owner_id = payload.user_id
    session.commit()
    return {"contract_id": contract.id, "owner_id": contract.owner_id}
```

- [ ] **Step 2: Register admin router in app_factory**

```python
# backend/app/core/app_factory.py
from app.api.routes.admin import router as admin_router
# ...
app.include_router(admin_router)
```

- [ ] **Step 3: Commit**

```bash
git add backend/app/api/routes/admin.py backend/app/core/app_factory.py
git commit -m "feat: add admin api for user management and contract assignment"
```

---

## Task 5: Remove LLM/Analysis Modules

**Files:**
- Delete: `backend/app/infrastructure/prompts.py`
- Delete: `backend/app/infrastructure/llm_models.py`
- Delete: `backend/app/infrastructure/openai_client.py`
- Delete: `backend/app/infrastructure/contract_chunker.py`
- Delete: `backend/app/infrastructure/embeddings.py`
- Delete: `backend/app/infrastructure/semantic_search.py`
- Delete: `backend/app/infrastructure/docx_generator.py`
- Delete: `backend/app/domain/contract_analysis.py`
- Delete: `backend/app/domain/playbook.py`
- Delete: `backend/app/api/routes/search.py`
- Modify: `backend/app/core/app_factory.py`
- Modify: `backend/app/application/contract_pipeline.py`

- [ ] **Step 1: Delete files**

```bash
cd backend
rm app/infrastructure/prompts.py
rm app/infrastructure/llm_models.py
rm app/infrastructure/openai_client.py
rm app/infrastructure/contract_chunker.py
rm app/infrastructure/embeddings.py
rm app/infrastructure/semantic_search.py
rm app/infrastructure/docx_generator.py
rm app/domain/contract_analysis.py
rm app/domain/playbook.py
rm app/api/routes/search.py
```

- [ ] **Step 2: Update app_factory.py — remove LLM references**

```python
# backend/app/core/app_factory.py
# Remove imports:
# from app.infrastructure.openai_client import OpenAIAnalysisClient
# from app.infrastructure.embeddings import EmbeddingClient
# from app.api.routes.search import router as search_router

# Remove global _embedding_client
# Remove app.include_router(search_router)
# Remove LLM client initialization block:
# openai_api_key = os.environ.get("OPENAI_API_KEY")
# ...
```

- [ ] **Step 3: Update contract_pipeline.py — remove LLM analysis**

```python
# backend/app/application/contract_pipeline.py
# Remove imports of:
#   app.domain.contract_analysis
#   app.infrastructure.contract_chunker
#   app.infrastructure.openai_client
# Remove run_policy_analysis function entirely
# In run_contract_pipeline:
#   Remove call to run_policy_analysis
#   Add call to extract_clauses and save to extraction_metadata
```

Exemplo de como ficar `run_contract_pipeline`:

```python
def run_contract_pipeline(
    session: Session,
    contract: Contract,
    contract_version: ContractVersion,
) -> None:
    text = contract_version.text_content
    if not text:
        return

    metadata_result = extract_contract_metadata(text)
    contract.signature_date = metadata_result.signature_date
    contract.start_date = metadata_result.start_date
    contract.end_date = metadata_result.end_date
    contract.term_months = metadata_result.term_months
    if metadata_result.parties:
        contract.parties = {"entities": metadata_result.parties}
    if metadata_result.financial_terms:
        contract.financial_terms = metadata_result.financial_terms
    contract.status = "analisado"

    clauses = extract_clauses(text)
    existing_meta = dict(contract_version.extraction_metadata or {})
    existing_meta["field_confidence"] = metadata_result.field_confidence
    existing_meta["match_labels"] = metadata_result.match_labels
    existing_meta["clauses"] = [
        {"title": c.title, "content": c.content, "order_index": c.order_index}
        for c in clauses
    ]
    contract_version.extraction_metadata = existing_meta

    scheduled_events = (
        build_contract_events(metadata_result)
        if metadata_result.ready_for_event_generation
        else []
    )
    persist_version_snapshot(
        contract_version,
        build_version_snapshot(
            metadata_result,
            scheduled_events=scheduled_events,
            contract_version_id=contract_version.id,
        ),
    )

    if metadata_result.ready_for_event_generation:
        replace_contract_events(
            contract,
            scheduled_events=scheduled_events,
            contract_version_id=contract_version.id,
        )
```

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "feat: hard remove all LLM, analysis, scoring, embeddings and search modules"
```

---

## Task 6: Ownership Filters + Dashboard Cleanup

**Files:**
- Modify: `backend/app/api/routes/contracts.py`
- Modify: `backend/app/api/routes/dashboard.py`
- Modify: `backend/app/application/dashboard.py`

- [ ] **Step 1: Add ownership filter to contracts list**

```python
# backend/app/api/routes/contracts.py
from sqlalchemy import select

@router.get("")
def list_contracts(
    scope: ContractScope = Query("all"),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    stmt = select(Contract)
    if current_user.role != "admin":
        stmt = stmt.where(Contract.owner_id == current_user.id)
    # ... rest of existing logic ...
```

- [ ] **Step 2: Add ownership filter to dashboard**

```python
# backend/app/application/dashboard.py
from app.db.models.user import User

def build_dashboard_snapshot(
    *,
    session: Session,
    today: date | str,
    current_user: User | None = None,
) -> DashboardSnapshotResponse:
    reference_date = date.fromisoformat(today) if isinstance(today, str) else today
    stmt = select(Contract)
    if current_user and current_user.role != "admin":
        stmt = stmt.where(Contract.owner_id == current_user.id)
    contracts = session.scalars(stmt.options(...)).all()
    # ... remove critical_findings logic (no more analysis) ...
    return DashboardSnapshotResponse(
        summary=DashboardSummaryResponse(
            active_contracts=active_contracts,
            critical_findings=0,  # removed
            expiring_soon=expiring_soon_count,
        ),
        expiring_contracts=expiring_contracts[:10],
        notifications=notification_items,
    )
```

- [ ] **Step 3: Pass current_user to dashboard**

```python
# backend/app/api/routes/dashboard.py
from app.api.dependencies import get_current_user

@router.get("")
def get_dashboard_snapshot(
    today: date | None = None,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> DashboardSnapshotResponse:
    return build_dashboard_snapshot(
        session=session,
        today=today or date.today(),
        current_user=current_user,
    )
```

- [ ] **Step 4: Commit**

```bash
git add backend/app/api/routes/contracts.py backend/app/api/routes/dashboard.py backend/app/application/dashboard.py
git commit -m "feat: add ownership filters and remove analysis metrics from dashboard"
```

---

## Task 7: Frontend Auth + Role

**Files:**
- Modify: `web/src/lib/api/auth.ts`
- Modify: `web/src/contexts/auth-context.tsx`

- [ ] **Step 1: Add role to auth types**

```typescript
// web/src/lib/api/auth.ts
export type AuthResponse = {
  accessToken: string;
  tokenType: string;
  userId: string;
  email: string;
  fullName: string;
  role: string;
};

export type AuthUser = {
  id: string;
  email: string;
  fullName: string;
  isActive: boolean;
  role: string;
};
```

Update `mapAuthResponse` e `mapUser` para incluir `role`.

- [ ] **Step 2: Update AuthContext**

```typescript
// web/src/contexts/auth-context.tsx
type AuthState = {
  user: AuthUser | null;
  token: string | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, fullName: string) => Promise<void>;
  logout: () => void;
};

// No handleAuthSuccess:
setUser({
  id: res.userId,
  email: res.email,
  fullName: res.fullName,
  isActive: true,
  role: res.role,
});
```

- [ ] **Step 3: Commit**

```bash
git add web/src/lib/api/auth.ts web/src/contexts/auth-context.tsx
git commit -m "feat: expose user role in frontend auth"
```

---

## Task 8: Frontend Conditional Navigation

**Files:**
- Modify: `web/src/components/navigation/app-shell.tsx`

- [ ] **Step 1: Add admin link conditionally**

```tsx
// web/src/components/navigation/app-shell.tsx
const { logout, user } = useAuth();
const isAdmin = user?.role === "admin";

// No nav:
{isAdmin && (
  <Link aria-label="Admin" className={navLinkClass("/admin")} href="/admin/usuarios">
    <span className={styles.navTitle}>Admin</span>
    <small className={styles.navMeta}>Gerenciar usuários</small>
  </Link>
)}
```

Repetir no mobile nav também.

- [ ] **Step 2: Commit**

```bash
git add web/src/components/navigation/app-shell.tsx
git commit -m "feat: conditional admin menu based on user role"
```

---

## Task 9: Consultative Contract Detail Screen

**Files:**
- Modify: `web/src/features/contracts/screens/contract-detail-screen.tsx`

- [ ] **Step 1: Remove analysis/score sections, add clauses accordion**

Remover:
- Import de `ClauseStepper`, `FindingsSection`, `useGenerateCorrectedContract`, `getDownloadCorrectedUrl`
- Estado `correctedReady`
- Todo o bloco `selectedAnalysis` (análise de cláusulas com score)
- Todo o bloco de "Gerar Contrato Corrigido"

Adicionar:
- Nova section após "Versão em visualização" mostrando cláusulas extraídas do `selectedVersion.extractionMetadata?.clauses`

```tsx
{selectedVersion?.extractionMetadata?.clauses?.length > 0 && (
  <SurfaceCard title="Cláusulas do contrato">
    <div className={styles.clausesList}>
      {selectedVersion.extractionMetadata.clauses.map((clause: any) => (
        <details key={clause.order_index} className={styles.collapsible}>
          <summary className={styles.collapsibleSummary}>
            <span className={styles.collapsibleTitle}>{clause.title}</span>
            <span className={styles.collapsibleChevron} aria-hidden="true" />
          </summary>
          <div className={styles.collapsibleContent}>
            <p className={styles.inlineText}>{clause.content}</p>
          </div>
        </details>
      ))}
    </div>
  </SurfaceCard>
)}
```

- [ ] **Step 2: Commit**

```bash
git add web/src/features/contracts/screens/contract-detail-screen.tsx
git commit -m "feat: remove analysis/score from contract detail, add extracted clauses"
```

---

## Task 10: Admin Users Screen

**Files:**
- Create: `web/src/features/admin/screens/admin-users-screen.tsx`
- Create: `web/src/app/(app)/admin/usuarios/page.tsx`
- Create: `web/src/lib/api/admin.ts`

- [ ] **Step 1: Create admin API client**

```typescript
// web/src/lib/api/admin.ts
import { getClientEnv } from "../env";
import { getAuthHeaders } from "./auth";

export type AdminUser = {
  id: string;
  email: string;
  full_name: string;
  role: string;
  is_active: boolean;
};

export async function listUsers(): Promise<AdminUser[]> {
  const { NEXT_PUBLIC_API_URL } = getClientEnv();
  const res = await fetch(`${NEXT_PUBLIC_API_URL}/api/admin/users`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) throw new Error("Failed to load users");
  return res.json();
}

export async function createUser(payload: {
  email: string;
  password: string;
  full_name: string;
  role?: string;
}): Promise<AdminUser> {
  const { NEXT_PUBLIC_API_URL } = getClientEnv();
  const res = await fetch(`${NEXT_PUBLIC_API_URL}/api/admin/users`, {
    method: "POST",
    headers: { ...getAuthHeaders(), "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error("Failed to create user");
  return res.json();
}

export async function updateUser(
  userId: string,
  payload: { role?: string; is_active?: boolean }
): Promise<void> {
  const { NEXT_PUBLIC_API_URL } = getClientEnv();
  const res = await fetch(`${NEXT_PUBLIC_API_URL}/api/admin/users/${userId}`, {
    method: "PATCH",
    headers: { ...getAuthHeaders(), "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error("Failed to update user");
}
```

- [ ] **Step 2: Create admin screen**

```tsx
// web/src/features/admin/screens/admin-users-screen.tsx
"use client";

import React, { useCallback, useEffect, useState } from "react";
import { PageHeader } from "../../../components/ui/page-header";
import { SurfaceCard } from "../../../components/ui/surface-card";
import { LoadingSkeleton } from "../../../components/ui/loading-skeleton";
import { createUser, listUsers, updateUser, type AdminUser } from "../../../lib/api/admin";
import styles from "./admin-users-screen.module.css";

export function AdminUsersScreen() {
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState({ email: "", password: "", full_name: "", role: "user" });

  const load = useCallback(async () => {
    setIsLoading(true);
    try {
      const data = await listUsers();
      setUsers(data);
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Erro");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => { void load(); }, [load]);

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    try {
      await createUser(form);
      setForm({ email: "", password: "", full_name: "", role: "user" });
      await load();
    } catch (e) {
      alert(e instanceof Error ? e.message : "Erro");
    }
  }

  async function toggleActive(user: AdminUser) {
    try {
      await updateUser(user.id, { is_active: !user.is_active });
      await load();
    } catch (e) {
      alert(e instanceof Error ? e.message : "Erro");
    }
  }

  return (
    <section className={styles.page}>
      <PageHeader eyebrow="Admin" title="Usuários" description="Gerenciar contas de acesso." />

      <SurfaceCard title="Criar usuário">
        <form onSubmit={handleCreate} className={styles.form}>
          <input placeholder="Nome completo" value={form.full_name} onChange={e => setForm({ ...form, full_name: e.target.value })} required />
          <input placeholder="Email" type="email" value={form.email} onChange={e => setForm({ ...form, email: e.target.value })} required />
          <input placeholder="Senha" type="password" value={form.password} onChange={e => setForm({ ...form, password: e.target.value })} required />
          <select value={form.role} onChange={e => setForm({ ...form, role: e.target.value })}>
            <option value="user">Usuário</option>
            <option value="admin">Admin</option>
          </select>
          <button type="submit">Criar</button>
        </form>
      </SurfaceCard>

      <SurfaceCard title="Lista de usuários">
        {isLoading ? <LoadingSkeleton heading lines={3} /> : error ? (
          <p className={styles.alert}>{error}</p>
        ) : (
          <table className={styles.table}>
            <thead>
              <tr><th>Nome</th><th>Email</th><th>Role</th><th>Ativo</th><th>Ações</th></tr>
            </thead>
            <tbody>
              {users.map(u => (
                <tr key={u.id}>
                  <td>{u.full_name}</td>
                  <td>{u.email}</td>
                  <td>{u.role}</td>
                  <td>{u.is_active ? "Sim" : "Não"}</td>
                  <td>
                    <button onClick={() => toggleActive(u)}>
                      {u.is_active ? "Desativar" : "Ativar"}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </SurfaceCard>
    </section>
  );
}
```

- [ ] **Step 3: Create route page**

```tsx
// web/src/app/(app)/admin/usuarios/page.tsx
import { AdminUsersScreen } from "../../../../features/admin/screens/admin-users-screen";

export default function AdminUsersPage() {
  return <AdminUsersScreen />;
}
```

- [ ] **Step 4: Commit**

```bash
git add web/src/features/admin/ web/src/app/(app)/admin/ web/src/lib/api/admin.ts
git commit -m "feat: add admin users management screen"
```

---

## Task 11: Run Tests + Build

- [ ] **Step 1: Run backend tests**

```bash
cd backend && pytest -x -q
```

- [ ] **Step 2: Run frontend build**

```bash
cd web && npm run build
```

- [ ] **Step 3: Fix any failures**

Ajustar testes que quebrarem devido à remoção de módulos.

- [ ] **Step 4: Commit**

```bash
git commit -m "test: fix tests after consultative refactor"
```

---

## Self-Review Checklist

**1. Spec coverage:**
- [x] Hard remove LLM — Task 5
- [x] Extração de cláusulas regex — Task 2
- [x] RBAC role em users — Task 1, 3
- [x] Register restrito a admin — Task 3
- [x] Ownership owner_id — Task 1, 6
- [x] Filtro admin/user — Task 6
- [x] API admin — Task 4
- [x] Frontend menu condicional — Task 8
- [x] Tela admin — Task 10
- [x] Tela contrato consultiva — Task 9

**2. Placeholder scan:** ✅ Nenhum TBD/TODO/fill in details encontrado.

**3. Type consistency:** ✅ `role` string em todos os lugares. `owner_id` string/FK consistente.

---

## Execution Handoff

**Plan complete and saved to `docs/superpowers/plans/2026-04-27-legaltech-consultative-rbac.md`.**

**Two execution options:**

**1. Subagent-Driven (recommended)** — I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** — Execute tasks in this session using executing-plans, batch execution with checkpoints

**Which approach?**
