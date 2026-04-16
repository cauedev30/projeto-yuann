import { describe, expect, it } from "vitest";

import { mapDashboardSnapshotPayload } from "./model";

describe("dashboard entity mapping", () => {
  it("maps transport payloads into UI-facing dashboard entities", () => {
    const snapshot = mapDashboardSnapshotPayload({
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
      ],
      events: [
        {
          id: "evt-1",
          event_type: "renewal",
          event_date: "2030-09-30",
          lead_time_days: 30,
          contract_id: "ctr-1",
          contract_title: "Loja Centro",
          external_reference: "LOC-001",
          days_until_due: -5,
          is_overdue: true,
        },
      ],
      notifications: [
        {
          id: "ntf-1",
          contract_event_id: "evt-1",
          channel: "email",
          recipient: "alerts@example.com",
          status: "success",
          sent_at: null,
          event_type: "renewal",
          contract_title: "Loja Centro",
          external_reference: "LOC-001",
        },
      ],
    });

    expect(snapshot.summary.activeContracts).toBe(12);
    expect(snapshot.expiring_contracts[0].urgency_level).toBe("red");
    expect(snapshot.events[0].eventType).toBe("renewal");
    expect(snapshot.events[0].contractTitle).toBe("Loja Centro");
    expect(snapshot.events[0].leadTimeDays).toBe(30);
    expect(snapshot.notifications[0].sentAt).toBeNull();
    expect(snapshot.notifications[0].eventType).toBe("renewal");
  });
});
