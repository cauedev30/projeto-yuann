from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

from app.application.analysis import persist_contract_analysis
from app.db.models.contract import Contract, ContractSource, ContractVersion
from app.schemas.analysis import AnalysisItem, ContractAnalysisResult
from app.tasks.archive import process_signed_contract_archive
from tests.support.pdf_factory import build_pdf_with_text


def upload_contract(client, *, external_reference: str = "LOC-001") -> dict:
    response = client.post(
        "/api/uploads/contracts",
        data={
            "title": "Loja Centro",
            "external_reference": external_reference,
            "source": "third_party_draft",
        },
        files={
            "file": (
                "contract.pdf",
                build_pdf_with_text("Prazo de vigencia 36 meses"),
                "application/pdf",
            )
        },
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["version_number"] == 1
    return payload


def upload_contract_version(
    client,
    *,
    contract_id: str,
    filename: str,
    contract_text: str,
    source: str = "third_party_draft",
) -> dict:
    response = client.post(
        f"/api/contracts/{contract_id}/versions",
        data={"source": source},
        files={
            "file": (
                filename,
                build_pdf_with_text(contract_text),
                "application/pdf",
            )
        },
    )

    assert response.status_code == 201
    return response.json()


def persist_contract_analysis_for(
    client,
    *,
    contract_id: str,
    contract_version_id: str | None = None,
    contract_risk_score: float = 80,
    items: list[AnalysisItem] | None = None,
) -> None:
    session = client.app.state.session_factory()
    try:
        persist_contract_analysis(
            session,
            contract_id=contract_id,
            contract_version_id=contract_version_id,
            policy_version="v1",
            analysis_result=ContractAnalysisResult(
                contract_risk_score=contract_risk_score,
                items=items
                or [
                    AnalysisItem(
                        clause_name="Prazo de vigencia",
                        status="critical",
                        severity="critical",
                        current_summary="Prazo atual de 36 meses.",
                        policy_rule="Prazo minimo exigido: 60 meses.",
                        risk_explanation="Prazo abaixo do minimo permitido pela politica.",
                        suggested_adjustment_direction="Solicitar prazo minimo de 60 meses.",
                        metadata={},
                    )
                ],
            ),
        )
    finally:
        session.close()


def enrich_contract_metadata(client, *, external_reference: str = "LOC-001") -> None:
    session = client.app.state.session_factory()
    try:
        contract = session.query(Contract).filter_by(external_reference=external_reference).one()
        contract.term_months = 36
        contract.parties = {"tenant": "Loja Centro"}
        contract.financial_terms = {"monthly_rent": 12000}
        session.commit()
    finally:
        session.close()


def create_contract_record(
    client,
    *,
    title: str,
    external_reference: str,
    status: str = "enviado",
    is_active: bool = False,
    activated_at: datetime | None = None,
    last_accessed_at: datetime | None = None,
    last_analyzed_at: datetime | None = None,
    created_at: datetime | None = None,
    updated_at: datetime | None = None,
) -> str:
    session = client.app.state.session_factory()
    try:
        contract = Contract(
            title=title,
            external_reference=external_reference,
            status=status,
            is_active=is_active,
            activated_at=activated_at,
            last_accessed_at=last_accessed_at,
            last_analyzed_at=last_analyzed_at,
        )
        if created_at is not None:
            contract.created_at = created_at
        if updated_at is not None:
            contract.updated_at = updated_at

        session.add(contract)
        session.commit()
        session.refresh(contract)
        return contract.id
    finally:
        session.close()


def test_list_contracts_returns_empty_collection(client) -> None:
    response = client.get("/api/contracts")

    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["page"] == 1
    assert data["per_page"] == 20
    assert data["total"] == 0
    assert data["total_pages"] == 1


def test_list_contracts_returns_enriched_summary_fields(client) -> None:
    now = datetime.now(timezone.utc)
    upload_payload = upload_contract(client)
    enrich_contract_metadata(client)
    persist_contract_analysis_for(client, contract_id=upload_payload["contract_id"])
    session = client.app.state.session_factory()
    try:
        contract = session.query(Contract).filter_by(id=upload_payload["contract_id"]).one()
        contract.is_active = True
        contract.activated_at = now - timedelta(days=7)
        contract.last_accessed_at = now - timedelta(days=1)
        session.commit()
    finally:
        session.close()

    response = client.get("/api/contracts")

    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    item = data["items"][0]
    assert item["id"] == upload_payload["contract_id"]
    assert item["title"] == "Loja Centro"
    assert item["external_reference"] == "LOC-001"
    assert item["status"] in ("enviado", "analisado")
    assert item["term_months"] == 36
    assert item["is_active"] is True
    assert item["activated_at"] is not None
    assert item["last_accessed_at"] is not None
    assert item["last_analyzed_at"] is not None
    assert item["latest_analysis_status"] == "completed"
    assert item["latest_contract_risk_score"] == 80.0
    assert item["latest_version_source"] == "third_party_draft"


def test_list_contracts_scope_active_returns_only_active_contracts(client) -> None:
    base_time = datetime(2026, 1, 10, tzinfo=timezone.utc)
    older_active_id = create_contract_record(
        client,
        title="Contrato Ativo Antigo",
        external_reference="ACT-001",
        is_active=True,
        activated_at=base_time - timedelta(days=10),
        created_at=base_time,
        updated_at=base_time,
    )
    newer_active_id = create_contract_record(
        client,
        title="Contrato Ativo Novo",
        external_reference="ACT-002",
        is_active=True,
        activated_at=base_time - timedelta(days=5),
        created_at=base_time + timedelta(hours=1),
        updated_at=base_time + timedelta(days=1),
    )
    create_contract_record(
        client,
        title="Contrato Historico",
        external_reference="HIS-001",
        is_active=False,
        last_analyzed_at=base_time + timedelta(days=2),
        created_at=base_time + timedelta(days=2),
        updated_at=base_time + timedelta(days=2),
    )

    response = client.get("/api/contracts?scope=active")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert data["total_pages"] == 1
    assert [item["id"] for item in data["items"]] == [newer_active_id, older_active_id]
    assert all(item["is_active"] is True for item in data["items"])


def test_list_contracts_scope_history_returns_only_inactive_analyzed_contracts(client) -> None:
    base_time = datetime(2026, 1, 10, tzinfo=timezone.utc)
    older_history_id = create_contract_record(
        client,
        title="Historico Antigo",
        external_reference="HIS-010",
        is_active=False,
        last_analyzed_at=base_time,
        created_at=base_time,
        updated_at=base_time,
    )
    newer_history_id = create_contract_record(
        client,
        title="Historico Novo",
        external_reference="HIS-011",
        is_active=False,
        last_analyzed_at=base_time + timedelta(days=3),
        created_at=base_time + timedelta(days=1),
        updated_at=base_time + timedelta(days=1),
    )
    create_contract_record(
        client,
        title="Contrato Ativo",
        external_reference="ACT-010",
        is_active=True,
        last_analyzed_at=base_time + timedelta(days=5),
        created_at=base_time + timedelta(days=2),
        updated_at=base_time + timedelta(days=2),
    )

    response = client.get("/api/contracts?scope=history")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert [item["id"] for item in data["items"]] == [newer_history_id, older_history_id]
    assert all(item["is_active"] is False for item in data["items"])
    assert all(item["last_analyzed_at"] is not None for item in data["items"])


def test_list_contracts_scope_history_excludes_inactive_without_analysis(client) -> None:
    create_contract_record(
        client,
        title="Sem Analise",
        external_reference="HIS-020",
        is_active=False,
    )
    analyzed_history_id = create_contract_record(
        client,
        title="Com Analise",
        external_reference="HIS-021",
        is_active=False,
        last_analyzed_at=datetime(2026, 1, 20, tzinfo=timezone.utc),
    )

    response = client.get("/api/contracts?scope=history")

    assert response.status_code == 200
    data = response.json()
    assert [item["id"] for item in data["items"]] == [analyzed_history_id]


def test_get_contract_detail_returns_contract_version_and_analysis(client) -> None:
    upload_payload = upload_contract(client)
    enrich_contract_metadata(client)
    persist_contract_analysis_for(client, contract_id=upload_payload["contract_id"])

    response = client.get(f"/api/contracts/{upload_payload['contract_id']}")

    assert response.status_code == 200
    data = response.json()
    contract = data["contract"]
    assert contract["id"] == upload_payload["contract_id"]
    assert contract["title"] == "Loja Centro"
    assert contract["external_reference"] == "LOC-001"
    assert contract["status"] in ("enviado", "analisado")
    assert contract["term_months"] == 36
    assert contract["is_active"] is False
    assert contract["activated_at"] is None
    assert contract["last_accessed_at"] is not None
    assert contract["last_analyzed_at"] is not None
    assert contract["parties"] == {"tenant": "Loja Centro"}
    assert contract["financial_terms"] == {"monthly_rent": 12000}
    assert isinstance(contract["field_confidence"], dict)

    assert data["latest_version"]["contract_version_id"] == upload_payload["contract_version_id"]
    assert data["latest_version"]["version_number"] == 1
    assert data["latest_version"]["created_at"] is not None
    assert data["latest_version"]["source"] == "third_party_draft"
    assert data["latest_version"]["text"] == "Prazo de vigencia 36 meses"

    analysis = data["latest_analysis"]
    assert analysis is not None
    assert analysis["analysis_status"] == "completed"
    assert analysis["policy_version"] == "v1"
    assert analysis["contract_risk_score"] == 80.0
    assert len(analysis["findings"]) == 1
    assert analysis["findings"][0]["clause_name"] == "Prazo de vigencia"
    assert analysis["findings"][0]["status"] == "critical"


def test_get_contract_detail_returns_null_analysis_when_not_available(client) -> None:
    upload_payload = upload_contract(client, external_reference="LOC-002")
    enrich_contract_metadata(client, external_reference="LOC-002")

    response = client.get(f"/api/contracts/{upload_payload['contract_id']}")

    assert response.status_code == 200
    assert response.json()["contract"]["external_reference"] == "LOC-002"
    assert response.json()["contract"]["last_accessed_at"] is not None
    assert response.json()["contract"]["last_analyzed_at"] is None
    assert response.json()["latest_version"] == {
        "contract_version_id": upload_payload["contract_version_id"],
        "version_number": 1,
        "created_at": response.json()["latest_version"]["created_at"],
        "source": "third_party_draft",
        "original_filename": "contract.pdf",
        "used_ocr": False,
        "text": "Prazo de vigencia 36 meses",
    }
    assert response.json()["latest_analysis"] is None


def test_post_contract_version_creates_new_version_for_existing_contract(client) -> None:
    first_upload = upload_contract(client)
    second_upload = upload_contract_version(
        client,
        contract_id=first_upload["contract_id"],
        filename="contract-v2.pdf",
        contract_text="Prazo de vigencia 24 meses",
    )

    assert second_upload["contract_id"] == first_upload["contract_id"]
    assert second_upload["contract_version_id"] != first_upload["contract_version_id"]
    assert second_upload["version_number"] == 2

    session = client.app.state.session_factory()
    try:
        assert session.query(Contract).count() == 1
        versions = (
            session.query(ContractVersion)
            .filter_by(contract_id=first_upload["contract_id"])
            .order_by(ContractVersion.version_number.asc())
            .all()
        )
        assert [version.version_number for version in versions] == [1, 2]
    finally:
        session.close()


def test_get_contract_detail_uses_analysis_from_latest_version_instead_of_latest_global_analysis(client) -> None:
    first_upload = upload_contract(client, external_reference="LOC-100")
    second_upload = upload_contract_version(
        client,
        contract_id=first_upload["contract_id"],
        filename="contract-v2.pdf",
        contract_text="Prazo de vigencia 24 meses",
    )

    persist_contract_analysis_for(
        client,
        contract_id=first_upload["contract_id"],
        contract_version_id=second_upload["contract_version_id"],
        contract_risk_score=15,
    )
    persist_contract_analysis_for(
        client,
        contract_id=first_upload["contract_id"],
        contract_version_id=first_upload["contract_version_id"],
        contract_risk_score=95,
    )

    response = client.get(f"/api/contracts/{first_upload['contract_id']}")

    assert response.status_code == 200
    data = response.json()
    assert data["latest_version"]["contract_version_id"] == second_upload["contract_version_id"]
    assert data["latest_version"]["version_number"] == 2
    assert data["latest_analysis"]["contract_risk_score"] == 15.0


def test_list_contract_versions_returns_descending_history_with_current_marker(client) -> None:
    first_upload = upload_contract(client, external_reference="LOC-110")
    second_upload = upload_contract_version(
        client,
        contract_id=first_upload["contract_id"],
        filename="contract-v2.pdf",
        contract_text="Prazo de vigencia 24 meses",
    )
    persist_contract_analysis_for(
        client,
        contract_id=first_upload["contract_id"],
        contract_version_id=second_upload["contract_version_id"],
        contract_risk_score=42,
    )

    response = client.get(f"/api/contracts/{first_upload['contract_id']}/versions")

    assert response.status_code == 200
    data = response.json()
    assert [item["version_number"] for item in data["items"]] == [2, 1]
    assert [item["contract_version_id"] for item in data["items"]] == [
        second_upload["contract_version_id"],
        first_upload["contract_version_id"],
    ]
    assert data["items"][0]["is_current"] is True
    assert data["items"][0]["analysis_status"] == "completed"
    assert data["items"][0]["contract_risk_score"] == 42.0
    assert data["items"][0]["created_at"] is not None
    assert data["items"][1]["is_current"] is False
    assert data["items"][1]["analysis_status"] is None


def test_get_contract_version_detail_returns_snapshot_for_requested_version(client) -> None:
    first_response = client.post(
        "/api/uploads/contracts",
        data={
            "title": "Loja Centro",
            "external_reference": "LOC-120",
            "source": "signed_contract",
        },
        files={
            "file": (
                "signed-v1.pdf",
                build_pdf_with_text(
                    "Data de assinatura: 01/03/2026\n"
                    "Inicio de vigencia: 01/04/2026\n"
                    "Prazo de vigencia: 60 meses\n"
                    "Locataria: Franquia XPTO LTDA\n"
                    "Carencia de 3 meses\n"
                    "Reajuste anual"
                ),
                "application/pdf",
            )
        },
    )
    assert first_response.status_code == 201
    first_upload = first_response.json()
    assert first_upload["version_number"] == 1

    second_upload = upload_contract_version(
        client,
        contract_id=first_upload["contract_id"],
        filename="signed-v2.pdf",
        source="signed_contract",
        contract_text=(
            "Data de assinatura: 01/03/2027\n"
            "Inicio de vigencia: 01/05/2027\n"
            "Prazo de vigencia: 24 meses\n"
            "Locataria: Franquia XPTO LTDA"
        ),
    )
    persist_contract_analysis_for(
        client,
        contract_id=first_upload["contract_id"],
        contract_version_id=first_upload["contract_version_id"],
    )

    response = client.get(
        f"/api/contracts/{first_upload['contract_id']}/versions/{first_upload['contract_version_id']}"
    )

    assert response.status_code == 200
    data = response.json()
    assert data["is_current"] is False
    assert data["selected_version"]["contract_version_id"] == first_upload["contract_version_id"]
    assert data["selected_version"]["version_number"] == 1
    assert data["latest_version"]["contract_version_id"] == second_upload["contract_version_id"]
    assert data["contract"]["signature_date"] == "2026-03-01"
    assert data["contract"]["start_date"] == "2026-04-01"
    assert data["contract"]["end_date"] == "2031-03-31"
    assert data["contract"]["term_months"] == 60
    assert data["contract"]["parties"] == {
        "entities": ["Franquia XPTO LTDA"],
        "locatario": "Franquia XPTO LTDA",
    }
    assert data["selected_analysis"]["analysis_status"] == "completed"
    assert {event["metadata"]["source_contract_version_id"] for event in data["events"]} == {
        first_upload["contract_version_id"]
    }


def test_get_contract_version_detail_returns_404_when_version_is_not_owned_by_contract(client) -> None:
    first_upload = upload_contract(client, external_reference="LOC-130")
    other_upload = upload_contract(client, external_reference="LOC-131")

    response = client.get(
        f"/api/contracts/{first_upload['contract_id']}/versions/{other_upload['contract_version_id']}"
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Contract version not found"}


def test_get_contract_summary_uses_requested_version_text(client) -> None:
    first_upload = upload_contract(client, external_reference="LOC-140")
    second_upload = upload_contract_version(
        client,
        contract_id=first_upload["contract_id"],
        filename="contract-v2.pdf",
        contract_text="Prazo de vigencia 24 meses",
    )

    summary_client = SimpleNamespace(
        summarize_contract=lambda text: SimpleNamespace(
            summary=f"Resumo: {text}",
            key_points=[text],
        )
    )
    previous_llm_client = getattr(client.app.state, "llm_client", None)
    client.app.state.llm_client = summary_client
    try:
        response = client.get(
            f"/api/contracts/{first_upload['contract_id']}/summary?version_id={first_upload['contract_version_id']}"
        )
    finally:
        client.app.state.llm_client = previous_llm_client

    assert response.status_code == 200
    assert response.json() == {
        "summary": "Resumo: Prazo de vigencia 36 meses",
        "key_points": ["Prazo de vigencia 36 meses"],
    }
    assert second_upload["version_number"] == 2


def test_get_contract_compare_returns_text_and_finding_diffs_between_versions(client) -> None:
    first_upload = upload_contract(client, external_reference="LOC-150")
    second_upload = upload_contract_version(
        client,
        contract_id=first_upload["contract_id"],
        filename="contract-v2.pdf",
        contract_text=(
            "Prazo de vigencia 60 meses\n"
            "Reajuste anual pelo IGP-M\n"
            "Fiador obrigatorio"
        ),
    )

    persist_contract_analysis_for(
        client,
        contract_id=first_upload["contract_id"],
        contract_version_id=first_upload["contract_version_id"],
        contract_risk_score=82,
        items=[
            AnalysisItem(
                clause_name="Prazo de vigencia",
                status="critical",
                severity="critical",
                current_summary="Prazo atual de 36 meses.",
                policy_rule="Prazo minimo exigido: 60 meses.",
                risk_explanation="Prazo abaixo do minimo permitido pela politica.",
                suggested_adjustment_direction="Solicitar prazo minimo de 60 meses.",
                metadata={},
            ),
            AnalysisItem(
                clause_name="Reajuste monetario",
                status="attention",
                severity="medium",
                current_summary="Clausula de reajuste ausente.",
                policy_rule="Contrato deve prever reajuste monetario.",
                risk_explanation="Nao ha indice de reajuste expresso.",
                suggested_adjustment_direction="Incluir indice e periodicidade de reajuste.",
                metadata={},
            ),
        ],
    )
    persist_contract_analysis_for(
        client,
        contract_id=first_upload["contract_id"],
        contract_version_id=second_upload["contract_version_id"],
        contract_risk_score=28,
        items=[
            AnalysisItem(
                clause_name="Prazo de vigencia",
                status="conforme",
                severity="low",
                current_summary="Prazo atual de 60 meses.",
                policy_rule="Prazo minimo exigido: 60 meses.",
                risk_explanation="Prazo alinhado com a politica.",
                suggested_adjustment_direction="Nenhum ajuste necessario.",
                metadata={},
            ),
            AnalysisItem(
                clause_name="Fiador",
                status="attention",
                severity="medium",
                current_summary="Fiador identificado, mas sem regra de substituicao.",
                policy_rule="Garantia precisa prever substituicao adequada.",
                risk_explanation="Clausula de fiador exige detalhamento operacional.",
                suggested_adjustment_direction="Detalhar substituicao e obrigacoes do fiador.",
                metadata={},
            ),
        ],
    )

    response = client.get(
        f"/api/contracts/{first_upload['contract_id']}/compare"
        f"?selected_version_id={second_upload['contract_version_id']}"
        f"&baseline_version_id={first_upload['contract_version_id']}"
    )

    assert response.status_code == 200
    data = response.json()
    assert data["selected_version"]["contract_version_id"] == second_upload["contract_version_id"]
    assert data["baseline_version"]["contract_version_id"] == first_upload["contract_version_id"]
    assert data["summary"]
    assert data["text_diff"]["has_changes"] is True
    assert any(
        line["kind"] == "removed" and "Prazo de vigencia 36 meses" in line["value"]
        for line in data["text_diff"]["lines"]
    )
    assert any(
        line["kind"] == "added" and "Prazo de vigencia 60 meses" in line["value"]
        for line in data["text_diff"]["lines"]
    )
    assert any(
        item["change_type"] == "changed" and item["clause_name"] == "Prazo de vigencia"
        and item["previous_status"] == "critical" and item["current_status"] == "conforme"
        for item in data["findings_diff"]["items"]
    )
    assert any(
        item["change_type"] == "removed" and item["clause_name"] == "Reajuste monetario"
        for item in data["findings_diff"]["items"]
    )
    assert any(
        item["change_type"] == "added" and item["clause_name"] == "Fiador"
        for item in data["findings_diff"]["items"]
    )


def test_get_contract_detail_returns_404_when_contract_does_not_exist(client) -> None:
    response = client.get("/api/contracts/unknown-contract")

    assert response.status_code == 404
    assert response.json() == {"detail": "Contract not found"}


def test_get_contract_detail_returns_empty_events_when_none_exist(client) -> None:
    upload_payload = upload_contract(client, external_reference="LOC-010")

    response = client.get(f"/api/contracts/{upload_payload['contract_id']}")

    assert response.status_code == 200
    assert response.json()["events"] == []


def test_get_contract_detail_returns_events_when_populated(client) -> None:
    session = client.app.state.session_factory()
    try:
        contract = Contract(
            title="Contrato Eventos",
            external_reference="LOC-020",
            status="active",
        )
        text = (
            "assinatura: 01/01/2025\n"
            "inicio de vigencia: 01/02/2025\n"
            "prazo de vigencia: 12 meses\n"
            "locataria: Empresa XYZ Ltda."
        )
        version = ContractVersion(
            version_number=1,
            source=ContractSource.signed_contract,
            original_filename="contrato.pdf",
            storage_key="uploads/contrato.pdf",
            text_content=text,
        )
        contract.versions.append(version)
        session.add(contract)
        session.commit()
        session.refresh(version)
        contract_id = contract.id

        process_signed_contract_archive(session=session, contract_version=version)
        session.commit()
    finally:
        session.close()

    response = client.get(f"/api/contracts/{contract_id}")

    assert response.status_code == 200
    events = response.json()["events"]
    assert isinstance(events, list)
    assert len(events) > 0
    first = events[0]
    assert "id" in first
    assert "event_type" in first
    assert "lead_time_days" in first
    assert "metadata" in first


def test_get_contract_detail_returns_field_confidence(client) -> None:
    session = client.app.state.session_factory()
    try:
        contract = Contract(
            title="Contrato Confidence",
            external_reference="LOC-030",
            status="active",
        )
        text = (
            "assinatura: 01/01/2025\n"
            "inicio de vigencia: 01/02/2025\n"
            "prazo de vigencia: 12 meses\n"
            "locataria: Empresa XYZ Ltda."
        )
        version = ContractVersion(
            version_number=1,
            source=ContractSource.signed_contract,
            original_filename="contrato.pdf",
            storage_key="uploads/contrato.pdf",
            text_content=text,
        )
        contract.versions.append(version)
        session.add(contract)
        session.commit()
        session.refresh(version)
        contract_id = contract.id

        process_signed_contract_archive(session=session, contract_version=version)
        session.commit()
    finally:
        session.close()

    response = client.get(f"/api/contracts/{contract_id}")

    assert response.status_code == 200
    field_confidence = response.json()["contract"]["field_confidence"]
    assert isinstance(field_confidence, dict)
    assert len(field_confidence) > 0


def test_update_contract_can_activate_and_set_activated_at(client) -> None:
    upload_payload = upload_contract(client, external_reference="LOC-040")

    response = client.patch(
        f"/api/contracts/{upload_payload['contract_id']}",
        json={"is_active": True, "title": "Loja Centro Ativa"},
    )

    assert response.status_code == 200
    contract = response.json()["contract"]
    assert contract["title"] == "Loja Centro Ativa"
    assert contract["is_active"] is True
    assert contract["activated_at"] is not None

    session = client.app.state.session_factory()
    try:
        stored_contract = session.query(Contract).filter_by(id=upload_payload["contract_id"]).one()
        assert stored_contract.title == "Loja Centro Ativa"
        assert stored_contract.is_active is True
        assert stored_contract.activated_at is not None
    finally:
        session.close()


def test_update_contract_can_deactivate_without_clearing_activated_at(client) -> None:
    upload_payload = upload_contract(client, external_reference="LOC-041")
    original_activated_at = datetime(2026, 1, 15, 12, 0, tzinfo=timezone.utc)
    session = client.app.state.session_factory()
    try:
        contract = session.query(Contract).filter_by(id=upload_payload["contract_id"]).one()
        contract.is_active = True
        contract.activated_at = original_activated_at
        session.commit()
    finally:
        session.close()

    response = client.patch(
        f"/api/contracts/{upload_payload['contract_id']}",
        json={"is_active": False},
    )

    assert response.status_code == 200
    contract_payload = response.json()["contract"]
    assert contract_payload["is_active"] is False
    assert contract_payload["activated_at"] is not None

    session = client.app.state.session_factory()
    try:
        stored_contract = session.query(Contract).filter_by(id=upload_payload["contract_id"]).one()
        assert stored_contract.is_active is False
        assert stored_contract.activated_at is not None
        assert stored_contract.activated_at.replace(tzinfo=timezone.utc) == original_activated_at
    finally:
        session.close()


def test_get_contract_detail_updates_last_accessed_at(client) -> None:
    upload_payload = upload_contract(client, external_reference="LOC-050")
    session = client.app.state.session_factory()
    try:
        stored_contract = session.query(Contract).filter_by(id=upload_payload["contract_id"]).one()
        assert stored_contract.last_accessed_at is None
    finally:
        session.close()

    response = client.get(f"/api/contracts/{upload_payload['contract_id']}")

    assert response.status_code == 200
    assert response.json()["contract"]["last_accessed_at"] is not None

    session = client.app.state.session_factory()
    try:
        stored_contract = session.query(Contract).filter_by(id=upload_payload["contract_id"]).one()
        assert stored_contract.last_accessed_at is not None
    finally:
        session.close()


def test_persist_contract_analysis_updates_last_analyzed_at(client) -> None:
    upload_payload = upload_contract(client, external_reference="LOC-060")
    session = client.app.state.session_factory()
    try:
        stored_contract = session.query(Contract).filter_by(id=upload_payload["contract_id"]).one()
        assert stored_contract.last_analyzed_at is None
    finally:
        session.close()

    persist_contract_analysis_for(client, contract_id=upload_payload["contract_id"])

    session = client.app.state.session_factory()
    try:
        stored_contract = session.query(Contract).filter_by(id=upload_payload["contract_id"]).one()
        assert stored_contract.last_analyzed_at is not None
    finally:
        session.close()
