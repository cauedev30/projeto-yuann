"use client";

import { useQuery } from "@tanstack/react-query";
import { getDashboardSnapshot } from "@/lib/api/dashboard";
import type { DashboardSnapshot } from "@/entities/dashboard/model";

export const dashboardKeys = {
  all: ["dashboard"] as const,
  snapshot: () => [...dashboardKeys.all, "snapshot"] as const,
};

export function useDashboard() {
  return useQuery<DashboardSnapshot | null>({
    queryKey: dashboardKeys.snapshot(),
    queryFn: () => getDashboardSnapshot(),
  });
}
