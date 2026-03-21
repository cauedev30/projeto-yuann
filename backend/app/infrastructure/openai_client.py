from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.domain.playbook import PlaybookClause

from app.infrastructure.gemini_models import (
    ContractAnalysisResult,
    ContractSummaryResult,
    CorrectedContractResult,
)
from app.infrastructure.prompts import (
    CORRECTION_SYSTEM_PROMPT,
    SUMMARY_SYSTEM_PROMPT,
    SYSTEM_PROMPT,
    build_correction_prompt,
    build_summary_user_prompt,
    build_user_prompt,
)

logger = logging.getLogger(__name__)

CHUNK_SEPARATOR = "\n\n---\n\n"


class OpenAIAnalysisClient:
    def __init__(self, api_key: str, model: str = "gpt-4o-mini") -> None:
        self._api_key = api_key
        self._model = model
        try:
            import openai
            self._client = openai.OpenAI(api_key=api_key)
        except ImportError:
            self._client = None
            logger.warning("openai package not installed")

    def analyze_contract(
        self,
        chunks: list[str],
        playbook: list[PlaybookClause],
    ) -> ContractAnalysisResult:
        if not self._client:
            return ContractAnalysisResult(
                contract_risk_score=0,
                items=[],
                summary="Analysis failed: openai package not installed",
            )

        contract_text = CHUNK_SEPARATOR.join(chunks)
        user_prompt = build_user_prompt(contract_text, playbook)

        try:
            completion = self._client.beta.chat.completions.parse(
                model=self._model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.1,
                response_format=ContractAnalysisResult,
            )
            return completion.choices[0].message.parsed
        except Exception as e:
            logger.exception("OpenAI analysis failed")
            return ContractAnalysisResult(
                contract_risk_score=0,
                items=[],
                summary=f"Analysis failed: {str(e)}",
            )

    def summarize_contract(self, text: str) -> ContractSummaryResult:
        if not self._client:
            return ContractSummaryResult(
                summary="Summary failed: openai package not installed",
                key_points=[],
            )

        user_prompt = build_summary_user_prompt(text)

        try:
            completion = self._client.beta.chat.completions.parse(
                model=self._model,
                messages=[
                    {"role": "system", "content": SUMMARY_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.2,
                response_format=ContractSummaryResult,
            )
            return completion.choices[0].message.parsed
        except Exception as e:
            logger.exception("OpenAI summary failed")
            return ContractSummaryResult(
                summary=f"Summary failed: {str(e)}",
                key_points=[],
            )

    def generate_corrected_contract(
        self,
        original: str,
        findings: list[dict],
        playbook: list[PlaybookClause],
    ) -> CorrectedContractResult:
        if not self._client:
            return CorrectedContractResult(
                corrected_text="",
                corrections=[],
            )

        user_prompt = build_correction_prompt(original, findings, playbook)

        try:
            completion = self._client.beta.chat.completions.parse(
                model=self._model,
                messages=[
                    {"role": "system", "content": CORRECTION_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.1,
                response_format=CorrectedContractResult,
            )
            return completion.choices[0].message.parsed
        except Exception as e:
            logger.exception("OpenAI correction failed")
            return CorrectedContractResult(
                corrected_text="",
                corrections=[],
            )
