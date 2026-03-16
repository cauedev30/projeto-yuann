export type DashboardSummary = {
  activeContracts: number;
  criticalFindings: number;
  expiringSoon: number;
};

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

export type DashboardSnapshot = {
  summary: DashboardSummary;
  events: DashboardEvent[];
  notifications: DashboardNotification[];
};

export type DashboardSummaryPayload = {
  active_contracts: number;
  critical_findings: number;
  expiring_soon: number;
};

export type DashboardEventPayload = {
  id: string;
  event_type: string;
  event_date: string;
};

export type DashboardNotificationPayload = {
  id: string;
  channel: string;
  recipient: string;
  status: string;
  sent_at: string | null;
};

export type DashboardSnapshotPayload = {
  summary: DashboardSummaryPayload;
  events: DashboardEventPayload[];
  notifications: DashboardNotificationPayload[];
};

export function mapDashboardSnapshotPayload(payload: DashboardSnapshotPayload): DashboardSnapshot {
  return {
    summary: {
      activeContracts: payload.summary.active_contracts,
      criticalFindings: payload.summary.critical_findings,
      expiringSoon: payload.summary.expiring_soon,
    },
    events: payload.events.map((event) => ({
      id: event.id,
      eventType: event.event_type,
      eventDate: event.event_date,
    })),
    notifications: payload.notifications.map((notification) => ({
      id: notification.id,
      channel: notification.channel,
      recipient: notification.recipient,
      status: notification.status,
      sentAt: notification.sent_at,
    })),
  };
}
