# App-Wide Visual Refresh Design

## Objetivo
- Modernizar a experiencia visual do produto inteiro, transformando a home e a area logada em uma interface mais executiva, clara e consistente, sem alterar contratos de API nem reescrever o modelo atual de dados do frontend.

## Contexto Atual
- O frontend atual em `web/` possui rotas funcionais para `/`, `/dashboard`, `/contracts` e `/contracts/[contractId]`.
- A home `web/src/app/page.tsx` hoje e minima e nao comunica valor de produto.
- O layout raiz `web/src/app/layout.tsx` ainda nao concentra identidade visual ou estrutura compartilhada relevante.
- As telas do app logado, como `web/src/features/dashboard/screens/dashboard-screen.tsx` e `web/src/features/contracts/screens/contracts-screen.tsx`, operam de forma isolada e sem um shell comum.
- O redesign recente de `/contracts` elevou a qualidade da feature, mas continua localizado e nao resolve a falta de consistencia global.

## Meta do Trabalho
- Criar uma camada visual compartilhada para o produto.
- Transformar `/` em uma home comercial inspirada no site de referencia.
- Criar um shell logado reutilizavel para as areas operacionais do app.
- Levar a linguagem escolhida para `dashboard` e `contracts` sem alterar sua logica central.
- Preservar responsividade e clareza de uso em desktop e mobile.
- Nesta iteracao, o refresh cobre explicitamente `/`, `/(app)/dashboard`, `/(app)/contracts` e a heranca do shell em `/(app)/contracts/[contractId]`.

## Fora de Escopo
- Alterar endpoints, payloads ou integracoes do backend.
- Criar um design system amplo e generico para todo tipo de tela futura.
- Resolver a ausencia de dados reais no dashboard por meio de fixtures artificiais.
- Reescrever regras de negocio, fluxo de upload ou processamento do contrato.
- Implementar auth, areas administrativas novas ou modulos ainda inexistentes.
- Redesenhar em profundidade a tela placeholder de detalhe em `/(app)/contracts/[contractId]`; nesta fase ela apenas herda o shell visual novo.

## Direcao Escolhida

### Direcao Visual
- Opcao escolhida: `B`, produto empresarial premium.
- A home deve herdar parte da linguagem do site de referencia, mas a area logada precisa manter cara de SaaS operacional.
- A interface deve ser mais executiva do que promocional: clara, sofisticada e previsivel.
- "Site de referencia" neste spec significa direcao de linguagem e composicao, nao copia literal da interface externa.

### Principios de UX
1. Hierarquia muito clara entre navegacao, contexto e conteudo.
2. Pouco ruido visual e bastante respiro.
3. Superficies consistentes para cards, secoes e estados.
4. Navegacao compartilhada entre modulos logados.
5. Estados vazios, indisponiveis e de erro apresentados com honestidade, sem simular dados.

## Estrutura Proposta

### 1. Layout Global
- `web/src/app/layout.tsx` passa a ser o composition root visual do frontend.
- O layout global deve definir:
  - base tipografica
  - variaveis de cor
  - fundo e superficies principais
  - espacamento padrao
  - estilo de links, botoes e texto utilitario
- Essa camada deve servir tanto para a home quanto para o shell logado, evitando duplicacao visual entre rotas.

### 2. Home Comercial em `/`
- A rota `/` deixa de ser apenas um placeholder e passa a funcionar como entrada institucional do produto.
- Estrutura recomendada:
  - topbar institucional simples
  - hero com mensagem principal e CTA
  - faixa de prova de valor ou contexto de negocio
  - secoes curtas explicando intake, analise, governanca e acompanhamento
  - CTA final
- A home deve vender clareza operacional e governanca contratual, nao apenas parecer uma landing generica.

### 3. Shell Logado para `/(app)`
- Criar `web/src/app/(app)/layout.tsx` como shell compartilhado das areas logadas.
- O shell escolhido combina:
  - topbar compacta para marca, contexto e acoes globais
  - sidebar esquerda leve para navegacao operacional
  - area central de conteudo com largura controlada
- Em desktop, a sidebar permanece fixa.
- Em mobile, a sidebar vira drawer ou menu colapsavel.
- Nesta fase, a navegacao principal precisa cobrir apenas as entradas reais do app: `Dashboard` e `Contracts`.
- A rota `/(app)/contracts/[contractId]` continua como tela contextual subordinada ao modulo de contratos, sem virar item primario da sidebar.

### 4. Dashboard
- O dashboard deve passar a usar o shell compartilhado e blocos visuais mais executivos.
- A ausencia de snapshot real continua sendo um estado valido.
- O estado `snapshot = null` nao deve parecer quebra de produto; deve parecer indisponibilidade honesta, com empty state mais intencional.
- Quando houver snapshot, resumo, timeline e historico de notificacoes devem parecer partes de um painel unico, nao secoes independentes sem relacao visual.

### 5. Contracts
- A tela `/contracts` reaproveita o trabalho recente de fluxo guiado, mas passa a viver dentro do novo shell compartilhado.
- A feature continua organizada em torno de:
  - contexto da feature
  - upload principal
  - estado da sessao
  - resumo executivo
  - findings
  - texto extraido
- A prioridade aqui nao e redesenhar novamente a regra da tela, e sim encaixa-la numa identidade de produto maior.
- A rota `/(app)/contracts/[contractId]` deve receber apenas a nova moldura visual e alinhamento de espacamento nesta iteracao, preservando seu conteudo placeholder atual.

## Componentes Compartilhados

### Primitives Recomendadas
- `SurfaceCard`
  - card base para resumo, secoes e blocos de leitura
- `PageHeader`
  - cabecalho padrao de area logada com titulo, descricao e acoes
- `StatCard`
  - bloco curto para numeros e indicadores executivos
- `StatusBadge`
  - marcador visual de estado
- `EmptyState`
  - apresentacao padronizada de vazio ou indisponibilidade
- `ActionBar`
  - alinhamento curto de acoes principais e secundarias

### Componentes de Navegacao
- `MarketingTopbar`
  - navegacao da home
- `AppTopbar`
  - barra superior do app logado
- `AppSidebar`
  - navegacao principal do workspace
- `AppShell`
  - composicao estrutural da area logada

### Regra de Escopo
- O objetivo nao e montar uma biblioteca extensa de componentes.
- So devem ser extraidos os blocos necessarios para evitar duplicacao estrutural e garantir consistencia visual real entre telas.

## Fluxo de Dados e Responsabilidades

### Estrategia
- O refresh visual nao deve introduzir estado global novo por padrao.
- Cada pagina continua buscando seus dados como faz hoje.
- O shell novo e estrutural e visual; ele nao passa a centralizar dados de negocio.

### Responsabilidades
- Rotas em `web/src/app/` continuam como composition roots.
- `features/*/screens` continuam controlando apresentacao e estados de cada fluxo.
- `lib/api/*` continua sendo a fronteira de integracao HTTP.
- Componentes compartilhados cuidam de estrutura, navegacao e consistencia visual.

### Consequencia
- A mudanca tem baixo impacto de contrato e alto impacto de composicao.
- O maior risco esta em regressao de layout e responsividade, nao em logica de dominio.

## Modelo de Estados

### Home
- Deve permanecer utilizavel sem depender de dados do backend.
- Conteudo prioritariamente estatico, com foco em narrativa e CTA.

### Dashboard
- `loading`
  - opcional, se no futuro houver carregamento async visivel
- `empty` ou `indisponivel`
  - estado atual mais importante, pois `snapshot` pode ser `null`
- `success`
  - quando o snapshot existir
- `error`
  - manter consistente com o padrao visual do restante do app

### Contracts
- Manter os estados ja modelados no redesign:
  - vazio
  - loading
  - erro
  - sucesso
- O refresh visual nao deve esconder o CTA principal nem deslocar a leitura prioritaria da sessao.

## Estilo e Tonalidade
- Base clara e limpa.
- Acentos em verde e azul.
- Mais sobrio do que chamativo.
- Tipografia com presenca, mas sem cair em visual editorial exagerado.
- Bordas, sombras e superficies devem reforcar organizacao, nao decoracao excessiva.

## Responsividade
- Desktop:
  - shell com sidebar fixa e area central com respiro
  - home com secoes mais abertas e melhor exploracao horizontal
- Tablet:
  - comprimindo grelhas antes de colapsar completamente a navegacao
- Mobile:
  - sidebar colapsada
  - topbar mais enxuta
  - cards e secoes em coluna unica
- A navegacao precisa continuar obvia em todas as larguras, especialmente nas rotas operacionais.

## Estrategia de Implementacao
1. Criar a base visual global no layout raiz.
2. Criar o shell compartilhado de `/(app)`.
3. Reescrever a home `/` na nova linguagem.
4. Adaptar `dashboard` ao shell e aos componentes compartilhados.
5. Adaptar `contracts` para a mesma linguagem, preservando o fluxo guiado ja aprovado.

## Verificacao

### Verificacao Tecnica
- `cd web && npm run test`
- `cd web && npm run build`
- `cd web && npm run e2e` fica `a confirmar` ate a remocao do hardcode Windows atual em `web/playwright.config.ts`

### Verificacao de UX
- Conferir navegacao e leitura da home em desktop e mobile.
- Conferir shell logado em desktop e mobile nas rotas `/dashboard`, `/contracts` e `/contracts/[contractId]`.
- Conferir que `dashboard` permanece honesto quando nao ha snapshot real.
- Conferir que `/contracts` continua com CTA principal evidente e fluxo responsivo.
- Se o e2e ainda estiver bloqueado pelo setup atual, registrar verificacao manual responsiva dessas rotas como evidencia temporaria.

## Riscos e Contencoes
- Risco: o shell visual novo conflitar com as telas atuais.
  - contencao: extrair primitives pequenas e adaptar tela por tela.
- Risco: a home ficar bonita, mas desconectada da linguagem do produto logado.
  - contencao: compartilhar tokens, tipografia e principios de superficie entre marketing e app.
- Risco: dashboard parecer completo demais sem dados reais.
  - contencao: tratar indisponibilidade como estado de produto, nao maquiar com fixtures.
- Risco: mudanca ampla demais para uma iteracao so.
  - contencao: implementar em camadas e validar cada rota principal.

## Criterios de Sucesso
- A home passa a comunicar valor de produto de forma clara e profissional.
- O app logado ganha um shell compartilhado coerente.
- `dashboard` e `contracts` passam a parecer partes do mesmo produto.
- O frontend fica visualmente mais executivo e consistente sem alterar contratos de dados.
- A experiencia continua clara em desktop e mobile.
