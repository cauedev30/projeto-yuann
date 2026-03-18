import React from "react";

import styles from "./ui-primitives.module.css";

type StatCardProps = {
  label: string;
  value: string | number;
  hint?: string;
  compact?: boolean;
};

export function StatCard({ label, value, hint, compact }: StatCardProps) {
  const className = compact
    ? `${styles.statCard} ${styles.statCardCompact}`
    : styles.statCard;

  return (
    <article className={className}>
      <p className={styles.statLabel}>{label}</p>
      <strong className={styles.statValue}>{value}</strong>
      {hint ? <p className={styles.statHint}>{hint}</p> : null}
    </article>
  );
}
