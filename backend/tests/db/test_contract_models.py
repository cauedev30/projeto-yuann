from app.db.models.analysis import ContractAnalysis
from app.db.models.contract import Contract
from app.db.models.event import ContractEvent


def test_contract_relations_expose_analysis_and_events() -> None:
    contract = Contract(title="Loja Centro", external_reference="LOC-001")

    contract.analyses.append(ContractAnalysis(policy_version="v1"))
    contract.events.append(ContractEvent(event_type="renewal", lead_time_days=180))

    assert contract.analyses[0].policy_version == "v1"
    assert contract.events[0].event_type == "renewal"
