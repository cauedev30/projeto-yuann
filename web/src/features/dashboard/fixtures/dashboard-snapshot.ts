import { mapDashboardSnapshotPayload } from "../../../entities/dashboard/model";

export function buildDashboardSnapshotFixture() {
  return mapDashboardSnapshotPayload({
    summary: {
      active_contracts: 12,
      critical_findings: 3,
      expiring_soon: 2,
    },
    expiring_contracts: [
      {
        id: "ctr-1",
        title: "Loja Centro",
        unit: "Andar 1",
        source_label: "Contrato assinado",
        end_date: "2026-05-15",
        days_remaining: 29,
        urgency_level: "red",
      },
      {
        id: "ctr-2",
        title: "Loja Norte",
        unit: "Andar 2",
        source_label: "Contrato assinado",
        end_date: "2026-07-20",
        days_remaining: 95,
        urgency_level: "green",
      },
    ],
    events: [
      {
        id: "evt-1",
        event_type: "renewal",
        event_date: "2030-09-30",
        lead_time_days: 45,
        contract_id: "ctr-1",
        contract_title: "Loja Centro",
        external_reference: "LOC-001",
        days_until_due: -5,
        is_overdue: true,
      },
      {
        id: "evt-2",
        event_type: "expiration",
        event_date: "2031-03-31",
        lead_time_days: 30,
        contract_id: "ctr-2",
        contract_title: "Loja Norte",
        external_reference: "LOC-002",
        days_until_due: 30,
        is_overdue: false,
      },
    ],
    notifications: [
      {
        id: "ntf-1",
        contract_event_id: "evt-2",
        channel: "email",
        recipient: "alerts@example.com",
        status: "success",
        sent_at: "2026-04-01T10:00:00Z",
        event_type: "expiration",
        contract_title: "Loja Norte",
        external_reference: "LOC-002",
      },
    ],
  });
}
