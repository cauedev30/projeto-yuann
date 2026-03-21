"""Tests for GeminiAnalysisClient with mocked google.genai SDK."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from app.domain.playbook import PlaybookClause
from app.infrastructure.gemini_client import GeminiAnalysisClient
from app.infrastructure.gemini_models import (
    ContractAnalysisResult,
    ContractSummaryResult,
    CorrectedContractResult,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_playbook() -> list[PlaybookClause]:
    return [
        PlaybookClause(
            code="INFRAESTRUTURA",
            title="Ciência da Infraestrutura",
            full_text="O LOCADOR manifesta ciência quanto à necessidade de infraestrutura.",
            category="infraestrutura",
        ),
        PlaybookClause(
            code="PRAZO",
            title="Do Prazo",
            full_text="Contrato renovado automaticamente por igual período.",
            category="temporal",
        ),
    ]


VALID_ANALYSIS_JSON = """{
    "contract_risk_score": 45,
    "items": [
        {
            "clause_code": "INFRAESTRUTURA",
            "clause_title": "Ciência da Infraestrutura",
            "severity": "attention",
            "risk_score": 45,
            "explanation": "Clausula presente mas incompleta. Falta menção a rede trifásica.",
            "suggested_correction": "Incluir referência à rede trifásica.",
            "page_reference": "p.2"
        }
    ],
    "summary": "Contrato com risco moderado."
}"""

VALID_SUMMARY_JSON = """{
    "summary": "Resumo do contrato de locação.",
    "key_points": ["Prazo de 60 meses", "Aluguel R$ 3.000"]
}"""

VALID_CORRECTION_JSON = """{
    "corrected_text": "Contrato corrigido completo aqui.",
    "corrections": [
        {
            "clause_name": "INFRAESTRUTURA",
            "original_text": "Texto antigo",
            "corrected_text": "Texto novo",
            "reason": "Adequação ao playbook"
        }
    ]
}"""


def _make_mock_response(text: str) -> MagicMock:
    """Create a mock genai response with the given text."""
    response = MagicMock()
    response.text = text
    return response


# ---------------------------------------------------------------------------
# analyze_contract
# ---------------------------------------------------------------------------

class TestAnalyzeContract:
    """Tests for GeminiAnalysisClient.analyze_contract."""

    @patch("app.infrastructure.gemini_client.genai")
    def test_returns_validated_result(self, mock_genai, sample_playbook):
        mock_client = MagicMock()
        mock_genai.Client.return_value = mock_client
        mock_client.models.generate_content.return_value = _make_mock_response(
            VALID_ANALYSIS_JSON
        )

        client = GeminiAnalysisClient(api_key="fake-key")
        result = client.analyze_contract(
            chunks=["Texto do contrato parte 1", "Texto parte 2"],
            playbook=sample_playbook,
        )

        assert isinstance(result, ContractAnalysisResult)
        assert result.contract_risk_score == 45
        assert len(result.items) == 1
        assert result.items[0].clause_code == "INFRAESTRUTURA"
        assert result.items[0].severity == "attention"
        assert result.summary == "Contrato com risco moderado."
        mock_client.models.generate_content.assert_called_once()

    @patch("app.infrastructure.gemini_client.genai")
    def test_concatenates_chunks_with_separator(self, mock_genai, sample_playbook):
        mock_client = MagicMock()
        mock_genai.Client.return_value = mock_client
        mock_client.models.generate_content.return_value = _make_mock_response(
            VALID_ANALYSIS_JSON
        )

        client = GeminiAnalysisClient(api_key="fake-key")
        client.analyze_contract(
            chunks=["Chunk A", "Chunk B", "Chunk C"],
            playbook=sample_playbook,
        )

        call_args = mock_client.models.generate_content.call_args
        contents_arg = call_args.kwargs.get("contents") or call_args[1].get("contents")
        assert "Chunk A" in contents_arg
        assert "Chunk B" in contents_arg
        assert "Chunk C" in contents_arg

    @patch("app.infrastructure.gemini_client.time.sleep")
    @patch("app.infrastructure.gemini_client.genai")
    def test_retry_on_api_error(self, mock_genai, _mock_sleep, sample_playbook):
        mock_client = MagicMock()
        mock_genai.Client.return_value = mock_client
        mock_client.models.generate_content.side_effect = [
            Exception("API error"),
            _make_mock_response(VALID_ANALYSIS_JSON),
        ]

        client = GeminiAnalysisClient(api_key="fake-key")
        result = client.analyze_contract(
            chunks=["Texto"],
            playbook=sample_playbook,
        )

        assert isinstance(result, ContractAnalysisResult)
        assert result.contract_risk_score == 45
        assert mock_client.models.generate_content.call_count == 2

    @patch("app.infrastructure.gemini_client.time.sleep")
    @patch("app.infrastructure.gemini_client.genai")
    def test_returns_failed_result_after_retries_exhausted(self, mock_genai, _mock_sleep, sample_playbook):
        mock_client = MagicMock()
        mock_genai.Client.return_value = mock_client
        mock_client.models.generate_content.side_effect = Exception("Persistent error")

        client = GeminiAnalysisClient(api_key="fake-key")
        result = client.analyze_contract(
            chunks=["Texto"],
            playbook=sample_playbook,
        )

        assert isinstance(result, ContractAnalysisResult)
        assert result.contract_risk_score == 0
        assert result.items == []
        assert "failed" in result.summary.lower() or "Persistent error" in result.summary

    @patch("app.infrastructure.gemini_client.time.sleep")
    @patch("app.infrastructure.gemini_client.genai")
    def test_returns_failed_on_validation_error(self, mock_genai, _mock_sleep, sample_playbook):
        mock_client = MagicMock()
        mock_genai.Client.return_value = mock_client
        mock_client.models.generate_content.return_value = _make_mock_response(
            '{"invalid": "json structure"}'
        )

        client = GeminiAnalysisClient(api_key="fake-key")
        result = client.analyze_contract(
            chunks=["Texto"],
            playbook=sample_playbook,
        )

        assert isinstance(result, ContractAnalysisResult)
        assert result.contract_risk_score == 0
        assert result.items == []
        assert "failed" in result.summary.lower() or "Analysis failed" in result.summary


# ---------------------------------------------------------------------------
# summarize_contract
# ---------------------------------------------------------------------------

class TestSummarizeContract:
    """Tests for GeminiAnalysisClient.summarize_contract."""

    @patch("app.infrastructure.gemini_client.genai")
    def test_returns_validated_result(self, mock_genai):
        mock_client = MagicMock()
        mock_genai.Client.return_value = mock_client
        mock_client.models.generate_content.return_value = _make_mock_response(
            VALID_SUMMARY_JSON
        )

        client = GeminiAnalysisClient(api_key="fake-key")
        result = client.summarize_contract(text="Texto completo do contrato.")

        assert isinstance(result, ContractSummaryResult)
        assert result.summary == "Resumo do contrato de locação."
        assert len(result.key_points) == 2

    @patch("app.infrastructure.gemini_client.time.sleep")
    @patch("app.infrastructure.gemini_client.genai")
    def test_retry_on_error(self, mock_genai, _mock_sleep):
        mock_client = MagicMock()
        mock_genai.Client.return_value = mock_client
        mock_client.models.generate_content.side_effect = [
            Exception("Timeout"),
            _make_mock_response(VALID_SUMMARY_JSON),
        ]

        client = GeminiAnalysisClient(api_key="fake-key")
        result = client.summarize_contract(text="Texto")

        assert isinstance(result, ContractSummaryResult)
        assert result.summary == "Resumo do contrato de locação."
        assert mock_client.models.generate_content.call_count == 2

    @patch("app.infrastructure.gemini_client.time.sleep")
    @patch("app.infrastructure.gemini_client.genai")
    def test_returns_failed_after_retries(self, mock_genai, _mock_sleep):
        mock_client = MagicMock()
        mock_genai.Client.return_value = mock_client
        mock_client.models.generate_content.side_effect = Exception("Permanent failure")

        client = GeminiAnalysisClient(api_key="fake-key")
        result = client.summarize_contract(text="Texto")

        assert isinstance(result, ContractSummaryResult)
        assert "failed" in result.summary.lower() or "Permanent failure" in result.summary
        assert result.key_points == []


# ---------------------------------------------------------------------------
# generate_corrected_contract
# ---------------------------------------------------------------------------

class TestGenerateCorrectedContract:
    """Tests for GeminiAnalysisClient.generate_corrected_contract."""

    @patch("app.infrastructure.gemini_client.genai")
    def test_returns_validated_result(self, mock_genai, sample_playbook):
        mock_client = MagicMock()
        mock_genai.Client.return_value = mock_client
        mock_client.models.generate_content.return_value = _make_mock_response(
            VALID_CORRECTION_JSON
        )

        client = GeminiAnalysisClient(api_key="fake-key")
        findings = [
            {
                "clause_name": "INFRAESTRUTURA",
                "status": "attention",
                "suggested_adjustment_direction": "Incluir rede trifásica.",
            }
        ]
        result = client.generate_corrected_contract(
            original="Contrato original.",
            findings=findings,
            playbook=sample_playbook,
        )

        assert isinstance(result, CorrectedContractResult)
        assert result.corrected_text == "Contrato corrigido completo aqui."
        assert len(result.corrections) == 1
        assert result.corrections[0].clause_name == "INFRAESTRUTURA"

    @patch("app.infrastructure.gemini_client.time.sleep")
    @patch("app.infrastructure.gemini_client.genai")
    def test_returns_failed_after_retries(self, mock_genai, _mock_sleep, sample_playbook):
        mock_client = MagicMock()
        mock_genai.Client.return_value = mock_client
        mock_client.models.generate_content.side_effect = Exception("Error")

        client = GeminiAnalysisClient(api_key="fake-key")
        result = client.generate_corrected_contract(
            original="Contrato.",
            findings=[],
            playbook=sample_playbook,
        )

        assert isinstance(result, CorrectedContractResult)
        assert result.corrected_text == ""
        assert result.corrections == []


# ---------------------------------------------------------------------------
# Constructor
# ---------------------------------------------------------------------------

class TestConstructor:
    """Tests for GeminiAnalysisClient constructor."""

    @patch("app.infrastructure.gemini_client.genai")
    def test_default_model(self, mock_genai):
        client = GeminiAnalysisClient(api_key="test-key")
        assert client._model == "gemini-2.5-flash"

    @patch("app.infrastructure.gemini_client.genai")
    def test_custom_model(self, mock_genai):
        client = GeminiAnalysisClient(api_key="test-key", model="gemini-2.5-pro")
        assert client._model == "gemini-2.5-pro"
