from __future__ import annotations

import json
import logging

from app.infrastructure.prompts import SYSTEM_PROMPT, SUMMARY_SYSTEM_PROMPT, build_user_prompt, build_summary_user_prompt

logger = logging.getLogger(__name__)


class OpenAIAnalysisClient:
    def __init__(self, *, api_key: str, model: str = "gpt-4o-mini") -> None:
        self._api_key = api_key
        self._model = model

    def analyze_contract(self, *, contract_text: str, policy_rules: list[dict]) -> dict:
        try:
            import openai
        except ImportError:
            logger.warning("openai package not installed, returning empty analysis")
            return {"contract_risk_score": 0, "items": []}

        client = openai.OpenAI(api_key=self._api_key)
        user_prompt = build_user_prompt(contract_text, policy_rules)

        try:
            response = client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.1,
                response_format={"type": "json_object"},
            )
            content = response.choices[0].message.content or "{}"
            return json.loads(content)
        except Exception:
            logger.exception("OpenAI analysis failed, returning empty result")
            return {"contract_risk_score": 0, "items": []}

    def summarize_contract(self, *, contract_text: str) -> dict:
        try:
            import openai
        except ImportError:
            logger.warning("openai package not installed, returning empty summary")
            return {"summary": "", "key_points": []}

        client = openai.OpenAI(api_key=self._api_key)
        user_prompt = build_summary_user_prompt(contract_text)

        try:
            response = client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": SUMMARY_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.2,
                response_format={"type": "json_object"},
            )
            content = response.choices[0].message.content or "{}"
            return json.loads(content)
        except Exception:
            logger.exception("OpenAI summary failed, returning empty result")
            return {"summary": "", "key_points": []}
