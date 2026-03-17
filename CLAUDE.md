# CLAUDE

- Use `./.codex-memory/` como unica memoria persistente compartilhada.
- No inicio da sessao, leia `./.codex-memory/source-of-truth.md` e `./.codex-memory/current-state.md`.
- Antes de mudar arquitetura, contratos, setup ou convencoes, leia `./.codex-memory/decisions.md`.
- Antes de repetir uma abordagem, leia `./.codex-memory/patterns.md`.
- Ao terminar uma tarefa, atualize `./.codex-memory/current-state.md` e adicione uma entrada curta em `./.codex-memory/session-log.md`.
- Registre em `decisions.md` e `patterns.md` apenas informacao duravel.
- Marque como `a confirmar` tudo o que nao puder ser verificado.
- Para fluxo operacional do projeto, siga `docs/squad/README.md` e `docs/squad/routing-matrix.md`.
- Os prompts universais de retomada e encerramento estao em `./.codex-memory/prompts.md`.
