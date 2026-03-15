import { ContractsSummary } from "@/features/dashboard/components/contracts-summary";
import { EventsTimeline } from "@/features/dashboard/components/events-timeline";
import { NotificationHistory } from "@/features/notifications/components/notification-history";
import { buildFallbackDashboardSnapshot } from "@/lib/api/dashboard";

export default function DashboardPage() {
  const snapshot = buildFallbackDashboardSnapshot();

  return (
    <main>
      <header>
        <p>Portifolio contratual</p>
        <h1>Dashboard de renovacoes</h1>
      </header>

      <ContractsSummary summary={snapshot.summary} />
      <EventsTimeline events={snapshot.events} />
      <NotificationHistory items={snapshot.notifications} />
    </main>
  );
}
