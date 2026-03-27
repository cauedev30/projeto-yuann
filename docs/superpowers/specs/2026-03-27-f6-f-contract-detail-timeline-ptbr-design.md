# LegalBoard - F6-F Revisar detalhe do contrato, timeline e linguagem PT-BR

> Data: 2026-03-27
> Status: Em revisao do usuario

## 1. Objetivo

Executar a task `F6-F` do Trello para melhorar o detalhe do contrato no LegalBoard, com foco em:

- revisão de termos em inglês e copy errada
- apresentação mais útil de partes e metadados
- enriquecimento de `Principais Pontos`
- inclusão e melhor rotulagem de `reajuste monetário` na timeline
- cobertura de testes para detalhe e timeline

O objetivo não é redesenhar todo o fluxo de contratos nem abrir uma nova fase arquitetural. A entrega deve ser contida e diretamente aderente ao card.

## 2. Escopo

### 2.1 Dentro do escopo

- revisar a linguagem PT-BR da tela de detalhe e componentes ligados a ela
- ajustar a nomenclatura de origem `third_party_draft` para `Contrato padrao` nos pontos afetados por esta task
- melhorar o bloco de metadados para evidenciar:
  - locador
  - locatario
  - fiador
  - datas principais
  - aluguel
  - reajuste
  - carencia e multa, quando existirem
- enriquecer a apresentacao do resumo executivo e dos `Principais Pontos`
- melhorar a timeline do detalhe para tratar `readjustment` explicitamente como `Reajuste monetario`
- adicionar ou atualizar testes backend e frontend diretamente relacionados a esse comportamento

### 2.2 Fora do escopo

- refatorar o fluxo completo de upload
- redesenhar toda a UX do workspace
- alterar o modelo de versionamento
- mexer em `Acervo` ou `Historico` fora de copy residual relacionada ao card
- criar novas rotas para a F6-F

## 3. Decisao de implementacao

### 3.1 Abordagem escolhida

Implementar a F6-F como `frontend-first com pequenos ajustes de backend`.

### 3.2 Motivo

O frontend atual já suporta grande parte da melhoria de UX, mas dois pontos do card dependem de melhor base de dados:

- `Partes` hoje chega ao frontend de forma genérica demais para evidenciar papeis contratuais
- `Resumo do contrato` hoje não força cobertura suficiente das clausulas essenciais pedidas no card

O backend será ajustado apenas para melhorar esses contratos de leitura. A meta é evitar remendos na UI sem abrir refactor amplo.

## 4. Arquitetura da solucao

### 4.1 Backend

#### Extração de partes

O enriquecimento principal ficará em `backend/app/domain/contract_metadata.py`.

Direção:

- preservar a extração atual de entidades já encontrada no texto
- passar a montar uma estrutura mais rica para `parties`, com chaves específicas quando possível, por exemplo:
  - `landlord`
  - `tenant`
  - `guarantor`
  - `entities`
- manter comportamento honesto: se o parser não encontrar um papel específico, ele não inventa o valor

Compatibilidade:

- a API pode continuar expondo `parties` como `dict[str, Any]`
- o frontend deverá aceitar tanto o formato rico novo quanto payloads mais antigos

#### Resumo executivo com IA

O endurecimento do resumo ficará em `backend/app/infrastructure/prompts.py`.

Direção:

- o prompt de resumo deve obrigar a IA a cobrir, de forma concisa:
  - prazo
  - aluguel/valor
  - reajuste monetario
  - exclusividade
  - cessao/sublocacao
  - garantias/fiador
  - vistorias
  - obras/infraestrutura
- quando uma informacao estiver ausente no contrato, o resumo deve deixar isso claro
- os `key_points` devem priorizar utilidade juridica e operacional, não bullets genéricos

Restrição:

- não mudar o endpoint `/api/contracts/{id}/summary`
- não ampliar o schema público além do necessário para esta fase

### 4.2 Frontend

#### Tela de detalhe

O centro da F6-F ficará em `web/src/features/contracts/screens/contract-detail-screen.tsx`.

Direção:

- manter o fluxo atual de carregamento, erro, refresh, histórico e diff
- melhorar o topo do detalhe com leitura executiva mais clara sobre:
  - origem
  - status
  - prazo
  - score
  - ultimo acesso
  - ultima analise
- revisar textos e nomenclaturas para PT-BR consistente

#### Bloco de metadados

O componente `web/src/features/contracts/components/metadata-section.tsx` deve deixar de ser uma lista genérica e passar a organizar os dados em grupos compreensíveis.

Direção:

- seção `Partes` com papeis claros quando disponíveis
- seção `Datas` com assinatura, inicio e termino
- seção `Condicoes financeiras` com aluguel, reajuste, carencia e multa
- estado honesto para ausências: `Nao identificado` ou equivalente já adotado pela tela

#### Timeline

O componente `web/src/features/contracts/components/event-timeline.tsx` deve:

- manter a filtragem de eventos de notificacao técnica
- melhorar o rótulo de `readjustment` para `Reajuste monetario`
- deixar a timeline mais legível no detalhe do contrato

#### Principais Pontos

O componente `web/src/features/contracts/components/contract-summary-panel.tsx` deve apresentar os resultados do resumo com hierarquia melhor.

Direção:

- manter o resumo em texto corrido curto
- tratar `Principais Pontos` como checklist executivo e jurídico
- evitar linguagem vaga ou redundante na renderização

## 5. Arquivos afetados

### 5.1 Backend

- `backend/app/domain/contract_metadata.py`
- `backend/app/infrastructure/prompts.py`
- `backend/app/schemas/contract.py` se houver necessidade de clarificar contrato de resposta
- `backend/tests/infrastructure/test_prompts.py`
- testes focados de metadata, se a estrutura de `parties` mudar

### 5.2 Frontend

- `web/src/features/contracts/screens/contract-detail-screen.tsx`
- `web/src/features/contracts/screens/contract-detail-screen.module.css`
- `web/src/features/contracts/screens/contract-detail-screen.test.tsx`
- `web/src/features/contracts/components/metadata-section.tsx`
- `web/src/features/contracts/components/metadata-section.test.tsx`
- `web/src/features/contracts/components/event-timeline.tsx`
- `web/src/features/contracts/components/event-timeline.test.tsx`
- `web/src/features/contracts/components/contract-summary-panel.tsx`
- `web/src/entities/contracts/model.ts` se o payload de `parties` ficar mais rico

## 6. Regras de UX e linguagem

- priorizar português brasileiro simples e direto
- trocar `Minuta de terceiro` por `Contrato padrao` nos pontos tocados pela F6-F
- evitar termos mistos em inglês quando já houver equivalentes claros no produto
- não simular certeza em dado ausente
- preservar a linguagem já consolidada do projeto: objetiva, operacional e sem marketing desnecessário

## 7. Testes

### 7.1 Backend

- testar a nova estrutura de `parties` quando houver texto suficiente para separar papeis
- testar o prompt de resumo para garantir que os checks obrigatórios da F6-F constem na instrução

### 7.2 Frontend

- cobrir renderização dos metadados enriquecidos
- cobrir o novo rótulo do reajuste monetário na timeline
- cobrir a renderização do detalhe com copy PT-BR revisada
- atualizar fixtures ou payloads de teste apenas no mínimo necessário

### 7.3 Verificação final esperada

- `backend`: `.venv\Scripts\python -m pytest -q --basetemp=.pytest-tmp`
- `frontend`: `npm.cmd run test`

## 8. Riscos e mitigacoes

### 8.1 Parser de partes imperfeito

Risco:

- contratos diferentes podem não seguir o mesmo padrão textual

Mitigação:

- extrair papeis só quando houver evidência suficiente
- manter fallback em `entities`
- UI compatível com informação parcial

### 8.2 Resumo da IA continuar genérico

Risco:

- mesmo com prompt melhor, o modelo pode variar

Mitigação:

- endurecer o prompt com checklist explícito
- tratar `key_points` como complemento, não como fonte única da tela

### 8.3 Escopo escapar para refactor amplo

Risco:

- a task puxar mudanças grandes em contratos, dashboard ou análise

Mitigação:

- limitar alterações ao detalhe, metadados, resumo, timeline e suporte mínimo de payload
- deixar qualquer ampliação estrutural fora desta F6-F

## 9. Resultado esperado

Ao final da F6-F, o detalhe do contrato deve:

- comunicar melhor o estado do contrato em PT-BR
- mostrar partes e metadados com mais clareza operacional
- expor `Principais Pontos` mais úteis juridicamente
- tratar `reajuste monetario` como item explícito da timeline
- ficar coberto por testes suficientes para evitar regressões nesses pontos
