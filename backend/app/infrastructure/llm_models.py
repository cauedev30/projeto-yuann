"""Typed response models shared by the OpenAI-backed LLM workflows."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class AnalysisFindingItem(BaseModel):
    clause_code: str = Field(description="Codigo interno da clausula analisada.")
    clause_title: str = Field(description="Nome amigavel da clausula em portugues.")
    classification: Literal["adequada", "risco_medio", "ausente", "conflitante"] = (
        Field(
            description="Classificacao canonica: adequada, risco_medio, ausente ou conflitante."
        )
    )
    severity: Literal["critical", "attention"] = Field(
        description="Severidade do achado: critical ou attention."
    )
    risk_score: int = Field(ge=0, le=100, description="Score de risco do achado.")
    explanation: str = Field(description="Explicacao objetiva do problema encontrado.")
    suggested_correction: str = Field(
        default="",
        description="Correcao sugerida para resolver o achado.",
    )
    page_reference: str | None = Field(
        default=None,
        description="Referencia de pagina quando disponivel.",
    )


class ContractAnalysisResult(BaseModel):
    contract_risk_score: int = Field(ge=0, le=100)
    items: list[AnalysisFindingItem]
    summary: str


class ContractSummaryResult(BaseModel):
    summary: str
    key_points: list[str]


class LLMTokenUsage(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class CorrectionItem(BaseModel):
    clause_name: str
    original_text: str
    corrected_text: str
    reason: str


class CorrectedContractResult(BaseModel):
    corrected_text: str
    corrections: list[CorrectionItem]
