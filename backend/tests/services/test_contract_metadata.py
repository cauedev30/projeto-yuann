from app.services.contract_metadata import extract_contract_metadata


def test_extract_contract_metadata_parses_dates_and_term() -> None:
    contract_text = (
        "Data de assinatura: 01/03/2026. "
        "Inicio de vigencia: 01/04/2026. "
        "Prazo de vigencia: 60 meses. "
        "Locataria: Franquia XPTO LTDA."
    )

    result = extract_contract_metadata(contract_text)

    assert result.signature_date.isoformat() == "2026-03-01"
    assert result.start_date.isoformat() == "2026-04-01"
    assert result.end_date.isoformat() == "2031-03-31"
    assert result.term_months == 60
    assert result.field_confidence["term_months"] == 1.0
