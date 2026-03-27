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


def test_extract_contract_metadata_accepts_label_variants_and_tracks_snapshot_context() -> None:
    contract_text = (
        "Data de assinatura: 01/03/2026. "
        "Inicio da vigencia: 01/04/2026. "
        "Prazo contratual: 60 meses. "
        "Locataria / Franqueada: Franquia XPTO LTDA. "
        "Carencia: 3 meses. "
        "Reajuste anual pelo IGP-M."
    )

    result = extract_contract_metadata(contract_text)

    assert result.signature_date.isoformat() == "2026-03-01"
    assert result.start_date.isoformat() == "2026-04-01"
    assert result.end_date.isoformat() == "2031-03-31"
    assert result.term_months == 60
    assert result.parties == {
        "entities": ["Franquia XPTO LTDA"],
        "locatario": "Franquia XPTO LTDA",
    }
    assert result.financial_terms == {
        "grace_period_months": 3,
        "readjustment_type": "annual",
    }
    assert result.field_confidence == {
        "signature_date": 1.0,
        "start_date": 1.0,
        "term_months": 1.0,
        "end_date": 1.0,
        "parties": 1.0,
        "grace_period_months": 1.0,
        "readjustment_type": 1.0,
        "monthly_rent": 0.0,
        "penalty_months": 0.0,
    }
    assert result.match_labels == {
        "signature_date": "data de assinatura",
        "start_date": "inicio da vigencia",
        "end_date": "prazo contratual",
        "term_months": "prazo contratual",
        "parties": "locataria / franqueada",
        "grace_period_months": "carencia",
        "readjustment_type": "reajuste anual",
    }
    assert result.ready_for_event_generation is True


def test_extract_contract_metadata_separates_contract_roles_when_text_is_explicit() -> None:
    contract_text = (
        "LOCADOR: Imobiliaria Centro SPE LTDA, inscrita no CNPJ 00.000.000/0001-00. "
        "LOCATARIO: Franquia XPTO LTDA, inscrita no CNPJ 11.111.111/0001-11. "
        "FIADOR: Joao da Silva, portador do CPF 222.222.222-22."
    )

    result = extract_contract_metadata(contract_text)

    assert result.parties == {
        "entities": [
            "Imobiliaria Centro SPE LTDA",
            "Franquia XPTO LTDA",
            "Joao da Silva",
        ],
        "locador": "Imobiliaria Centro SPE LTDA",
        "locatario": "Franquia XPTO LTDA",
        "fiador": "Joao da Silva",
    }
    assert result.field_confidence["parties"] == 1.0
