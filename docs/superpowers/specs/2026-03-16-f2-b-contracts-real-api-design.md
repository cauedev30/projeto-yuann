# F2-B Contracts Real API Design

## Objetivo
- Conectar a listagem e o detalhe de contratos da UI aos endpoints canonicos ja publicados no backend, mantendo estados honestos de loading, empty, error e refresh.

## Contexto Atual
- `origin/main` no commit `2815cad` ja inclui a `F2-A`, com `GET /api/contracts` enriquecido e `GET /api/contracts/{contract_id}` canonico.
- `web/src/app/(app)/contracts/page.tsx` continua fino e compoe `ContractsScreen`.
- `web/src/features/contracts/screens/contracts-screen.tsx` hoje concentra o fluxo de upload e a triagem imediata do PDF enviado, mas ainda nao mostra a lista real de contratos persistidos.
- `web/src/app/(app)/contracts/[contractId]/page.tsx` ainda e placeholder dentro do shell compartilhado.
- O card `F2-B` pede explicitamente: conectar listagem, conectar detalhe, tratar processamento/erro/vazio/refresh, validar navegacao entre lista e detalhe e ajustar componentes ao payload final.

## Fora de Escopo
- Alterar o contrato HTTP do backend definido na `F2-A`.
- Criar novos endpoints de contratos.
- Redesenhar a identidade visual ou o shell compartilhado do app.
- Introduzir store global, cache dedicado ou nova infra de data fetching.
- Alterar regras de analise, upload ou persistencia.

## Rota do Squad
- Classificacao: `medium-risk feature`
- Areas tocadas: `web`, UX de operador, contrato HTTP consumido pela UI, testes frontend, documentacao
- Rota minima: `implementation-manager -> tech-lead -> frontend-engineer -> qa-frontend -> documentation-engineer`

## Direcao Escolhida

### 1. Manter `/contracts` como porta de entrada dual
- A rota `/contracts` continua sendo o lugar do intake operacional.
- A screen passa a combinar:
  - bloco existente de upload e triagem imediata
  - bloco novo de listagem real dos contratos persistidos
- O upload continua com comportamento local imediato, sem depender da listagem para mostrar a triagem recem-concluida.
- Apos upload bem-sucedido, a listagem deve ser recarregada a partir de `GET /api/contracts`, em vez de fabricar localmente um novo item com payload parcial.

### 2. Separar claramente os boundaries de dados
- `web/src/lib/api/contracts.ts` deve ficar responsavel apenas por transporte:
  - `uploadContract`
  - `listContracts`
  - `getContractDetail`
- `web/src/entities/contracts/model.ts` deve mapear o payload HTTP para modelos UI-facing distintos:
  - resumo de contrato para lista
  - detalhe canonico do contrato
  - findings e summaries usados pela tela
- A UI nao deve consumir payload bruto do backend diretamente.

### 3. Conectar a listagem a `GET /api/contracts`
- A listagem em `/contracts` deve usar o endpoint de resumo, nao o payload de detalhe.
- Cada item deve exibir apenas o que ja vem na listagem:
  - identidade do contrato
  - status
  - metadados resumidos
  - score/estado de analise mais recente quando existir
- Cada item deve navegar para `/contracts/[contractId]` por rota canonica, sem manter estado de selecao fora da URL.

### 4. Substituir o placeholder do detalhe por uma tela real
- `/contracts/[contractId]` deve buscar `GET /api/contracts/{contract_id}` e renderizar:
  - cabecalho com identidade do contrato
  - resumo do contrato
  - versao mais recente
  - analise mais recente
  - findings persistidos
- Se `latest_analysis` for `null`, a tela deve assumir um estado parcial honesto, explicando que a analise ainda nao esta disponivel.
- Se `latest_version` for `null`, a tela deve assumir um estado parcial honesto para origem e documento, sem presumir texto extraido ou metadata inexistente.
- Se o backend responder `404`, a tela deve assumir estado de contrato nao encontrado, sem fallback enganoso.

### 5. Loading, empty, error e refresh sao parte do contrato
- `/contracts` precisa cobrir:
  - loading inicial da lista
  - lista vazia
  - erro de carregamento
  - refresh manual da listagem
- `/contracts/[contractId]` precisa cobrir:
  - loading inicial
  - erro de detalhe
  - `404`
  - refresh manual do detalhe
- QA frontend deve tratar a ausencia desses estados como bloqueio objetivo.

### 6. Navegacao simples e sem cache prematuro
- A navegacao lista -> detalhe deve acontecer por `Link`/URL.
- O detalhe sempre pode refazer seu proprio fetch; nao ha necessidade de store global ou prefetch sofisticado nesta fase.
- Se houver reaproveitamento local de helpers entre lista e detalhe, ele deve ficar em `entities/` ou `features/`, nunca acoplando `app/` ao transporte.

## Contrato de UI Proposto

### Lista em `/contracts`
- Mantem o painel de upload existente.
- Adiciona um painel de contratos persistidos com:
  - cabecalho da secao
  - acao de refresh
  - items clicaveis
  - copy explicita para vazio e erro

### Detalhe em `/contracts/[contractId]`
- Mantem `PageHeader` e `SurfaceCard` do shell compartilhado.
- Troca o placeholder por uma composicao real com:
  - resumo do contrato
  - bloco da ultima versao
  - bloco da ultima analise
  - findings persistidos
- O layout deve usar os componentes visuais do app onde isso reduzir duplicacao; nao precisa inventar um novo sistema visual.

## Testes Necessarios
- Testes unitarios do client API para:
  - `listContracts`
  - `getContractDetail`
  - erros genericos de transporte
- Testes de screen para `/contracts` cobrindo:
  - loading
  - empty
  - erro
  - refresh
  - refresh da lista apos upload bem-sucedido
  - navegacao para detalhe
- Testes de screen para o detalhe cobrindo:
  - detalhe completo
  - detalhe sem analise
  - detalhe sem versao recente
  - contrato inexistente
- E2E cobrindo o fluxo:
  - operador abre `/contracts`
  - enxerga contratos persistidos
  - navega para um detalhe real

## Riscos
- Misturar demais a nova listagem com o fluxo de upload na mesma screen.
  - mitigacao: manter upload e listagem em secoes separadas e com responsabilidades claras.
- Duplicar formatacao de campos entre lista e detalhe.
  - mitigacao: extrair mapeamento e formatacao compartilhavel para `entities/contracts`.
- Deixar o detalhe dependente de estado vindo da lista.
  - mitigacao: cada rota resolve seu proprio fetch.
- Criar fallback visual enganoso quando faltar analise.
  - mitigacao: usar copy explicita para estado parcial, sem simular findings.

## Resultado Esperado
- A `F2-B` fecha a conexao real entre frontend e backend de contratos sem reabrir a `F2-A`.
- `/contracts` deixa de ser apenas upload + triagem local e passa a mostrar o portfolio real de contratos.
- `/contracts/[contractId]` deixa de ser placeholder e vira a rota canonica de review do contrato persistido.
