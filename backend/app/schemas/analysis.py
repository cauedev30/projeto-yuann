from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class AnalysisItem(BaseModel):
    clause_name: str
    status: str
    severity: str
    current_summary: str
    policy_rule: str
    risk_explanation: str
    suggested_adjustment_direction: str
    metadata: dict[str, object] = Field(default_factory=dict)


class ContractAnalysisResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    contract_risk_score: float = 0
    items: list[AnalysisItem] = Field(default_factory=list)
