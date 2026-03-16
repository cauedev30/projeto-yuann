import React from "react";

import type { ContractFinding } from "@/entities/contracts/model";

import styles from "../screens/contracts-screen.module.css";

type FindingsSectionProps = {
  items: ContractFinding[];
};

const statusLabelMap: Record<ContractFinding["status"], string> = {
  critical: "Critico",
  attention: "Atencao",
  conforme: "Conforme",
};

export function FindingsSection({ items }: FindingsSectionProps) {
  return (
    <section className={`${styles.panel} ${styles.findingsSection}`}>
      <div className={styles.sectionHeader}>
        <div>
          <p className={styles.panelEyebrow}>Leitura orientada</p>
          <h2 className={styles.sectionTitle}>Findings principais</h2>
        </div>
        <span className={styles.sectionMeta}>{items.length} item(ns) destacados</span>
      </div>

      <ul className={styles.findingsList}>
        {items.map((item) => (
          <li className={styles.findingItem} key={`${item.clauseName}-${item.status}`}>
            <div className={styles.findingHeader}>
              <strong className={styles.findingTitle}>{item.clauseName}</strong>
              <span
                className={`${styles.statusPill} ${styles[`status${statusLabelMap[item.status]}`]}`}
              >
                {statusLabelMap[item.status]}
              </span>
            </div>
            <p className={styles.findingDescription}>{item.riskExplanation}</p>
            <p className={styles.findingMeta}>Atual: {item.currentSummary}</p>
            <p className={styles.findingMeta}>Direcao sugerida: {item.suggestedAdjustmentDirection}</p>
          </li>
        ))}
      </ul>
    </section>
  );
}
