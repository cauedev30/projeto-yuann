from app.services.rule_evaluator import evaluate_rules


def test_rule_evaluator_marks_short_term_as_critical() -> None:
    rules = [
        {"code": "MIN_TERM_MONTHS", "value": 60},
    ]
    extracted = {"term_months": 36}

    result = evaluate_rules(rules, extracted)

    assert result.items[0].status == "critical"
    assert result.items[0].clause_name == "Prazo de vigencia"
