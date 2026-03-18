import React, { type ReactNode } from "react";

import styles from "./ui-primitives.module.css";

type StatusBadgeProps = {
  variant: "critical" | "attention" | "conforme" | "neutral";
  size?: "sm" | "md";
  children: ReactNode;
};

const variantClassMap: Record<StatusBadgeProps["variant"], string> = {
  critical: styles.statusBadgeCritical,
  attention: styles.statusBadgeAttention,
  conforme: styles.statusBadgeConforme,
  neutral: styles.statusBadgeNeutral,
};

export function StatusBadge({ variant, size = "sm", children }: StatusBadgeProps) {
  const sizeClass = size === "md" ? styles.statusBadgeMd : "";
  const variantClass = variantClassMap[variant];

  return (
    <span className={`${styles.statusBadge} ${variantClass} ${sizeClass}`}>
      {children}
    </span>
  );
}
