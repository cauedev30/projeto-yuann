import React from "react";

import { SurfaceCard } from "../../../components/ui/surface-card";
import type { ContractVersionComparison } from "../../../entities/contracts/model";
import styles from "./version-diff-panel.module.css";

type VersionDiffPanelProps = {
  comparison: ContractVersionComparison | null;
  isLoading: boolean;
  errorMessage?: string | null;
};

function changeTypeLabel(changeType: string): string {
  if (changeType === "added") {
    return "Novo";
  }
  if (changeType === "removed") {
    return "Removido";
  }
  return "Alterado";
}

export function VersionDiffPanel({
  comparison,
  isLoading,
  errorMessage,
}: VersionDiffPanelProps) {
  return (
    <SurfaceCard title="Painel de comparação">
      <div className={styles.stack}>
        {isLoading ? <p className={styles.hint}>Carregando comparação...</p> : null}
        {errorMessage ? (
          <p className={styles.alert} role="alert">
            {errorMessage}
          </p>
        ) : null}
        {!isLoading && !errorMessage && !comparison ? (
          <p className={styles.hint}>Nenhuma comparação selecionada.</p>
        ) : null}
        {!isLoading && !errorMessage && comparison ? (
          <>
            <section className={styles.section}>
              <h3 className={styles.sectionTitle}>Resumo executivo</h3>
              <p className={styles.hint}>{comparison.summary}</p>
            </section>
            <section className={styles.section}>
              <h3 className={styles.sectionTitle}>Comparação de texto</h3>
              <div className={styles.diffLines}>
                {comparison.textDiff.lines.length === 0 ? (
                  <p className={styles.hint}>Nenhuma diferença textual relevante.</p>
                ) : (
                  comparison.textDiff.lines.map((line, index) => (
                    <p
                      className={`${styles.diffLine} ${styles[line.kind]}`}
                      key={`${line.kind}-${index}`}
                    >
                      {line.value}
                    </p>
                  ))
                )}
              </div>
            </section>
            <section className={styles.section}>
              <h3 className={styles.sectionTitle}>Comparação de achados</h3>
              <div className={styles.findingList}>
                {comparison.findingsDiff.items.length === 0 ? (
                  <p className={styles.hint}>Nenhuma mudança de achado detectada.</p>
                ) : (
                  comparison.findingsDiff.items.map((item) => (
                    <article className={styles.findingItem} key={`${item.changeType}-${item.clauseName}`}>
                      <div className={styles.findingHeader}>
                        <strong>{item.clauseName}</strong>
                        <span className={styles.findingBadge}>
                          {changeTypeLabel(item.changeType)}
                        </span>
                      </div>
                      <p className={styles.findingBody}>
                        Antes: {item.previousStatus ?? "sem registro"} | Agora:{" "}
                        {item.currentStatus ?? "sem registro"}
                      </p>
                      <p className={styles.findingBody}>
                        {item.currentSummary ?? item.previousSummary ?? "Sem resumo disponível."}
                      </p>
                    </article>
                  ))
                )}
              </div>
            </section>
          </>
        ) : null}
      </div>
    </SurfaceCard>
  );
}
