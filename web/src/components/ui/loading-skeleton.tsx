import React from "react";

import styles from "./ui-primitives.module.css";

type LoadingSkeletonProps = {
  lines?: number;
  heading?: boolean;
  variant?: "default" | "stat" | "list" | "table";
};

export function LoadingSkeleton({ lines = 3, heading = true, variant = "default" }: LoadingSkeletonProps) {
  if (variant === "stat") {
    return (
      <div className={styles.skeletonStat} aria-busy="true" aria-label="Carregando estatisticas">
        <div className={styles.skeletonStatCard} />
        <div className={styles.skeletonStatCard} />
        <div className={styles.skeletonStatCard} />
      </div>
    );
  }

  if (variant === "list") {
    return (
      <div className={styles.skeletonList} aria-busy="true" aria-label="Carregando lista">
        {Array.from({ length: lines }, (_, index) => (
          <div key={index} className={styles.skeletonListItem} />
        ))}
      </div>
    );
  }

  if (variant === "table") {
    return (
      <div className={styles.skeletonTable} aria-busy="true" aria-label="Carregando tabela">
        {Array.from({ length: lines + 1 }, (_, index) => (
          <div key={index} className={styles.skeletonTableRow} />
        ))}
      </div>
    );
  }

  return (
    <div className={styles.skeleton} aria-busy="true" aria-label="Carregando conteudo">
      {heading ? <div className={styles.skeletonHeading} /> : null}
      {Array.from({ length: lines }, (_, index) => (
        <div
          key={index}
          className={styles.skeletonLine}
          style={{ width: `${85 - index * 12}%` }}
        />
      ))}
    </div>
  );
}
