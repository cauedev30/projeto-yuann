import React from "react";

import type { DashboardSummary } from "@/entities/dashboard/model";
import { StatCard } from "../../../components/ui/stat-card";
import styles from "../screens/dashboard-screen.module.css";

type ContractsSummaryProps = {
  summary: DashboardSummary;
};

export function ContractsSummary({ summary }: ContractsSummaryProps) {
  return (
    <div className={styles.summaryGrid}>
      <StatCard label="Contratos ativos" value={summary.activeContracts} />
      <StatCard label="Findings criticos" value={summary.criticalFindings} />
      <StatCard label="Vencendo em 12 meses" value={summary.expiringSoon} />
    </div>
  );
}
