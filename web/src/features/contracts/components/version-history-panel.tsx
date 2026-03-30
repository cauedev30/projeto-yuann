import React from "react";

import { SurfaceCard } from "../../../components/ui/surface-card";
import uiStyles from "../../../components/ui/ui-primitives.module.css";
import type { ContractVersionListResponse } from "../../../entities/contracts/model";
import styles from "./version-history-panel.module.css";

type VersionHistoryPanelProps = {
  versions: ContractVersionListResponse["items"];
  isLoading: boolean;
  errorMessage?: string | null;
  selectedVersionId: string | null;
  comparisonBaselineId: string | null;
  onOpenVersion: (contractVersionId: string | null) => void;
  onCompareWith: (contractVersionId: string | null) => void;
};

export function VersionHistoryPanel({
  versions,
  isLoading,
  errorMessage,
  selectedVersionId,
  comparisonBaselineId,
  onOpenVersion,
  onCompareWith,
}: VersionHistoryPanelProps) {
  function formatVersionTimestamp(createdAt: string): string {
    const timestamp = new Date(createdAt);
    if (Number.isNaN(timestamp.getTime())) {
      return createdAt;
    }

    return new Intl.DateTimeFormat("pt-BR", {
      dateStyle: "short",
      timeStyle: "short",
    }).format(timestamp);
  }

  return (
    <SurfaceCard title="Histórico de versões">
      <div className={styles.stack}>
        {isLoading ? <p className={styles.hint}>Carregando versões do contrato...</p> : null}
        {errorMessage ? (
          <p className={styles.alert} role="alert">
            {errorMessage}
          </p>
        ) : null}
        {!isLoading && !errorMessage && versions.length === 0 ? (
          <p className={styles.hint}>Histórico de versões ainda não disponível.</p>
        ) : null}
        {!isLoading && !errorMessage && versions.length > 0 ? (
          <ul className={styles.list}>
            {versions.map((version) => {
              const isSelected = version.contractVersionId === selectedVersionId;
              const isBaseline = version.contractVersionId === comparisonBaselineId;
              return (
                <li className={styles.item} key={version.contractVersionId}>
                  <div className={styles.row}>
                    <div>
                      <strong>Versão {version.versionNumber}</strong>
                      <p className={styles.meta}>
                        {version.originalFilename} · {formatVersionTimestamp(version.createdAt)}
                      </p>
                    </div>
                    <div className={styles.badgeRow}>
                      {version.isCurrent ? (
                        <span className={`${styles.badge} ${styles.badgeCurrent}`}>Atual</span>
                      ) : null}
                      {isSelected ? (
                        <span className={`${styles.badge} ${styles.badgeSelected}`}>
                          Em visualização
                        </span>
                      ) : null}
                      {isBaseline ? (
                        <span className={`${styles.badge} ${styles.badgeBaseline}`}>Base de comparação</span>
                      ) : null}
                    </div>
                  </div>
                  <div className={styles.actions}>
                    <button
                      className={uiStyles.buttonSecondary}
                      onClick={() => onOpenVersion(version.isCurrent ? null : version.contractVersionId)}
                      type="button"
                    >
                      {version.isCurrent ? "Abrir versão atual" : `Abrir versão ${version.versionNumber}`}
                    </button>
                    <button
                      className={uiStyles.buttonPrimary}
                      disabled={isSelected}
                      onClick={() => onCompareWith(version.contractVersionId)}
                      type="button"
                    >
                      Usar como base de comparação
                    </button>
                  </div>
                </li>
              );
            })}
          </ul>
        ) : null}
      </div>
    </SurfaceCard>
  );
}
