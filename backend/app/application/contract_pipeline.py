from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.application.contract_versions import (
    build_version_snapshot,
    persist_version_snapshot,
    replace_contract_events,
)
from app.application.analysis import mark_contract_analysis_completed
from app.db.models.analysis import AnalysisStatus, ContractAnalysis, ContractAnalysisFinding
from app.db.models.contract import Contract, ContractVersion
from app.db.models.policy import Policy
from app.domain.contract_analysis import (
    calculate_final_risk_score,
    evaluate_rules,
    extract_contract_facts,
    merge_analysis_items,
)
from app.domain.contract_metadata import extract_contract_metadata
from app.domain.events import build_contract_events
from app.domain.playbook import PLAYBOOK_CLAUSES
from app.infrastructure.contract_chunker import chunk_contract
from app.schemas.analysis import AnalysisItem

if TYPE_CHECKING:
    from app.infrastructure.openai_client import OpenAIAnalysisClient


def run_policy_analysis(
    session: Session,
    contract: Contract,
    contract_text: str,
    *,
    contract_version: ContractVersion | None = None,
    llm_client: OpenAIAnalysisClient | None = None,
) -> None:
    """Run policy analysis using OpenAI plus deterministic legal checks."""
    policy = session.scalar(select(Policy).order_by(Policy.created_at.desc()))
    if not policy:
        return

    analysis_version = contract_version
    if analysis_version is None:
        analysis_version = session.scalar(
            select(ContractVersion)
            .where(ContractVersion.contract_id == contract.id)
            .order_by(
                ContractVersion.version_number.desc(),
                ContractVersion.created_at.desc(),
                ContractVersion.id.desc(),
            )
        )
    if analysis_version is None:
        return

    # Chunk the contract text
    chunks = chunk_contract(contract_text)
    chunk_texts = [c.content for c in chunks]

    rules_dicts = [
        {"code": r.code, "value": r.value, "description": r.description}
        for r in (policy.rules if policy and policy.rules else [])
    ]
    extracted_facts = extract_contract_facts(contract_text)
    fallback_result = evaluate_rules(rules_dicts, extracted_facts)

    if llm_client is not None:
        llm_result = llm_client.analyze_contract(
            chunks=chunk_texts,
            playbook=list(PLAYBOOK_CLAUSES),
        )
        llm_analysis_items = [
            AnalysisItem(
                clause_name=item.clause_title,
                status=item.severity,
                severity="high" if item.severity == "critical" else "medium",
                current_summary=item.explanation,
                policy_rule=item.clause_code,
                risk_explanation=item.explanation,
                suggested_adjustment_direction=item.suggested_correction or "",
                metadata={
                    "category": "essencial"
                    if item.clause_code in {"EXCLUSIVIDADE", "PRAZO", "ASSINATURAS"}
                    else "redacao",
                    "essential_clause": item.clause_code in {"EXCLUSIVIDADE", "PRAZO", "ASSINATURAS"},
                    "risk_score": item.risk_score,
                    "clause_code": item.clause_code,
                    "page_reference": item.page_reference,
                },
            )
            for item in llm_result.items
        ]
        merged_items = merge_analysis_items(llm_analysis_items, fallback_result.items)
        filtered_items = [item for item in merged_items if item.status != "conforme"]
        analysis = ContractAnalysis(
            contract_id=contract.id,
            contract_version_id=analysis_version.id,
            policy_version=policy.version if policy else "v1.0",
            status=AnalysisStatus.completed,
            contract_risk_score=calculate_final_risk_score(
                llm_score=float(llm_result.contract_risk_score),
                llm_items=llm_analysis_items,
                deterministic_items=fallback_result.items,
            ),
            raw_payload={
                "summary": llm_result.summary,
                "llm_items": [item.model_dump() for item in llm_result.items],
                "deterministic_items": [item.model_dump() for item in fallback_result.items],
                "merged_items": [item.model_dump() for item in filtered_items],
            },
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
                for item in filtered_items
            ],
        )
    else:
        analysis = ContractAnalysis(
            contract_id=contract.id,
            contract_version_id=analysis_version.id,
            policy_version=policy.version if policy else "v1.0",
            status=AnalysisStatus.completed,
            contract_risk_score=fallback_result.contract_risk_score,
            raw_payload=fallback_result.model_dump(),
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
                for item in fallback_result.items
            ],
        )

    session.add(analysis)
    mark_contract_analysis_completed(contract)
    session.flush()


def run_contract_pipeline(
    session: Session,
    contract: Contract,
    contract_version: ContractVersion,
    *,
    llm_client: OpenAIAnalysisClient | None = None,
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
    contract.status = "analisado"

    existing_meta = dict(contract_version.extraction_metadata or {})
    existing_meta["field_confidence"] = metadata_result.field_confidence
    existing_meta["match_labels"] = metadata_result.match_labels
    contract_version.extraction_metadata = existing_meta

    scheduled_events = (
        build_contract_events(metadata_result)
        if metadata_result.ready_for_event_generation
        else []
    )
    persist_version_snapshot(
        contract_version,
        build_version_snapshot(
            metadata_result,
            scheduled_events=scheduled_events,
            contract_version_id=contract_version.id,
        ),
    )

    if metadata_result.ready_for_event_generation:
        replace_contract_events(
            contract,
            scheduled_events=scheduled_events,
            contract_version_id=contract_version.id,
        )

    run_policy_analysis(
        session,
        contract,
        text,
        contract_version=contract_version,
        llm_client=llm_client,
    )
