import React from "react";

import type { DashboardNotification } from "@/lib/api/dashboard";

type NotificationHistoryProps = {
  items: DashboardNotification[];
};

export function NotificationHistory({ items }: NotificationHistoryProps) {
  return (
    <section>
      <h2>Historico de notificacoes</h2>
      <ul>
        {items.map((item) => (
          <li key={item.id}>
            <span>{item.recipient}</span> <strong>{item.status}</strong> <span>{item.channel}</span>
          </li>
        ))}
      </ul>
    </section>
  );
}
