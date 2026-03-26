"""Tests for OpenAI prompts with playbook-based analysis."""

import pytest

from app.domain.playbook import PlaybookClause
from app.infrastructure.prompts import (
    CORRECTION_SYSTEM_PROMPT,
    SUMMARY_SYSTEM_PROMPT,
    SYSTEM_PROMPT,
    build_correction_prompt,
    build_user_prompt,
    build_summary_user_prompt,
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
            full_text="Contrato renovado automaticamente por igual período com aviso de 90 dias.",
            category="temporal",
        ),
        PlaybookClause(
            code="EXCLUSIVIDADE",
            title="Da Exclusividade",
            full_text="O LOCADOR não locará espaço para atividades de lavanderia concorrentes.",
            category="comercial",
        ),
    ]


SAMPLE_CONTRACT = "Contrato de locação entre LOCADOR e LOCATÁRIO com prazo de 60 meses."


# ---------------------------------------------------------------------------
# SYSTEM_PROMPT tests
# ---------------------------------------------------------------------------

class TestSystemPrompt:
    def test_references_playbook(self):
        assert "playbook" in SYSTEM_PROMPT.lower()

    def test_contains_severity_criteria(self):
        assert "critical" in SYSTEM_PROMPT
        assert "attention" in SYSTEM_PROMPT

    def test_requires_pt_br_only(self):
        assert "PT-BR" in SYSTEM_PROMPT

    def test_requires_legal_checks_for_lease_law(self):
        assert "Lei 8.245" in SYSTEM_PROMPT
        assert "cessao" in SYSTEM_PROMPT.lower()
        assert "subloc" in SYSTEM_PROMPT.lower()
        assert "garantia" in SYSTEM_PROMPT.lower()

    def test_requires_auditable_score_justification(self):
        assert "score" in SYSTEM_PROMPT.lower()
        assert "justific" in SYSTEM_PROMPT.lower()

    def test_requires_essential_clause_presence_or_absence_checks(self):
        prompt = SYSTEM_PROMPT.lower()
        assert "exclusividade" in prompt
        assert "prazo" in prompt
        assert "reajuste" in prompt
        assert "vistorias" in prompt
        assert "obras" in prompt
        assert "infraestrutura" in prompt
        assert "fiador" in prompt


# ---------------------------------------------------------------------------
# SUMMARY_SYSTEM_PROMPT tests
# ---------------------------------------------------------------------------

class TestSummarySystemPrompt:
    def test_still_has_instructions(self):
        assert "resumo" in SUMMARY_SYSTEM_PROMPT.lower()
        assert "portugues brasileiro" in SUMMARY_SYSTEM_PROMPT.lower()


# ---------------------------------------------------------------------------
# CORRECTION_SYSTEM_PROMPT tests
# ---------------------------------------------------------------------------

class TestCorrectionSystemPrompt:
    def test_exists_and_references_correction(self):
        assert "corrig" in CORRECTION_SYSTEM_PROMPT.lower() or "correc" in CORRECTION_SYSTEM_PROMPT.lower()

    def test_references_playbook(self):
        assert "playbook" in CORRECTION_SYSTEM_PROMPT.lower()

    def test_references_findings(self):
        # Should mention findings / achados
        assert "achado" in CORRECTION_SYSTEM_PROMPT.lower() or "finding" in CORRECTION_SYSTEM_PROMPT.lower()

    def test_requires_preserving_business_data(self):
        prompt = CORRECTION_SYSTEM_PROMPT.lower()
        assert "95% do contrato original intacto" in prompt
        assert "nomes das partes" in prompt
        assert "valores de aluguel" in prompt


# ---------------------------------------------------------------------------
# build_user_prompt tests
# ---------------------------------------------------------------------------

class TestBuildUserPrompt:
    def test_contains_clause_codes(self, sample_playbook):
        result = build_user_prompt(SAMPLE_CONTRACT, sample_playbook)
        assert "INFRAESTRUTURA" in result
        assert "PRAZO" in result
        assert "EXCLUSIVIDADE" in result

    def test_contains_clause_titles(self, sample_playbook):
        result = build_user_prompt(SAMPLE_CONTRACT, sample_playbook)
        assert "Ciência da Infraestrutura" in result
        assert "Do Prazo" in result

    def test_contains_contract_text(self, sample_playbook):
        result = build_user_prompt(SAMPLE_CONTRACT, sample_playbook)
        assert SAMPLE_CONTRACT in result

    def test_signature_accepts_playbook_list(self, sample_playbook):
        """Signature must accept list[PlaybookClause], not list[dict]."""
        # Should not raise
        result = build_user_prompt(SAMPLE_CONTRACT, sample_playbook)
        assert isinstance(result, str)

    def test_truncates_long_full_text(self):
        long_clause = PlaybookClause(
            code="OBRAS",
            title="Das Obras",
            full_text="A" * 500,
            category="obras",
        )
        result = build_user_prompt("contrato", [long_clause])
        # Full text should be truncated (not all 500 chars present)
        assert "A" * 500 not in result
        assert "OBRAS" in result

    def test_no_json_return_instruction(self, sample_playbook):
        result = build_user_prompt(SAMPLE_CONTRACT, sample_playbook)
        assert "retorne o JSON" not in result

    def test_mentions_legal_and_business_focus(self, sample_playbook):
        result = build_user_prompt(SAMPLE_CONTRACT, sample_playbook)
        lowered = result.lower()
        assert "playbook" in lowered
        assert "contrato" in lowered


# ---------------------------------------------------------------------------
# build_correction_prompt tests
# ---------------------------------------------------------------------------

class TestBuildCorrectionPrompt:
    def test_contains_original_text(self, sample_playbook):
        findings = [{"clause_code": "PRAZO", "severity": "critical"}]
        result = build_correction_prompt(SAMPLE_CONTRACT, findings, sample_playbook)
        assert SAMPLE_CONTRACT in result

    def test_contains_findings(self, sample_playbook):
        findings = [{"clause_code": "PRAZO", "severity": "critical", "explanation": "Prazo insuficiente", "suggested_correction": "Ajustar prazo"}]
        result = build_correction_prompt(SAMPLE_CONTRACT, findings, sample_playbook)
        assert "PRAZO" in result
        assert "critical" in result

    def test_contains_playbook_clauses(self, sample_playbook):
        # Only clauses mentioned in findings are included now
        findings = [{"clause_code": "PRAZO", "severity": "critical"}]
        result = build_correction_prompt(SAMPLE_CONTRACT, findings, sample_playbook)
        assert "PRAZO" in result


# ---------------------------------------------------------------------------
# build_summary_user_prompt tests
# ---------------------------------------------------------------------------

class TestBuildSummaryUserPrompt:
    def test_contains_contract(self):
        result = build_summary_user_prompt(SAMPLE_CONTRACT)
        assert SAMPLE_CONTRACT in result

    def test_no_json_return_instruction(self):
        result = build_summary_user_prompt(SAMPLE_CONTRACT)
        assert "JSON especificado" not in result
