import Link from "next/link";
import React from "react";

import type { ContractListItemSummary } from "@/entities/contracts/model";

import { EmptyState } from "../../../components/ui/empty-state";
import { LoadingSkeleton } from "../../../components/ui/loading-skeleton";
import { StatusBadge } from "../../../components/ui/status-badge";
import styles from "../screens/contracts-screen.module.css";

const SOURCE_LABELS: Record<string, string> = {
  third_party_draft: "Contrato padrão",
  signed_contract: "Contrato assinado",
};

type ContractsListPanelProps = {
  items: ContractListItemSummary[];
  isLoading: boolean;
  isRefreshing: boolean;
  error: string | null;
  onRefresh: () => Promise<void> | void;
  navigateToContract?: (contractId: string) => void;
  eyebrow?: string;
  title?: string;
  emptyTitle?: string;
  emptyBody?: string;
  renderRowActions?: (item: ContractListItemSummary) => React.ReactNode;
  renderExtraMeta?: (item: ContractListItemSummary) => React.ReactNode;
};

function getStatusVariant(status: string | null | undefined): "critical" | "attention" | "conforme" | "neutral" {
  switch (status) {
    case "failed":
      return "critical";
    case "pending":
      return "attention";
    case "completed":
      return "conforme";
    default:
      return "neutral";
  }
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

  return statusStr;
}

export function ContractsListPanel({
  items,
  isLoading,
  error,
  navigateToContract,
  eyebrow = "Lista",
  title = "Contratos monitorados",
  emptyTitle = "Nenhum contrato persistido",
  emptyBody = "Envie um PDF na area de upload para iniciar a lista de contratos monitorados.",
  renderRowActions,
  renderExtraMeta,
}: ContractsListPanelProps) {
  return (
    <section className={`${styles.panel} ${styles.listPanel}`}>
      <div className={styles.sectionHeader}>
        <div>
          <p className={styles.panelEyebrow}>{eyebrow}</p>
          <h2 className={styles.sectionTitle}>{title}</h2>
        </div>
      </div>

      {isLoading ? (
        <div className={styles.listStateBlock}>
          <LoadingSkeleton heading={false} lines={3} variant="list" />
          <p className="sr-only">Carregando contratos...</p>
        </div>
      ) : error ? (
        <div className={styles.listStateBlock}>
          <p className={styles.listState}>Não foi possível atualizar a lista.</p>
          <p className={styles.listAlert} role="alert">
            {error}
          </p>
        </div>
      ) : items.length === 0 ? (
        <EmptyState
          title={emptyTitle}
          body={emptyBody}
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
                  <StatusBadge variant={getStatusVariant(item.latestAnalysisStatus)}>
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
                  {renderExtraMeta && renderExtraMeta(item)}
                </div>
              </Link>
              {renderRowActions && renderRowActions(item)}
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
