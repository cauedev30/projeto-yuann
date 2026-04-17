"use client";

import React, { useCallback, useEffect, useState } from "react";

import { PageHeader } from "../../../components/ui/page-header";
import { SurfaceCard } from "../../../components/ui/surface-card";
import type { NotificationItem } from "../../../lib/api/notifications";
import { dismissNotification, listNotifications } from "../../../lib/api/notifications";
import styles from "./notifications-page.module.css";

export default function NotificationsPage() {
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [filter, setFilter] = useState<"unread" | "all">("unread");

  const fetchNotifications = useCallback(async () => {
    setIsLoading(true);
    try {
      const dismissed = filter === "unread" ? false : undefined;
      const result = await listNotifications(dismissed);
      setNotifications(result.items);
    } catch {
      // show empty on error
    } finally {
      setIsLoading(false);
    }
  }, [filter]);

  useEffect(() => {
    void fetchNotifications();
  }, [fetchNotifications]);

  const handleDismiss = async (id: string) => {
    try {
      await dismissNotification(id);
      setNotifications((prev) => prev.filter((n) => n.id !== id));
    } catch {
      // silently ignore
    }
  };

  return (
    <section className={styles.page}>
      <PageHeader
        eyebrow="Notificações"
        title="Central de notificações"
        description="Gerencie alertas de contratos e prazos."
      />

      <div className={styles.filters}>
        <button
          className={filter === "unread" ? styles.filterActive : styles.filterButton}
          onClick={() => setFilter("unread")}
          type="button"
        >
          Não lidas
        </button>
        <button
          className={filter === "all" ? styles.filterActive : styles.filterButton}
          onClick={() => setFilter("all")}
          type="button"
        >
          Todas
        </button>
      </div>

      <SurfaceCard title="Notificações">
        {isLoading ? (
          <p>Carregando...</p>
        ) : notifications.length === 0 ? (
          <p>Nenhuma notificação.</p>
        ) : (
          <ul className={styles.list}>
            {notifications.map((n) => (
              <li key={n.id} className={styles.item}>
                <div className={styles.itemContent}>
                  <span className={styles.itemStatus}>{n.status}</span>
                  <span className={styles.itemRecipient}>{n.recipient}</span>
                  <span className={styles.itemDate}>
                    {new Date(n.createdAt).toLocaleDateString("pt-BR")}
                  </span>
                </div>
                {!n.dismissedAt && (
                  <button
                    className={styles.dismissButton}
                    onClick={() => void handleDismiss(n.id)}
                    type="button"
                  >
                    Dispensar
                  </button>
                )}
              </li>
            ))}
          </ul>
        )}
      </SurfaceCard>
    </section>
  );
}