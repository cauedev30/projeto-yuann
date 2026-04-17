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
      <svg
        className={styles.bellIcon}
        width="18"
        height="18"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        aria-hidden="true"
      >
        <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" />
        <path d="M13.73 21a2 2 0 0 1-3.46 0" />
      </svg>
      {count > 0 && (
        <span className={styles.countBadge}>{count > 99 ? "99+" : count}</span>
      )}
    </Link>
  );
}