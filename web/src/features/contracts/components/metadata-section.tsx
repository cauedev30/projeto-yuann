import React from "react";

import { SurfaceCard } from "../../../components/ui/surface-card";
import styles from "./metadata-section.module.css";

type MetadataSectionProps = {
  parties: Record<string, unknown> | null;
  financialTerms: Record<string, unknown> | null;
  fieldConfidence?: Record<string, number> | null;
  signatureDate: string | null;
  startDate: string | null;
  endDate: string | null;
};

const FINANCIAL_TERM_LABELS: Record<string, string> = {
  grace_period_months: "Carência",
  readjustment_type: "Tipo de reajuste",
};

function formatDate(iso: string | null): string {
  if (!iso) return "Não identificado";
  const [year, month, day] = iso.split("-");
  if (!year || !month || !day) return iso;
  return `${day}/${month}/${year}`;
}

function confidencePill(
  key: string,
  fieldConfidence: Record<string, number> | null | undefined,
): React.ReactElement | null {
  if (!fieldConfidence || !(key in fieldConfidence)) return null;
  const value = fieldConfidence[key];
  if (value >= 0.8) {
    return (
      <span className={`${styles.pill} ${styles.pillHigh}`} data-testid={`pill-${key}`}>
        Alta
      </span>
    );
  }
  if (value >= 0.5) {
    return (
      <span className={`${styles.pill} ${styles.pillMedium}`} data-testid={`pill-${key}`}>
        Média
      </span>
    );
  }
  return (
    <span className={`${styles.pill} ${styles.pillLow}`} data-testid={`pill-${key}`}>
      Baixa
    </span>
  );
}

export function MetadataSection({
  parties,
  financialTerms,
  fieldConfidence,
  signatureDate,
  startDate,
  endDate,
}: MetadataSectionProps) {
  const entities =
    parties && Array.isArray((parties as { entities?: unknown }).entities)
      ? ((parties as { entities: unknown[] }).entities.filter(
          (e): e is string => typeof e === "string",
        ))
      : [];

  const hasParties = entities.length > 0;

  const financialEntries = financialTerms ? Object.entries(financialTerms) : [];
  const hasFinancial = financialEntries.length > 0;

  return (
    <SurfaceCard title="Metadados do contrato">
      <dl className={styles.list}>
        {/* Parties */}
        <div className={styles.row}>
          <div className={styles.rowHeader}>
            <dt className={styles.label}>Partes</dt>
            {confidencePill("parties", fieldConfidence)}
          </div>
          <dd className={styles.value}>
            {hasParties ? (
              <ul className={styles.partiesList}>
                {entities.map((party, idx) => (
                  <li key={idx} className={styles.partiesItem}>
                    {party}
                  </li>
                ))}
              </ul>
            ) : (
              <span className={styles.emptyText}>Não identificado</span>
            )}
          </dd>
        </div>

        {/* Signature Date */}
        <div className={styles.row}>
          <div className={styles.rowHeader}>
            <dt className={styles.label}>Data de assinatura</dt>
            {confidencePill("signatureDate", fieldConfidence)}
          </div>
          <dd className={styles.value}>
            {signatureDate ? (
              formatDate(signatureDate)
            ) : (
              <span className={styles.emptyText}>Não identificado</span>
            )}
          </dd>
        </div>

        {/* Start Date */}
        <div className={styles.row}>
          <div className={styles.rowHeader}>
            <dt className={styles.label}>Data de início</dt>
            {confidencePill("startDate", fieldConfidence)}
          </div>
          <dd className={styles.value}>
            {startDate ? (
              formatDate(startDate)
            ) : (
              <span className={styles.emptyText}>Não identificado</span>
            )}
          </dd>
        </div>

        {/* End Date */}
        <div className={styles.row}>
          <div className={styles.rowHeader}>
            <dt className={styles.label}>Data de término</dt>
            {confidencePill("endDate", fieldConfidence)}
          </div>
          <dd className={styles.value}>
            {endDate ? (
              formatDate(endDate)
            ) : (
              <span className={styles.emptyText}>Não identificado</span>
            )}
          </dd>
        </div>

        {/* Financial Terms */}
        <div className={styles.row}>
          <div className={styles.rowHeader}>
            <dt className={styles.label}>Termos financeiros</dt>
          </div>
          <dd className={styles.value}>
            {hasFinancial ? (
              <dl className={styles.list}>
                {financialEntries.map(([key, val]) => (
                  <div key={key} className={styles.row}>
                    <div className={styles.rowHeader}>
                      <dt className={styles.label}>
                        {FINANCIAL_TERM_LABELS[key] ?? key}
                      </dt>
                      {confidencePill(key, fieldConfidence)}
                    </div>
                    <dd className={styles.value}>
                      {typeof val === "string" || typeof val === "number"
                        ? String(val)
                        : "—"}
                    </dd>
                  </div>
                ))}
              </dl>
            ) : (
              <span className={styles.emptyText}>Sem termos financeiros</span>
            )}
          </dd>
        </div>
      </dl>
    </SurfaceCard>
  );
}
