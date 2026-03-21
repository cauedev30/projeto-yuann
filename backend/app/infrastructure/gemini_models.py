"""Pydantic response models for Gemini structured output.

These models define the expected JSON schema for responses from Gemini 2.5 Flash.
They live in the infrastructure layer because they represent the shape of the LLM
response, not domain objects.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class AnalysisFindingItem(BaseModel):
    """A single finding from the contract analysis."""

    clause_code: str = Field(description="Playbook clause code (e.g., EXCLUSIVIDADE, PRAZO)")
    clause_title: str = Field(description="Human-readable clause title")
    severity: Literal["critical", "attention", "conforme"] = Field(
        description="Risk severity: critical=high risk, attention=medium risk, conforme=compliant"
    )
    risk_score: int = Field(ge=0, le=100, description="Risk score 0-100 (100=highest risk)")
    explanation: str = Field(description="Detailed explanation of the finding in Portuguese")
    suggested_correction: str = Field(description="Suggested text adjustment or 'N/A' if compliant")
    page_reference: str | None = Field(default=None, description="Page reference if available")


class ContractAnalysisResult(BaseModel):
    """Full result of a contract risk analysis."""

    contract_risk_score: int = Field(ge=0, le=100)
    items: list[AnalysisFindingItem]
    summary: str


class ContractSummaryResult(BaseModel):
    """Result of a contract summarization."""

    summary: str
    key_points: list[str]


class CorrectionItem(BaseModel):
    """A single correction applied to a contract clause."""

    clause_name: str
    original_text: str
    corrected_text: str
    reason: str


class CorrectedContractResult(BaseModel):
    """Result of a contract correction operation."""

    corrected_text: str
    corrections: list[CorrectionItem]
