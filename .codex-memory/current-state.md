# Current State

## Projeto
- Monorepo `projeto-yuann` do MVP `LegalTech` para ingestao, analise e governanca de contratos.
- Fonte de verdade usada nesta sessao: repositorio GitHub `git@github.com:cauedev30/projeto-yuann.git`.
- Checkout verificado desta execucao: `C:\Users\win\projeto-yuann`
- Interface canonica de memoria compartilhada: `./.codex-memory/`

## Snapshot verificado
- Resincronizacao local (2026-03-25): clone limpo confirmado em `main` no commit `97c3409c519267cfc8bd70524f918cd5ed136109` (`Implement contract version history and per-version analysis`).
- Base anterior: `19dab0b feat: prepare f5-b product release [F5-B]` / `main` (`0c09517`)
- Hardening de deploy (2026-03-22): `backend/app/core/app_factory.py` agora aceita `DATABASE_URL`, `UPLOAD_DIR` e `CORS_ORIGINS` por env com fallback local; `backend/pyproject.toml` e `backend/requirements.txt` passaram a incluir `psycopg[binary]` e `pydantic-settings`; `.env.example` e `DEPLOY_GUIDE.md` foram reescritos para o fluxo `Railway + Postgres + volume` no backend e `Vercel` no frontend.
- Fix de runtime Railway (2026-03-22): `backend/nixpacks.toml` passou a usar o provider Python padrao e os manifests do backend agora declaram `PyMuPDF`, corrigindo a falha `ModuleNotFoundError: No module named 'fitz'` durante o boot do container.
- Fix de DATABASE_URL Railway (2026-03-22): `_get_database_url` agora normaliza URLs `postgres://` e `postgresql://` para `postgresql+psycopg://`, evitando que o SQLAlchemy tente usar `psycopg2` quando o ambiente do Railway injeta a URL padrao do Postgres.
- Pos-release implementado (2026-03-18): 5 fases do plano pos-MVP concluidas sobre a base publicada.
- Fase 1: Pipeline de upload conectada — `contract_upload.py` agora chama `run_contract_pipeline` (metadata + events + analysis) para drafts, e `run_policy_analysis` para signed contracts (apos archive).
- Fase 2: Regras de negocio — `MAX_TERM_MONTHS`, `MAX_VALUE`, `GRACE_PERIOD_DAYS` adicionadas a `evaluate_rules`; `extract_contract_facts` expandido com `contract_value` e `grace_period_days`; politica padrao seedada em `app_factory.py`.
- Fase 3: Integracao OpenAI — `OpenAIAnalysisClient` em `infrastructure/openai_client.py` com prompts em `infrastructure/prompts.py`; fallback deterministico quando `OPENAI_API_KEY` ausente.
- Task 1.7: `GeminiAnalysisClient` em `infrastructure/gemini_client.py` — wraps google.genai SDK, structured output com Pydantic, retry 1x, fallback tipado. 12 testes.
- Fase 4: Notificacoes SMTP — `SmtpEmailSender` em `infrastructure/notifications.py`; eventos de notificacao em 10/9/8/7 meses antes do vencimento; corpo do email enriquecido.
- Fase 5: Auth JWT — modelo `User`, rotas `/api/auth/register|login|me`, dependency `get_current_user`, migracao `0006`; frontend com `AuthProvider`, `AuthGuard`, pagina `/login` glassmorphic, headers `Authorization` em todos os API clients.
- Fase 6 (Micro Ajustes): AI summary ativado passando `.env` para o uvicorn localmente. UI com titulo de achados alterado para "Principais Pontos". Duplicidade de visualizacao do Prazo de Vigencia resolvida limpando DB obsoleto via reanalise da API.
- Fase 7: F6-B (Acervo e Histórico) — Rotas segregadas no frontend separando o workflow operacional (Acervo/Histórico) do fluxo de ingestão (contracts upload).
- Fase 8: F6-D (Histórico de versões e diff) — `GET /api/contracts/{id}/compare` adicionado com diff determinístico de texto e achados entre versões; detalhe do contrato agora carrega histórico navegável de versões, baseline automática e painel de diff no frontend.

## Plano de melhorias (2026-03-18) — 4 fases concluidas
- Fase 1 (Correcoes rapidas frontend): data hardcoded na timeline corrigida para `new Date()`; traducoes "Contracts"→"Contratos", "Findings principais"→"Achados principais", "Findings criticos"→"Achados criticos"; labels de origem traduzidos; botao "Sair" na sidebar e mobile nav; StatCards com variante compact.
- Fase 2 (Bugs de logica frontend): botao "Atualizar Lista" corrigido (removido prop `refreshContracts`, usa `loadContracts` via `useCallback`); botao "Atualizar Detalhe" com feedback "Atualizado!" por 2s e `cache: "no-store"` nos fetches; botao flutuante scroll-to-bottom com glassmorphism e animacao CSS.
- Fase 3 (Backend): evento `renewal` agora usa `end_date - 180 dias` (data distinta de `expiration`); eventos de `notification_sequence` filtrados no frontend; prompt LLM reescrito com 8 clausulas obrigatorias, criterios de severidade e regras estritas; dedup de findings com normalizacao unicode; novo endpoint `GET /api/contracts/{id}/summary` + `summarize_contract` no OpenAI client; novo componente `ContractSummaryPanel` substitui "Texto extraido" como secao principal.
- Fase 4 (Verificacao e polimento): endpoint `POST /api/notifications/process-due` adicionado para trigger de notificacoes; varredura de traducoes: "score"→"pontuacao", ultima eyebrow "Contracts" corrigida.
- Fase 5 (Contratos e IA): substituicao de "Texto extraido" por `ContractSummaryPanel`; remocao de botoes falhos de atualizar; correcao do erro de "Hydration failed" no `AuthGuard`; otimizacao em `evaluate_rules` para agrupar limites de `Prazo de vigencia` e fix do parser regex de entidades locais; estilizacao premium com glassmorphism no `AppShell` da sidebar.

## Evidencia operacional mais recente
- F6-D versões/diff: backend `22 passed` em `backend/tests/api/test_contracts_api.py -q`; frontend `23 passed` em `src/lib/api/contracts.test.ts` + `src/features/contracts/screens/contract-detail-screen.test.tsx`; `npx tsc --noEmit` verde em 2026-03-25.
- UI Acervo/Histórico: testes unitários web (23 testes) passando em 2026-03-25.
- Backend focado em deploy: `5 passed in 1.45s` (`backend/tests/core/test_app_factory.py` + `backend/tests/core/test_config.py`)
- Packaging/backend deploy: `6 passed in 1.38s` incluindo `backend/tests/core/test_packaging.py`
- Bootstrap/backend deploy: `7 passed in 1.47s` incluindo normalizacao da `DATABASE_URL` do Railway
- Frontend build: `npm run build` verde em 2026-03-22
- Observacao: o build do frontend segue com warnings de ESLint/Next pre-existentes sobre `<img>` e variaveis nao usadas, mas sem bloquear a compilacao.

## Riscos / pendencias
- O deploy real ainda depende de configurar `DATABASE_URL`, `UPLOAD_DIR`, `CORS_ORIGINS`, `JWT_SECRET` e `NEXT_PUBLIC_API_URL` na plataforma.
- O backend continua usando storage local; em producao isso exige volume persistente no Railway montado em `/data`.
- `backend/pyproject.toml` continua declarando `requires-python = ">=3.12"`; a verificacao local usou `Python 3.12.3`.
- Testes E2E Playwright nao foram re-executados nesta sessao (podem precisar de ajustes para o auth guard + traducoes).
- A `OPENAI_API_KEY` deve ser configurada via `.env` apenas; nunca hardcoded.
- `JWT_SECRET` padrao e `dev-secret-change-in-production` — deve ser substituido em producao.
- Endpoint `POST /api/notifications/process-due` precisa de um cron externo para chamada diaria.
- Cleanup de `.worktrees/`, `tmp/`, uploads legados permanece fora do escopo.

## Proximo passo recomendado
- Criar o servico `backend` no Railway com `Root Directory=backend`.
- Adicionar `Postgres` e um `Volume` no Railway, configurando `UPLOAD_DIR=/data/uploads`.
- Publicar o frontend na Vercel com `Root Directory=web` e `NEXT_PUBLIC_API_URL` apontando para o backend.
- Atualizar `CORS_ORIGINS` no Railway com a URL final do frontend e validar `GET /health`.

## Ultima atualizacao
- 2026-03-25
