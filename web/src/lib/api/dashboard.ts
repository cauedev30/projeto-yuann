export type DashboardEvent = {
  id: string;
  eventType: string;
  eventDate: string;
};

export type DashboardNotification = {
  id: string;
  channel: string;
  recipient: string;
  status: string;
  sentAt: string | null;
};

export type DashboardSummary = {
  activeContracts: number;
  criticalFindings: number;
  expiringSoon: number;
};

export type DashboardSnapshot = {
  summary: DashboardSummary;
  events: DashboardEvent[];
  notifications: DashboardNotification[];
};

export function buildFallbackDashboardSnapshot(): DashboardSnapshot {
  return {
    summary: {
      activeContracts: 12,
      criticalFindings: 3,
      expiringSoon: 2,
    },
    events: [
      { id: "evt-1", eventType: "renewal", eventDate: "2030-09-30" },
      { id: "evt-2", eventType: "expiration", eventDate: "2031-03-31" },
    ],
    notifications: [
      {
        id: "ntf-1",
        channel: "email",
        recipient: "alerts@example.com",
        status: "success",
        sentAt: "2026-04-01T10:00:00Z",
      },
    ],
  };
}
