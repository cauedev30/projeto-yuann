import { mapDashboardSnapshotPayload } from "../../../entities/dashboard/model";

export function buildDashboardSnapshotFixture() {
  return mapDashboardSnapshotPayload({
    summary: {
      active_contracts: 12,
      critical_findings: 3,
      expiring_soon: 2,
    },
    events: [
      { id: "evt-1", event_type: "renewal", event_date: "2030-09-30" },
      { id: "evt-2", event_type: "expiration", event_date: "2031-03-31" },
    ],
    notifications: [
      {
        id: "ntf-1",
        channel: "email",
        recipient: "alerts@example.com",
        status: "success",
        sent_at: "2026-04-01T10:00:00Z",
      },
    ],
  });
}
