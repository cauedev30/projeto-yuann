from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.analysis import AnalysisStatus, ContractAnalysis, ContractAnalysisFinding
from app.db.models.contract import Contract, ContractVersion
from app.db.models.event import ContractEvent
from app.db.models.policy import Policy
from app.domain.contract_analysis import evaluate_rules, extract_contract_facts
from app.domain.contract_metadata import extract_contract_metadata
from app.domain.events import build_contract_events


def run_policy_analysis(
    session: Session,
    contract: Contract,
    contract_text: str,
    *,
    llm_client: object | None = None,
) -> None:
    """Run policy analysis only (no metadata/events). Use for signed contracts where archive already handled the rest."""
    policy = session.scalar(select(Policy).order_by(Policy.created_at.desc()))
    if not policy or not policy.rules:
        return

    rules_dicts = [
        {"code": r.code, "value": r.value, "description": r.description}
        for r in policy.rules
    ]
    extracted_facts = extract_contract_facts(contract_text)

    if llm_client is not None:
        from app.services.policy_analysis import analyze_contract_against_policy

        analysis_result = analyze_contract_against_policy(
            contract_text=contract_text,
            policy_rules=rules_dicts,
            llm_client=llm_client,
        )
    else:
        analysis_result = evaluate_rules(rules_dicts, extracted_facts)

    analysis = ContractAnalysis(
        contract_id=contract.id,
        policy_version=policy.version,
        status=AnalysisStatus.completed,
        contract_risk_score=analysis_result.contract_risk_score,
        raw_payload=analysis_result.model_dump(),
        findings=[
            ContractAnalysisFinding(
                clause_name=item.clause_name,
                status=item.status,
                severity=item.severity,
                current_summary=item.current_summary,
                policy_rule=item.policy_rule,
                risk_explanation=item.risk_explanation,
                suggested_adjustment_direction=item.suggested_adjustment_direction,
                metadata_json=item.metadata,
            )
            for item in analysis_result.items
        ],
    )
    session.add(analysis)
    session.flush()


def run_contract_pipeline(
    session: Session,
    contract: Contract,
    contract_version: ContractVersion,
    *,
    llm_client: object | None = None,
) -> None:
    """Full pipeline: extract metadata, generate events, and run policy analysis.

    Use for non-signed contracts. For signed contracts, use process_signed_contract_archive
    (which handles metadata+events) followed by run_policy_analysis.
    """
    text = contract_version.text_content
    if not text:
        return

    metadata_result = extract_contract_metadata(text)

    contract.signature_date = metadata_result.signature_date
    contract.start_date = metadata_result.start_date
    contract.end_date = metadata_result.end_date
    contract.term_months = metadata_result.term_months
    if metadata_result.parties:
        contract.parties = {"entities": metadata_result.parties}
    if metadata_result.financial_terms:
        contract.financial_terms = metadata_result.financial_terms
    contract.status = "analyzed"

    existing_meta = dict(contract_version.extraction_metadata or {})
    existing_meta["field_confidence"] = metadata_result.field_confidence
    existing_meta["match_labels"] = metadata_result.match_labels
    contract_version.extraction_metadata = existing_meta

    if metadata_result.ready_for_event_generation:
        for event in list(contract.events):
            session.delete(event)
        session.flush()

        scheduled_events = build_contract_events(metadata_result)
        for scheduled in scheduled_events:
            session.add(
                ContractEvent(
                    contract_id=contract.id,
                    event_type=scheduled.event_type,
                    event_date=scheduled.event_date,
                    lead_time_days=scheduled.lead_time_days,
                    metadata_json=scheduled.metadata,
                )
            )

    run_policy_analysis(session, contract, text, llm_client=llm_client)
