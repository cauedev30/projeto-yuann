from __future__ import annotations

import re
import unicodedata

from app.schemas.analysis import AnalysisItem, ContractAnalysisResult


CATEGORY_WEIGHTS = {
    "essencial": 55,
    "prazo": 35,
    "financeiro": 32,
    "garantia": 28,
    "operacional": 22,
    "infraestrutura": 24,
    "comercial": 26,
    "temporal": 18,
    "redacao": 14,
    "other": 16,
}

CLASSIFICATION_TO_STATUS = {
    "adequada": "conforme",
    "risco_medio": "attention",
    "ausente": "critical",
    "conflitante": "critical",
}

STATUS_MULTIPLIERS = {
    "critical": 1.0,
    "attention": 0.55,
    "conforme": 0.0,
}

SEVERITY_MULTIPLIERS = {
    "high": 1.0,
    "medium": 0.75,
    "low": 0.35,
}


def _coerce_number(value: object) -> int | None:
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str) and value.isdigit():
        return int(value)
    return None


def _parse_brl(raw: str) -> float | None:
    cleaned = raw.strip().rstrip(".,;:").replace(".", "").replace(",", ".")
    try:
        return float(cleaned)
    except ValueError:
        return None


def extract_contract_facts(contract_text: str) -> dict[str, object]:
    facts: dict[str, object] = {}

    # Term months: use specific patterns to avoid matching reajuste/other periods
    term_patterns = [
        r"prazo\s+do\s+presente\s+contrato\s+[eé]\s+de\s+(\d+)\s*(?:\([^)]*\)\s*)?meses",
        r"prazo\s+de\s+vig[eê]ncia\s*(?::\s*|\s+[eé]\s+de\s+)(\d+)\s*(?:\([^)]*\)\s*)?meses",
        r"prazo\s+contratual\s*(?::\s*|\s+[eé]\s+de\s+)(\d+)\s*(?:\([^)]*\)\s*)?meses",
        r"prazo\s+de\s+(\d+)\s*(?:\([^)]*\)\s*)?meses",
        r"vig[eê]ncia\s+de\s+(\d+)\s*(?:\([^)]*\)\s*)?meses",
        r"(\d+)\s*meses",  # generic fallback
    ]
    for pattern in term_patterns:
        m = re.search(pattern, contract_text, re.IGNORECASE)
        if m:
            facts["term_months"] = int(m.group(1))
            break

    # Penalty: "multa ... NN vezes" or "multa de NN aluguéis"
    fine_patterns = [
        r"multa\s+.*?(\d+)\s*(?:\([^)]*\)\s*)?vezes\s+o\s+valor",
        r"multa\s+de\s+(\d+)\s+alug",
        r"equivalente\s+a\s+(\d+)\s*(?:\([^)]*\)\s*)?(?:vezes|alug)",
    ]
    for pattern in fine_patterns:
        m = re.search(pattern, contract_text, re.IGNORECASE)
        if m:
            facts["penalty_months"] = int(m.group(1))
            break

    # Contract value: prefer explicit aluguel context over any R$ value
    value_patterns = [
        r"aluguel\s+mensal\s+(?:de\s+)?R\$\s*([\d.,]+)",
        r"aluguel\s+mensal\s+ser[aá]\s+de\s+R\$\s*([\d.,]+)",
        r"valor\s+(?:do\s+)?aluguel\s*(?::\s*|de\s+|ser[aá]\s+de\s+)R\$\s*([\d.,]+)",
        r"aluguel\s+(?:de\s+)?R\$\s*([\d.,]+)",
        r"R\$\s*([\d.,]+)\s*(?:\([^)]*\)\s*)?[,.]?\s*(?:mensal|mensais|por\s+m[eê]s|de\s+aluguel)",
        r"R\$\s*([\d.,]+)",  # generic fallback
    ]
    for pattern in value_patterns:
        m = re.search(pattern, contract_text, re.IGNORECASE)
        if m:
            parsed = _parse_brl(m.group(1))
            if parsed is not None:
                facts["contract_value"] = parsed
                break

    # Grace period
    grace_days_match = re.search(
        r"car[eê]ncia\s*(?:de\s*)?(\d+)\s*dias", contract_text, re.IGNORECASE
    )
    grace_months_match = re.search(
        r"car[eê]ncia\s*(?:de\s*)?(\d+)\s*meses", contract_text, re.IGNORECASE
    )

    if grace_days_match:
        facts["grace_period_days"] = int(grace_days_match.group(1))
    elif grace_months_match:
        facts["grace_period_days"] = int(grace_months_match.group(1)) * 30

    return facts


def _normalize_clause_key(name: str) -> str:
    normalized = unicodedata.normalize("NFD", name)
    stripped = "".join(c for c in normalized if unicodedata.category(c) != "Mn")
    return stripped.strip().lower()


def _score_items(items: list[AnalysisItem], *, source: str) -> float:
    total = 0.0
    source_multiplier = 0.45 if source == "llm" else 1.0

    for item in items:
        status_multiplier = STATUS_MULTIPLIERS.get(item.status, 0.0)
        if status_multiplier == 0:
            continue

        severity_multiplier = SEVERITY_MULTIPLIERS.get(item.severity, 0.55)
        category = str(item.metadata.get("category", "other")).lower()
        weight = CATEGORY_WEIGHTS.get(category, CATEGORY_WEIGHTS["other"])
        if item.metadata.get("essential_clause"):
            weight = max(weight, CATEGORY_WEIGHTS["essencial"])

        item_score = (
            weight * status_multiplier * severity_multiplier * source_multiplier
        )
        if item.metadata.get("essential_clause") and item.status == "critical":
            item_score += 8
        if item.metadata.get("missing_clause") and item.status == "critical":
            item_score += 12

        total += item_score

    return total


def calculate_final_risk_score(
    *,
    llm_score: float,
    llm_items: list[AnalysisItem],
    deterministic_items: list[AnalysisItem],
) -> float:
    llm_component = min(float(llm_score) * 0.18, 18.0)
    llm_item_component = _score_items(llm_items, source="llm")
    deterministic_component = _score_items(deterministic_items, source="deterministic")
    final_score = min(
        llm_component + llm_item_component + deterministic_component, 100.0
    )
    return round(final_score, 2)


def merge_analysis_items(
    llm_items: list[AnalysisItem],
    deterministic_items: list[AnalysisItem],
) -> list[AnalysisItem]:
    merged: dict[str, AnalysisItem] = {
        _normalize_clause_key(item.clause_name): item for item in llm_items
    }

    for item in deterministic_items:
        merged[_normalize_clause_key(item.clause_name)] = item

    return list(merged.values())


def evaluate_rules(
    rules: list[dict[str, object]],
    extracted: dict[str, object],
) -> ContractAnalysisResult:
    items: list[AnalysisItem] = []

    actual_term = _coerce_number(extracted.get("term_months"))
    min_term = next(
        (
            _coerce_number(r.get("value"))
            for r in rules
            if str(r.get("code", "")).upper() == "MIN_TERM_MONTHS"
        ),
        None,
    )
    max_term = next(
        (
            _coerce_number(r.get("value"))
            for r in rules
            if str(r.get("code", "")).upper() == "MAX_TERM_MONTHS"
        ),
        None,
    )

    if actual_term is not None and (min_term is not None or max_term is not None):
        is_critical_min = min_term is not None and actual_term < min_term
        is_critical_max = max_term is not None and actual_term > max_term
        is_critical = is_critical_min or is_critical_max

        policy_str_parts = []
        if min_term is not None:
            policy_str_parts.append(f"Minimo: {min_term} meses")
        if max_term is not None:
            policy_str_parts.append(f"Maximo: {max_term} meses")

        if is_critical_min:
            explanation = "O prazo encontrado esta abaixo da politica minima."
            suggestion = f"Solicitar prazo minimo de {min_term} meses."
        elif is_critical_max:
            explanation = "O prazo encontrado excede o maximo da politica."
            suggestion = f"Reduzir prazo para no maximo {max_term} meses."
        else:
            explanation = "O prazo encontrado atende a politica."
            suggestion = "Nenhum ajuste necessario."

        items.append(
            AnalysisItem(
                clause_name="Prazo de vigencia",
                status="critical" if is_critical else "conforme",
                severity="high" if is_critical else "low",
                current_summary=f"Prazo atual de {actual_term} meses.",
                policy_rule=" | ".join(policy_str_parts),
                risk_explanation=explanation,
                suggested_adjustment_direction=suggestion,
                metadata={
                    "term_months": actual_term,
                    "min_term_months": min_term,
                    "max_term_months": max_term,
                    "category": "prazo",
                    "essential_clause": True,
                    "missing_clause": actual_term is None,
                },
            )
        )

    for rule in rules:
        code = str(rule.get("code", "")).upper()

        if code in ("MIN_TERM_MONTHS", "MAX_TERM_MONTHS"):
            continue

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
                        "category": "financeiro",
                    },
                )
            )

        if code == "MAX_VALUE":
            max_value = _coerce_number(rule.get("value"))
            actual_value_raw = extracted.get("contract_value")
            actual_value = None
            if isinstance(actual_value_raw, (int, float)):
                actual_value = (
                    int(actual_value_raw)
                    if isinstance(actual_value_raw, float)
                    and actual_value_raw == int(actual_value_raw)
                    else actual_value_raw
                )

            if max_value is None or actual_value is None:
                continue

            is_critical = float(actual_value) > float(max_value)
            items.append(
                AnalysisItem(
                    clause_name="Valor do contrato",
                    status="critical" if is_critical else "conforme",
                    severity="high" if is_critical else "low",
                    current_summary=f"Valor atual de R$ {actual_value}.",
                    policy_rule=f"Valor maximo permitido: R$ {max_value}.",
                    risk_explanation=(
                        "O valor do contrato excede o teto definido pela politica."
                        if is_critical
                        else "O valor do contrato esta dentro da politica."
                    ),
                    suggested_adjustment_direction=(
                        f"Renegociar valor para no maximo R$ {max_value}."
                        if is_critical
                        else "Nenhum ajuste necessario."
                    ),
                    metadata={
                        "contract_value": float(actual_value),
                        "maximum_value": float(max_value),
                        "category": "financeiro",
                        "essential_clause": True,
                    },
                )
            )

        if code == "GRACE_PERIOD_DAYS":
            allowed_raw = rule.get("value")
            allowed_values = (
                allowed_raw if isinstance(allowed_raw, list) else [allowed_raw]
            )
            allowed_days = [int(v) for v in allowed_values if v is not None]
            actual_grace = _coerce_number(extracted.get("grace_period_days"))

            if not allowed_days or actual_grace is None:
                continue

            is_attention = actual_grace not in allowed_days
            items.append(
                AnalysisItem(
                    clause_name="Periodo de carencia",
                    status="attention" if is_attention else "conforme",
                    severity="medium" if is_attention else "low",
                    current_summary=f"Carencia atual de {actual_grace} dias.",
                    policy_rule=f"Valores de carencia permitidos: {allowed_days} dias.",
                    risk_explanation=(
                        "O periodo de carencia nao esta entre os valores permitidos pela politica."
                        if is_attention
                        else "O periodo de carencia atende a politica."
                    ),
                    suggested_adjustment_direction=(
                        f"Ajustar carencia para um dos valores permitidos: {allowed_days} dias."
                        if is_attention
                        else "Nenhum ajuste necessario."
                    ),
                    metadata={
                        "grace_period_days": actual_grace,
                        "allowed_grace_period_days": allowed_days,
                        "category": "operacional",
                    },
                )
            )

    return ContractAnalysisResult(
        contract_risk_score=calculate_final_risk_score(
            llm_score=0,
            llm_items=[],
            deterministic_items=items,
        ),
        items=items,
    )
