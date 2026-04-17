import { getAuthHeaders } from "./auth";
import { getClientEnv } from "../env";

export type NotificationItem = {
  id: string;
  contractEventId: string;
  channel: string;
  recipient: string;
  status: string;
  createdAt: string;
  sentAt: string | null;
  dismissedAt: string | null;
};

export type NotificationListResult = {
  items: NotificationItem[];
  total: number;
};

type NotificationItemPayload = {
  id: string;
  contract_event_id: string;
  channel: string;
  recipient: string;
  status: string;
  created_at: string;
  sent_at: string | null;
  dismissed_at: string | null;
};

type NotificationListPayload = {
  items: NotificationItemPayload[];
  total: number;
};

function mapNotificationItem(payload: NotificationItemPayload): NotificationItem {
  return {
    id: payload.id,
    contractEventId: payload.contract_event_id,
    channel: payload.channel,
    recipient: payload.recipient,
    status: payload.status,
    createdAt: payload.created_at,
    sentAt: payload.sent_at,
    dismissedAt: payload.dismissed_at,
  };
}

export async function listNotifications(
  dismissed: boolean = false,
  fetchImpl: typeof fetch = fetch,
): Promise<NotificationListResult> {
  const { NEXT_PUBLIC_API_URL } = getClientEnv();
  const response = await fetchImpl(
    `${NEXT_PUBLIC_API_URL}/api/notifications?dismissed=${dismissed}`,
    { headers: getAuthHeaders() },
  );

  if (!response.ok) {
    throw new Error("Não foi possível carregar notificações.");
  }

  const payload = (await response.json()) as NotificationListPayload;
  return {
    items: payload.items.map(mapNotificationItem),
    total: payload.total,
  };
}

export async function dismissNotification(
  notificationId: string,
  fetchImpl: typeof fetch = fetch,
): Promise<NotificationItem> {
  const { NEXT_PUBLIC_API_URL } = getClientEnv();
  const response = await fetchImpl(
    `${NEXT_PUBLIC_API_URL}/api/notifications/${notificationId}/dismiss`,
    {
      method: "POST",
      headers: { ...getAuthHeaders(), "Content-Type": "application/json" },
    },
  );

  if (!response.ok) {
    throw new Error("Não foi possível dispensar a notificação.");
  }

  const payload = (await response.json()) as NotificationItemPayload;
  return mapNotificationItem(payload);
}

export async function getUnreadCount(
  fetchImpl: typeof fetch = fetch,
): Promise<number> {
  const result = await listNotifications(false, fetchImpl);
  return result.total;
}