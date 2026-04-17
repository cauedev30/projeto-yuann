"use client";

import { useRouter } from "next/navigation";
import React, { useCallback, useEffect, useState } from "react";

import type { ContractListItemSummary } from "@/entities/contracts/model";
import { ContractsListPanel } from "@/features/contracts/components/contracts-list-panel";
import { listContracts, updateContract } from "@/lib/api/contracts";
import styles from "./contracts-screen.module.css";

export function AcervoScreen() {
  const router = useRouter();
  const [contracts, setContracts] = useState<ContractListItemSummary[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchContracts = useCallback(async () => {
    try {
      const response = await listContracts("active");
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
          setError(err instanceof Error ? err.message : "Não foi possível carregar o acervo.");
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
      setError(err instanceof Error ? err.message : "Não foi possível atualizar o acervo.");
    } finally {
      setIsRefreshing(false);
    }
  };

  const handleDeactivate = async (e: React.MouseEvent, id: string) => {
    e.preventDefault();
    e.stopPropagation();
    try {
      await updateContract(id, { isActive: false });
      await handleRefresh();
    } catch (err) {
      alert(err instanceof Error ? err.message : "Falha ao desativar o contrato.");
    }
  };

  const renderRowActions = (item: ContractListItemSummary) => (
    <div style={{ display: 'flex', alignItems: 'center', paddingRight: '1rem' }}>
      <button
        onClick={(e) => handleDeactivate(e, item.id)}
        style={{
          marginLeft: "1rem",
          padding: "0.25rem 0.75rem",
          backgroundColor: "transparent",
          color: "var(--text-danger, #ef4444)",
          border: "1px solid var(--border-subtle, #e2e8f0)",
          borderRadius: "4px",
          cursor: "pointer",
          fontSize: "0.875rem"
        }}
      >
        Desativar
      </button>
    </div>
  );

  return (
    <main className={styles.page}>
      <ContractsListPanel
        eyebrow="Acervo Ativo"
        title="Contratos Vigentes"
        emptyTitle="Acervo vazio"
        emptyBody="Não há contratos ativos no momento."
        error={error}
        isLoading={isLoading}
        isRefreshing={isRefreshing}
        items={contracts}
        navigateToContract={(id) => router.push(`/contracts/${id}?context=acervo`)}
        onRefresh={handleRefresh}
        renderRowActions={renderRowActions}
      />
    </main>
  );
}
