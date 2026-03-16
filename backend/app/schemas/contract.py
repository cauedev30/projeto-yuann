from __future__ import annotations

from datetime import date
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ContractListItem(BaseModel):
    id: str
    title: str
    external_reference: str
    status: str
    signature_date: date | None = None
    start_date: date | None = None
    end_date: date | None = None
    term_months: int | None = None
    latest_analysis_status: str | None = None
    latest_contract_risk_score: float | None = None
    latest_version_source: str | None = None


class ContractListResponse(BaseModel):
    items: list[ContractListItem]


class ContractDetailSummary(BaseModel):
    id: str
    title: str
    external_reference: str
    status: str
    signature_date: date | None = None
    start_date: date | None = None
    end_date: date | None = None
    term_months: int | None = None
    parties: dict[str, Any] | None = None
    financial_terms: dict[str, Any] | None = None


class ContractVersionSummary(BaseModel):
    contract_version_id: str
    source: str
    original_filename: str
    used_ocr: bool
    text: str | None = None


class ContractAnalysisFindingSummary(BaseModel):
    id: str
    clause_name: str
    status: str
    severity: str
    current_summary: str
    policy_rule: str
    risk_explanation: str
    suggested_adjustment_direction: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class ContractLatestAnalysisSummary(BaseModel):
    analysis_id: str
    analysis_status: str
    policy_version: str
    contract_risk_score: float | None = None
    findings: list[ContractAnalysisFindingSummary] = Field(default_factory=list)


class ContractDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    contract: ContractDetailSummary
    latest_version: ContractVersionSummary | None = None
    latest_analysis: ContractLatestAnalysisSummary | None = None
