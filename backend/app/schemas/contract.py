from __future__ import annotations

from datetime import date, datetime
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
    is_active: bool
    activated_at: datetime | None = None
    last_accessed_at: datetime | None = None
    last_analyzed_at: datetime | None = None
    latest_analysis_status: str | None = None
    latest_contract_risk_score: float | None = None
    latest_version_source: str | None = None


class ContractListResponse(BaseModel):
    items: list[ContractListItem]


class ContractUpdateInput(BaseModel):
    title: str | None = None
    signature_date: date | None = None
    start_date: date | None = None
    end_date: date | None = None
    term_months: int | None = None
    is_active: bool | None = None


class ContractEventSummary(BaseModel):
    id: str
    event_type: str
    event_date: date | None = None
    lead_time_days: int
    metadata: dict[str, Any] = Field(default_factory=dict)


class ContractDetailSummary(BaseModel):
    id: str
    title: str
    external_reference: str
    status: str
    signature_date: date | None = None
    start_date: date | None = None
    end_date: date | None = None
    term_months: int | None = None
    is_active: bool
    activated_at: datetime | None = None
    last_accessed_at: datetime | None = None
    last_analyzed_at: datetime | None = None
    parties: dict[str, Any] | None = None
    financial_terms: dict[str, Any] | None = None
    field_confidence: dict[str, float] = Field(default_factory=dict)


class ContractVersionSummary(BaseModel):
    contract_version_id: str
    version_number: int
    created_at: datetime
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
    events: list[ContractEventSummary] = Field(default_factory=list)


class ContractSummaryResponse(BaseModel):
    summary: str
    key_points: list[str] = Field(default_factory=list)


class ContractVersionListItem(BaseModel):
    contract_version_id: str
    version_number: int
    created_at: datetime
    source: str
    original_filename: str
    used_ocr: bool
    analysis_status: str | None = None
    contract_risk_score: float | None = None
    is_current: bool


class ContractVersionListResponse(BaseModel):
    items: list[ContractVersionListItem] = Field(default_factory=list)


class ContractVersionDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    contract: ContractDetailSummary
    selected_version: ContractVersionSummary
    latest_version: ContractVersionSummary | None = None
    selected_analysis: ContractLatestAnalysisSummary | None = None
    events: list[ContractEventSummary] = Field(default_factory=list)
    is_current: bool


class ContractVersionTextDiffLine(BaseModel):
    kind: str
    value: str


class ContractVersionTextDiff(BaseModel):
    has_changes: bool
    lines: list[ContractVersionTextDiffLine] = Field(default_factory=list)


class ContractFindingDiffItem(BaseModel):
    clause_name: str
    change_type: str
    previous_status: str | None = None
    current_status: str | None = None
    previous_summary: str | None = None
    current_summary: str | None = None


class ContractFindingsDiff(BaseModel):
    items: list[ContractFindingDiffItem] = Field(default_factory=list)


class ContractVersionComparisonResponse(BaseModel):
    selected_version: ContractVersionSummary
    baseline_version: ContractVersionSummary | None = None
    summary: str
    text_diff: ContractVersionTextDiff
    findings_diff: ContractFindingsDiff


class PaginatedContractListResponse(BaseModel):
    """Paginated contract list response."""
    items: list[ContractListItem]
    page: int
    per_page: int
    total: int
    total_pages: int


class CorrectionItemResponse(BaseModel):
    """A single correction applied to a contract."""
    clause_name: str
    original_text: str
    corrected_text: str
    reason: str


class CorrectedContractResponse(BaseModel):
    """Response for contract correction generation."""
    corrected_text: str
    corrections: list[CorrectionItemResponse] = Field(default_factory=list)
