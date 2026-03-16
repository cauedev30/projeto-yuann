import React from "react";

import type { DashboardSnapshot } from "../../../entities/dashboard/model";
import { NotificationHistory } from "../../notifications/components/notification-history";
import { ContractsSummary } from "../components/contracts-summary";
import { EmptyDashboardState } from "../components/empty-dashboard-state";
import { EventsTimeline } from "../components/events-timeline";

type DashboardScreenProps = {
  snapshot: DashboardSnapshot | null;
};

export function DashboardScreen({ snapshot }: DashboardScreenProps) {
  return (
    <main>
      <header>
        <p>Portifolio contratual</p>
        <h1>Dashboard de renovacoes</h1>
      </header>

      {snapshot ? (
        <>
          <ContractsSummary summary={snapshot.summary} />
          <EventsTimeline events={snapshot.events} />
          <NotificationHistory items={snapshot.notifications} />
        </>
      ) : (
        <EmptyDashboardState />
      )}
    </main>
  );
}
