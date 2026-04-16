"use client";

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
  return `${days} dias`;
}

function urgencyLabel(level: string): string {
  if (level === "red") return "Urgente";
  if (level === "yellow") return "Atenção";
  return "Normal";
}

export function ExpiringContractsTable({ contracts }: Props) {
  if (!contracts.length) {
    return <p className={styles.empty}>Nenhum contrato próximo do vencimento.</p>;
  }

  return (
    <table className={styles.table}>
      <thead>
        <tr>
          <th>Contrato</th>
          <th>Unidade</th>
          <th>Tipo</th>
          <th>Vencimento</th>
          <th>Prazo</th>
          <th>Urgência</th>
        </tr>
      </thead>
      <tbody>
        {contracts.map((c) => (
          <tr key={c.id} className={styles[`urgency-${c.urgency_level}`]}>
            <td className={styles.contractTitle}>{c.title}</td>
            <td>{c.unit || "—"}</td>
            <td>{c.source_label}</td>
            <td>{c.end_date || "—"}</td>
            <td className={styles.daysRemaining}>{formatDaysRemaining(c.days_remaining)}</td>
            <td>
              <span className={`${styles.badge} ${styles[`badge-${c.urgency_level}`]}`}>
                {urgencyLabel(c.urgency_level)}
              </span>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}