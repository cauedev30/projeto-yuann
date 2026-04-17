from app.schemas.analysis import AnalysisItem

from app.domain.contract_analysis import (
    CLASSIFICATION_TO_STATUS,
    calculate_final_risk_score,
    extract_contract_facts,
    merge_analysis_items,
)


def test_classification_to_status_maps_correctly() -> None:
    assert CLASSIFICATION_TO_STATUS["adequada"] == "conforme"
    assert CLASSIFICATION_TO_STATUS["risco_medio"] == "attention"
    assert CLASSIFICATION_TO_STATUS["ausente"] == "critical"
    assert CLASSIFICATION_TO_STATUS["conflitante"] == "critical"


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


def test_calculate_final_risk_score_uses_weighted_composition_instead_of_max() -> None:
    llm_items = [
        AnalysisItem(
            clause_name="Redacao ambigua",
            status="attention",
            severity="medium",
            risk_explanation="Texto juridicamente ambiguo.",
            current_summary="Pode gerar interpretacao dupla.",
            policy_rule="Deve ser objetivo.",
            suggested_adjustment_direction="Redigir com maior precisao.",
            metadata={"category": "redacao"},
        )
    ]
    deterministic_items = [
        AnalysisItem(
            clause_name="Prazo de vigencia",
            status="conforme",
            severity="low",
            risk_explanation="Prazo dentro da politica.",
            current_summary="60 meses.",
            policy_rule="Minimo de 60 meses.",
            suggested_adjustment_direction="Nenhum ajuste necessario.",
            metadata={"category": "prazo", "essential_clause": True},
        )
    ]

    score = calculate_final_risk_score(
        llm_score=92,
        llm_items=llm_items,
        deterministic_items=deterministic_items,
    )

    assert score < 92
    assert score <= 45


def test_calculate_final_risk_score_penalizes_missing_essential_clause() -> None:
    score = calculate_final_risk_score(
        llm_score=18,
        llm_items=[],
        deterministic_items=[
            AnalysisItem(
                clause_name="Exclusividade",
                status="critical",
                severity="high",
                risk_explanation="Clausula essencial ausente.",
                current_summary="Clausula nao encontrada.",
                policy_rule="Clausula obrigatoria.",
                suggested_adjustment_direction="Inserir clausula de exclusividade.",
                metadata={
                    "category": "essencial",
                    "essential_clause": True,
                    "missing_clause": True,
                },
            )
        ],
    )

    assert score >= 70


def test_extract_contract_facts_parses_aluguel_mensal_sera_de_pattern() -> None:
    facts = extract_contract_facts(
        "CLAUSULA 2 - ALUGUEL. O aluguel mensal sera de R$ 8500,00, com carencia de 45 dias."
    )

    assert facts["contract_value"] == 8500.0


def test_auto_activate_signed_contract_sets_is_active() -> None:
    from app.application.analysis import auto_activate_signed_contract
    from app.db.models.contract import Contract, ContractSource, ContractVersion

    contract = Contract(
        title="Test",
        external_reference="TEST-001",
        status="analyzed",
        is_active=False,
    )
    version = ContractVersion(
        version_number=1,
        source=ContractSource.signed_contract,
        original_filename="test.pdf",
        storage_key="fixtures/test.pdf",
    )
    contract.versions.append(version)

    class FakeSession:
        committed = False

        def commit(self):
            self.committed = True

    session = FakeSession()
    auto_activate_signed_contract(contract, session)  # type: ignore

    assert contract.is_active is True
    assert contract.activated_at is not None
    assert session.committed is True


def test_auto_activate_skips_non_signed_contracts() -> None:
    from app.application.analysis import auto_activate_signed_contract
    from app.db.models.contract import Contract, ContractSource, ContractVersion

    contract = Contract(
        title="Test",
        external_reference="TEST-002",
        status="draft",
        is_active=False,
    )
    version = ContractVersion(
        version_number=1,
        source=ContractSource.third_party_draft,
        original_filename="test.pdf",
        storage_key="fixtures/test.pdf",
    )
    contract.versions.append(version)

    class FakeSession:
        committed = False

        def commit(self):
            self.committed = True

    session = FakeSession()
    auto_activate_signed_contract(contract, session)  # type: ignore

    assert contract.is_active is False
    assert session.committed is False
