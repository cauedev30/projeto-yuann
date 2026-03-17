import React from "react";

import type { DashboardNotification } from "@/entities/dashboard/model";
import styles from "./notification-history.module.css";

type NotificationHistoryProps = {
  items: DashboardNotification[];
  showTitle?: boolean;
};

export function NotificationHistory({ items, showTitle = true }: NotificationHistoryProps) {
  function formatStatus(status: string): string {
    switch (status) {
      case "success":
        return "Enviado";
      case "failed":
        return "Falhou";
      case "pending":
        return "Pendente";
      default:
        return status;
    }
  }

  function formatEventType(eventType: string): string {
    switch (eventType) {
      case "renewal":
        return "Renovacao";
      case "expiration":
        return "Expiracao";
      case "readjustment":
        return "Reajuste";
      case "grace_period_end":
        return "Fim da carencia";
      default:
        return eventType;
    }
  }

  function formatSentAt(sentAt: string | null): string {
    if (sentAt === null) {
      return "Ainda nao enviado";
    }

    return new Intl.DateTimeFormat("pt-BR", {
      dateStyle: "short",
      timeStyle: "short",
    }).format(new Date(sentAt));
  }

  if (items.length === 0) {
    return (
      <section className={styles.section}>
        {showTitle ? <h2>Historico de notificacoes</h2> : null}
        <p className={styles.emptyState}>Nenhuma notificacao registrada.</p>
      </section>
    );
  }

  return (
    <section className={styles.section}>
      {showTitle ? <h2>Historico de notificacoes</h2> : null}
      <ul className={styles.list}>
        {items.map((item) => (
          <li key={item.id} className={styles.item}>
            <div className={styles.itemTop}>
              <strong>{item.contractTitle}</strong>
              <span className={styles.status}>{formatStatus(item.status)}</span>
            </div>
            <p className={styles.metaText}>
              {item.externalReference} · {formatEventType(item.eventType)}
            </p>
            <p className={styles.metaText}>
              {item.recipient} · {item.channel} · {formatSentAt(item.sentAt)}
            </p>
          </li>
        ))}
      </ul>
    </section>
  );
}
