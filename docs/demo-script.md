# Demo Script: LegalTech MVP

## Setup (2 min)
1. Backend: `cd backend && python -m uvicorn app.main:app --host 127.0.0.1 --port 8000`
2. Frontend: `cd web && NEXT_PUBLIC_API_URL="http://127.0.0.1:8000" npm run dev -- --hostname 127.0.0.1 --port 3000`
3. Seed: `cd backend && python -m tests.support.seed_dashboard_runtime seed`

## Ato 1: Landing Page (~1 min)
- Abrir `http://127.0.0.1:3000`
- Destacar o badge de workspace pronto, a tipografia editorial e a proposta de valor
- Clicar em `Abrir workspace`

## Ato 2: Dashboard Operacional (~2 min)
- Mostrar o resumo do portifolio com contratos ativos, findings criticos e vencimentos
- Percorrer a timeline com filtros `Vencidos`, `Na janela` e `Futuros`
- Mostrar o historico de notificacoes com status, canal e destinatarios

## Ato 3: Intake de Contrato (~3 min)
- Navegar para `Contracts`
- Upload de PDF com titulo `Loja Demo` e referencia `LOC-DEMO-001`
- Mostrar a transicao da sessao para `Triagem concluida`
- Destacar o finding `Prazo de vigencia` como `Critico`
- Mostrar o texto extraido e a leitura orientada

## Ato 4: Detalhe do Contrato (~2 min)
- Clicar no contrato recem-enviado na lista
- Mostrar metadados, versao persistida e timeline de eventos
- Mostrar a analise consolidada e o texto extraido no detalhe

## Pontos de Venda
1. Criterio juridico: analise de risco por politicas configuraveis
2. Ritmo operacional: timeline com alertas antecipados e historico de notificacoes
3. Contexto compartilhado: intake, detalhe e dashboard no mesmo workspace
4. Acabamento premium: linguagem editorial, acessivel e responsiva para demo e venda
