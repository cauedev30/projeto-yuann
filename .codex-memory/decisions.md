# Decisions

## Regras
- Registrar apenas decisoes duraveis e relevantes.
- Nao registrar tarefas operacionais pequenas.

## Formato
- Data:
- Decisao:
- Motivo:
- Impacto:
- Status: ativo | obsoleto

## Registro
- Data: 2026-03-15
  - Decisao: manter o projeto organizado como monorepo com `web/` para a aplicacao operador e `backend/` para API e servicos.
  - Motivo: essa separacao ja aparece na estrutura atual, no `README.md` e no plano de implementacao.
  - Impacto: responsabilidades, testes e evolucao ficam divididos por fronteira clara.
  - Status: ativo
- Data: 2026-03-15
  - Decisao: manter a memoria persistente do projeto no vault `CODEX_MEMORY`, acessando-a dentro do workspace apenas por `./.codex-memory`.
  - Motivo: padronizar a memoria local entre projetos e manter os arquivos reais no Obsidian.
  - Impacto: o historico operacional do projeto fica centralizado no vault sem perder acesso direto no repositorio.
  - Status: ativo
- Data: 2026-03-16
  - Decisao: organizar o backend do MVP nas fronteiras `api -> application -> domain/infrastructure`, deixando `main.py` apenas como export do app e `core/app_factory.py` como composition root.
  - Motivo: reduzir acoplamento entre HTTP, orquestracao, regras puras e adapters concretos sem introduzir uma arquitetura pesada demais para o estagio atual.
  - Impacto: novos fluxos do backend devem entrar por `application/`, regras puras ficam em `domain/` e integracoes concretas ficam em `infrastructure/`.
  - Status: ativo
- Data: 2026-03-16
  - Decisao: organizar o frontend em `app/` como composition roots, `features/` para screens e componentes, `entities/` para modelos UI-facing e `lib/api/` para transporte.
  - Motivo: separar rota, estado de tela e mapeamento de payloads para deixar o MVP mais profissional e facil de evoluir.
  - Impacto: pages nao devem concentrar logica de produto, tipos de UI nao devem morar em clientes HTTP e fixtures de teste nao entram no runtime por padrao.
  - Status: ativo
- Data: 2026-03-16
  - Decisao: remover dados demo do caminho padrao do dashboard e exibir um estado honesto de indisponibilidade quando nao houver snapshot de runtime.
  - Motivo: evitar que a aplicacao pareca integrada quando ainda nao existe fonte real de dados para o dashboard.
  - Impacto: fixtures permanecem apenas em `web/src/features/dashboard/fixtures/` e testes usam esse caminho explicitamente.
  - Status: ativo
- Data: 2026-03-16
  - Decisao: oficializar um squad operacional repository-native em `docs/squad/`, com classificacao obrigatoria, roteamento por matriz e bloqueios condicionais por evidencia.
  - Motivo: transformar a spec do squad em um sistema util de execucao, evitando sobreposicao entre papeis e tornando revisao e documentacao parte normal da entrega.
  - Impacto: tarefas relevantes agora devem passar por `implementation-manager`, seguir `routing-matrix.md`, obedecer `blocking-rules.md` e usar os templates de handoff e review quando aplicavel.
  - Status: ativo
- Data: 2026-03-16
  - Decisao: persistir o snapshot estruturado da extracao de contratos assinados em `contract_versions.extraction_metadata`, mantendo `contracts` como snapshot canonico atual e `contract.events` como agenda derivada da versao assinada mais recente.
  - Motivo: separar historico de extracao e confianca por versao da leitura operacional atual do contrato sem abrir migracao de schema ou expandir a API nesta fase.
  - Impacto: confianca por campo, rotulos reconhecidos e contexto minimo de parse ficam ligados a cada `ContractVersion`; novos `signed_contract` substituem a agenda anterior do contrato.
  - Status: ativo
- Data: 2026-03-17
  - Decisao: tornar `GET /api/dashboard` a fonte agregada canonica do dashboard operador, mantendo a page de `/dashboard` fina e delegando leitura de loading, erro, vazio e refresh para `DashboardScreen`.
  - Motivo: evitar fan-out no frontend, concentrar o calculo de KPIs/timeline/historico no backend e preservar o estado honesto quando nao houver snapshot operacional util.
  - Impacto: evolucoes do dashboard agora passam por `backend/app/application/dashboard.py`, `backend/app/api/routes/dashboard.py`, `backend/app/schemas/dashboard.py`, `web/src/entities/dashboard/model.ts` e `web/src/lib/api/dashboard.ts`.
  - Status: ativo
