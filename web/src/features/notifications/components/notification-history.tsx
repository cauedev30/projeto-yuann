import React from "react";

import type { DashboardNotification } from "@/entities/dashboard/model";

type NotificationHistoryProps = {
  items: DashboardNotification[];
  showTitle?: boolean;
};

export function NotificationHistory({ items, showTitle = true }: NotificationHistoryProps) {
  if (items.length === 0) {
    return (
      <section>
        {showTitle ? <h2>Historico de notificacoes</h2> : null}
        <p>Nenhuma notificacao registrada.</p>
      </section>
    );
  }

  return (
    <section>
      {showTitle ? <h2>Historico de notificacoes</h2> : null}
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
