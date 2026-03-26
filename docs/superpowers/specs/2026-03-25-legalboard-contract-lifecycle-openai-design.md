# LegalBoard — Acervo, Historico, Versionamento e Analise Juridica OpenAI-Only

> Data: 2026-03-25
> Status: Aprovado pelo usuario

## 1. Objetivo

Evoluir o LegalBoard para um fluxo operacional mais util para contratos de locacao comercial da Lavanderia 60 Minutos, com:

- `Acervo` separado de `Historico`
- contratos ativos protegidos de expurgo automatico
- versionamento real dentro do mesmo contrato
- comparacao entre versoes e entre analises
- analise juridica mais detalhada, em PT-BR, baseada no playbook da franquia e na Lei 8.245/1991
- stack de LLM `OpenAI-only`

## 2. Decisoes de Produto

### 2.1 Acervo

- `Acervo` mostra apenas contratos `ativos`
- o usuario deve conseguir marcar ou desmarcar um contrato como ativo
- contratos ativos representam a carteira operacional real e nao entram na regra de expurgo de 30 dias

### 2.2 Historico

- `Historico` substitui o uso atual de `portfolio`
- mostra contratos analisados recentemente que `nao` estao ativos
- cada item deve expor pelo menos:
  - ultima analise
  - ultima vez que o contrato foi acessado
  - status resumido
  - score mais recente
- a regra de retencao e:
  - contratos nao ativos
  - expurgo automatico 30 dias apos a `ultima analise`

### 2.3 Versionamento

- o contrato continua sendo a entidade principal
- cada novo envio vira `nova versao do mesmo contrato`
- o usuario deve conseguir:
  - abrir qualquer versao anterior
  - ver o historico completo de versoes
  - ver o que mudou entre versoes
  - ver o que mudou entre as analises associadas a cada versao

## 3. Ajustes Funcionais Obrigatorios

### 3.1 Contrato e UI

- criar aba `Acervo`
- trocar `Portfolio` por `Historico`
- mostrar `ultimo acesso`
- adicionar marcacao de `ativo`
- incluir exclusao automatica de 30 dias apenas para contratos nao ativos

### 3.2 Textos e nomenclatura

- trocar `Minuta de terceiro` por `Contrato padrao`
- trocar `monthly` por `aluguel`
- revisar todos os termos em ingles restantes
- corrigir `portifolio` para `historico` ou `acervo`, conforme contexto

### 3.3 Analise e leitura contratual

- revisar score que hoje pode estar exagerando ou inconsistindo com os achados
- corrigir prazo quando a leitura mostrar `12` e o correto for `60`
- enriquecer `Principais Pontos` com clausulas essenciais, por exemplo:
  - exclusividade
  - reajuste monetario
  - prazo
  - valor/aluguel
  - cessao/sublocacao
  - garantias/fiador
  - vistorias
  - obras/infraestrutura
- em `Partes`, explicitar:
  - locador
  - locatario
  - fiador
- na timeline, mostrar `reajuste monetario`
- detalhar melhor a analise completa e os pontos-chave
- frisar se prazo, valor e clausulas essenciais estao presentes ou ausentes
- apontar possiveis clausulas abusivas, lacunas criticas ou desvios relevantes

## 4. Base de Conhecimento Juridica

### 4.1 Playbook obrigatorio da franquia

O arquivo local abaixo deve ser tratado como fonte obrigatoria de regras de negocio:

- `/home/dvdev/Downloads/CLÁSULAS - LAVANDERIA 60 MINUTOS (1).docx`

Topicos obrigatorios extraidos do documento:

- exclusividade
- prazo
- vistorias
- obras e melhorias autorizadas
- cessao e sublocacao
- substituicao de fiador
- manutencao da destinacao do ponto
- disposicoes gerais de infraestrutura
- obrigacao de nao fazer
- assinaturas

### 4.2 Base legal

Tambem deve entrar como referencia obrigatoria:

- Lei 8.245/1991: https://www.planalto.gov.br/ccivil_03/leis/l8245.htm

Checks minimos derivados da lei para o produto:

- consentimento para cessao/sublocacao
- obrigacoes do locatario sobre aluguel e uso do imovel
- modalidades de garantia locaticia
- elementos de renovacao em locacao nao residencial
- atencao a benfeitorias, rescisao e infracao contratual

## 5. Arquitetura Recomendada

### 5.1 Modelo de dados

#### `Contract`

Adicionar campos de ciclo de vida:

- `is_active: bool`
- `activated_at`
- `last_accessed_at`
- `last_analyzed_at`

Observacoes:

- `is_active=true` coloca o contrato no `Acervo`
- contratos nao ativos entram no `Historico`
- a regra de expurgo usa `last_analyzed_at`

#### `ContractVersion`

Ampliar para suportar versionamento explicito:

- `version_number`
- `comparison_summary` opcional ou calculado sob demanda

#### `ContractAnalysis`

Vincular a analise a uma versao especifica:

- `contract_version_id` como FK obrigatoria
- `analysis_model`
- `analysis_prompt_version`
- `knowledge_base_version`

Motivo:

- hoje a analise esta ligada ao contrato, mas nao preserva claramente qual versao gerou qual leitura

### 5.2 API

Adicionar ou expandir endpoints para:

- listar `Acervo`
- listar `Historico`
- ativar/desativar contrato
- listar versoes do contrato
- abrir detalhe de uma versao especifica
- comparar versao atual vs anterior
- comparar analise atual vs anterior
- registrar ultimo acesso
- expurgo automatico de contratos nao ativos expirados

## 6. Estrategia OpenAI-Only

### 6.1 Decisao

- remover o provedor alternativo legado do runtime, dependencias e configuracao
- manter apenas clientes e variaveis da OpenAI
- padronizar a camada de IA em um unico adaptador OpenAI

### 6.2 Recomendacao de modelo

Recomendacao principal para a `analise juridica`, `comparacao entre versoes` e `resumo executivo`:

- `gpt-5-mini`

Motivo:

- a documentacao atual de modelos da OpenAI recomenda a linha GPT-5.x como ponto de partida para apps novos e indica variantes menores para menor custo e latencia
- a pagina oficial de pricing atual mostra `gpt-5-mini` com custo inferior ao `gpt-4.1-mini` na entrada e bem abaixo do flagship
- para este caso, o ganho de raciocinio controlado tende a valer mais do que o menor preco bruto do `gpt-4o-mini`

Isto e uma `inferencia tecnica` a partir das fontes oficiais abaixo:

- Models: https://developers.openai.com/api/docs/models
- Pricing: https://platform.openai.com/pricing

### 6.3 Recomendacao operacional

- usar `gpt-5-mini` como modelo padrao
- executar benchmark local com contratos reais para validar:
  - presenca/ausencia de clausulas essenciais
  - estabilidade do score
  - qualidade do diff entre versoes
  - custo medio por contrato
- somente se o benchmark falhar, promover a etapa principal de analise para `gpt-5.4` ou `gpt-5.4-mini`

## 7. Score e Rigor da Analise

O score nao deve depender apenas do julgamento livre da LLM.

Modelo recomendado:

- `camada deterministica` para clausulas obrigatorias, prazo, valor, reajuste, cessao, fiador e demais checks objetivos
- `camada LLM` para nuance juridica, redacao ambigua, risco interpretativo e comparacao entre versoes
- score final com pesos e tetos por categoria, nunca por `max(llm, deterministic)` puro

Regras desejadas:

- ausencia de clausula essencial pesa alto
- prazo e valor fora do padrao pesam alto
- ambiguidade pesa medio
- conformidade explicita reduz risco
- justificativa do score deve ser auditavel por item

## 8. UX Recomendada

### 8.1 Workspace

- sidebar com `Dashboard`, `Contratos`, `Acervo`, `Historico`
- `Acervo` com foco operacional
- `Historico` com foco de consulta recente e expiracao

### 8.2 Detalhe do contrato

Adicionar secoes novas:

- historico de versoes
- abrir versao anterior
- comparativo entre versoes
- comparativo entre analises
- linha do tempo com reajuste monetario
- painel de clausulas essenciais presentes/ausentes

## 9. Supabase

### 9.1 Analise

Migrar para Supabase `faz sentido`, mas nao deve bloquear esta fase funcional.

Vantagens:

- Postgres gerenciado
- melhor base para queries operacionais e crescimento
- suporte a cron no ecossistema Postgres para o expurgo automatico
- caminho melhor para separar banco e storage

Riscos se migrar agora:

- o projeto ainda carrega decisoes orientadas a SQLite
- varios modelos usam tipos e defaults que merecem portabilidade melhor antes da migracao
- a migracao pode atrasar a entrega do valor funcional principal

### 9.2 Decisao recomendada

- preparar a modelagem nova de forma compativel com Postgres
- abrir `spike` especifico de Supabase
- decidir a migracao apos estabilizar ciclo de vida, versoes e motor juridico

Fonte oficial consultada:

- Supabase pg_cron: https://supabase.com/docs/guides/database/extensions/pg_cron

## 10. Fora de Escopo desta Fase

- migracao completa imediata para Supabase
- OCR multimodal
- multi-tenant
- controle refinado de permissao por organizacao
- workflow de aprovacao juridica por multiplos revisores

## 11. Resultado Esperado

Ao final desta fase, o sistema deve:

- separar claramente `Acervo` e `Historico`
- manter contratos ativos fora do expurgo
- permitir versionamento real por contrato
- abrir e comparar versoes anteriores
- produzir analises juridicas mais confiaveis, detalhadas e em portugues
- operar apenas com modelos OpenAI
- deixar a migracao para Supabase pronta para decisao com menos risco
