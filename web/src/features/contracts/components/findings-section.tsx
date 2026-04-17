import React from "react";

import type { ContractFinding } from "@/entities/contracts/model";

import styles from "../screens/contracts-screen.module.css";

type FindingsSectionProps = {
  items: ContractFinding[];
};

const classificationLabel: Record<string, string> = {
  adequada: "Presente",
  risco_medio: "Parcial",
  ausente: "Ausente",
  conflitante: "Conflitante",
};

function getClassification(item: ContractFinding): string {
  if (item.metadata?.classification) return String(item.metadata.classification);
  if (item.status === "conforme") return "adequada";
  if (item.status === "critical") return "ausente";
  return "risco_medio";
}

function classificationIcon(cls: string): string {
  if (cls === "adequada") return "\u2713";
  if (cls === "ausente") return "\u2717";
  if (cls === "conflitante") return "\u26A0";
  return "~";
}

export function FindingsSection({ items }: FindingsSectionProps) {
  const present = items.filter((i) => getClassification(i) === "adequada").length;
  const missing = items.filter((i) => getClassification(i) === "ausente").length;
  const partial = items.length - present - missing;

  return (
    <section className={`${styles.panel} ${styles.findingsSection}`}>
      <div className={styles.sectionHeader}>
        <div>
          <p className={styles.panelEyebrow}>Verificacao de clausulas</p>
          <h2 className={styles.sectionTitle}>Principais Pontos</h2>
        </div>
        <span className={styles.sectionMeta}>
          {present} presentes &middot; {partial} parciais &middot; {missing} ausentes
        </span>
      </div>

      <ul className={styles.findingsList}>
        {items.map((item) => {
          const cls = getClassification(item);
          return (
            <li
              className={`${styles.findingItem} ${
                cls === "ausente" || cls === "conflitante"
                  ? styles.findingCritical
                  : cls === "risco_medio"
                    ? styles.findingAttention
                    : styles.findingConforme
              }`}
              key={`${item.clauseName}-${item.status}`}
            >
              <div className={styles.findingHeader}>
                <strong className={styles.findingTitle}>{item.clauseName}</strong>
                <span className={`${styles.classificationBadge} ${styles[`cls-${cls}`] || ""}`}>
                  <span aria-hidden="true">{classificationIcon(cls)}</span>
                  {" "}
                  {classificationLabel[cls] || cls}
                </span>
              </div>
            </li>
          );
        })}
      </ul>
    </section>
  );
}
