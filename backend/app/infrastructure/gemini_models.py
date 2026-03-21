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

    clause_code: str = Field(description="Codigo interno da clausula (ex: EXCLUSIVIDADE, PRAZO)")
    clause_title: str = Field(description="Nome amigavel da clausula em portugues (ex: 'Prazo do Contrato', 'Multa Rescisoria', 'Infraestrutura do Imovel')")
    severity: Literal["critical", "attention"] = Field(
        description="Severidade: critical=risco alto, attention=requer revisao"
    )
    risk_score: int = Field(ge=0, le=100, description="Score de risco 0-100")
    explanation: str = Field(description="Explicacao CONCISA do problema (max 2 frases)")
    suggested_correction: str = Field(default="", description="Acao sugerida em 1 frase. Vazio se nao aplicavel.")
    page_reference: str | None = Field(default=None, description="Referencia de pagina se disponivel")


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
