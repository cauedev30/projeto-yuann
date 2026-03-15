import React from "react";

import type { DashboardSummary } from "@/lib/api/dashboard";

type ContractsSummaryProps = {
  summary: DashboardSummary;
};

export function ContractsSummary({ summary }: ContractsSummaryProps) {
  return (
    <section>
      <article>
        <p>Contratos ativos</p>
        <strong>{summary.activeContracts}</strong>
      </article>
      <article>
        <p>Findings criticos</p>
        <strong>{summary.criticalFindings}</strong>
      </article>
      <article>
        <p>Vencendo em 12 meses</p>
        <strong>{summary.expiringSoon}</strong>
      </article>
    </section>
  );
}
