from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import openai


@dataclass
class SummaryResult:
    summary: str
    key_points: list[str]


class OpenAiLlmClient:
    def __init__(self, api_key: str, model: str = "gpt-4o-mini") -> None:
        import openai as _openai

        self.client: openai.OpenAI = _openai.OpenAI(api_key=api_key)
        self.model = model

    def summarize_contract(self, text: str) -> SummaryResult:
        system_prompt = (
            "Voce e um assistente juridico especializado em contratos de locacao. "
            "Resuma o contrato em 1 paragrafo curto e destaque ate 5 pontos-chave em bullets. "
            "Responda em portugues do Brasil."
        )
        user_prompt = f"Resuma o seguinte contrato:\n\n{text[:12000]}"

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
            max_tokens=800,
        )

        content = response.choices[0].message.content or ""
        lines = content.split("\n")
        summary_lines: list[str] = []
        key_points: list[str] = []
        in_key_points = False

        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            if stripped.lower().startswith(("pontos-chave", "pontos chave", "principais pontos", "key points")):
                in_key_points = True
                continue
            if in_key_points and (stripped.startswith("-") or stripped.startswith("*")):
                key_points.append(stripped.lstrip("-* ").strip())
            elif not in_key_points:
                summary_lines.append(stripped)

        summary = " ".join(summary_lines).strip()
        if not summary:
            summary = content[:500]

        return SummaryResult(summary=summary, key_points=key_points)
