from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.domain.playbook import PlaybookClause

try:
    import openai
except ImportError:  # pragma: no cover - exercised via runtime fallback
    openai = None

from app.infrastructure.llm_models import (
    ContractAnalysisResult,
    ContractSummaryResult,
    CorrectedContractResult,
    LLMTokenUsage,
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
    def __init__(self, api_key: str, model: str = "gpt-5-mini") -> None:
        self._api_key = api_key
        self._model = model
        self.last_analysis_usage: LLMTokenUsage | None = None
        if openai is None:
            self._client = None
            logger.warning("openai package not installed")
            return

        self._client = openai.OpenAI(api_key=api_key)

    @staticmethod
    def _extract_usage(completion: object) -> LLMTokenUsage | None:
        usage = getattr(completion, "usage", None)
        if usage is None:
            return None

        return LLMTokenUsage(
            prompt_tokens=int(getattr(usage, "prompt_tokens", 0) or 0),
            completion_tokens=int(getattr(usage, "completion_tokens", 0) or 0),
            total_tokens=int(getattr(usage, "total_tokens", 0) or 0),
        )

    def _parse_completion(
        self,
        *,
        messages: list[dict[str, str]],
        response_format: type[object],
        temperature: float,
    ) -> object:
        kwargs: dict[str, object] = {
            "model": self._model,
            "messages": messages,
            "response_format": response_format,
        }
        if not self._model.startswith("gpt-5"):
            kwargs["temperature"] = temperature

        return self._client.beta.chat.completions.parse(**kwargs)

    def analyze_contract(
        self,
        chunks: list[str],
        playbook: list[PlaybookClause],
    ) -> ContractAnalysisResult:
        self.last_analysis_usage = None
        if not self._client:
            return ContractAnalysisResult(
                contract_risk_score=0,
                items=[],
                summary="Analysis failed: openai package not installed",
            )

        contract_text = CHUNK_SEPARATOR.join(chunks)
        user_prompt = build_user_prompt(contract_text, playbook)

        try:
            completion = self._parse_completion(
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.1,
                response_format=ContractAnalysisResult,
            )
            self.last_analysis_usage = self._extract_usage(completion)
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
            completion = self._parse_completion(
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
            completion = self._parse_completion(
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
