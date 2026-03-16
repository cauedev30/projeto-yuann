# Contracts Screen Redesign Design

## Objetivo
- Redesenhar a tela `/contracts` para que o fluxo de upload e triagem inicial de contratos pareca profissional, claro e operacionalmente confiavel, sem alterar o backend nem expandir o escopo alem do card `F1-B Redesenhar tela de contratos`.

## Contexto Atual
- A rota `web/src/app/(app)/contracts/page.tsx` apenas monta a screen atual.
- A screen `web/src/features/contracts/screens/contracts-screen.tsx` concentra header, upload, estado de erro, preview findings, score e texto extraido em uma unica estrutura minima.
- O formulario `web/src/features/contracts/components/upload-form.tsx` funciona, mas hoje tem apresentacao muito crua.
- O contrato atual de upload, vindo de `web/src/entities/contracts/model.ts` e `web/src/lib/api/contracts.ts`, expoe apenas:
  - `contractId`
  - `contractVersionId`
  - `source`
  - `usedOcr`
  - `text`
- O frontend nao possui hoje uma linguagem visual consolidada nem arquivos de estilo ativos no `src/app/`.

## Meta do Card
- Melhorar a hierarquia visual da `/contracts`.
- Refinar a area de upload e seus feedbacks visuais.
- Tratar explicitamente os estados de vazio, loading, erro e sucesso.
- Garantir boa leitura em desktop e mobile.
- Permanecer compativel com o payload atual de upload, sem depender de mudancas do card `F1-A`.

## Fora de Escopo
- Alterar contrato HTTP do upload.
- Corrigir problemas backend do fluxo de upload.
- Adicionar listagem persistida de contratos.
- Introduzir detalhe real de contrato.
- Criar design system global para todo o produto.

## Abordagem Escolhida

### Direcao de UX
- Seguir a direcao `fluxo guiado com resumo executivo primeiro`.
- A tela deve primeiro orientar o operador a subir o arquivo, depois comunicar o estado da sessao atual e, so apos sucesso, revelar detalhes de triagem.
- O objetivo nao e transformar a tela em um workspace denso; e torna-la confiavel, legivel e comercialmente apresentavel com o backend atual.

### Principio de Hierarquia
1. Contexto da feature
2. Acao principal de upload
3. Estado atual da sessao
4. Resumo executivo da triagem
5. Findings principais
6. Texto extraido

## Estrutura da Tela

### 1. Hero da Tela
- Exibir contexto curto da feature:
  - categoria: governanca contratual
  - titulo: envio para triagem inicial
  - descricao curta: o que acontece apos enviar o PDF
- Esse bloco deve criar confianca e preparar o operador para o fluxo.

### 2. Area Principal de Upload
- O upload deve ganhar presenca visual clara dentro da tela.
- O formulario atual permanece como base funcional, mas com apresentacao mais forte:
  - campos agrupados
  - escolha de tipo de contrato com melhor leitura
  - area de arquivo mais evidente que um input cru
  - CTA principal destacado
- O formulario continua sendo a unica porta de entrada da acao principal da pagina.

### 3. Card de Estado da Sessao
- Ao lado do upload em desktop e abaixo dele em mobile, a tela deve mostrar um bloco que sintetiza o estado atual da sessao.
- Esse card muda de acordo com o estado:
  - `vazio`: explica que nenhuma triagem foi executada nesta sessao
  - `loading`: informa que o contrato esta sendo processado
  - `erro`: mostra a falha de envio com mensagem contextual
  - `sucesso`: confirma que a triagem inicial foi concluida
- O card de estado serve como ancora visual do feedback principal, evitando mensagens soltas.

### 4. Resumo Executivo
- Em caso de sucesso, a primeira area de resultado deve ser um resumo executivo com leitura rapida.
- O resumo deve usar apenas dados que o frontend ja possui hoje:
  - score derivado dos findings locais
  - uso ou nao de OCR
  - tipo de contrato enviado
  - status geral da triagem inicial
- Esse resumo deve responder imediatamente:
  - o envio deu certo?
  - houve risco relevante?
  - o processamento usou OCR?

### 5. Findings Principais
- A tabela atual de findings pode ser preservada como estrutura base, mas deve ganhar enquadramento visual melhor.
- Ela fica abaixo do resumo, nunca acima.
- Os findings precisam parecer parte de uma analise guiada, nao de um dump tecnico.

### 6. Texto Extraido
- O texto extraido continua visivel porque faz parte do valor atual da tela.
- Ele deve aparecer por ultimo, em um painel proprio, claramente secundario ao resumo e aos findings.
- O painel precisa privilegiar legibilidade e nao competir visualmente com a acao principal.

## Arquitetura de Frontend Proposta

### Composition Root
- `web/src/app/(app)/contracts/page.tsx` continua apenas montando a screen.

### Screen
- `web/src/features/contracts/screens/contracts-screen.tsx` continua coordenando estado e submissao, mas deixa de renderizar toda a pagina de forma monolitica.
- A screen passa a montar blocos focados de UI.

### Componentes Recomendados
- `ContractsHero`
  - responsabilidade: contexto e cabecalho da pagina
- `UploadPanel`
  - responsabilidade: conter a versao refinada do formulario de upload
- `SessionStatusCard`
  - responsabilidade: comunicar vazio, loading, erro e sucesso
- `UploadSummaryCards`
  - responsabilidade: mostrar resumo executivo apos sucesso
- `FindingsSection`
  - responsabilidade: enquadrar findings com titulo e contexto
- `ExtractedTextPanel`
  - responsabilidade: exibir texto extraido em area secundaria

### Componentes Existentes
- `UploadForm` deve ser reutilizado e refinado, nao descartado.
- `RiskScoreCard` pode ser absorvido por um bloco maior de resumo ou evoluido visualmente.
- `FindingsTable` pode ser mantida como componente base, desde que ganhe enquadramento melhor na nova hierarquia.

## Estrategia de Estilo
- Como o projeto nao possui hoje um sistema visual global consolidado, o redesign deve usar estilo local da feature.
- A solucao preferida e uma folha de estilo escopada a screen e aos componentes de contratos, evitando poluir o layout global.
- A linguagem visual deve buscar:
  - contraste claro entre area de acao e area de leitura
  - cards com funcao evidente
  - espaco em branco suficiente
  - tipografia com hierarquia forte
  - layout que colapse bem para uma coluna em telas menores

## Modelo de Estados

### Estado Vazio
- Mostrar orientacao util e nao apenas ausencia de conteudo.
- A area de resultados nao deve parecer quebrada; ela deve explicar o que aparecera apos um envio bem-sucedido.

### Estado Loading
- Desabilitar a acao principal de envio.
- Comunicar processamento dentro do card de estado da sessao.
- Manter a tela estavel, sem saltos desnecessarios de layout.

### Estado Erro
- Mostrar feedback proximo da area de upload.
- Preservar o formulario para nova tentativa.
- Evitar mensagens genericas isoladas sem contexto visual.

### Estado Sucesso
- Exibir confirmacao clara no card de estado.
- Mostrar resumo executivo antes dos detalhes.
- Revelar findings e texto extraido sem competir com o topo da pagina.

## Responsividade
- Desktop:
  - upload e estado da sessao em composicao de duas colunas
  - resumo em cards alinhados
  - detalhes abaixo em fluxo vertical
- Mobile:
  - todos os blocos em coluna unica
  - upload primeiro
  - estado da sessao imediatamente abaixo
  - resumo antes de findings e texto
- Nenhum bloco pode depender exclusivamente de largura fixa lateral para continuar legivel.

## Compatibilidade com o Contrato Atual
- O redesign deve continuar funcionando apenas com o payload atual de upload.
- A UI nao deve assumir listagem real de contratos, findings vindos da API ou novos metadados de backend.
- Qualquer resumo exibido deve derivar somente de informacoes ja disponiveis no frontend hoje.

## Verificacao

### Testes de Frontend
- A screen precisa passar a cobrir pelo menos:
  - estado vazio
  - estado loading
  - estado erro
  - estado sucesso com resumo executivo antes dos detalhes
- Componentes extraidos podem receber testes proprios quando houver valor claro.

### QA de UX
- Verificar leitura e hierarquia em desktop.
- Verificar colapso correto para mobile.
- Confirmar que a acao principal da pagina continua obvia.
- Confirmar que feedback de erro e sucesso esta visivel sem confundir o operador.

## Mapeamento do Card F1-B
- `Alinhar contrato de upload com F1-A`
  - manter compatibilidade do frontend com o payload atual e explicitar qualquer dependencia ainda nao resolvida como `a confirmar`
- `Redefinir a hierarquia visual da tela /contracts`
  - implementar hero, upload, estado da sessao, resumo, findings e texto na nova ordem
- `Resolver estados de loading, erro, vazio e sucesso`
  - cobrir UI e testes desses estados
- `Refinar a area de upload e os feedbacks visuais`
  - evoluir apresentacao do formulario e do status da sessao
- `Validar UX em desktop e mobile`
  - verificar responsividade e ajustar layout final

## Riscos e Contencoes
- Risco: tentar compensar limites do backend com UI inventada.
  - contencao: usar apenas dados reais disponiveis hoje.
- Risco: criar componentes demais para uma tela ainda simples.
  - contencao: extrair apenas blocos com responsabilidade visual clara.
- Risco: polimento visual quebrar usabilidade em mobile.
  - contencao: priorizar estrutura de uma coluna como fallback confiavel.

## Criterios de Sucesso
- A tela `/contracts` parece intencional e profissional.
- O upload fica claramente identificado como acao principal.
- Os estados `vazio`, `loading`, `erro` e `sucesso` ficam explicitos.
- O resumo executivo aparece antes dos detalhes tecnicos.
- A tela continua compativel com o contrato atual de upload.
- A experiencia permanece clara em desktop e mobile.
