import Link from "next/link";
import React from "react";

import type { ContractListItemSummary } from "@/entities/contracts/model";

import { EmptyState } from "../../../components/ui/empty-state";
import { LoadingSkeleton } from "../../../components/ui/loading-skeleton";
import { StatusBadge } from "../../../components/ui/status-badge";
import styles from "../screens/contracts-screen.module.css";

const SOURCE_LABELS: Record<string, string> = {
  third_party_draft: "Minuta de terceiro",
  signed_contract: "Contrato assinado",
};

type ContractsListPanelProps = {
  items: ContractListItemSummary[];
  isLoading: boolean;
  isRefreshing: boolean;
  error: string | null;
  onRefresh: () => Promise<void> | void;
  navigateToContract?: (contractId: string) => void;
};

function getRiskVariant(score: number | null): "critical" | "attention" | "conforme" | "neutral" {
  if (score === null) return "neutral";
  if (score >= 60) return "critical";
  if (score >= 30) return "attention";
  return "conforme";
}

function buildStatusLabel(
  item: ContractListItemSummary,
): string {
  const statusLabels: Record<string, string> = {
    completed: "concluído",
    pending: "pendente",
    failed: "falha",
  };

  const statusStr = statusLabels[item.latestAnalysisStatus ?? ""] ?? item.latestAnalysisStatus ?? item.status;

  if (item.latestAnalysisStatus && item.latestRiskScore !== null) {
    return `${statusStr} · pontuação ${item.latestRiskScore}`;
  }

  return statusStr;
}

export function ContractsListPanel({
  items,
  isLoading,
  isRefreshing,
  error,
  onRefresh,
  navigateToContract,
}: ContractsListPanelProps) {
  return (
    <section className={`${styles.panel} ${styles.listPanel}`}>
      <div className={styles.sectionHeader}>
        <div>
          <p className={styles.panelEyebrow}>Portfólio</p>
          <h2 className={styles.sectionTitle}>Contratos monitorados</h2>
        </div>
      </div>

      {isLoading ? (
        <div className={styles.listStateBlock}>
          <LoadingSkeleton heading={false} lines={3} variant="list" />
          <p className="sr-only">Carregando contratos...</p>
        </div>
      ) : error ? (
        <div className={styles.listStateBlock}>
          <p className={styles.listState}>Nao foi possivel atualizar o portfolio.</p>
          <p className={styles.listAlert} role="alert">
            {error}
          </p>
        </div>
      ) : items.length === 0 ? (
        <EmptyState
          title="Nenhum contrato persistido"
          body="Envie um PDF na area de upload para iniciar o portfólio de contratos monitorados."
        />
      ) : (
        <ul className={styles.contractsList}>
          {items.map((item) => (
            <li className={styles.contractRow} key={item.id}>
              <Link
                className={styles.contractLink}
                href={`/contracts/${item.id}`}
                onClick={(event) => {
                  if (!navigateToContract) {
                    return;
                  }

                  event.preventDefault();
                  navigateToContract(item.id);
                }}
              >
                <div className={styles.contractRowHeader}>
                  <strong className={styles.contractTitle}>{item.title}</strong>
                  <StatusBadge variant={getRiskVariant(item.latestRiskScore)}>
                    {buildStatusLabel(item)}
                  </StatusBadge>
                </div>

                <div className={styles.contractMetaGrid}>
                  <span>Ref: {item.externalReference}</span>
                  <span>
                    Prazo: {item.termMonths !== null ? `${item.termMonths} meses` : "a confirmar"}
                  </span>
                  <span>
                    Origem: {item.latestVersionSource ? (SOURCE_LABELS[item.latestVersionSource] ?? item.latestVersionSource) : "a confirmar"}
                  </span>
                </div>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
