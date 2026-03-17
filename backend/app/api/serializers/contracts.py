from __future__ import annotations

from app.db.models.analysis import ContractAnalysis, ContractAnalysisFinding
from app.db.models.contract import Contract, ContractVersion
from app.db.models.event import ContractEvent
from app.schemas.contract import (
    ContractAnalysisFindingSummary,
    ContractDetailResponse,
    ContractDetailSummary,
    ContractEventSummary,
    ContractLatestAnalysisSummary,
    ContractListItem,
    ContractVersionSummary,
)


def _latest_version(contract: Contract) -> ContractVersion | None:
    if not contract.versions:
        return None
    return max(contract.versions, key=lambda version: (version.created_at, version.id))


def _latest_analysis(contract: Contract) -> ContractAnalysis | None:
    if not contract.analyses:
        return None
    return max(contract.analyses, key=lambda analysis: (analysis.created_at, analysis.id))


def _serialize_event(event: ContractEvent) -> ContractEventSummary:
    return ContractEventSummary(
        id=event.id,
        event_type=event.event_type if isinstance(event.event_type, str) else event.event_type.value,
        event_date=event.event_date,
        lead_time_days=event.lead_time_days,
        metadata=event.metadata_json or {},
    )


def _extract_field_confidence(contract: Contract) -> dict[str, float]:
    version = _latest_version(contract)
    if version is None:
        return {}
    metadata = version.extraction_metadata or {}
    return metadata.get("field_confidence") or {}


def _normalize_used_ocr(version: ContractVersion) -> bool:
    metadata = version.extraction_metadata or {}
    return bool(metadata.get("ocr_attempted"))


def _serialize_finding(finding: ContractAnalysisFinding) -> ContractAnalysisFindingSummary:
    return ContractAnalysisFindingSummary(
        id=finding.id,
        clause_name=finding.clause_name,
        status=finding.status,
        severity=finding.severity,
        current_summary=finding.current_summary,
        policy_rule=finding.policy_rule,
        risk_explanation=finding.risk_explanation,
        suggested_adjustment_direction=finding.suggested_adjustment_direction,
        metadata=finding.metadata_json or {},
    )


def _serialize_version(version: ContractVersion | None) -> ContractVersionSummary | None:
    if version is None:
        return None

    return ContractVersionSummary(
        contract_version_id=version.id,
        source=version.source.value,
        original_filename=version.original_filename,
        used_ocr=_normalize_used_ocr(version),
        text=version.text_content,
    )


def _serialize_analysis(analysis: ContractAnalysis | None) -> ContractLatestAnalysisSummary | None:
    if analysis is None:
        return None

    return ContractLatestAnalysisSummary(
        analysis_id=analysis.id,
        analysis_status=analysis.status.value,
        policy_version=analysis.policy_version,
        contract_risk_score=float(analysis.contract_risk_score)
        if analysis.contract_risk_score is not None
        else None,
        findings=[_serialize_finding(finding) for finding in analysis.findings],
    )


def serialize_contract_list_item(contract: Contract) -> ContractListItem:
    latest_version = _latest_version(contract)
    latest_analysis = _latest_analysis(contract)

    return ContractListItem(
        id=contract.id,
        title=contract.title,
        external_reference=contract.external_reference,
        status=contract.status,
        signature_date=contract.signature_date,
        start_date=contract.start_date,
        end_date=contract.end_date,
        term_months=contract.term_months,
        latest_analysis_status=latest_analysis.status.value if latest_analysis is not None else None,
        latest_contract_risk_score=float(latest_analysis.contract_risk_score)
        if latest_analysis is not None and latest_analysis.contract_risk_score is not None
        else None,
        latest_version_source=latest_version.source.value if latest_version is not None else None,
    )


def serialize_contract_detail(contract: Contract) -> ContractDetailResponse:
    return ContractDetailResponse(
        contract=ContractDetailSummary(
            id=contract.id,
            title=contract.title,
            external_reference=contract.external_reference,
            status=contract.status,
            signature_date=contract.signature_date,
            start_date=contract.start_date,
            end_date=contract.end_date,
            term_months=contract.term_months,
            parties=contract.parties,
            financial_terms=contract.financial_terms,
            field_confidence=_extract_field_confidence(contract),
        ),
        latest_version=_serialize_version(_latest_version(contract)),
        latest_analysis=_serialize_analysis(_latest_analysis(contract)),
        events=[_serialize_event(event) for event in contract.events],
    )
