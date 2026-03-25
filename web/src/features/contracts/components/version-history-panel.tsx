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
  return (
    <SurfaceCard title="Historico de versoes">
      <div className={styles.stack}>
        {isLoading ? <p className={styles.hint}>Carregando versoes do contrato...</p> : null}
        {errorMessage ? (
          <p className={styles.alert} role="alert">
            {errorMessage}
          </p>
        ) : null}
        {!isLoading && !errorMessage && versions.length === 0 ? (
          <p className={styles.hint}>Historico de versoes ainda nao disponivel.</p>
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
                      <strong>Versao {version.versionNumber}</strong>
                      <p className={styles.meta}>
                        {version.originalFilename} · {version.createdAt}
                      </p>
                    </div>
                    <div className={styles.badgeRow}>
                      {version.isCurrent ? (
                        <span className={`${styles.badge} ${styles.badgeCurrent}`}>Atual</span>
                      ) : null}
                      {isSelected ? (
                        <span className={`${styles.badge} ${styles.badgeSelected}`}>
                          Em visualizacao
                        </span>
                      ) : null}
                      {isBaseline ? (
                        <span className={`${styles.badge} ${styles.badgeBaseline}`}>Baseline</span>
                      ) : null}
                    </div>
                  </div>
                  <div className={styles.actions}>
                    <button
                      className={uiStyles.buttonSecondary}
                      onClick={() => onOpenVersion(version.isCurrent ? null : version.contractVersionId)}
                      type="button"
                    >
                      {version.isCurrent ? "Abrir versao atual" : `Abrir versao ${version.versionNumber}`}
                    </button>
                    <button
                      className={uiStyles.buttonPrimary}
                      disabled={isSelected}
                      onClick={() => onCompareWith(version.contractVersionId)}
                      type="button"
                    >
                      Usar como baseline
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
