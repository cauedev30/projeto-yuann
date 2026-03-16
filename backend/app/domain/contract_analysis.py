from __future__ import annotations

import re

from app.schemas.analysis import AnalysisItem, ContractAnalysisResult


def _score_for_status(status: str) -> int:
    if status == "critical":
        return 80
    if status == "attention":
        return 40
    return 0


def _coerce_number(value: object) -> int | None:
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str) and value.isdigit():
        return int(value)
    return None


def extract_contract_facts(contract_text: str) -> dict[str, int]:
    facts: dict[str, int] = {}

    term_match = re.search(r"(\d+)\s*meses", contract_text, re.IGNORECASE)
    fine_match = re.search(r"multa\s+de\s+(\d+)\s+alug", contract_text, re.IGNORECASE)

    if term_match:
        facts["term_months"] = int(term_match.group(1))

    if fine_match:
        facts["penalty_months"] = int(fine_match.group(1))

    return facts


def merge_analysis_items(
    llm_items: list[AnalysisItem],
    deterministic_items: list[AnalysisItem],
) -> list[AnalysisItem]:
    merged: dict[str, AnalysisItem] = {item.clause_name: item for item in llm_items}

    for item in deterministic_items:
        merged[item.clause_name] = item

    return list(merged.values())


def evaluate_rules(
    rules: list[dict[str, object]],
    extracted: dict[str, object],
) -> ContractAnalysisResult:
    items: list[AnalysisItem] = []

    for rule in rules:
        code = str(rule.get("code", "")).upper()

        if code == "MIN_TERM_MONTHS":
            required_term = _coerce_number(rule.get("value"))
            actual_term = _coerce_number(extracted.get("term_months"))

            if required_term is None or actual_term is None:
                continue

            is_critical = actual_term < required_term
            items.append(
                AnalysisItem(
                    clause_name="Prazo de vigencia",
                    status="critical" if is_critical else "conforme",
                    severity="high" if is_critical else "low",
                    current_summary=f"Prazo atual de {actual_term} meses.",
                    policy_rule=f"Prazo minimo exigido: {required_term} meses.",
                    risk_explanation=(
                        "O prazo encontrado esta abaixo da politica minima."
                        if is_critical
                        else "O prazo encontrado atende a politica."
                    ),
                    suggested_adjustment_direction=(
                        f"Solicitar prazo minimo de {required_term} meses."
                        if is_critical
                        else "Nenhum ajuste necessario."
                    ),
                    metadata={
                        "term_months": actual_term,
                        "required_term_months": required_term,
                    },
                )
            )

        if code == "MAX_FINE_MONTHS":
            maximum_fine = _coerce_number(rule.get("value"))
            actual_fine = _coerce_number(extracted.get("penalty_months"))

            if maximum_fine is None or actual_fine is None:
                continue

            is_attention = actual_fine > maximum_fine
            items.append(
                AnalysisItem(
                    clause_name="Multa",
                    status="attention" if is_attention else "conforme",
                    severity="medium" if is_attention else "low",
                    current_summary=f"Multa atual de {actual_fine} alugueis.",
                    policy_rule=f"Multa maxima permitida: {maximum_fine} alugueis.",
                    risk_explanation=(
                        "A multa supera o teto definido pela politica."
                        if is_attention
                        else "A multa esta dentro da politica."
                    ),
                    suggested_adjustment_direction=(
                        f"Reduzir multa para no maximo {maximum_fine} alugueis."
                        if is_attention
                        else "Nenhum ajuste necessario."
                    ),
                    metadata={
                        "penalty_months": actual_fine,
                        "maximum_fine_months": maximum_fine,
                    },
                )
            )

    return ContractAnalysisResult(
        contract_risk_score=max((_score_for_status(item.status) for item in items), default=0),
        items=items,
    )
