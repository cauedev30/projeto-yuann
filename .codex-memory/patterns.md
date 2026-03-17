# Patterns

## Regras
- Registrar apenas padroes reutilizaveis.
- Evitar duplicar decisoes arquiteturais.

## Padroes reutilizaveis
- Memoria local via `.codex-memory`
  - contexto: quando precisar ler ou atualizar memoria persistente do projeto a partir do workspace.
  - como usar: acessar os arquivos por `./.codex-memory/*`, mantendo os arquivos reais no vault `CODEX_MEMORY/projects/Projeto_yuann`.
  - observacoes: em Windows, preferir junction de diretorio antes de symlink.
  - status: ativo
- Fechamento curto de tarefa
  - contexto: ao concluir uma tarefa relevante.
  - como usar: atualizar `current-state.md` com estado, mudancas, pendencias e proximo passo; depois registrar uma linha curta em `session-log.md`.
  - observacoes: qualquer ponto nao verificado deve ficar marcado como `a confirmar`.
  - status: ativo
- Boundary transacional em fluxos de upload
  - contexto: casos de uso em `application/` que orquestram storage, extracao e persistencia em mais de uma etapa.
  - como usar: deixar `commit` e `rollback` no caso de uso da camada `application/`; helpers em `tasks/` e `infrastructure/` devem apenas `flush` ou levantar erro traduzido.
  - observacoes: em falha apos gravacao de arquivo, limpar storage e impedir persistencia parcial antes de devolver erro HTTP.
  - status: ativo
- Traducao de erros HTTP conhecidos no boundary de transporte
  - contexto: fluxos frontend em que a API devolve `detail` tecnico ou em ingles, mas a tela precisa de copy amigavel.
  - como usar: mapear detalhes conhecidos em `web/src/lib/api/*` antes de lancar `Error`, deixando a screen apenas renderizar `Error.message`.
  - observacoes: manter fallback generico para respostas sem JSON ou sem `detail` utilizavel.
  - status: ativo
- Snapshot de extracao por versao para contratos assinados
  - contexto: fluxos backend em que uma versao do documento precisa guardar contexto de parse, mas o agregado do contrato deve manter apenas o estado canonico atual.
  - como usar: preservar os metadados de OCR no topo de `contract_versions.extraction_metadata` e anexar um snapshot estruturado da extracao em chave dedicada; atualizar `contracts` e `contract.events` a partir da versao mais recente relevante.
  - observacoes: confianca por campo e rotulos reconhecidos pertencem a `ContractVersion`, nao ao snapshot canonico do contrato.
  - status: ativo
- Verificacao backend em Windows com Python do sistema
  - contexto: ao rodar testes do backend neste workspace Windows quando `pytest` ou `python` do PATH nao estao disponiveis diretamente.
  - como usar: executar `py -3.13 -m pytest -q` a partir de `backend/`; se o sandbox bloquear o Python empacotado pela Microsoft Store, repetir a verificacao fora do sandbox.
  - observacoes: `pytest` puro pode falhar por ausencia no PATH e `python.exe` pode apontar para o stub de `WindowsApps`.
  - status: ativo
