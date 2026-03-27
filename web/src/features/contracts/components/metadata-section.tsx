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

type PartyRole = {
  key: string;
  label: string;
  value: string;
};

const FINANCIAL_TERM_LABELS: Record<string, string> = {
  grace_period_months: "Carência",
  monthly_rent: "Aluguel",
  readjustment_type: "Tipo de reajuste",
};

const PARTY_ROLE_ALIASES: Array<{ keys: string[]; label: string }> = [
  { keys: ["locatario", "tenant"], label: "Locatário" },
  { keys: ["locador", "landlord"], label: "Locador" },
  { keys: ["fiador", "guarantor"], label: "Fiador" },
];

function formatDate(iso: string | null): string {
  if (!iso) return "Não identificado";
  const [year, month, day] = iso.split("-");
  if (!year || !month || !day) return iso;
  return `${day}/${month}/${year}`;
}

function getConfidenceValue(
  key: string,
  fieldConfidence: Record<string, number> | null | undefined,
): number | null {
  if (!fieldConfidence) {
    return null;
  }

  if (key in fieldConfidence && typeof fieldConfidence[key] === "number") {
    return fieldConfidence[key];
  }

  const snakeCaseKey = key.replace(/[A-Z]/g, (match) => `_${match.toLowerCase()}`);
  if (
    snakeCaseKey in fieldConfidence &&
    typeof fieldConfidence[snakeCaseKey] === "number"
  ) {
    return fieldConfidence[snakeCaseKey];
  }

  return null;
}

function confidencePill(
  key: string,
  fieldConfidence: Record<string, number> | null | undefined,
): React.ReactElement | null {
  const value = getConfidenceValue(key, fieldConfidence);
  if (value === null) return null;

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

function extractStringArray(value: unknown): string[] {
  if (!Array.isArray(value)) {
    return [];
  }

  return value.filter(
    (entry): entry is string => typeof entry === "string" && entry.trim() !== "",
  );
}

function extractPartyRoles(parties: Record<string, unknown> | null): PartyRole[] {
  if (!parties) {
    return [];
  }

  return PARTY_ROLE_ALIASES.flatMap(({ keys, label }) => {
    for (const key of keys) {
      const value = parties[key];
      if (typeof value === "string" && value.trim() !== "") {
        return [{ key, label, value }];
      }
    }

    return [];
  });
}

function formatFinancialValue(key: string, value: unknown): string {
  if (value === null || value === undefined) {
    return "Não identificado";
  }

  if (key === "readjustment_type" && typeof value === "string") {
    const normalized = value.trim().toLowerCase();
    if (normalized === "annual") {
      return "Anual";
    }
    if (normalized === "monthly") {
      return "Mensal";
    }
    return value;
  }

  if (key === "monthly_rent" && typeof value === "number") {
    return new Intl.NumberFormat("pt-BR", {
      style: "currency",
      currency: "BRL",
      minimumFractionDigits: 2,
    }).format(value);
  }

  if (typeof value === "string" || typeof value === "number") {
    return String(value);
  }

  return "Não identificado";
}

export function MetadataSection({
  parties,
  financialTerms,
  fieldConfidence,
  signatureDate,
  startDate,
  endDate,
}: MetadataSectionProps) {
  const entities = extractStringArray(parties?.entities);
  const partyRoles = extractPartyRoles(parties);
  const roleValues = new Set(partyRoles.map((partyRole) => partyRole.value));
  const remainingEntities = entities.filter((entity) => !roleValues.has(entity));
  const hasParties = partyRoles.length > 0 || remainingEntities.length > 0;

  const financialEntries = financialTerms ? Object.entries(financialTerms) : [];
  const hasFinancial = financialEntries.length > 0;

  return (
    <SurfaceCard title="Metadados do contrato">
      <dl className={styles.list}>
        <div className={styles.row}>
          <div className={styles.rowHeader}>
            <dt className={styles.label}>Partes</dt>
            {confidencePill("parties", fieldConfidence)}
          </div>
          <dd className={styles.value}>
            {hasParties ? (
              <div className={styles.section}>
                {partyRoles.length > 0 ? (
                  <dl className={styles.list}>
                    {partyRoles.map((partyRole) => (
                      <div key={partyRole.key} className={styles.row}>
                        <dt className={styles.label}>{partyRole.label}</dt>
                        <dd className={styles.value}>{partyRole.value}</dd>
                      </div>
                    ))}
                  </dl>
                ) : null}

                {remainingEntities.length > 0 ? (
                  <ul className={styles.partiesList}>
                    {remainingEntities.map((party, idx) => (
                      <li key={`${party}-${idx}`} className={styles.partiesItem}>
                        {party}
                      </li>
                    ))}
                  </ul>
                ) : null}
              </div>
            ) : (
              <span className={styles.emptyText}>Não identificado</span>
            )}
          </dd>
        </div>

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

        <div className={styles.row}>
          <div className={styles.rowHeader}>
            <dt className={styles.label}>Termos financeiros</dt>
          </div>
          <dd className={styles.value}>
            {hasFinancial ? (
              <dl className={styles.list}>
                {financialEntries.map(([key, value]) => (
                  <div key={key} className={styles.row}>
                    <div className={styles.rowHeader}>
                      <dt className={styles.label}>
                        {FINANCIAL_TERM_LABELS[key] ?? key}
                      </dt>
                      {confidencePill(key, fieldConfidence)}
                    </div>
                    <dd className={styles.value}>{formatFinancialValue(key, value)}</dd>
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
