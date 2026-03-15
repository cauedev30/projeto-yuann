from app.services.policy_analysis import analyze_contract_against_policy


class OpenAiStub:
    def analyze_contract(self, *, contract_text: str, policy_rules: list[dict]) -> dict:
        return {
            "contract_risk_score": 0,
            "items": [],
        }


def test_policy_analysis_returns_structured_items() -> None:
    result = analyze_contract_against_policy(
        contract_text="Prazo de 36 meses e multa de 6 alugueis",
        policy_rules=[{"code": "MIN_TERM_MONTHS", "value": 60}],
        llm_client=OpenAiStub(),
    )

    assert result.contract_risk_score > 0
    assert result.items[0].suggested_adjustment_direction
