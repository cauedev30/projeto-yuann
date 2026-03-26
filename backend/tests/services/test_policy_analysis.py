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


class HighRiskLlMStub:
    def analyze_contract(self, *, contract_text: str, policy_rules: list[dict]) -> dict:
        return {
            "contract_risk_score": 95,
            "items": [
                {
                    "clause_name": "Redacao ambigua",
                    "status": "attention",
                    "severity": "medium",
                    "current_summary": "Texto com ambiguidade.",
                    "policy_rule": "Clausula deve ser objetiva.",
                    "risk_explanation": "Ambiguidade redacional.",
                    "suggested_adjustment_direction": "Reescrever trecho.",
                    "metadata": {"category": "redacao"},
                }
            ],
        }


def test_policy_analysis_does_not_use_pure_max_between_llm_and_deterministic() -> None:
    result = analyze_contract_against_policy(
        contract_text="Prazo de 60 meses e aluguel mensal de R$ 2.500,00.",
        policy_rules=[
            {"code": "MIN_TERM_MONTHS", "value": 60},
            {"code": "MAX_VALUE", "value": 3000},
        ],
        llm_client=HighRiskLlMStub(),
    )

    assert result.contract_risk_score < 95
    assert result.contract_risk_score <= 50
