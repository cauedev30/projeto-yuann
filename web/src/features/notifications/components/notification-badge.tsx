"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";

import { getUnreadCount } from "../../../lib/api/notifications";
import styles from "./notification-badge.module.css";

type NotificationBadgeProps = {
  pollIntervalMs?: number;
  loadUnreadCount?: typeof getUnreadCount;
};

export function NotificationBadge({
  pollIntervalMs = 60000,
  loadUnreadCount = getUnreadCount,
}: NotificationBadgeProps) {
  const [count, setCount] = useState(0);

  useEffect(() => {
    let cancelled = false;
    const load = async () => {
      try {
        const unreadCount = await loadUnreadCount();
        if (!cancelled) setCount(unreadCount);
      } catch {
        // silently ignore — badge is non-critical
      }
    };
    void load();
    const interval = setInterval(() => void load(), pollIntervalMs);
    return () => {
      cancelled = true;
      clearInterval(interval);
    };
  }, [loadUnreadCount, pollIntervalMs]);

  return (
    <Link
      aria-label={`Notificações: ${count} não lidas`}
      className={styles.badgeLink}
      href="/notifications"
    >
      <span className={styles.bellIcon} aria-hidden="true">
        🔔
      </span>
      {count > 0 && (
        <span className={styles.countBadge}>{count > 99 ? "99+" : count}</span>
      )}
    </Link>
  );
}