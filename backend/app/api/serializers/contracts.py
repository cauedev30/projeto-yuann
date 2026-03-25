from __future__ import annotations

from typing import Any

from app.application.contract_versions import get_contract_version_snapshot
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
    ContractVersionDetailResponse,
    ContractVersionListItem,
    ContractVersionListResponse,
    ContractVersionSummary,
)


def latest_contract_version(contract: Contract) -> ContractVersion | None:
    if not contract.versions:
        return None
    return max(
        contract.versions,
        key=lambda version: (version.version_number, version.created_at, version.id),
    )


def latest_version_analysis(version: ContractVersion | None) -> ContractAnalysis | None:
    if version is None or not version.analyses:
        return None
    return max(
        version.analyses,
        key=lambda analysis: (analysis.created_at, analysis.id),
    )


def _serialize_event(event: ContractEvent) -> ContractEventSummary:
    return ContractEventSummary(
        id=event.id,
        event_type=event.event_type if isinstance(event.event_type, str) else event.event_type.value,
        event_date=event.event_date,
        lead_time_days=event.lead_time_days,
        metadata=event.metadata_json or {},
    )


def _serialize_snapshot_event(
    item: dict[str, Any],
    *,
    index: int,
) -> ContractEventSummary:
    return ContractEventSummary(
        id=f"snapshot-{index}",
        event_type=str(item.get("event_type", "")),
        event_date=item.get("event_date"),
        lead_time_days=int(item.get("lead_time_days", 0)),
        metadata=item.get("metadata") or {},
    )


def _extract_field_confidence(version: ContractVersion | None) -> dict[str, float]:
    if version is None:
        return {}
    snapshot = get_contract_version_snapshot(version) or {}
    contract_snapshot = snapshot.get("contract") or {}
    field_confidence = contract_snapshot.get("field_confidence")
    if isinstance(field_confidence, dict):
        return field_confidence
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
        version_number=version.version_number,
        created_at=version.created_at,
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


def _build_contract_summary(
    contract: Contract,
    *,
    version: ContractVersion | None,
    snapshot_contract: dict[str, Any] | None = None,
) -> ContractDetailSummary:
    return ContractDetailSummary(
        id=contract.id,
        title=contract.title,
        external_reference=contract.external_reference,
        status=contract.status,
        signature_date=(snapshot_contract or {}).get("signature_date", contract.signature_date),
        start_date=(snapshot_contract or {}).get("start_date", contract.start_date),
        end_date=(snapshot_contract or {}).get("end_date", contract.end_date),
        term_months=(snapshot_contract or {}).get("term_months", contract.term_months),
        is_active=contract.is_active,
        activated_at=contract.activated_at,
        last_accessed_at=contract.last_accessed_at,
        last_analyzed_at=contract.last_analyzed_at,
        parties=(snapshot_contract or {}).get("parties", contract.parties),
        financial_terms=(snapshot_contract or {}).get("financial_terms", contract.financial_terms),
        field_confidence=(snapshot_contract or {}).get(
            "field_confidence",
            _extract_field_confidence(version),
        ),
    )


def serialize_contract_list_item(contract: Contract) -> ContractListItem:
    latest_version = latest_contract_version(contract)
    latest_analysis = latest_version_analysis(latest_version)

    return ContractListItem(
        id=contract.id,
        title=contract.title,
        external_reference=contract.external_reference,
        status=contract.status,
        signature_date=contract.signature_date,
        start_date=contract.start_date,
        end_date=contract.end_date,
        term_months=contract.term_months,
        is_active=contract.is_active,
        activated_at=contract.activated_at,
        last_accessed_at=contract.last_accessed_at,
        last_analyzed_at=contract.last_analyzed_at,
        latest_analysis_status=latest_analysis.status.value if latest_analysis is not None else None,
        latest_contract_risk_score=float(latest_analysis.contract_risk_score)
        if latest_analysis is not None and latest_analysis.contract_risk_score is not None
        else None,
        latest_version_source=latest_version.source.value if latest_version is not None else None,
    )


def serialize_contract_detail(contract: Contract) -> ContractDetailResponse:
    latest_version = latest_contract_version(contract)
    latest_analysis = latest_version_analysis(latest_version)

    return ContractDetailResponse(
        contract=_build_contract_summary(contract, version=latest_version),
        latest_version=_serialize_version(latest_version),
        latest_analysis=_serialize_analysis(latest_analysis),
        events=[_serialize_event(event) for event in contract.events],
    )


def serialize_contract_version_list(contract: Contract) -> ContractVersionListResponse:
    current_version = latest_contract_version(contract)
    versions = sorted(
        contract.versions,
        key=lambda version: (version.version_number, version.created_at, version.id),
        reverse=True,
    )
    return ContractVersionListResponse(
        items=[
            ContractVersionListItem(
                contract_version_id=version.id,
                version_number=version.version_number,
                created_at=version.created_at,
                source=version.source.value,
                original_filename=version.original_filename,
                used_ocr=_normalize_used_ocr(version),
                analysis_status=latest_version_analysis(version).status.value
                if latest_version_analysis(version) is not None
                else None,
                contract_risk_score=float(latest_version_analysis(version).contract_risk_score)
                if latest_version_analysis(version) is not None
                and latest_version_analysis(version).contract_risk_score is not None
                else None,
                is_current=current_version is not None and version.id == current_version.id,
            )
            for version in versions
        ]
    )


def serialize_contract_version_detail(
    contract: Contract,
    contract_version: ContractVersion,
) -> ContractVersionDetailResponse:
    latest_version = latest_contract_version(contract)
    selected_analysis = latest_version_analysis(contract_version)
    snapshot = get_contract_version_snapshot(contract_version) or {}
    snapshot_contract = snapshot.get("contract") if isinstance(snapshot.get("contract"), dict) else None
    snapshot_events = snapshot.get("events") if isinstance(snapshot.get("events"), list) else None

    return ContractVersionDetailResponse(
        contract=_build_contract_summary(
            contract,
            version=contract_version,
            snapshot_contract=snapshot_contract,
        ),
        selected_version=_serialize_version(contract_version),
        latest_version=_serialize_version(latest_version),
        selected_analysis=_serialize_analysis(selected_analysis),
        events=[
            _serialize_snapshot_event(item, index=index)
            for index, item in enumerate(snapshot_events or [])
        ],
        is_current=latest_version is not None and latest_version.id == contract_version.id,
    )
