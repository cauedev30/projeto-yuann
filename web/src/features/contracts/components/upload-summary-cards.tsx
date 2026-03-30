import React from "react";

import type { ContractSource } from "@/entities/contracts/model";

import styles from "../screens/contracts-screen.module.css";

type UploadSummaryCardsProps = {
  source: ContractSource;
  usedOcr: boolean;
  hasCriticalFinding: boolean;
};

const sourceLabelMap: Record<ContractSource, string> = {
  third_party_draft: "Contrato padrão",
  signed_contract: "Contrato assinado",
};

export function UploadSummaryCards({
  source,
  usedOcr,
  hasCriticalFinding,
}: UploadSummaryCardsProps) {
  return (
    <section className={`${styles.panel} ${styles.summarySection}`}>
      <div className={styles.sectionHeader}>
        <div>
          <p className={styles.panelEyebrow}>Resumo executivo</p>
          <h2 className={styles.sectionTitle}>Resumo da triagem</h2>
        </div>
        <span className={styles.summaryCallout}>
          {hasCriticalFinding ? "Revisao prioritaria" : "Fluxo liberado"}
        </span>
      </div>

      <div className={styles.summaryGrid}>
        <article className={styles.summaryCard}>
          <p className={styles.summaryLabel}>Status geral</p>
          <strong className={styles.summaryValue}>
            {hasCriticalFinding ? "Atencao" : "Conforme"}
          </strong>
          <p className={styles.summaryMeta}>
            {hasCriticalFinding
              ? "Existe ao menos um finding critico na triagem inicial."
              : "Nenhum risco critico foi identificado na primeira leitura."}
          </p>
        </article>

        <article className={styles.summaryCard}>
          <p className={styles.summaryLabel}>Processamento</p>
          <strong className={styles.summaryValue}>{usedOcr ? "OCR" : "Texto direto"}</strong>
          <p className={styles.summaryMeta}>
            {sourceLabelMap[source]} analisado na sessao atual.
          </p>
        </article>
      </div>
    </section>
  );
}
