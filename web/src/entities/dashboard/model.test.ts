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
      events: [
        {
          id: "evt-1",
          event_type: "renewal",
          event_date: "2030-09-30",
        },
      ],
      notifications: [
        {
          id: "ntf-1",
          channel: "email",
          recipient: "alerts@example.com",
          status: "success",
          sent_at: null,
        },
      ],
    });

    expect(snapshot.summary.activeContracts).toBe(12);
    expect(snapshot.events[0].eventType).toBe("renewal");
    expect(snapshot.notifications[0].sentAt).toBeNull();
  });
});
