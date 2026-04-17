"use client";

import Link from "next/link";
import React from "react";
import type { ExpiringContract } from "../../../entities/dashboard/model";
import styles from "./expiring-contracts-table.module.css";

type Props = {
  contracts: ExpiringContract[];
};

function formatDaysRemaining(days: number | null): string {
  if (days === null) return "—";
  if (days < 0) return `Vencido há ${Math.abs(days)} dias`;
  if (days === 0) return "Vence hoje";
  if (days === 1) return "1 dia";
  return `${days} dias`;
}

function formatEndDate(dateStr: string | null): string {
  if (!dateStr) return "—";
  const d = new Date(dateStr + "T00:00:00Z");
  if (Number.isNaN(d.getTime())) return dateStr;
  return new Intl.DateTimeFormat("pt-BR", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    timeZone: "UTC",
  }).format(d);
}

function urgencyConfig(level: string) {
  if (level === "red") return { label: "Urgente", icon: "\u2726" };
  if (level === "yellow") return { label: "Atenção", icon: "\u25B2" };
  if (level === "green") return { label: "Normal", icon: "\u25CF" };
  return { label: "Longo prazo", icon: "\u25CB" };
}

function progressWidth(days: number | null): string {
  if (days === null) return "100%";
  if (days <= 0) return "0%";
  if (days > 365) return "100%";
  return `${Math.min(100, (days / 365) * 100)}%`;
}

export function ExpiringContractsTable({ contracts }: Props) {
  if (!contracts.length) {
    return (
      <div className={styles.emptyState}>
        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" aria-hidden="true">
          <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <p className={styles.emptyText}>Todos os contratos estão dentro do prazo.</p>
      </div>
    );
  }

  return (
    <div className={styles.grid}>
      {contracts.map((c) => {
        const urgency = urgencyConfig(c.urgency_level);
        return (
          <Link
            key={c.id}
            href={`/contracts/${c.id}?context=acervo`}
            className={`${styles.card} ${styles[`urgency-${c.urgency_level}`]}`}
          >
            <div className={styles.cardHeader}>
              <div className={styles.contractInfo}>
                <h3 className={styles.contractTitle}>{c.title}</h3>
                <span className={styles.unitLabel}>{c.unit || "Sem unidade"}</span>
              </div>
              <span className={`${styles.urgencyBadge} ${styles[`badge-${c.urgency_level}`]}`}>
                <span aria-hidden="true">{urgency.icon}</span>
                {urgency.label}
              </span>
            </div>

            <div className={styles.cardBody}>
              <div className={styles.detailRow}>
                <span className={styles.detailLabel}>Tipo</span>
                <span className={styles.detailValue}>{c.source_label}</span>
              </div>
              <div className={styles.detailRow}>
                <span className={styles.detailLabel}>Vencimento</span>
                <span className={styles.detailValue}>{formatEndDate(c.end_date)}</span>
              </div>
              <div className={styles.detailRow}>
                <span className={styles.detailLabel}>Prazo</span>
                <span className={`${styles.detailValue} ${styles.daysValue} ${c.urgency_level === "red" ? styles.daysCritical : ""}`}>
                  {formatDaysRemaining(c.days_remaining)}
                </span>
              </div>
            </div>

            <div className={styles.progressBarTrack}>
              <div
                className={`${styles.progressBarFill} ${styles[`fill-${c.urgency_level}`]}`}
                style={{ width: progressWidth(c.days_remaining) }}
              />
            </div>
          </Link>
        );
      })}
    </div>
  );
}