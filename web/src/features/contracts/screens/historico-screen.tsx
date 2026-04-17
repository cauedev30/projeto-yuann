"use client";

import { useRouter } from "next/navigation";
import React, { useCallback, useEffect, useState } from "react";

import type { ContractListItemSummary } from "@/entities/contracts/model";
import { ContractsListPanel } from "@/features/contracts/components/contracts-list-panel";
import { listContracts, updateContract } from "@/lib/api/contracts";
import styles from "./contracts-screen.module.css";

function getRetentionText(lastAnalyzedAt: string | null): string | null {
  if (!lastAnalyzedAt) return null;
  const analysisDate = new Date(lastAnalyzedAt);
  const now = new Date();
  
  // Calculate difference in days
  const diffTime = Math.abs(now.getTime() - analysisDate.getTime());
  const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
  const remainingDays = 30 - diffDays;
  
  if (remainingDays < 0) return "Expirado";
  if (remainingDays === 0) return "Expira hoje";
  return `Expira em ${remainingDays} dias`;
}

export function HistoricoScreen() {
  const router = useRouter();
  const [contracts, setContracts] = useState<ContractListItemSummary[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchContracts = useCallback(async () => {
    try {
      const response = await listContracts("history");
      setContracts(response.items);
      return response.items;
    } catch (err) {
      throw err;
    }
  }, []);

  useEffect(() => {
    let isActive = true;

    async function load() {
      setIsLoading(true);
      setError(null);
      try {
        await fetchContracts();
      } catch (err) {
        if (isActive) {
          setError(err instanceof Error ? err.message : "Não foi possível carregar o histórico.");
        }
      } finally {
        if (isActive) {
          setIsLoading(false);
        }
      }
    }

    void load();
    return () => { isActive = false; };
  }, [fetchContracts]);

  const handleRefresh = async () => {
    setIsRefreshing(true);
    setError(null);
    try {
      await fetchContracts();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Não foi possível atualizar o histórico.");
    } finally {
      setIsRefreshing(false);
    }
  };

  const handleActivate = async (e: React.MouseEvent, id: string) => {
    e.preventDefault();
    e.stopPropagation();
    try {
      await updateContract(id, { isActive: true });
      await handleRefresh();
    } catch (err) {
      alert(err instanceof Error ? err.message : "Falha ao ativar o contrato.");
    }
  };

  const renderRowActions = (item: ContractListItemSummary) => (
    <div style={{ display: 'flex', alignItems: 'center', paddingRight: '1rem' }}>
      <button
        onClick={(e) => handleActivate(e, item.id)}
        style={{
          marginLeft: "1rem",
          padding: "0.25rem 0.75rem",
          backgroundColor: "transparent",
          color: "var(--brand-main, #0070f3)",
          border: "1px solid var(--border-subtle, #e2e8f0)",
          borderRadius: "4px",
          cursor: "pointer",
          fontSize: "0.875rem"
        }}
      >
        Ativar
      </button>
    </div>
  );

  const renderExtraMeta = (item: ContractListItemSummary) => {
    const retentionText = getRetentionText(item.lastAnalyzedAt);
    return (
      <>
        {item.lastAnalyzedAt && (
          <span>
            Última análise: {new Date(item.lastAnalyzedAt).toLocaleDateString("pt-BR")}
          </span>
        )}
        {item.lastAccessedAt && (
           <span>
             Último acesso: {new Date(item.lastAccessedAt).toLocaleDateString("pt-BR")}
           </span>
        )}
        {retentionText && (
          <span style={{ color: retentionText === 'Expirado' ? 'var(--text-danger, #ef4444)' : 'inherit', fontWeight: 500 }}>
            {retentionText}
          </span>
        )}
      </>
    );
  };

  return (
    <main className={styles.page}>
      <ContractsListPanel
        eyebrow="Histórico"
        title="Contratos Analisados"
        emptyTitle="Histórico vazio"
        emptyBody="Não há contratos finalizados ou desativados."
        error={error}
        isLoading={isLoading}
        isRefreshing={isRefreshing}
        items={contracts}
        navigateToContract={(id) => router.push(`/contracts/${id}?context=historico`)}
        onRefresh={handleRefresh}
        renderRowActions={renderRowActions}
        renderExtraMeta={renderExtraMeta}
      />
    </main>
  );
}
