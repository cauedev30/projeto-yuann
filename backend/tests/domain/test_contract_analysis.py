from app.schemas.analysis import AnalysisItem

from app.domain.contract_analysis import merge_analysis_items


def test_merge_analysis_items_prefers_deterministic_result_for_same_clause() -> None:
    llm_items = [
        AnalysisItem(
            clause_name="Prazo de vigencia",
            status="attention",
            severity="medium",
            risk_explanation="LLM",
            current_summary="36 meses",
            policy_rule="60 meses",
            suggested_adjustment_direction="Revisar",
            metadata={},
        )
    ]
    deterministic_items = [
        AnalysisItem(
            clause_name="Prazo de vigencia",
            status="critical",
            severity="high",
            risk_explanation="Deterministico",
            current_summary="36 meses",
            policy_rule="60 meses",
            suggested_adjustment_direction="Solicitar prazo minimo",
            metadata={},
        )
    ]

    merged = merge_analysis_items(llm_items, deterministic_items)

    assert merged[0].status == "critical"
    assert merged[0].risk_explanation == "Deterministico"
