from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from app.domain.playbook import PlaybookClause
from app.infrastructure.llm_models import (
    AnalysisFindingItem,
    ContractAnalysisResult,
    ContractSummaryResult,
    CorrectedContractResult,
    CorrectionItem,
    LLMTokenUsage,
)
from app.infrastructure.openai_client import OpenAIAnalysisClient


@pytest.fixture
def sample_playbook() -> list[PlaybookClause]:
    return [
        PlaybookClause(
            code="PRAZO",
            title="Prazo contratual",
            full_text="O contrato deve prever prazo minimo de 60 meses.",
            category="temporal",
        ),
        PlaybookClause(
            code="EXCLUSIVIDADE",
            title="Exclusividade da operacao",
            full_text="O locador nao pode instalar lavanderia concorrente no mesmo imovel.",
            category="essencial",
        ),
    ]


def _make_completion(parsed) -> SimpleNamespace:
    return SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(parsed=parsed))]
    )


@patch("app.infrastructure.openai_client.openai")
def test_openai_client_uses_gpt_5_mini_by_default(mock_openai) -> None:
    mock_openai.OpenAI.return_value = MagicMock()

    client = OpenAIAnalysisClient(api_key="test-key")

    assert client._model == "gpt-5-mini"


@patch("app.infrastructure.openai_client.openai")
def test_analyze_contract_returns_typed_result(mock_openai, sample_playbook) -> None:
    parsed = ContractAnalysisResult(
        contract_risk_score=47,
        summary="Contrato com risco juridico moderado.",
        items=[
            AnalysisFindingItem(
                clause_code="PRAZO",
                clause_title="Prazo contratual",
                severity="critical",
                risk_score=47,
                explanation="O contrato nao fixa prazo minimo compativel com o playbook.",
                suggested_correction="Ajustar o prazo para no minimo 60 meses.",
                page_reference="p. 2",
            )
        ],
    )
    sdk_client = MagicMock()
    completion = _make_completion(parsed)
    completion.usage = SimpleNamespace(
        prompt_tokens=1800,
        completion_tokens=250,
        total_tokens=2050,
    )
    sdk_client.beta.chat.completions.parse.return_value = completion
    mock_openai.OpenAI.return_value = sdk_client

    client = OpenAIAnalysisClient(api_key="test-key")
    result = client.analyze_contract(
        chunks=["Prazo de vigencia de 24 meses."],
        playbook=sample_playbook,
    )

    assert result.contract_risk_score == 47
    assert result.items[0].clause_code == "PRAZO"
    assert client.last_analysis_usage == LLMTokenUsage(
        prompt_tokens=1800,
        completion_tokens=250,
        total_tokens=2050,
    )
    sdk_client.beta.chat.completions.parse.assert_called_once()
    assert "temperature" not in sdk_client.beta.chat.completions.parse.call_args.kwargs


@patch("app.infrastructure.openai_client.openai")
def test_summarize_contract_returns_typed_result(mock_openai) -> None:
    parsed = ContractSummaryResult(
        summary="Resumo executivo em portugues.",
        key_points=["Prazo de 60 meses", "Aluguel de R$ 3.000,00"],
    )
    sdk_client = MagicMock()
    sdk_client.beta.chat.completions.parse.return_value = _make_completion(parsed)
    mock_openai.OpenAI.return_value = sdk_client

    client = OpenAIAnalysisClient(api_key="test-key")
    result = client.summarize_contract("Texto do contrato")

    assert result.summary == "Resumo executivo em portugues."
    assert len(result.key_points) == 2
    assert "temperature" not in sdk_client.beta.chat.completions.parse.call_args.kwargs


@patch("app.infrastructure.openai_client.openai")
def test_generate_corrected_contract_returns_typed_result(mock_openai, sample_playbook) -> None:
    parsed = CorrectedContractResult(
        corrected_text="Contrato corrigido completo.",
        corrections=[
            CorrectionItem(
                clause_name="PRAZO",
                original_text="Prazo de 24 meses.",
                corrected_text="Prazo de 60 meses.",
                reason="Adequacao ao playbook.",
            )
        ],
    )
    sdk_client = MagicMock()
    sdk_client.beta.chat.completions.parse.return_value = _make_completion(parsed)
    mock_openai.OpenAI.return_value = sdk_client

    client = OpenAIAnalysisClient(api_key="test-key")
    result = client.generate_corrected_contract(
        original="Contrato original",
        findings=[{"clause_code": "PRAZO", "severity": "critical"}],
        playbook=sample_playbook,
    )

    assert result.corrected_text == "Contrato corrigido completo."
    assert result.corrections[0].clause_name == "PRAZO"
    assert "temperature" not in sdk_client.beta.chat.completions.parse.call_args.kwargs


@patch("app.infrastructure.openai_client.openai")
def test_analyze_contract_returns_typed_fallback_on_failure(mock_openai, sample_playbook) -> None:
    sdk_client = MagicMock()
    sdk_client.beta.chat.completions.parse.side_effect = RuntimeError("upstream timeout")
    mock_openai.OpenAI.return_value = sdk_client

    client = OpenAIAnalysisClient(api_key="test-key")
    result = client.analyze_contract(
        chunks=["Contrato"],
        playbook=sample_playbook,
    )

    assert result.contract_risk_score == 0
    assert result.items == []
    assert "upstream timeout" in result.summary
    assert client.last_analysis_usage is None
