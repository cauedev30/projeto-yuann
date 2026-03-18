import React from "react";

import styles from "./ui-primitives.module.css";

type LoadingSkeletonProps = {
  lines?: number;
  heading?: boolean;
};

export function LoadingSkeleton({ lines = 3, heading = true }: LoadingSkeletonProps) {
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
