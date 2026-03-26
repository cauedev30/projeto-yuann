"""Tests for the playbook clauses domain module."""

from app.domain.playbook import (
    PLAYBOOK_CLAUSES,
    PlaybookClause,
    get_clause_by_code,
)


class TestPlaybookClauses:
    """Tests for PLAYBOOK_CLAUSES list."""

    def test_playbook_covers_required_contract_knowledge(self):
        codes = {clause.code for clause in PLAYBOOK_CLAUSES}
        assert {
            "INFRAESTRUTURA",
            "RESCISAO_INFRAESTRUTURA",
            "CONDOMINIO",
            "OBRAS",
            "EXCLUSIVIDADE",
            "PRAZO",
            "VISTORIAS",
            "CESSAO",
            "OBRIGACAO_NAO_FAZER",
            "REAJUSTE",
            "GARANTIA_LOCATICIA",
            "RENOVACAO_EMPRESARIAL",
            "ASSINATURAS",
        }.issubset(codes)

    def test_no_duplicate_codes(self):
        codes = [c.code for c in PLAYBOOK_CLAUSES]
        assert len(codes) == len(set(codes))

    def test_all_clauses_are_playbook_clause_instances(self):
        for clause in PLAYBOOK_CLAUSES:
            assert isinstance(clause, PlaybookClause)

    def test_all_clauses_have_required_fields(self):
        for clause in PLAYBOOK_CLAUSES:
            assert clause.code
            assert clause.title
            assert clause.full_text
            assert clause.category


class TestGetClauseByCode:
    """Tests for get_clause_by_code()."""

    def test_returns_clause_for_valid_code(self):
        clause = get_clause_by_code("INFRAESTRUTURA")
        assert clause is not None
        assert clause.code == "INFRAESTRUTURA"
        assert clause.title == "Ciência da Infraestrutura"

    def test_returns_none_for_invalid_code(self):
        assert get_clause_by_code("INEXISTENTE") is None

    def test_returns_correct_clause_for_each_code(self):
        expected_codes = [
            "INFRAESTRUTURA",
            "RESCISAO_INFRAESTRUTURA",
            "CONDOMINIO",
            "OBRAS",
            "EXCLUSIVIDADE",
            "PRAZO",
            "VISTORIAS",
            "CESSAO",
            "OBRIGACAO_NAO_FAZER",
            "REAJUSTE",
            "GARANTIA_LOCATICIA",
            "RENOVACAO_EMPRESARIAL",
            "ASSINATURAS",
        ]
        for code in expected_codes:
            clause = get_clause_by_code(code)
            assert clause is not None, f"Clause {code} not found"
            assert clause.code == code
