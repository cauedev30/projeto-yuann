from __future__ import annotations

from typing import Protocol

from app.domain.contract_analysis import (
    calculate_final_risk_score,
    evaluate_rules,
    extract_contract_facts,
    merge_analysis_items,
)
from app.schemas.analysis import ContractAnalysisResult


class AnalysisLLMClient(Protocol):
    def analyze_contract(self, *, contract_text: str, policy_rules: list[dict]) -> dict: ...

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
    merged_items = merge_analysis_items(llm_result.items, deterministic_result.items)
    risk_score = calculate_final_risk_score(
        llm_score=float(llm_result.contract_risk_score),
        llm_items=llm_result.items,
        deterministic_items=deterministic_result.items,
    )

    return ContractAnalysisResult(contract_risk_score=risk_score, items=merged_items)
