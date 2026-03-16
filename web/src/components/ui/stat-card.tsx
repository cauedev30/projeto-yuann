import React from "react";

import styles from "./ui-primitives.module.css";

type StatCardProps = {
  label: string;
  value: string | number;
  hint?: string;
};

export function StatCard({ label, value, hint }: StatCardProps) {
  return (
    <article className={styles.statCard}>
      <p className={styles.statLabel}>{label}</p>
      <strong className={styles.statValue}>{value}</strong>
      {hint ? <p className={styles.statHint}>{hint}</p> : null}
    </article>
  );
}
