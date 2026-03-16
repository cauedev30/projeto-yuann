import React from "react";

import { PageHeader } from "../../../components/ui/page-header";
import { SurfaceCard } from "../../../components/ui/surface-card";
import type { DashboardSnapshot } from "../../../entities/dashboard/model";
import { NotificationHistory } from "../../notifications/components/notification-history";
import { ContractsSummary } from "../components/contracts-summary";
import { EmptyDashboardState } from "../components/empty-dashboard-state";
import { EventsTimeline } from "../components/events-timeline";
import styles from "./dashboard-screen.module.css";

type DashboardScreenProps = {
  snapshot: DashboardSnapshot | null;
};

export function DashboardScreen({ snapshot }: DashboardScreenProps) {
  return (
    <section className={styles.page}>
      <PageHeader
        eyebrow="Mesa juridica"
        title="Governanca contratual em andamento"
        description="Portfolio, eventos e notificacoes sob a mesma leitura executiva, sem mascarar a ausencia de dados runtime."
      />

      {snapshot ? (
        <div className={styles.stack}>
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
