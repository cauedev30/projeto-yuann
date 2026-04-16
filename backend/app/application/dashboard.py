from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db.models.analysis import ContractAnalysis
from app.db.models.contract import Contract
from app.db.models.event import ContractEvent, Notification
from app.schemas.dashboard import (
    DashboardEventResponse,
    DashboardNotificationResponse,
    DashboardSnapshotResponse,
    DashboardSummaryResponse,
    ExpiringContractResponse,
)


def _latest_analysis(contract: Contract) -> ContractAnalysis | None:
    if not contract.analyses:
        return None
    return max(
        contract.analyses, key=lambda analysis: (analysis.created_at, analysis.id)
    )


def _is_operational_contract(contract: Contract) -> bool:
    return contract.status != "draft"


def build_dashboard_snapshot(
    *,
    session: Session,
    today: date | str,
) -> DashboardSnapshotResponse:
    reference_date = date.fromisoformat(today) if isinstance(today, str) else today
    horizon_end = reference_date + timedelta(days=365)

    contracts = session.scalars(
        select(Contract).options(
            selectinload(Contract.analyses).selectinload(ContractAnalysis.findings),
            selectinload(Contract.events),
        )
    ).all()

    operational_contracts = [
        contract for contract in contracts if _is_operational_contract(contract)
    ]
    active_contracts = len(operational_contracts)

    from app.api.serializers.contracts import SOURCE_LABELS

    expiring_contracts: list[ExpiringContractResponse] = []
    for contract in operational_contracts:
        if contract.end_date is None or not contract.is_active:
            continue
        days_remaining = (contract.end_date - reference_date).days
        if days_remaining > 365:
            continue
        if days_remaining < 30:
            urgency = "red"
        elif days_remaining < 90:
            urgency = "yellow"
        else:
            urgency = "green"
        unit = None
        if contract.parties and isinstance(contract.parties, dict):
            unit = contract.parties.get("locatario") or contract.parties.get(
                "locatário"
            )
        source_label = (
            SOURCE_LABELS.get(
                contract.versions[0].source.value if contract.versions else "",
                contract.versions[0].source.value if contract.versions else "",
            )
            if contract.versions
            else ""
        )
        expiring_contracts.append(
            ExpiringContractResponse(
                id=contract.id,
                title=contract.title,
                unit=unit,
                source_label=source_label,
                end_date=contract.end_date,
                days_remaining=days_remaining,
                urgency_level=urgency,
            )
        )
    expiring_contracts.sort(key=lambda c: c.days_remaining or 999999)

    critical_findings = 0
    event_items: list[DashboardEventResponse] = []
    for contract in operational_contracts:
        latest_analysis = _latest_analysis(contract)
        if latest_analysis is not None:
            critical_findings += sum(
                1
                for finding in latest_analysis.findings
                if finding.severity == "critical"
            )

        for event in contract.events:
            if event.event_date is None:
                continue
            if event.event_date > horizon_end:
                continue

            days_until_due = (event.event_date - reference_date).days
            event_items.append(
                DashboardEventResponse(
                    id=event.id,
                    event_type=event.event_type.value
                    if hasattr(event.event_type, "value")
                    else str(event.event_type),
                    event_date=event.event_date,
                    lead_time_days=event.lead_time_days,
                    contract_id=contract.id,
                    contract_title=contract.title,
                    external_reference=contract.external_reference,
                    days_until_due=days_until_due,
                    is_overdue=days_until_due < 0,
                )
            )

    event_items.sort(key=lambda event: (event.event_date, event.id))

    notifications = session.scalars(
        select(Notification).options(
            selectinload(Notification.event).selectinload(ContractEvent.contract),
        )
    ).all()

    notification_items: list[DashboardNotificationResponse] = []
    for notification in notifications:
        event = notification.event
        contract = event.contract if event is not None else None
        if event is None or contract is None:
            continue
        if not _is_operational_contract(contract):
            continue

        notification_items.append(
            DashboardNotificationResponse(
                id=notification.id,
                contract_event_id=notification.contract_event_id,
                channel=notification.channel.value,
                recipient=notification.recipient,
                status=notification.status,
                sent_at=notification.sent_at,
                event_type=event.event_type.value
                if hasattr(event.event_type, "value")
                else str(event.event_type),
                contract_title=contract.title,
                external_reference=contract.external_reference,
            )
        )

    notification_items.sort(
        key=lambda notification: (
            notification.sent_at is None,
            notification.sent_at or datetime.min.replace(tzinfo=timezone.utc),
            notification.id,
        ),
        reverse=True,
    )

    return DashboardSnapshotResponse(
        summary=DashboardSummaryResponse(
            active_contracts=active_contracts,
            critical_findings=critical_findings,
            expiring_soon=len(event_items),
        ),
        expiring_contracts=expiring_contracts[:10],
        events=event_items,
        notifications=notification_items,
    )
