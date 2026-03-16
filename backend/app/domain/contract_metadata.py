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


def extract_contract_metadata(contract_text: str) -> ContractMetadataResult:
    signature_match = re.search(r"assinatura:\s*(\d{2}/\d{2}/\d{4})", contract_text, re.IGNORECASE)
    start_match = re.search(r"inicio de vigencia:\s*(\d{2}/\d{2}/\d{4})", contract_text, re.IGNORECASE)
    term_match = re.search(r"prazo de vigencia:\s*(\d+)\s*meses", contract_text, re.IGNORECASE)
    tenant_match = re.search(r"locataria:\s*([^.]+)", contract_text, re.IGNORECASE)
    grace_match = re.search(r"carencia de\s*(\d+)\s*meses", contract_text, re.IGNORECASE)
    readjustment_match = re.search(r"reajuste\s+anual", contract_text, re.IGNORECASE)

    signature_date = _parse_brazilian_date(signature_match.group(1) if signature_match else None)
    start_date = _parse_brazilian_date(start_match.group(1) if start_match else None)
    term_months = int(term_match.group(1)) if term_match else None

    end_date = None
    if start_date is not None and term_months is not None:
        end_date = _add_months(start_date, term_months) - timedelta(days=1)

    parties = [tenant_match.group(1).strip()] if tenant_match else []
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
    }

    return ContractMetadataResult(
        signature_date=signature_date,
        start_date=start_date,
        end_date=end_date,
        term_months=term_months,
        parties=parties,
        financial_terms=financial_terms,
        field_confidence=field_confidence,
    )
