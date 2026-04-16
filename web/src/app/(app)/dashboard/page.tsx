import dynamic from "next/dynamic";

const DashboardScreen = dynamic(
  () => import("../../../features/dashboard/screens/dashboard-screen").then((m) => m.DashboardScreen),
  { loading: () => <div>Carregando...</div> },
);

export default function DashboardPage() {
  return <DashboardScreen />;
}