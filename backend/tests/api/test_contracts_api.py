from app.application.analysis import persist_contract_analysis
from app.db.models.contract import Contract
from app.schemas.analysis import AnalysisItem, ContractAnalysisResult
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
    return response.json()


def persist_contract_analysis_for(client, *, contract_id: str) -> None:
    session = client.app.state.session_factory()
    try:
        persist_contract_analysis(
            session,
            contract_id=contract_id,
            policy_version="v1",
            analysis_result=ContractAnalysisResult(
                contract_risk_score=80,
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


def test_list_contracts_returns_empty_collection(client) -> None:
    response = client.get("/api/contracts")

    assert response.status_code == 200
    assert response.json() == {"items": []}


def test_list_contracts_returns_enriched_summary_fields(client) -> None:
    upload_payload = upload_contract(client)
    enrich_contract_metadata(client)
    persist_contract_analysis_for(client, contract_id=upload_payload["contract_id"])

    response = client.get("/api/contracts")

    assert response.status_code == 200
    assert response.json() == {
        "items": [
            {
                "id": upload_payload["contract_id"],
                "title": "Loja Centro",
                "external_reference": "LOC-001",
                "status": "uploaded",
                "signature_date": None,
                "start_date": None,
                "end_date": None,
                "term_months": 36,
                "latest_analysis_status": "completed",
                "latest_contract_risk_score": 80.0,
                "latest_version_source": "third_party_draft",
            }
        ]
    }


def test_get_contract_detail_returns_contract_version_and_analysis(client) -> None:
    upload_payload = upload_contract(client)
    enrich_contract_metadata(client)
    persist_contract_analysis_for(client, contract_id=upload_payload["contract_id"])

    response = client.get(f"/api/contracts/{upload_payload['contract_id']}")

    assert response.status_code == 200
    assert response.json() == {
        "contract": {
            "id": upload_payload["contract_id"],
            "title": "Loja Centro",
            "external_reference": "LOC-001",
            "status": "uploaded",
            "signature_date": None,
            "start_date": None,
            "end_date": None,
            "term_months": 36,
            "parties": {"tenant": "Loja Centro"},
            "financial_terms": {"monthly_rent": 12000},
        },
        "latest_version": {
            "contract_version_id": upload_payload["contract_version_id"],
            "source": "third_party_draft",
            "original_filename": "contract.pdf",
            "used_ocr": False,
            "text": "Prazo de vigencia 36 meses",
        },
        "latest_analysis": {
            "analysis_id": response.json()["latest_analysis"]["analysis_id"],
            "analysis_status": "completed",
            "policy_version": "v1",
            "contract_risk_score": 80.0,
            "findings": [
                {
                    "id": response.json()["latest_analysis"]["findings"][0]["id"],
                    "clause_name": "Prazo de vigencia",
                    "status": "critical",
                    "severity": "critical",
                    "current_summary": "Prazo atual de 36 meses.",
                    "policy_rule": "Prazo minimo exigido: 60 meses.",
                    "risk_explanation": "Prazo abaixo do minimo permitido pela politica.",
                    "suggested_adjustment_direction": "Solicitar prazo minimo de 60 meses.",
                    "metadata": {},
                }
            ],
        },
    }


def test_get_contract_detail_returns_null_analysis_when_not_available(client) -> None:
    upload_payload = upload_contract(client, external_reference="LOC-002")
    enrich_contract_metadata(client, external_reference="LOC-002")

    response = client.get(f"/api/contracts/{upload_payload['contract_id']}")

    assert response.status_code == 200
    assert response.json()["contract"]["external_reference"] == "LOC-002"
    assert response.json()["latest_version"] == {
        "contract_version_id": upload_payload["contract_version_id"],
        "source": "third_party_draft",
        "original_filename": "contract.pdf",
        "used_ocr": False,
        "text": "Prazo de vigencia 36 meses",
    }
    assert response.json()["latest_analysis"] is None


def test_get_contract_detail_returns_404_when_contract_does_not_exist(client) -> None:
    response = client.get("/api/contracts/unknown-contract")

    assert response.status_code == 404
    assert response.json() == {"detail": "Contract not found"}
