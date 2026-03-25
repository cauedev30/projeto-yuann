from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.db.models.analysis import AnalysisStatus, ContractAnalysis, ContractAnalysisFinding
from app.db.models.contract import Contract
from app.schemas.analysis import ContractAnalysisResult


def mark_contract_analysis_completed(
    contract: Contract,
    *,
    analyzed_at: datetime | None = None,
) -> None:
    contract.last_analyzed_at = analyzed_at or datetime.now(timezone.utc)


def persist_contract_analysis(
    session: Session,
    *,
    contract_id: str,
    policy_version: str,
    analysis_result: ContractAnalysisResult,
) -> ContractAnalysis:
    analysis = ContractAnalysis(
        contract_id=contract_id,
        policy_version=policy_version,
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
    contract = session.get(Contract, contract_id)
    if contract is not None:
        mark_contract_analysis_completed(contract)
    session.commit()
    session.refresh(analysis)
    return analysis
