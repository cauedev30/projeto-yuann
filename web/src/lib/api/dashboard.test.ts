import { afterEach, describe, expect, it, vi } from "vitest";

import { DashboardApiError, getDashboardSnapshot } from "./dashboard";

describe("getDashboardSnapshot", () => {
  afterEach(() => {
    vi.unstubAllEnvs();
  });

  it("maps the dashboard payload returned by the backend", async () => {
    vi.stubEnv("NEXT_PUBLIC_API_URL", "http://127.0.0.1:8000");
    const fetchImpl: typeof fetch = async () =>
      new Response(
        JSON.stringify({
          summary: {
            active_contracts: 2,
            critical_findings: 1,
            expiring_soon: 2,
          },
          events: [
            {
              id: "evt-1",
              event_type: "renewal",
              event_date: "2026-03-27",
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
              recipient: "ops@example.com",
              status: "success",
              sent_at: "2026-03-27T14:00:00Z",
              event_type: "renewal",
              contract_title: "Loja Centro",
              external_reference: "LOC-001",
            },
          ],
        }),
        {
          status: 200,
          headers: { "Content-Type": "application/json" },
        },
      );

    const snapshot = await getDashboardSnapshot(fetchImpl);

    expect(snapshot?.summary.activeContracts).toBe(2);
    expect(snapshot?.events[0].daysUntilDue).toBe(-5);
    expect(snapshot?.notifications[0].contractTitle).toBe("Loja Centro");
  });

  it("returns null when the backend snapshot is operationally empty", async () => {
    vi.stubEnv("NEXT_PUBLIC_API_URL", "http://127.0.0.1:8000");
    const fetchImpl: typeof fetch = async () =>
      new Response(
        JSON.stringify({
          summary: {
            active_contracts: 0,
            critical_findings: 0,
            expiring_soon: 0,
          },
          events: [],
          notifications: [],
        }),
        {
          status: 200,
          headers: { "Content-Type": "application/json" },
        },
      );

    await expect(getDashboardSnapshot(fetchImpl)).resolves.toBeNull();
  });

  it("throws a generic dashboard error when the backend response is unusable", async () => {
    vi.stubEnv("NEXT_PUBLIC_API_URL", "http://127.0.0.1:8000");
    const fetchImpl: typeof fetch = async () =>
      new Response("internal-error", {
        status: 500,
      });

    await expect(getDashboardSnapshot(fetchImpl)).rejects.toEqual(
      new DashboardApiError("Nao foi possivel carregar o dashboard.", 500),
    );
  });
});
