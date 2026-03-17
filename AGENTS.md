# AGENTS

## Escopo
- Este arquivo e o contrato operacional nativo do Codex para este repositorio.
- A unica interface de memoria persistente e `./.codex-memory/`. Nao dependa de caminho fisico absoluto.

## Inicio de sessao
1. Leia `./.codex-memory/source-of-truth.md`.
2. Leia `./.codex-memory/current-state.md`.
3. Consulte `./.codex-memory/decisions.md` antes de mudar arquitetura, contrato, setup ou convencoes.
4. Consulte `./.codex-memory/patterns.md` antes de repetir padroes de implementacao.
5. Abra no codigo apenas os arquivos relevantes citados pelas fontes acima.

## Contrato de memoria
- Os papeis de cada arquivo de memoria estao definidos em `./.codex-memory/source-of-truth.md`.
- `./.codex-memory/prompts.md` contem os prompts universais de retomada e encerramento.
- Informacao volatil fica em `current-state.md`.
- Informacao duravel fica em `decisions.md` ou `patterns.md`.
- Handoff curto fica em `session-log.md`.
- Nao duplique a mesma informacao em mais de um arquivo.

## Regras de atualizacao
- Verifique no codigo, nos docs e no git antes de escrever memoria.
- Use `a confirmar` para qualquer ponto nao verificado.
- Atualize apenas o arquivo necessario.
- Ao encerrar uma tarefa, atualize `current-state.md` e adicione uma entrada curta em `session-log.md`.
- Atualize `decisions.md` e `patterns.md` somente quando surgir uma mudanca realmente reutilizavel ou duravel.

## Workflow do squad
- Para tarefas em `backend/`, `web/`, setup, API, arquitetura, UX ou documentacao operacional, siga `docs/squad/README.md`.
- Defina o caminho minimo em `docs/squad/routing-matrix.md`.
- Trate QA e documentacao como obrigatorios quando a rota do squad pedir.
- Se algum papel do squad nao puder ser executado literalmente neste harness, siga o equivalente mais proximo e registre a lacuna.

## Contexto inicial
- Projeto: monorepo `projeto-yuann` do MVP `LegalTech`.
- Areas principais: `backend/`, `web/` e `docs/`.
- Fontes repo mais frequentes: `README.md`, `docs/squad/README.md`, `docs/squad/routing-matrix.md`, `docs/superpowers/plans/2026-03-15-legaltech-mvp.md`, `backend/app/` e `web/src/`.
