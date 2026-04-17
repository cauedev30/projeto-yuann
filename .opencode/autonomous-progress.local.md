---
phase: PLANNING
iteration: 1
spec_path: docs/superpowers/specs/2026-04-17-legaltech-assertiveness-and-ux-design.md
plan_path: docs/superpowers/plans/2026-04-17-legaltech-assertiveness-ux-notifications.md
worktree_path: null
current_task: 0
total_tasks: 9
evaluation_cycle: 0
max_eval_cycles: 3
finish_action: pr
blocker_count: 0
suspended_from_phase: null
spec_review_round: 3
spec_review_attempt: 0
---

## Brainstorming Summary
Spec revisada em 2026-04-17 abordando 3 problemas estruturais: (1) LLM pouco assertiva com prompt genérico → prompt profundo com checklist de 9 cláusulas canônicas + regras de decisão, (2) UX incompleta sem ClauseStepper, dashboard com tabela vazia, componentes obsoletos → ClauseStepper, remoção de timeline/diff/historico, dashboard com ExpiringContractsTable, diferenciação Acervo/Histórico, (3) Notificações inexistentes em produção → sequência 12/9/7 meses, email do usuário, badge in-app. Plano já escrito com 9 tasks e revisado (review encontrou 17 issues, todos corrigidos).

## Contexto do Projeto
- Monorepo `projeto-yuann` do MVP LegalTech
- Backend: Python 3.12+ / FastAPI / SQLAlchemy 2 / PostgreSQL (Railway) / OpenAI gpt-5-mini
- Frontend: Next.js 15 / React 19
- Testes backend: `cd backend && source .venv/bin/activate && python -m pytest tests/ -q --tb=short`
- Testes frontend: `cd web && npm run test`
- Build frontend: `cd web && npm run build`
- Type check frontend: `cd web && npx tsc --noEmit`
- Branch atual: main

## Criterios de Aceite
1. Prompt profundo produz 9 findings canônicos com classification (adequada/risco_medio/ausente/conflitante), cita artigos Lei 8.245, sugestões específicas
2. Classification mapeada corretamente para status existente (adequada→conforme, risco_medio→attention, ausente→critical, conflitante→critical)
3. ClauseStepper funcional: 1 cláusula por vez, Anterior/Próximo, scroll check, veredito final, context acervo/historico
4. Dashboard sem EventsTimeline, com ExpiringContractsTable com dados reais e semáforo (red/yellow/green/blue)
5. active_contracts conta is_active=True (não status != "draft")
6. expiring_soon conta contratos (não events)
7. Filtro days_remaining > 365 removido do dashboard
8. Version-diff-panel e version-history-panel removidos
9. Acervo não mostra sugestões, Histórico mostra sugestões
10. Notificações: 3 eventos por contrato vencendo (12, 9, 7 meses antes)
11. Notificações: email do usuário autenticado como destinatário
12. Notification badge no header com polling
13. Signed contracts auto-ativam para o acervo após análise
14. POST /api/search retorna 503 (não 500) quando pgvector indisponível
15. ContractEmbedding compatível com SQLite para testes
16. Todos os testes passando (backend + frontend)

## Tasks
| # | Task | Status | Resumo |
|---|------|--------|--------|
| 1 | Reescrever prompt de análise | PENDING | SYSTEM_PROMPT profundo, classification mapping, llm_models.py |
| 2 | Bugs de produção | PENDING | expiring_soon, active_contracts, 365 filter, SQLite/pgvector |
| 3 | Remover EventsTimeline do dashboard | PENDING | events fora do schema e UI |
| 4 | ClauseStepper no frontend | PENDING | Componente com scroll check, veredito, context |
| 5 | Diferenciar Acervo/Histórico | PENDING | Context prop, sugestões ocultas no acervo |
| 6 | Notificações 12/9/7 meses | PENDING | Sequência, email usuário, endpoints |
| 7 | Notification Badge no header | PENDING | Badge, dropdown, polling, página |
| 8 | Auto-activate signed contracts | PENDING | is_active=true após análise |
| 9 | Integração final | PENDING | Suite completa, TypeScript, build |

## Decisoes & Aprendizados (destilado)
(preenchido incrementalmente a cada task)

## Rastreabilidade (criterio -> tasks)
| Criterio | Tasks |
|----------|-------|
| AC1 (prompt profundo) | T1 |
| AC2 (classification mapping) | T1 |
| AC3 (ClauseStepper) | T4 |
| AC4 (dashboard sem timeline) | T3 |
| AC5 (active_contracts) | T2 |
| AC6 (expiring_soon) | T2 |
| AC7 (filtro 365 removido) | T2 |
| AC8 (diff/history removidos) | T4 |
| AC9 (acervo/historico) | T4, T5 |
| AC10 (notificações 12/9/7) | T6 |
| AC11 (email do usuário) | T6 |
| AC12 (badge) | T7 |
| AC13 (auto-activate) | T8 |
| AC14 (search 503) | T2 |
| AC15 (SQLite compat) | T2 |
| AC16 (testes passando) | T9 |

## Sanity Check (ultima iteracao)
(preenchido a cada iteracao)

## Fix Context
(preenchido quando QA falha)

## Human Input
(preenchido se SUSPENDED)

## Avaliacao
(preenchido apos a avaliacao na FASE 4)

## Anti-patterns
- NAO adicionar comentarios exceto onde logica e genuinamente nao-obvia
- NAO comitar secrets/credenciais
- NAO usar any em TypeScript
- NAO adicionar features extras fora do escopo da task

## Blocker Log
(preenchido quando blockers encontrados)