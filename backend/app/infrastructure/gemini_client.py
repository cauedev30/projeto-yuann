"""Gemini 2.5 Flash client with structured output for contract analysis."""

from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING

from google import genai

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

if TYPE_CHECKING:
    from app.domain.playbook import PlaybookClause

logger = logging.getLogger(__name__)

CHUNK_SEPARATOR = "\n\n---\n\n"
MAX_RETRIES = 3
RETRY_BACKOFF_SECONDS = 2.0


class GeminiAnalysisClient:
    """Client for Gemini 2.5 Flash with structured JSON output.

    Uses google.genai SDK with response_schema for validated Pydantic responses.
    Retries once on failure; never returns empty dicts — always typed results.
    """

    def __init__(self, api_key: str, model: str = "gemini-1.5-flash") -> None:
        self._api_key = api_key
        self._model = model
        self._client = genai.Client(api_key=api_key)

    def analyze_contract(
        self,
        chunks: list[str],
        playbook: list[PlaybookClause],
    ) -> ContractAnalysisResult:
        """Analyze a contract against playbook clauses.

        Args:
            chunks: List of text chunks from the contract.
            playbook: List of PlaybookClause to validate against.

        Returns:
            ContractAnalysisResult — always a valid typed result, never {}.
        """
        contract_text = CHUNK_SEPARATOR.join(chunks)
        user_prompt = build_user_prompt(contract_text, playbook)

        return self._call_with_retry(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            response_model=ContractAnalysisResult,
            fallback=ContractAnalysisResult(
                contract_risk_score=0,
                items=[],
                summary="Analysis failed: {error}",
            ),
        )

    def summarize_contract(self, text: str) -> ContractSummaryResult:
        """Generate an executive summary of a contract.

        Args:
            text: Full contract text.

        Returns:
            ContractSummaryResult — always a valid typed result, never {}.
        """
        user_prompt = build_summary_user_prompt(text)

        return self._call_with_retry(
            system_prompt=SUMMARY_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            response_model=ContractSummaryResult,
            fallback=ContractSummaryResult(
                summary="Summary failed: {error}",
                key_points=[],
            ),
        )

    def generate_corrected_contract(
        self,
        original: str,
        findings: list[dict],
        playbook: list[PlaybookClause],
    ) -> CorrectedContractResult:
        """Generate a corrected version of the contract.

        Args:
            original: Original contract text.
            findings: List of finding dicts from a previous analysis.
            playbook: List of PlaybookClause for reference.

        Returns:
            CorrectedContractResult — always a valid typed result, never {}.
        """
        user_prompt = build_correction_prompt(original, findings, playbook)

        return self._call_with_retry(
            system_prompt=CORRECTION_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            response_model=CorrectedContractResult,
            fallback=CorrectedContractResult(
                corrected_text="",
                corrections=[],
            ),
        )

    def _call_with_retry(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        response_model: type,
        fallback,
    ):
        """Call Gemini API with one retry on failure.

        On error (API or validation), retries once after backoff.
        If retry also fails, returns the fallback with error message.
        """
        last_error: Exception | None = None

        for attempt in range(MAX_RETRIES + 1):
            try:
                response = self._client.models.generate_content(
                    model=self._model,
                    contents=user_prompt,
                    config=genai.types.GenerateContentConfig(
                        system_instruction=system_prompt,
                        response_mime_type="application/json",
                        response_schema=response_model,
                    ),
                )
                return response_model.model_validate_json(response.text)

            except Exception as exc:
                last_error = exc
                logger.warning(
                    "Gemini call failed (attempt %d/%d): %s",
                    attempt + 1,
                    MAX_RETRIES + 1,
                    exc,
                )
                if attempt < MAX_RETRIES:
                    wait_time = RETRY_BACKOFF_SECONDS * (2**attempt)
                    logger.warning(
                        "Gemini call failed (attempt %d/%d). Retrying in %.1fs...",
                        attempt + 1,
                        MAX_RETRIES + 1,
                        wait_time,
                    )
                    time.sleep(wait_time)

        # All retries exhausted — return fallback with error detail
        error_msg = str(last_error)
        return self._build_fallback(fallback, error_msg)

    @staticmethod
    def _build_fallback(fallback, error_msg: str):
        """Replace {error} placeholder in fallback string fields."""
        data = fallback.model_dump()
        for key, value in data.items():
            if isinstance(value, str) and "{error}" in value:
                data[key] = value.format(error=error_msg)
        return type(fallback).model_validate(data)
