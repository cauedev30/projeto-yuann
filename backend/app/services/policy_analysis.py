from __future__ import annotations

import re
from typing import Protocol

from app.schemas.analysis import AnalysisItem, ContractAnalysisResult
from app.services.rule_evaluator import evaluate_rules


class AnalysisLLMClient(Protocol):
    def analyze_contract(self, *, contract_text: str, policy_rules: list[dict]) -> dict: ...


def extract_contract_facts(contract_text: str) -> dict[str, int]:
    facts: dict[str, int] = {}

    term_match = re.search(r"(\d+)\s*meses", contract_text, re.IGNORECASE)
    fine_match = re.search(r"multa\s+de\s+(\d+)\s+alug", contract_text, re.IGNORECASE)

    if term_match:
        facts["term_months"] = int(term_match.group(1))

    if fine_match:
        facts["penalty_months"] = int(fine_match.group(1))

    return facts


def _merge_items(
    llm_items: list[AnalysisItem],
    deterministic_items: list[AnalysisItem],
) -> list[AnalysisItem]:
    merged: dict[str, AnalysisItem] = {item.clause_name: item for item in llm_items}

    for item in deterministic_items:
        merged[item.clause_name] = item

    return list(merged.values())


def analyze_contract_against_policy(
    *,
    contract_text: str,
    policy_rules: list[dict],
    llm_client: AnalysisLLMClient,
) -> ContractAnalysisResult:
    llm_payload = llm_client.analyze_contract(
        contract_text=contract_text,
        policy_rules=policy_rules,
    )
    llm_result = ContractAnalysisResult.model_validate(llm_payload)

    extracted_facts = extract_contract_facts(contract_text)
    deterministic_result = evaluate_rules(policy_rules, extracted_facts)
    merged_items = _merge_items(llm_result.items, deterministic_result.items)
    risk_score = max(llm_result.contract_risk_score, deterministic_result.contract_risk_score)

    return ContractAnalysisResult(contract_risk_score=risk_score, items=merged_items)
