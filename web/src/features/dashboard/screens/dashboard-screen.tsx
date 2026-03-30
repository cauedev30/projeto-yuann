"use client";

import Link from "next/link";
import React from "react";
import { useEffect, useState } from "react";

import { LoadingSkeleton } from "../../../components/ui/loading-skeleton";
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
  return error instanceof Error ? error : new Error("Não foi possível carregar o dashboard.");
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
      <div aria-atomic="true" aria-live="polite" className="sr-only">
        {isLoading ? "Carregando dashboard operacional..." : ""}
        {isRefreshing ? "Atualizando dashboard operacional..." : ""}
        {error?.message ?? ""}
      </div>
      <PageHeader
        eyebrow="Dashboard"
        title="Visão geral"
        description="Resumo dos contratos, eventos e notificações."
      />

      {isLoading ? (
        <SurfaceCard title="Dashboard operacional">
          <LoadingSkeleton heading lines={3} />
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
                disabled={isRefreshing}
                onClick={() => void handleRefresh()}
                type="button"
              >
                {isRefreshing ? "Atualizando..." : "Tentar novamente"}
              </button>
            </div>
          </div>
        </SurfaceCard>
      ) : snapshot ? (
        <div className={styles.stack}>
          <div className={styles.refreshRow}>
            <Link className={styles.manageButton} href="/acervo">
              Abrir Acervo
            </Link>
            <Link className={styles.manageButton} href="/historico" style={{ marginLeft: "1rem" }}>
              Abrir Histórico
            </Link>
          </div>

          <SurfaceCard title="Resumo geral">
            <ContractsSummary summary={snapshot.summary} />
          </SurfaceCard>

          <div className={styles.detailGrid}>
            <SurfaceCard title="Timeline de eventos">
              <EventsTimeline events={snapshot.events} showTitle={false} />
            </SurfaceCard>

            <SurfaceCard title="Histórico de notificações">
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
