import React from "react";

import type { DashboardSummary } from "@/entities/dashboard/model";
import uiStyles from "../../../components/ui/ui-primitives.module.css";
import styles from "../screens/dashboard-screen.module.css";

type ContractsSummaryProps = {
  summary: DashboardSummary;
};

export function ContractsSummary({ summary }: ContractsSummaryProps) {
  return (
    <div className={styles.summaryGrid}>
      <article
        className={`${uiStyles.statCard} ${summary.activeContracts > 0 ? styles.accentStatCard : ""}`}
      >
        <p className={uiStyles.statLabel}>Contratos ativos</p>
        <strong className={uiStyles.statValue}>{summary.activeContracts}</strong>
        <p className={uiStyles.statHint}>Base monitorada pelo workspace</p>
      </article>
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
      <article
        className={`${uiStyles.statCard} ${summary.expiringSoon > 0 ? styles.warningStatCard : ""}`}
      >
        <p className={uiStyles.statLabel}>Vencendo em 12 meses</p>
        <strong className={uiStyles.statValue}>{summary.expiringSoon}</strong>
        <p className={uiStyles.statHint}>Eventos dentro da janela anual</p>
      </article>
    </div>
  );
}
