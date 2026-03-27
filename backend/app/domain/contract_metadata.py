from __future__ import annotations

import calendar
import re
from datetime import date, timedelta

from app.schemas.metadata import ContractMetadataResult

_MONTH_NAMES: dict[str, int] = {
    "janeiro": 1,
    "fevereiro": 2,
    "marco": 3,
    "março": 3,
    "abril": 4,
    "maio": 5,
    "junho": 6,
    "julho": 7,
    "agosto": 8,
    "setembro": 9,
    "outubro": 10,
    "novembro": 11,
    "dezembro": 12,
}

_RE_NUMERIC_DATE = re.compile(r"(\d{1,2})/(\d{1,2})/(\d{4})")
_RE_WRITTEN_DATE = re.compile(
    r"(\d{1,2})\s+de\s+([A-Za-zÀ-ÿ]+)\s+de\s+(\d{4})",
    re.IGNORECASE,
)


def _parse_date_numeric(match: re.Match[str]) -> date | None:
    try:
        return date(int(match.group(3)), int(match.group(2)), int(match.group(1)))
    except (ValueError, IndexError):
        return None


def _parse_date_written(match: re.Match[str]) -> date | None:
    month = _MONTH_NAMES.get(match.group(2).lower())
    if month is None:
        return None
    try:
        return date(int(match.group(3)), month, int(match.group(1)))
    except (ValueError, IndexError):
        return None


def _extract_date_from_fragment(text: str) -> date | None:
    numeric_match = _RE_NUMERIC_DATE.search(text)
    if numeric_match:
        return _parse_date_numeric(numeric_match)

    written_match = _RE_WRITTEN_DATE.search(text)
    if written_match:
        return _parse_date_written(written_match)

    return None


def _parse_brazilian_date(value: str | None) -> date | None:
    if value is None:
        return None
    day, month, year = value.split("/")
    return date(int(year), int(month), int(day))


def _parse_brl(raw: str) -> float | None:
    cleaned = raw.replace(".", "").replace(",", ".")
    try:
        return float(cleaned)
    except ValueError:
        return None


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


def _extract_parties(contract_text: str) -> tuple[dict[str, object], str | None]:
    entities: list[str] = []
    seen_names: set[str] = set()
    parties: dict[str, object] = {}
    label: str | None = None
    party_patterns: list[tuple[str, str, str | None]] = [
        (
            r"LOCADOR(?:A)?\s*:\s*(.{2,130}?)(?:\n|,\s*(?:inscrit|CNPJ|CPF|com sede|residente|portador|pessoa|empresa|denominad)|[.;]|$)",
            "locador",
            "locador",
        ),
        (
            r"LOCAT[ÁA]RIO(?:A)?\s*:\s*(.{2,130}?)(?:\n|,\s*(?:inscrit|CNPJ|CPF|com sede|residente|portador|pessoa|empresa|denominad)|[.;]|$)",
            "locatario",
            "locatario",
        ),
        (
            r"locat[áa]ria\s*/\s*franqueada\s*:\s*(.{2,130}?)(?=\s+(?:car[êe]ncia|reajuste|data|assinatura|in[íi]cio|prazo)\b|[.;\n]|$)",
            "locataria / franqueada",
            "locatario",
        ),
        (
            r"locat[áa]ria\s*:\s*(.{2,130}?)(?=\s+(?:car[êe]ncia|reajuste|data|assinatura|in[íi]cio|prazo)\b|[.;\n]|$)",
            "locataria",
            "locatario",
        ),
        (
            r"franqueada\s*:\s*(.{2,130}?)(?=\s+(?:car[êe]ncia|reajuste|data|assinatura|in[íi]cio|prazo)\b|[.;\n]|$)",
            "franqueada",
            "locatario",
        ),
        (
            r"FIADOR(?:A)?\s*:\s*(.{2,130}?)(?:\n|,\s*(?:inscrit|CNPJ|CPF|com sede|residente|portador|pessoa|empresa|denominad)|[.;]|$)",
            "fiador",
            "fiador",
        ),
    ]

    for pattern, role_label, party_key in party_patterns:
        match = re.search(pattern, contract_text, re.IGNORECASE)
        if not match:
            continue

        name = match.group(1).strip().rstrip(",;.")
        normalized = name.upper()
        if not name or len(name) <= 2:
            continue

        if normalized not in seen_names:
            entities.append(name[:145])
            seen_names.add(normalized)

        if party_key and party_key not in parties:
            parties[party_key] = name[:145]

        if label is None:
            label = role_label

    if entities:
        parties["entities"] = entities

    return parties, label


def extract_contract_metadata(contract_text: str) -> ContractMetadataResult:
    signature_label, signature_match = _first_match(
        contract_text,
        [
            ("data de assinatura", r"data de assinatura\s*:\s*(\d{2}/\d{2}/\d{4})"),
            ("assinatura", r"assinatura\s*:\s*(\d{2}/\d{2}/\d{4})"),
            ("assinado em", r"assinad[oa]\s+em\s+(.+?)(?:\.|$)"),
            ("firmado em", r"firmad[oa]\s+em\s+(.+?)(?:\.|$)"),
        ],
    )
    signature_date = None
    if signature_match:
        raw = signature_match.group(1)
        if re.match(r"\d{2}/\d{2}/\d{4}$", raw.strip()):
            signature_date = _parse_brazilian_date(raw.strip())
        else:
            signature_date = _extract_date_from_fragment(raw)

    start_label, start_match = _first_match(
        contract_text,
        [
            ("inicio de vigencia", r"in[íi]cio de vig[êe]ncia\s*:\s*(\d{2}/\d{2}/\d{4})"),
            ("inicio da vigencia", r"in[íi]cio da vig[êe]ncia\s*:\s*(\d{2}/\d{2}/\d{4})"),
            ("vigencia inicial", r"vig[êe]ncia inicial\s*:\s*(\d{2}/\d{2}/\d{4})"),
            ("iniciando-se", r"iniciando[- ]se\s+(?:no dia\s+|em\s+)(.+?)(?:[,.]|\s+e\s+terminando|\s+at[ée])"),
            ("com inicio em", r"com\s+in[íi]cio\s+em\s+(.+?)(?:[,.]|\s+e\s+|\s+at[ée])"),
            ("a partir de", r"a\s+partir\s+de\s+(.+?)(?:[,.]|\s+e\s+|\s+at[ée])"),
        ],
    )
    start_date = None
    if start_match:
        raw = start_match.group(1)
        if re.match(r"\d{2}/\d{2}/\d{4}$", raw.strip()):
            start_date = _parse_brazilian_date(raw.strip())
        else:
            start_date = _extract_date_from_fragment(raw)

    end_label, end_match = _first_match(
        contract_text,
        [
            ("terminando", r"terminando\s+(?:no dia\s+|em\s+)(.+?)(?:[,.]|\s+(?:podendo|prorrog|renov))"),
            ("termino em", r"t[ée]rmino\s+em\s+(.+?)(?:[,.]|\s+(?:podendo|prorrog|renov))"),
            ("data de termino", r"data\s+de\s+t[ée]rmino\s*:\s*(.+?)(?:[,.]|\s+(?:podendo|prorrog|renov))"),
            ("ate o dia", r"at[ée]\s+o\s+dia\s+(.+?)(?:[,.]|\s+(?:podendo|prorrog|renov))"),
            ("vigencia ate", r"vig[êe]ncia\s+at[ée]\s+(.+?)(?:[,.]|\s+(?:podendo|prorrog|renov))"),
        ],
    )
    explicit_end_date = None
    if end_match:
        raw = end_match.group(1)
        if re.match(r"\d{2}/\d{2}/\d{4}$", raw.strip()):
            explicit_end_date = _parse_brazilian_date(raw.strip())
        else:
            explicit_end_date = _extract_date_from_fragment(raw)

    term_label, term_match = _first_match(
        contract_text,
        [
            ("prazo do contrato", r"prazo\s+do\s+presente\s+contrato\s+[ée]\s+de\s+(\d+)\s*(?:\([^)]*\)\s*)?meses"),
            ("prazo de vigencia", r"prazo\s+de\s+vig[êe]ncia\s*(?::\s*|\s+[ée]\s+de\s+)(\d+)\s*(?:\([^)]*\)\s*)?meses"),
            ("prazo contratual", r"prazo\s+contratual\s*(?::\s*|\s+[ée]\s+de\s+)(\d+)\s*(?:\([^)]*\)\s*)?meses"),
            ("prazo de N meses", r"prazo\s+de\s+(\d+)\s*(?:\([^)]*\)\s*)?meses"),
            ("vigencia de N meses", r"vig[êe]ncia\s+de\s+(\d+)\s*(?:\([^)]*\)\s*)?meses"),
        ],
    )
    term_months = int(term_match.group(1)) if term_match else None

    end_date = explicit_end_date
    if end_date is None and start_date is not None and term_months is not None:
        end_date = _add_months(start_date, term_months) - timedelta(days=1)

    if term_months is None and start_date is not None and end_date is not None:
        delta_months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
        if delta_months > 0:
            term_months = delta_months
            term_label = "calculado"

    parties, parties_label = _extract_parties(contract_text)

    grace_label, grace_match = _first_match(
        contract_text,
        [
            ("carencia de", r"car[êe]ncia\s+de\s+(\d+)\s*meses"),
            ("carencia", r"car[êe]ncia\s*:\s*(\d+)\s*meses"),
        ],
    )

    financial_terms: dict[str, object] = {}

    rent_label, rent_match = _first_match(
        contract_text,
        [
            ("aluguel mensal", r"aluguel\s+mensal\s+(?:de\s+)?R\$\s*([\d.,]+)"),
            ("valor do aluguel", r"valor\s+(?:do\s+)?aluguel\s*(?::\s*|de\s+|ser[áa]\s+de\s+)R\$\s*([\d.,]+)"),
            ("aluguel de R$", r"aluguel\s+(?:de\s+)?R\$\s*([\d.,]+)"),
            ("R$ mensal", r"R\$\s*([\d.,]+)\s*(?:\([^)]*\)\s*)?[,.]?\s*(?:mensal|mensais|por\s+m[êe]s|de\s+aluguel)"),
        ],
    )
    if rent_match:
        parsed = _parse_brl(rent_match.group(1))
        if parsed is not None:
            financial_terms["monthly_rent"] = parsed

    if grace_match:
        financial_terms["grace_period_months"] = int(grace_match.group(1))

    readjustment_label, readjustment_match = _first_match(
        contract_text,
        [
            ("reajuste anual", r"reajuste\s+anual"),
            ("reajuste IGP-M", r"(?:IGP[- ]?M|IGPM)"),
            ("reajuste IPCA", r"IPCA"),
        ],
    )
    if readjustment_match:
        financial_terms["readjustment_type"] = "annual"

    fine_label, fine_match = _first_match(
        contract_text,
        [
            ("multa N vezes aluguel", r"multa\s+.*?(\d+)\s*(?:\([^)]*\)\s*)?vezes\s+o\s+valor"),
            ("multa de N alugueis", r"multa\s+de\s+(\d+)\s+alug"),
            ("equivalente a N", r"equivalente\s+a\s+(\d+)\s*(?:\([^)]*\)\s*)?(?:vezes|alug)"),
        ],
    )
    if fine_match:
        financial_terms["penalty_months"] = int(fine_match.group(1))

    field_confidence = {
        "signature_date": 1.0 if signature_date else 0.0,
        "start_date": 1.0 if start_date else 0.0,
        "term_months": 1.0 if term_months is not None else 0.0,
        "end_date": 1.0 if end_date else 0.0,
        "parties": 1.0 if parties else 0.0,
        "grace_period_months": 1.0 if "grace_period_months" in financial_terms else 0.0,
        "readjustment_type": 1.0 if "readjustment_type" in financial_terms else 0.0,
        "monthly_rent": 1.0 if "monthly_rent" in financial_terms else 0.0,
        "penalty_months": 1.0 if "penalty_months" in financial_terms else 0.0,
    }

    match_labels = {}
    for field, label in {
        "signature_date": signature_label,
        "start_date": start_label,
        "end_date": end_label if explicit_end_date else (term_label if end_date else None),
        "term_months": term_label,
        "parties": parties_label,
        "grace_period_months": grace_label,
        "readjustment_type": readjustment_label,
        "monthly_rent": rent_label,
        "penalty_months": fine_label,
    }.items():
        if label is not None:
            match_labels[field] = label

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
