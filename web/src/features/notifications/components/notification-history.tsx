import React from "react";

import type { DashboardNotification } from "@/entities/dashboard/model";

type NotificationHistoryProps = {
  items: DashboardNotification[];
};

export function NotificationHistory({ items }: NotificationHistoryProps) {
  if (items.length === 0) {
    return (
      <section>
        <h2>Historico de notificacoes</h2>
        <p>Nenhuma notificacao registrada.</p>
      </section>
    );
  }

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
