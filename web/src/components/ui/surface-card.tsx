import React, { type ReactNode } from "react";

import styles from "./ui-primitives.module.css";

type SurfaceCardProps = {
  children: ReactNode;
  title?: string;
};

export function SurfaceCard({ children, title }: SurfaceCardProps) {
  return (
    <section className={styles.surfaceCard}>
      {title ? <h2 className={styles.surfaceTitle}>{title}</h2> : null}
      {children}
    </section>
  );
}
