from __future__ import annotations

import json
from pathlib import Path

from app.schemas.analysis import AnalysisItem
from tests.support.openai_benchmark import (
    BenchmarkPricing,
    BenchmarkVersionResult,
    compare_version_results,
    derive_item_identifier,
    estimate_analysis_cost_usd,
    evaluate_diff_expectations,
    evaluate_version_expectations,
    load_benchmark_cases,
)


def test_estimate_analysis_cost_uses_per_million_rates() -> None:
    pricing = BenchmarkPricing(input_cost_per_1m=0.25, output_cost_per_1m=2.0)

    result = estimate_analysis_cost_usd(
        prompt_tokens=2000,
        completion_tokens=500,
        pricing=pricing,
    )

    assert result == 0.0015


def test_derive_item_identifier_prefers_clause_code_metadata() -> None:
    item = AnalysisItem(
        clause_name="Prazo de vigencia",
        status="critical",
        severity="high",
        current_summary="Prazo atual de 24 meses.",
        policy_rule="Minimo de 48 meses.",
        risk_explanation="Prazo abaixo do minimo.",
        suggested_adjustment_direction="Aumentar prazo.",
        metadata={"clause_code": "PRAZO"},
    )

    assert derive_item_identifier(item) == "prazo"


def test_evaluate_version_expectations_reports_hits_and_violations() -> None:
    version_result = BenchmarkVersionResult(
        label="v1",
        final_risk_score=61.5,
        observed_identifiers={"prazo", "exclusividade", "valor"},
        prompt_tokens=1200,
        completion_tokens=220,
        total_tokens=1420,
        estimated_cost_usd=0.00074,
    )

    evaluation = evaluate_version_expectations(
        version_result=version_result,
        must_include_identifiers=("PRAZO", "EXCLUSIVIDADE"),
        must_exclude_identifiers=("ASSINATURAS",),
        min_expected_score=55,
        max_expected_score=80,
    )

    assert evaluation["missing_identifiers"] == []
    assert evaluation["unexpected_identifiers"] == []
    assert evaluation["score_within_expected_range"] is True
    assert evaluation["quality_passed"] is True


def test_compare_version_results_tracks_identifier_changes_and_score_drop() -> None:
    previous = BenchmarkVersionResult(
        label="v1",
        final_risk_score=72.0,
        observed_identifiers={"prazo", "exclusividade", "valor"},
        prompt_tokens=1000,
        completion_tokens=200,
        total_tokens=1200,
        estimated_cost_usd=0.00065,
    )
    current = BenchmarkVersionResult(
        label="v2",
        final_risk_score=24.0,
        observed_identifiers={"assinaturas"},
        prompt_tokens=900,
        completion_tokens=180,
        total_tokens=1080,
        estimated_cost_usd=0.00058,
    )

    diff = compare_version_results(previous, current)

    assert diff["score_delta"] == -48.0
    assert diff["changed_identifiers"] == [
        "assinaturas",
        "exclusividade",
        "prazo",
        "valor",
    ]


def test_evaluate_diff_expectations_supports_count_and_score_drop_gates() -> None:
    diff = {
        "changed_identifiers": ["exclusividade", "prazo", "valor"],
        "score_delta": -48.0,
    }

    evaluation = evaluate_diff_expectations(
        diff=diff,
        expected_identifiers=("EXCLUSIVIDADE",),
        min_changed_identifiers=3,
        min_score_drop=40.0,
    )

    assert evaluation["missing_expected_identifiers"] == []
    assert evaluation["changed_identifiers_count"] == 3
    assert evaluation["score_drop_passed"] is True
    assert evaluation["diff_passed"] is True


def test_load_benchmark_cases_accepts_custom_json_file(tmp_path: Path) -> None:
    cases_path = tmp_path / "cases.json"
    cases_path.write_text(
        json.dumps(
            [
                {
                    "scenario_id": "custom",
                    "title": "Custom benchmark case",
                    "versions": [
                        {
                            "label": "v1",
                            "text": "Prazo de vigencia de 24 meses.",
                            "must_include_identifiers": ["PRAZO"],
                            "max_expected_score": 90,
                        }
                    ],
                    "expected_diff_identifiers": ["PRAZO"],
                }
            ]
        ),
        encoding="utf-8",
    )

    cases = load_benchmark_cases(cases_path)

    assert len(cases) == 1
    assert cases[0].scenario_id == "custom"
    assert cases[0].versions[0].must_include_identifiers == ("PRAZO",)
