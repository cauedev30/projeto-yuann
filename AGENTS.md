# AGENTS

## Workflow de memoria
- Antes de comecar qualquer tarefa, ler `./.codex-memory/current-state.md` e resumir o estado atual.
- Consultar `./.codex-memory/source-of-truth.md` antes de navegar no projeto.
- Consultar `./.codex-memory/decisions.md` antes de mudar arquitetura, convencoes ou padroes.
- Registrar decisoes duraveis em `./.codex-memory/decisions.md`.
- Registrar padroes reutilizaveis em `./.codex-memory/patterns.md`.
- Ao concluir qualquer tarefa, atualizar `./.codex-memory/current-state.md` com estado atual, mudancas concluidas, arquivos alterados, pendencias e proximo passo.
- Ao concluir qualquer tarefa, acrescentar uma entrada curta em `./.codex-memory/session-log.md`.
- Manter tudo curto, objetivo, organizado e sem inventar fatos.
- Marcar como `a confirmar` qualquer ponto nao verificavel.

## Workflow do squad operacional
- Para qualquer tarefa relevante em `backend/`, `web/`, setup, API, arquitetura, UX ou documentacao operacional, iniciar por classificacao usando `docs/squad/README.md`.
- Tratar `implementation-manager` como a porta de entrada obrigatoria do fluxo.
- Definir o caminho obrigatorio da tarefa consultando `docs/squad/routing-matrix.md`.
- Acionar `tech-lead` sempre que houver impacto em arquitetura, contratos de API, persistencia, integracoes, deploy ou fluxo transversal.
- Acionar `qa-backend` e ou `qa-frontend` para toda area de implementacao tocada; QA nao e opcional.
- Usar `docs/squad/blocking-rules.md` para qualquer bloqueio; bloqueio sem evidencia objetiva nao vale.
- Produzir artefatos minimos com base em `docs/squad/templates/`: task brief, handoff, review e documentation update quando aplicavel.
- Antes de fechar uma tarefa, garantir que documentacao e memoria foram atualizadas ou marcadas como `a confirmar`.
- Se o harness atual nao permitir rodar um papel exatamente como descrito, seguir o equivalente mais proximo e registrar a lacuna explicitamente.

## Contexto inicial do projeto
- Projeto atual: MVP LegalTech para ingestao, analise e governanca de contratos de expansao.
- Estrutura principal atual: `backend/` para API e servicos, `web/` para app operador, `docs/` para planos, specs e sistema do squad.
- Fontes principais iniciais: `README.md`, `docs/squad/README.md`, `docs/superpowers/plans/2026-03-15-legaltech-mvp.md`, `backend/app/`, `web/src/app/`.
