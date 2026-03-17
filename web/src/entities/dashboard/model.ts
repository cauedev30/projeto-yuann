export type DashboardSummary = {
  activeContracts: number;
  criticalFindings: number;
  expiringSoon: number;
};

export type DashboardEvent = {
  id: string;
  eventType: string;
  eventDate: string;
  leadTimeDays: number;
  contractId: string;
  contractTitle: string;
  externalReference: string;
  daysUntilDue: number;
  isOverdue: boolean;
};

export type DashboardNotification = {
  id: string;
  contractEventId: string;
  channel: string;
  recipient: string;
  status: string;
  sentAt: string | null;
  eventType: string;
  contractTitle: string;
  externalReference: string;
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
  lead_time_days: number;
  contract_id: string;
  contract_title: string;
  external_reference: string;
  days_until_due: number;
  is_overdue: boolean;
};

export type DashboardNotificationPayload = {
  id: string;
  contract_event_id: string;
  channel: string;
  recipient: string;
  status: string;
  sent_at: string | null;
  event_type: string;
  contract_title: string;
  external_reference: string;
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
      leadTimeDays: event.lead_time_days,
      contractId: event.contract_id,
      contractTitle: event.contract_title,
      externalReference: event.external_reference,
      daysUntilDue: event.days_until_due,
      isOverdue: event.is_overdue,
    })),
    notifications: payload.notifications.map((notification) => ({
      id: notification.id,
      contractEventId: notification.contract_event_id,
      channel: notification.channel,
      recipient: notification.recipient,
      status: notification.status,
      sentAt: notification.sent_at,
      eventType: notification.event_type,
      contractTitle: notification.contract_title,
      externalReference: notification.external_reference,
    })),
  };
}
