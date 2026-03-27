"use client";

import React, { useCallback, useEffect, useState } from "react";

import { SurfaceCard } from "../../../components/ui/surface-card";
import {
  type ContractSummaryResponse,
  getContractSummary,
} from "../../../lib/api/contracts";
import styles from "./contract-summary-panel.module.css";

type ContractSummaryPanelProps = {
  contractId: string;
  versionId?: string | null;
};

export function ContractSummaryPanel({ contractId, versionId }: ContractSummaryPanelProps) {
  const [summary, setSummary] = useState<ContractSummaryResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadSummary = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await getContractSummary(contractId, versionId ?? undefined);
      setSummary(response);
    } catch (loadError) {
      setError(
        loadError instanceof Error
          ? loadError.message
          : "Não foi possível gerar o resumo.",
      );
    } finally {
      setIsLoading(false);
    }
  }, [contractId, versionId]);

  useEffect(() => {
    void loadSummary();
  }, [loadSummary]);

  if (isLoading) {
    return (
      <SurfaceCard title="Resumo do contrato">
        <div className={styles.loadingState}>
          <div className={styles.spinner} />
          <p className={styles.loadingText}>Gerando resumo com IA...</p>
        </div>
      </SurfaceCard>
    );
  }

  if (error) {
    return (
      <SurfaceCard title="Resumo do contrato">
        <p className={styles.errorText}>{error}</p>
        <button
          className={styles.retryButton}
          onClick={() => void loadSummary()}
          type="button"
        >
          Tentar novamente
        </button>
      </SurfaceCard>
    );
  }

  if (!summary || !summary.summary.trim()) {
    return (
      <SurfaceCard title="Resumo do contrato">
        <p className={styles.paragraph}>Resumo ainda não disponível.</p>
      </SurfaceCard>
    );
  }

  return (
    <SurfaceCard title="Resumo do contrato">
      <div className={styles.content}>
        {summary.summary.split("\n\n").map((paragraph, index) => (
          <p className={styles.paragraph} key={index}>
            {paragraph}
          </p>
        ))}

        {summary.key_points.length > 0 ? (
          <div className={styles.keyPoints}>
            <h4 className={styles.keyPointsTitle}>Principais pontos</h4>
            <ul className={styles.keyPointsList}>
              {summary.key_points.map((point, index) => (
                <li className={styles.keyPointItem} key={index}>
                  {point}
                </li>
              ))}
            </ul>
          </div>
        ) : null}
      </div>
    </SurfaceCard>
  );
}
