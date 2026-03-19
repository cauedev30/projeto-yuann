# Current State

## Projeto
- Monorepo `projeto-yuann` do MVP `LegalTech` para ingestao, analise e governanca de contratos.
- Fonte de verdade usada nesta sessao: repositorio GitHub `git@github.com:cauedev30/projeto-yuann.git`.
- Checkout verificado desta execucao: `/home/dvdev/projeto-yuann`
- Interface canonica de memoria compartilhada: `./.codex-memory/`

## Snapshot verificado
- Base anterior: `19dab0b feat: prepare f5-b product release [F5-B]` / `main` (`0c09517`)
- Pos-release implementado (2026-03-18): 5 fases do plano pos-MVP concluidas sobre a base publicada.
- Fase 1: Pipeline de upload conectada — `contract_upload.py` agora chama `run_contract_pipeline` (metadata + events + analysis) para drafts, e `run_policy_analysis` para signed contracts (apos archive).
- Fase 2: Regras de negocio — `MAX_TERM_MONTHS`, `MAX_VALUE`, `GRACE_PERIOD_DAYS` adicionadas a `evaluate_rules`; `extract_contract_facts` expandido com `contract_value` e `grace_period_days`; politica padrao seedada em `app_factory.py`.
- Fase 3: Integracao OpenAI — `OpenAIAnalysisClient` em `infrastructure/openai_client.py` com prompts em `infrastructure/prompts.py`; fallback deterministico quando `OPENAI_API_KEY` ausente.
- Fase 4: Notificacoes SMTP — `SmtpEmailSender` em `infrastructure/notifications.py`; eventos de notificacao em 10/9/8/7 meses antes do vencimento; corpo do email enriquecido.
- Fase 5: Auth JWT — modelo `User`, rotas `/api/auth/register|login|me`, dependency `get_current_user`, migracao `0006`; frontend com `AuthProvider`, `AuthGuard`, pagina `/login` glassmorphic, headers `Authorization` em todos os API clients.
- Fase 6 (Micro Ajustes): AI summary ativado passando `.env` para o uvicorn localmente. UI com titulo de achados alterado para "Principais Pontos". Duplicidade de visualizacao do Prazo de Vigencia resolvida limpando DB obsoleto via reanalise da API.

## Plano de melhorias (2026-03-18) — 4 fases concluidas
- Fase 1 (Correcoes rapidas frontend): data hardcoded na timeline corrigida para `new Date()`; traducoes "Contracts"→"Contratos", "Findings principais"→"Achados principais", "Findings criticos"→"Achados criticos"; labels de origem traduzidos; botao "Sair" na sidebar e mobile nav; StatCards com variante compact.
- Fase 2 (Bugs de logica frontend): botao "Atualizar Lista" corrigido (removido prop `refreshContracts`, usa `loadContracts` via `useCallback`); botao "Atualizar Detalhe" com feedback "Atualizado!" por 2s e `cache: "no-store"` nos fetches; botao flutuante scroll-to-bottom com glassmorphism e animacao CSS.
- Fase 3 (Backend): evento `renewal` agora usa `end_date - 180 dias` (data distinta de `expiration`); eventos de `notification_sequence` filtrados no frontend; prompt LLM reescrito com 8 clausulas obrigatorias, criterios de severidade e regras estritas; dedup de findings com normalizacao unicode; novo endpoint `GET /api/contracts/{id}/summary` + `summarize_contract` no OpenAI client; novo componente `ContractSummaryPanel` substitui "Texto extraido" como secao principal.
- Fase 4 (Verificacao e polimento): endpoint `POST /api/notifications/process-due` adicionado para trigger de notificacoes; varredura de traducoes: "score"→"pontuacao", ultima eyebrow "Contracts" corrigida.
- Fase 5 (Contratos e IA): substituicao de "Texto extraido" por `ContractSummaryPanel`; remocao de botoes falhos de atualizar; correcao do erro de "Hydration failed" no `AuthGuard`; otimizacao em `evaluate_rules` para agrupar limites de `Prazo de vigencia` e fix do parser regex de entidades locais; estilizacao premium com glassmorphism no `AppShell` da sidebar.

## Evidencia operacional mais recente
- Backend: `55 passed in 1.62s`
- Frontend unitario: `19` arquivos e `81` testes passando
- TypeScript/Build: limpo (`npm run build` sem erros)
- ESLint: limpo (apenas warning pre-existente em dashboard)

## Riscos / pendencias
- `backend/pyproject.toml` continua declarando `requires-python = ">=3.13"`, mas a verificacao local usou `Python 3.12.3`.
- Testes E2E Playwright nao foram re-executados nesta sessao (podem precisar de ajustes para o auth guard + traducoes).
- A `OPENAI_API_KEY` deve ser configurada via `.env` apenas; nunca hardcoded.
- `JWT_SECRET` padrao e `dev-secret-change-in-production` — deve ser substituido em producao.
- Endpoint `POST /api/notifications/process-due` precisa de um cron externo para chamada diaria.
- Cleanup de `.worktrees/`, `tmp/`, uploads legados permanece fora do escopo.

## Proximo passo recomendado
- Configurar cron job para chamar `POST /api/notifications/process-due` diariamente.
- Rodar testes E2E e ajustar para auth guard + traducoes.
- Deploy em ambiente de staging para validacao integrada.

## Ultima atualizacao
- 2026-03-18
