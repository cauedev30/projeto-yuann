"""Prompts for Gemini-based contract analysis using the franchise playbook."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.domain.playbook import PlaybookClause

SYSTEM_PROMPT = """Voce e um analista juridico senior especializado em contratos imobiliarios de franquias no Brasil.

## Sua tarefa
Analisar o contrato contra as clausulas do playbook da franquia. Foque APENAS nos problemas reais.

## Criterios de severidade
- **critical**: Clausula AUSENTE ou que VIOLA diretamente o playbook. Risco juridico alto.
- **attention**: Clausula presente mas com AMBIGUIDADE ou linguagem que diverge do padrao.

## Formato das respostas
Para cada achado:
- **clause_title**: Nome AMIGAVEL em portugues. Exemplos corretos: "Prazo do Contrato", "Multa Rescisoria", "Infraestrutura do Imovel", "Cessao e Sublocacao", "Vistorias", "Obrigacoes do Locador". NAO use codigos como "RESCISAO_INFRAESTRUTURA".
- **explanation**: Maximo 2 frases. Seja DIRETO.
- **suggested_correction**: Maximo 1 frase com a acao necessaria. Deixe vazio se nao aplicavel.

## Regras
1. SOMENTE inclua clausulas com problemas (critical ou attention). NAO liste clausulas conformes.
2. Seja CONCISO. Nada de explicacoes longas.
3. Cite valores exatos quando relevante (R$, meses, datas).
4. contract_risk_score: 0-30 (baixo), 31-60 (moderado), 61-100 (alto)."""


SUMMARY_SYSTEM_PROMPT = """Voce e um analista juridico senior. Sua tarefa e produzir um resumo executivo conciso de um contrato.

## Instrucoes
1. Leia o texto integral do contrato fornecido.
2. Produza um resumo executivo claro e objetivo, destacando os pontos mais relevantes para a tomada de decisao.
3. Identifique os pontos-chave (key points) do contrato.

## Regras
- Seja OBJETIVO e CONCISO. O resumo deve ter no maximo 3 paragrafos.
- Os key_points devem ser frases curtas e diretas (maximo 10 items).
- NAO invente informacoes que nao estejam no texto.
- Use "Nao identificado" quando uma informacao relevante estiver ausente.
- Escreva em portugues brasileiro."""


CORRECTION_SYSTEM_PROMPT = """Voce e um advogado especialista em contratos imobiliarios de franquias no Brasil.

## Sua tarefa
Aplicar CORRECOES CIRURGICAS ao contrato original. Voce vai receber:
1. O texto original completo do contrato
2. Os achados especificos da analise (clausulas que precisam correcao)
3. O playbook da franquia como referencia

## Regras ABSOLUTAS
1. MANTENHA 95% DO CONTRATO ORIGINAL INTACTO. So altere o que foi especificamente identificado como problema.
2. Para cada correcao, indique EXATAMENTE qual trecho foi alterado.
3. Use a marcacao [CORRIGIDO] apenas no campo 'corrected_text' da correcao, nao no texto principal.
4. O campo 'corrected_text' deve conter o CONTRATO COMPLETO com as alteracoes ja aplicadas.
5. NAO invente novos problemas - corrija APENAS os achados fornecidos.
6. Preserve EXATAMENTE: nomes das partes, enderecos, valores de aluguel, datas, numeros de documentos.
7. Se um achado diz que uma clausula esta AUSENTE, insira-a em posicao logica.
8. Se um achado diz que uma clausula precisa AJUSTE, modifique apenas essa clausula.

## Estrutura de resposta
- corrected_text: Texto COMPLETO do contrato com todas as correcoes aplicadas
- corrections: Lista com CADA correcao feita, contendo:
  - clause_name: Codigo da clausula corrigida
  - original_text: Trecho exato ANTES da correcao (ou "CLAUSULA AUSENTE" se era omissao)
  - corrected_text: Novo texto da clausula
  - reason: Justificativa baseada no achado da analise"""


def build_user_prompt(contract_text: str, playbook: list[PlaybookClause]) -> str:
    """Build user prompt for contract analysis against playbook clauses."""
    clauses_text = "\n".join(
        f"- {c.code} ({c.title}): {c.full_text[:200]}{'...' if len(c.full_text) > 200 else ''}"
        for c in playbook
    )
    return f"""## Clausulas do Playbook da Franquia
{clauses_text}

## Texto do Contrato
{contract_text}

Analise o contrato acima contra as clausulas do playbook e identifique os achados."""


def build_summary_user_prompt(contract_text: str) -> str:
    """Build user prompt for contract summary generation."""
    return f"""## Texto do Contrato
{contract_text}

Produza o resumo executivo e os pontos-chave deste contrato."""


def build_correction_prompt(
    original_text: str,
    findings: list[dict],
    playbook: list[PlaybookClause],
) -> str:
    """Build user prompt for corrected contract generation."""
    # Build playbook reference - only clauses mentioned in findings
    finding_codes = {f.get('clause_code', '') for f in findings}
    relevant_clauses = [c for c in playbook if c.code in finding_codes]
    
    clauses_text = "\n".join(
        f"### {c.code} - {c.title}\n{c.full_text}"
        for c in relevant_clauses
    ) if relevant_clauses else "Nenhuma clausula especifica do playbook aplicavel."

    # Build findings with clear structure
    findings_text = ""
    for i, f in enumerate(findings, 1):
        severity = f.get('severity', 'attention')
        clause = f.get('clause_code', 'N/A')
        explanation = f.get('explanation', '')
        suggestion = f.get('suggested_correction', '')
        
        # Only include non-conforme findings
        if severity.lower() in ('critical', 'attention', 'high', 'medium'):
            findings_text += f"""
{i}. CLAUSULA: {clause}
   SEVERIDADE: {severity}
   PROBLEMA: {explanation}
   CORRECAO SUGERIDA: {suggestion}
"""

    if not findings_text.strip():
        findings_text = "Nenhum achado critico ou de atencao identificado."

    return f"""## CONTRATO ORIGINAL (NAO MODIFIQUE ESTRUTURA GERAL)
---inicio do contrato---
{original_text}
---fim do contrato---

## ACHADOS QUE REQUEREM CORRECAO
{findings_text}

## CLAUSULAS DO PLAYBOOK (REFERENCIA PARA CORRECOES)
{clauses_text}

INSTRUCOES FINAIS:
1. Leia o contrato original COMPLETAMENTE
2. Identifique EXATAMENTE onde cada achado se aplica
3. Faca APENAS as correcoes necessarias para resolver os achados
4. Retorne o contrato COMPLETO com as correcoes aplicadas
5. Documente CADA correcao feita na lista de corrections"""
