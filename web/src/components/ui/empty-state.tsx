import React from "react";

import styles from "./ui-primitives.module.css";

type EmptyStateProps = {
  eyebrow?: string;
  title: string;
  body: string;
};

export function EmptyState({ eyebrow, title, body }: EmptyStateProps) {
  return (
    <section className={styles.emptyState}>
      {eyebrow ? <p className={styles.eyebrow}>{eyebrow}</p> : null}
      <h2 className={styles.emptyTitle}>{title}</h2>
      <p className={styles.emptyBody}>{body}</p>
    </section>
  );
}
