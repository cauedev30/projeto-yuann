import { DashboardScreen } from "@/features/dashboard/screens/dashboard-screen";
import { getDashboardSnapshot } from "@/lib/api/dashboard";

export default async function DashboardPage() {
  const snapshot = await getDashboardSnapshot();
  return <DashboardScreen snapshot={snapshot} />;
}
