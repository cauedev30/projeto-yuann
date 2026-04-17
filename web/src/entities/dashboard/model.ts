export type DashboardSummary = {
  activeContracts: number;
  criticalFindings: number;
  expiringSoon: number;
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

export type ExpiringContract = {
  id: string;
  title: string;
  unit: string | null;
  source_label: string;
  end_date: string | null;
  days_remaining: number | null;
  urgency_level: "red" | "yellow" | "green" | "blue";
};

export type DashboardSnapshot = {
  summary: DashboardSummary;
  expiring_contracts: ExpiringContract[];
  notifications: DashboardNotification[];
};

export type DashboardSummaryPayload = {
  active_contracts: number;
  critical_findings: number;
  expiring_soon: number;
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

export type ExpiringContractPayload = {
  id: string;
  title: string;
  unit: string | null;
  source_label: string;
  end_date: string | null;
  days_remaining: number | null;
  urgency_level: string;
};

export type DashboardSnapshotPayload = {
  summary: DashboardSummaryPayload;
  expiring_contracts: ExpiringContractPayload[];
  notifications: DashboardNotificationPayload[];
};

export function mapDashboardSnapshotPayload(payload: DashboardSnapshotPayload): DashboardSnapshot {
  return {
    summary: {
      activeContracts: payload.summary.active_contracts,
      criticalFindings: payload.summary.critical_findings,
      expiringSoon: payload.summary.expiring_soon,
    },
    expiring_contracts: payload.expiring_contracts.map((c) => ({
      id: c.id,
      title: c.title,
      unit: c.unit,
      source_label: c.source_label,
      end_date: c.end_date,
      days_remaining: c.days_remaining,
      urgency_level: c.urgency_level as "red" | "yellow" | "green" | "blue",
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
