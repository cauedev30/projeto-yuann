from __future__ import annotations

import calendar
import re
from datetime import date, timedelta

from app.schemas.metadata import ContractMetadataResult


def _parse_brazilian_date(value: str | None) -> date | None:
    if value is None:
        return None

    day, month, year = value.split("/")
    return date(int(year), int(month), int(day))


def _add_months(base_date: date, months: int) -> date:
    zero_based_month = base_date.month - 1 + months
    year = base_date.year + zero_based_month // 12
    month = zero_based_month % 12 + 1
    day = min(base_date.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def _first_match(
    contract_text: str,
    patterns: list[tuple[str, str]],
) -> tuple[str | None, re.Match[str] | None]:
    for label, pattern in patterns:
        match = re.search(pattern, contract_text, re.IGNORECASE)
        if match:
            return label, match
    return None, None


def extract_contract_metadata(contract_text: str) -> ContractMetadataResult:
    signature_label, signature_match = _first_match(
        contract_text,
        [
            ("data de assinatura", r"data de assinatura\s*:\s*(\d{2}/\d{2}/\d{4})"),
            ("assinatura", r"assinatura\s*:\s*(\d{2}/\d{2}/\d{4})"),
        ],
    )
    start_label, start_match = _first_match(
        contract_text,
        [
            ("inicio de vigencia", r"in[ií]cio de vig[eê]ncia\s*:\s*(\d{2}/\d{2}/\d{4})"),
            ("inicio da vigencia", r"in[ií]cio da vig[eê]ncia\s*:\s*(\d{2}/\d{2}/\d{4})"),
            ("vigencia inicial", r"vig[eê]ncia inicial\s*:\s*(\d{2}/\d{2}/\d{4})"),
        ],
    )
    term_label, term_match = _first_match(
        contract_text,
        [
            ("prazo de vigencia", r"prazo de vig[eê]ncia\s*:\s*(\d+)\s*meses"),
            ("prazo contratual", r"prazo contratual\s*:\s*(\d+)\s*meses"),
        ],
    )
    parties_label, parties_match = _first_match(
        contract_text,
        [
            (
                "locataria / franqueada",
                r"locat[aá]ria\s*/\s*franqueada\s*:\s*(.+?)(?=\s+(?:car[eê]ncia|reajuste|data de assinatura|assinatura|in[ií]cio|prazo)\b|[.;]|$)",
            ),
            (
                "locataria",
                r"locat[aá]ria\s*:\s*(.+?)(?=\s+(?:car[eê]ncia|reajuste|data de assinatura|assinatura|in[ií]cio|prazo)\b|[.;]|$)",
            ),
            (
                "franqueada",
                r"franqueada\s*:\s*(.+?)(?=\s+(?:car[eê]ncia|reajuste|data de assinatura|assinatura|in[ií]cio|prazo)\b|[.;]|$)",
            ),
        ],
    )
    grace_label, grace_match = _first_match(
        contract_text,
        [
            ("carencia de", r"car[eê]ncia de\s*(\d+)\s*meses"),
            ("carencia", r"car[eê]ncia\s*:\s*(\d+)\s*meses"),
        ],
    )
    readjustment_label, readjustment_match = _first_match(
        contract_text,
        [("reajuste anual", r"reajuste\s+anual")],
    )

    signature_date = _parse_brazilian_date(signature_match.group(1) if signature_match else None)
    start_date = _parse_brazilian_date(start_match.group(1) if start_match else None)
    term_months = int(term_match.group(1)) if term_match else None

    end_date = None
    if start_date is not None and term_months is not None:
        end_date = _add_months(start_date, term_months) - timedelta(days=1)

    parties = [parties_match.group(1).strip()] if parties_match else []
    financial_terms: dict[str, object] = {}
    if grace_match:
        financial_terms["grace_period_months"] = int(grace_match.group(1))
    if readjustment_match:
        financial_terms["readjustment_type"] = "annual"

    field_confidence = {
        "signature_date": 1.0 if signature_date else 0.0,
        "start_date": 1.0 if start_date else 0.0,
        "term_months": 1.0 if term_months is not None else 0.0,
        "end_date": 1.0 if end_date else 0.0,
        "parties": 1.0 if parties else 0.0,
        "grace_period_months": 1.0 if "grace_period_months" in financial_terms else 0.0,
        "readjustment_type": 1.0 if "readjustment_type" in financial_terms else 0.0,
    }
    match_labels = {
        field: label
        for field, label in {
            "signature_date": signature_label,
            "start_date": start_label,
            "term_months": term_label,
            "parties": parties_label,
            "grace_period_months": grace_label,
            "readjustment_type": readjustment_label,
        }.items()
        if label is not None
    }

    return ContractMetadataResult(
        signature_date=signature_date,
        start_date=start_date,
        end_date=end_date,
        term_months=term_months,
        parties=parties,
        financial_terms=financial_terms,
        field_confidence=field_confidence,
        match_labels=match_labels,
        ready_for_event_generation=start_date is not None and end_date is not None,
    )
