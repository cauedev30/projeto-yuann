import { getAuthHeaders } from "./auth";
import { getClientEnv } from "../env";
import {
  type DashboardSnapshot,
  type DashboardSnapshotPayload,
  mapDashboardSnapshotPayload,
} from "../../entities/dashboard/model";

const GENERIC_DASHBOARD_ERROR = "Nao foi possivel carregar o dashboard.";

export class DashboardApiError extends Error {
  constructor(
    message: string,
    readonly statusCode?: number,
  ) {
    super(message);
    this.name = "DashboardApiError";
  }
}

async function buildDashboardError(response: Response): Promise<DashboardApiError> {
  try {
    const payload = (await response.json()) as { detail?: unknown };
    if (typeof payload.detail === "string" && payload.detail.trim()) {
      return new DashboardApiError(payload.detail, response.status);
    }
  } catch {
    // fall through to generic error
  }

  return new DashboardApiError(GENERIC_DASHBOARD_ERROR, response.status);
}

function isOperationallyEmpty(snapshot: DashboardSnapshot): boolean {
  return (
    snapshot.summary.activeContracts === 0 &&
    snapshot.summary.criticalFindings === 0 &&
    snapshot.summary.expiringSoon === 0 &&
    snapshot.events.length === 0 &&
    snapshot.notifications.length === 0
  );
}

export async function getDashboardSnapshot(
  fetchImpl: typeof fetch = fetch,
): Promise<DashboardSnapshot | null> {
  const { NEXT_PUBLIC_API_URL } = getClientEnv();
  const response = await fetchImpl(`${NEXT_PUBLIC_API_URL}/api/dashboard`, {
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    throw await buildDashboardError(response);
  }

  const payload = (await response.json()) as DashboardSnapshotPayload;
  const snapshot = mapDashboardSnapshotPayload(payload);

  return isOperationallyEmpty(snapshot) ? null : snapshot;
}
