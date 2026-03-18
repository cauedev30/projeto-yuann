import React from "react";

import type { DashboardSummary } from "@/entities/dashboard/model";
import { StatCard } from "../../../components/ui/stat-card";
import uiStyles from "../../../components/ui/ui-primitives.module.css";
import styles from "../screens/dashboard-screen.module.css";

type ContractsSummaryProps = {
  summary: DashboardSummary;
};

export function ContractsSummary({ summary }: ContractsSummaryProps) {
  return (
    <div className={styles.summaryGrid}>
      <StatCard
        label="Contratos ativos"
        value={summary.activeContracts}
        hint="Base monitorada pelo workspace"
      />
      <article
        className={`${uiStyles.statCard} ${summary.criticalFindings > 0 ? styles.criticalStatCard : ""}`}
      >
        <p className={uiStyles.statLabel}>Findings criticos</p>
        <strong
          className={`${uiStyles.statValue} ${summary.criticalFindings > 0 ? styles.criticalStatValue : ""}`}
        >
          {summary.criticalFindings}
        </strong>
        <p className={uiStyles.statHint}>
          {summary.criticalFindings > 0 ? "Atencao imediata no portifolio" : "Sem alerta critico no snapshot"}
        </p>
      </article>
      <StatCard
        label="Vencendo em 12 meses"
        value={summary.expiringSoon}
        hint="Eventos dentro da janela anual"
      />
    </div>
  );
}
