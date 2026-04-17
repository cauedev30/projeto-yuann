from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db.base import Base
from app.db.models.analysis import ContractAnalysis, ContractAnalysisFinding
from app.db.models.contract import Contract, ContractSource, ContractVersion
from app.db.models.event import (
    ContractEvent,
    EventType,
    Notification,
    NotificationChannel,
)


def reset_database(database_url: str) -> None:
    engine = create_engine(
        database_url,
        connect_args={"check_same_thread": False}
        if database_url.startswith("sqlite")
        else {},
    )
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def seed_dashboard_data(
    session: Session, *, reference_date: date = date(2026, 4, 1)
) -> None:

    uploaded_contract = Contract(
        title="Loja Centro",
        external_reference="LOC-001",
        status="uploaded",
        is_active=True,
        end_date=date(2026, 5, 15),
        parties={"locador": "Imobiliaria Centro", "locatario": "Rede Comercial X"},
        financial_terms={"valor_mensal": "R$ 12.500,00", "indice_reajuste": "IGPM"},
    )
    active_contract = Contract(
        title="Loja Norte",
        external_reference="LOC-002",
        status="active",
        is_active=True,
        end_date=date(2026, 5, 1),
        parties={
            "locador": "Patrimonio Norte S.A.",
            "locatario": "Operacao Varejo Norte",
        },
        financial_terms={"valor_mensal": "R$ 18.000,00", "indice_reajuste": "IPCA"},
    )
    draft_contract = Contract(
        title="Rascunho Interno",
        external_reference="LOC-003",
        status="draft",
        parties={"locador": "Fundo Urbano Atlas", "locatario": "Marca Piloto"},
        financial_terms={"valor_mensal": "R$ 9.800,00", "indice_reajuste": "IGPM"},
    )

    uploaded_version_v1 = ContractVersion(
        version_number=1,
        source=ContractSource.third_party_draft,
        original_filename="loc-001-v1.pdf",
        storage_key="fixtures/loc-001-v1.pdf",
        text_content="Versao inicial do contrato da Loja Centro.",
    )
    uploaded_version_v2 = ContractVersion(
        version_number=2,
        source=ContractSource.third_party_draft,
        original_filename="loc-001-v2.pdf",
        storage_key="fixtures/loc-001-v2.pdf",
        text_content="Versao atualizada do contrato da Loja Centro.",
    )
    active_version = ContractVersion(
        version_number=1,
        source=ContractSource.signed_contract,
        original_filename="loc-002-v1.pdf",
        storage_key="fixtures/loc-002-v1.pdf",
        text_content="Contrato assinado da Loja Norte.",
    )
    draft_version = ContractVersion(
        version_number=1,
        source=ContractSource.third_party_draft,
        original_filename="loc-003-v1.pdf",
        storage_key="fixtures/loc-003-v1.pdf",
        text_content="Rascunho interno.",
    )

    uploaded_contract.versions.extend([uploaded_version_v1, uploaded_version_v2])
    active_contract.versions.append(active_version)
    draft_contract.versions.append(draft_version)

    uploaded_contract.analyses.extend(
        [
            ContractAnalysis(
                contract_version=uploaded_version_v1,
                policy_version="v1",
                status="completed",
                contract_risk_score=85,
                findings=[
                    ContractAnalysisFinding(
                        clause_name="Prazo",
                        status="critical",
                        severity="critical",
                        current_summary="Prazo antigo abaixo da politica.",
                        policy_rule="Prazo minimo exigido: 60 meses.",
                        risk_explanation="Historico anterior critico.",
                        suggested_adjustment_direction="Atualizar prazo.",
                    )
                ],
            ),
            ContractAnalysis(
                contract_version=uploaded_version_v2,
                policy_version="v2",
                status="completed",
                contract_risk_score=20,
                findings=[
                    ContractAnalysisFinding(
                        clause_name="Prazo",
                        status="compliant",
                        severity="low",
                        current_summary="Prazo atualizado e dentro da politica.",
                        policy_rule="Prazo minimo exigido: 60 meses.",
                        risk_explanation="Sem desvio critico.",
                        suggested_adjustment_direction="Nenhum ajuste necessario.",
                    )
                ],
            ),
        ]
    )
    active_contract.analyses.append(
        ContractAnalysis(
            contract_version=active_version,
            policy_version="v1",
            status="completed",
            contract_risk_score=80,
            findings=[
                ContractAnalysisFinding(
                    clause_name="Multa",
                    status="critical",
                    severity="critical",
                    current_summary="Multa acima do teto aceito.",
                    policy_rule="Multa maxima de 3 meses.",
                    risk_explanation="Risco financeiro elevado.",
                    suggested_adjustment_direction="Reduzir multa contratual.",
                )
            ],
        )
    )

    overdue_event = ContractEvent(
        event_type=EventType.renewal,
        event_date=reference_date - timedelta(days=5),
        lead_time_days=30,
        metadata_json={"notification_recipient": "ops@example.com"},
    )
    upcoming_event = ContractEvent(
        event_type=EventType.expiration,
        event_date=reference_date + timedelta(days=30),
        lead_time_days=45,
        metadata_json={"notification_recipient": "alerts@example.com"},
    )
    far_future_event = ContractEvent(
        event_type=EventType.readjustment,
        event_date=reference_date + timedelta(days=400),
        lead_time_days=15,
        metadata_json={"notification_recipient": "alerts@example.com"},
    )

    uploaded_contract.events.append(overdue_event)
    active_contract.events.extend([upcoming_event, far_future_event])

    session.add_all([uploaded_contract, active_contract, draft_contract])
    session.commit()

    old_analysis, latest_uploaded_analysis = uploaded_contract.analyses
    old_analysis.created_at = datetime(2026, 3, 1, tzinfo=timezone.utc)
    latest_uploaded_analysis.created_at = datetime(2026, 3, 20, tzinfo=timezone.utc)
    active_contract.analyses[0].created_at = datetime(2026, 3, 22, tzinfo=timezone.utc)

    older_notification = Notification(
        contract_event_id=overdue_event.id,
        channel=NotificationChannel.email,
        recipient="ops@example.com",
        status="success",
        idempotency_key="renewal:email:older",
        sent_at=datetime(2026, 3, 27, 14, 0, tzinfo=timezone.utc),
    )
    newer_notification = Notification(
        contract_event_id=upcoming_event.id,
        channel=NotificationChannel.email,
        recipient="alerts@example.com",
        status="failed",
        idempotency_key="expiration:email:newer",
        sent_at=datetime(2026, 4, 1, 9, 0, tzinfo=timezone.utc),
    )
    future_notification = Notification(
        contract_event_id=far_future_event.id,
        channel=NotificationChannel.email,
        recipient="finance@example.com",
        status="pending",
        idempotency_key="readjustment:email:future",
        sent_at=None,
    )
    older_notification.created_at = datetime(2026, 3, 27, 14, 0, tzinfo=timezone.utc)
    newer_notification.created_at = datetime(2026, 4, 1, 9, 0, tzinfo=timezone.utc)
    future_notification.created_at = datetime(2026, 4, 2, 8, 0, tzinfo=timezone.utc)

    session.add_all([older_notification, newer_notification, future_notification])
    session.commit()
