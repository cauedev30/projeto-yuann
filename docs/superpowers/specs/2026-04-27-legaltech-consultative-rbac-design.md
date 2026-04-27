# Design: LegalTech Consultiva + RBAC

## Resumo
Reescopo do LegalTech de plataforma interpretativa (LLM) para plataforma consultiva (apenas extração de cláusulas + info do contrato). Adiciona RBAC com dois papéis: `admin` (acervo completo, gerenciamento de usuários) e `user` (acesso restrito aos seus contratos). Admin cria contas e fornece credenciais. Usuário final preenche formulário (futuro) e vê os contratos vinculados à conta.

## Contexto
A plataforma atual executa pipeline completo de análise jurídica com OpenAI: extração de cláusulas, scoring de risco, sugestões de correção, embeddings e busca semântica. O usuário quer abandonar a interpretação LLM e manter apenas a consulta ao texto do contrato. O público-alvo passa a ser usuários finais que recebem acesso à plataforma para consultar seus próprios contratos.

## Escopo — Inclui
- Remoção hard de todo o código de análise LLM, scoring, playbook, embeddings, semantic search, diff, correção automática
- Novo pipeline de extração de cláusulas por regex/heurísticas sobre texto OCR
- RBAC: campo `role` em `users` (`admin` | `user`)
- Registro restrito: apenas admin cria contas
- Ownership de contratos via `contracts.owner_id`
- Filtro automático: admin vê todos, user vê só seus contratos
- Nova tela admin `/admin/usuarios` para gerenciar usuários e atribuir contratos
- Exibição de cláusulas extraídas na tela de contrato detalhe (accordion, zero interpretação)

## Escopo — Não inclui (futuro)
- Formulário de onboarding do usuário final (substituir Google Forms)
- Envio automático de credenciais por email
- Integração N8N / workflows
- Notificações reais (sem SMTP, sem scheduler)
- Correção automática de contratos
- Busca semântica (pgvector/embedding)

---

## Backend

### 1. Remoção de módulos interpretativos
Módulos a remover completamente:
- `app/infrastructure/prompts.py`
- `app/infrastructure/llm_models.py`
- `app/infrastructure/openai_client.py`
- `app/infrastructure/contract_chunker.py`
- `app/infrastructure/embeddings.py`
- `app/infrastructure/semantic_search.py`
- `app/infrastructure/docx_generator.py`
- `app/domain/contract_analysis.py`
- `app/domain/playbook.py`
- `app/api/routes/search.py`

Módulos a alterar:
- `app/application/contract_pipeline.py` — remover `run_policy_analysis` e referências a LLM. Manter `extract_contract_metadata`, `build_contract_events`, `persist_version_snapshot`.
- `app/api/routes/contracts.py` — remover endpoints de análise, correção, diff entre versões. Manter upload, list, detail, update, e lista de versões (histórico de upload).
- `app/api/routes/dashboard.py` — remover métricas baseadas em análise (risk score, findings count).
- `app/db/models/analysis.py` — tabelas `contract_analyses` e `contract_analysis_findings` serão removidas via migração. Manter `AnalysisStatus` se ainda usado em outro lugar, senão remover.
- `app/core/app_factory.py` — remover registro do search router e embedding client.

### 2. Extração de cláusulas (novo módulo)
Novo módulo: `app/domain/clause_extraction.py`

Função principal:
```python
def extract_clauses(contract_text: str) -> list[ClauseItem]:
    ...
```

Regex padrões:
1. `CLÁUSULA\s+(\d+)ª?\s*[-–—]\s*(.+)`
2. `Art\.?\s*(\d+)º?\s*[-–—.]\s*(.+)`
3. `^(\d+)\.\s+([A-Z][A-Z\s]+)$` — seções numeradas
4. `^(CLÁUSULA|ARTIGO)\s+(.+)` — fallback

Conteúdo = texto entre match atual e próximo match (ou fim do documento).

Resultado: lista de `ClauseItem(title, content, order_index)`.

Persistência: salvar como JSONB em `contract_versions.extraction_metadata["clauses"]` (sem nova tabela, para manter simplicidade).

### 3. RBAC
Modelo `User` alteração:
```python
class UserRole(str, enum.Enum):
    admin = "admin"
    user = "user"

class User(TimestampMixin, Base):
    ...
    role: Mapped[str] = mapped_column(String(20), nullable=False, default=UserRole.user)
```

Dependências:
- `get_current_user` — já existe, retorna usuário do token JWT
- `require_admin` — novo, `Depends(get_current_user)` + checa `role == "admin"`

Auth endpoint alteração:
- `POST /api/auth/register` → adiciona `Depends(require_admin)`. Aceita `role` no payload (default `user`).
- `POST /api/auth/login` → retorna `role` no `AuthResponse`.
- `GET /api/auth/me` → retorna `role` no `UserResponse`.

### 4. Ownership de contratos
Modelo `Contract` alteração:
```python
owner_id: Mapped[str | None] = mapped_column(
    ForeignKey("users.id", ondelete="SET NULL"),
    nullable=True,
)
```

Filtros automáticos:
- Admin (`role == "admin"`): `SELECT * FROM contracts` (sem filtro)
- User (`role == "user"`): `SELECT * FROM contracts WHERE owner_id = :user_id`

Aplicar em todos os endpoints que listam contratos: `/api/contracts`, `/api/dashboard`, `/api/historico`.

### 5. Tela Admin (API)
Novo router: `app/api/routes/admin.py` — prefixo `/api/admin`

Endpoints:
- `GET /api/admin/users` — lista usuários (admin only)
- `POST /api/admin/users` — cria usuário com senha (admin only). Payload: `email`, `password`, `full_name`, `role` (default `user`)
- `PATCH /api/admin/users/{user_id}` — ativa/desativa, muda role
- `POST /api/admin/assign-contract` — vincula contrato a usuário. Payload: `contract_id`, `user_id`

---

## Frontend

### 1. Remoção de telas interpretativas
Remover ou desativar:
- Tela de análise com score, risco, sugestões, progress bar
- Painéis de diff/version comparison (já estavam ocultos)
- Componente `AnalysisProgressBar` (se não usado em outro lugar)
- Hook `use-analysis-stream.ts`

### 2. Tela de contrato detalhe (consultiva)
Mantém:
- Metadados do contrato (partes, prazo, valor, datas)
- Lista de cláusulas extraídas em accordion
- Cada cláusula mostra: título + texto bruto
- Zero interpretação, zero scoring, zero sugestão

### 3. Menu condicional
AuthContext armazena `role`.

Admin vê:
- Dashboard, Acervo, Histórico, Notificações, Admin (novo)

User vê:
- Dashboard (seus contratos), Acervo (seus contratos), Histórico (seus contratos)
- Sem menu Admin

### 4. Tela Admin (`/admin/usuarios`)
Nova página com:
- Tabela de usuários (nome, email, role, ativo/inativo)
- Botão "Criar usuário" → modal com nome, email, senha, role
- Botão toggle ativar/desativar
- Seção "Atribuir contrato" → dropdown contratos sem owner + dropdown usuário → vincular

---

## Database Migrations

### Migração 1: RBAC + Ownership
```sql
-- users.role
ALTER TABLE users ADD COLUMN role VARCHAR(20) NOT NULL DEFAULT 'user';

-- contracts.owner_id
ALTER TABLE contracts ADD COLUMN owner_id VARCHAR(36) REFERENCES users(id) ON DELETE SET NULL;
CREATE INDEX idx_contracts_owner_id ON contracts(owner_id);
```

### Migração 2: Remoção de análise
```sql
-- Remover tabelas de análise
DROP TABLE contract_analysis_findings;
DROP TABLE contract_analyses;

-- Remover colunas relacionadas a análise de contracts (se houver)
-- Nota: verificar se há colunas de score ou status de análise
```

### Migração 3: Cláusulas em metadata
Nenhuma alteração de schema — cláusulas serão salvas em `contract_versions.extraction_metadata["clauses"]`.

---

## API Summary

| Método | Rota | Auth | Descrição |
|--------|------|------|-----------|
| POST | /api/auth/register | Admin | Cria usuário |
| POST | /api/auth/login | Público | Login |
| GET | /api/auth/me | Autenticado | Perfil |
| GET | /api/admin/users | Admin | Lista usuários |
| POST | /api/admin/users | Admin | Cria usuário |
| PATCH | /api/admin/users/{id} | Admin | Atualiza usuário |
| POST | /api/admin/assign-contract | Admin | Vincula contrato |
| GET | /api/contracts | Autenticado (filtro owner) | Lista contratos |
| POST | /api/contracts/upload | Autenticado | Upload contrato |
| GET | /api/contracts/{id} | Autenticado (filtro owner) | Detalhe contrato |
| GET | /api/dashboard | Autenticado (filtro owner) | Dashboard |
| GET | /api/historico | Autenticado (filtro owner) | Histórico |

---

## Decisões
- **Hard remove vs. soft disable:** hard remove. Código interpretativo é removido completamente. Se quiser reverter, usa git history.
- **Extração de cláusulas em regex:** mantém o backend 100% offline, sem dependência de OpenAI ou LLM.
- **Role em users vs. tabela separada:** campo `role` em `users` é suficiente para 2 papéis. Se escalar para >5, migrar para tabela de roles/permissions.
- **Cláusulas em JSONB:** reusa `extraction_metadata` em vez de nova tabela. Simplifica schema e migrações.
- **N8N:** deixado para fase futura (v2). Não mencionado no plano de implementação.

---

## Checklist de implementação
1. Migrações de banco (role, owner_id, drop analysis tables)
2. Remover módulos LLM/análise
3. Implementar `clause_extraction.py`
4. Alterar pipeline de upload para extrair cláusulas
5. Implementar RBAC (middleware, register restrito)
6. Implementar filtros de ownership em contracts/dashboard/historico
7. Implementar API admin (/api/admin/*)
8. Alterar frontend: remover telas de análise, adicionar menu condicional
9. Implementar tela admin (/admin/usuarios)
10. Implementar tela de contrato detalhe com cláusulas (accordion)
11. Testes
12. Deploy
