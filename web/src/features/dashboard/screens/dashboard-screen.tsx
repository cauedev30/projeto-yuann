"use client";

import React from "react";
import { useEffect, useState } from "react";

import { PageHeader } from "../../../components/ui/page-header";
import { SurfaceCard } from "../../../components/ui/surface-card";
import type { DashboardSnapshot } from "../../../entities/dashboard/model";
import { getDashboardSnapshot } from "../../../lib/api/dashboard";
import { NotificationHistory } from "../../notifications/components/notification-history";
import { ContractsSummary } from "../components/contracts-summary";
import { EmptyDashboardState } from "../components/empty-dashboard-state";
import { EventsTimeline } from "../components/events-timeline";
import styles from "./dashboard-screen.module.css";

type DashboardScreenProps = {
  loadDashboardSnapshot?: () => Promise<DashboardSnapshot | null>;
};

function normalizeDashboardError(error: unknown): Error {
  return error instanceof Error ? error : new Error("Nao foi possivel carregar o dashboard.");
}

export function DashboardScreen({
  loadDashboardSnapshot = getDashboardSnapshot,
}: DashboardScreenProps) {
  const [snapshot, setSnapshot] = useState<DashboardSnapshot | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    let isActive = true;

    async function load() {
      setIsLoading(true);
      setError(null);

      try {
        const response = await loadDashboardSnapshot();
        if (!isActive) {
          return;
        }

        setSnapshot(response);
      } catch (loadError) {
        if (!isActive) {
          return;
        }

        setSnapshot(null);
        setError(normalizeDashboardError(loadError));
      } finally {
        if (isActive) {
          setIsLoading(false);
        }
      }
    }

    void load();

    return () => {
      isActive = false;
    };
  }, [loadDashboardSnapshot]);

  async function handleRefresh() {
    setIsRefreshing(true);
    setError(null);

    try {
      const response = await loadDashboardSnapshot();
      setSnapshot(response);
    } catch (loadError) {
      setSnapshot(null);
      setError(normalizeDashboardError(loadError));
    } finally {
      setIsRefreshing(false);
    }
  }

  return (
    <section className={styles.page}>
      <PageHeader
        eyebrow="Mesa juridica"
        title="Governanca contratual em andamento"
        description="Portfolio, eventos e notificacoes sob a mesma leitura executiva, sem mascarar a ausencia de dados runtime."
      />

      {isLoading ? (
        <SurfaceCard title="Dashboard operacional">
          <p className={styles.sectionText}>Carregando dashboard operacional...</p>
        </SurfaceCard>
      ) : error ? (
        <SurfaceCard title="Dashboard operacional">
          <div className={styles.stack}>
            <p className={styles.alert} role="alert">
              {error.message}
            </p>
            <div className={styles.refreshRow}>
              <button
                className={styles.refreshButton}
                onClick={() => void handleRefresh()}
                type="button"
              >
                Tentar novamente
              </button>
            </div>
          </div>
        </SurfaceCard>
      ) : snapshot ? (
        <div className={styles.stack}>
          <div className={styles.refreshRow}>
            <button
              className={styles.refreshButton}
              disabled={isRefreshing}
              onClick={() => void handleRefresh()}
              type="button"
            >
              {isRefreshing ? "Atualizando..." : "Atualizar painel"}
            </button>
          </div>

          <SurfaceCard title="Resumo do portifolio">
            <ContractsSummary summary={snapshot.summary} />
          </SurfaceCard>

          <div className={styles.detailGrid}>
            <SurfaceCard title="Timeline de eventos">
              <EventsTimeline events={snapshot.events} showTitle={false} />
            </SurfaceCard>

            <SurfaceCard title="Historico de notificacoes">
              <NotificationHistory items={snapshot.notifications} showTitle={false} />
            </SurfaceCard>
          </div>
        </div>
      ) : (
        <EmptyDashboardState />
      )}
    </section>
  );
}
