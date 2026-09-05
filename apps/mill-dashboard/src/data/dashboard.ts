import { getMillBatches, getMillDashboard, getMillRenewalStatuses } from "../api/dashboard";
import { batches, dashboardSuppliers, renewalStatuses } from "../mocks/dashboard";
import type { Batch, MillDashboardSupplier, RenewalStatus, UUID } from "../types/api";

export interface DashboardData {
  suppliers: MillDashboardSupplier[];
  renewals: RenewalStatus[];
  batches: Batch[];
}

export const usesMockData = import.meta.env.VITE_USE_MOCKS !== "false";

export async function loadDashboardData(millId: UUID): Promise<DashboardData> {
  if (usesMockData) {
    return {
      suppliers: dashboardSuppliers,
      renewals: renewalStatuses,
      batches,
    };
  }

  const [suppliers, renewals, millBatches] = await Promise.all([
    getMillDashboard(millId),
    getMillRenewalStatuses(millId),
    getMillBatches(millId),
  ]);

  return { suppliers, renewals, batches: millBatches };
}
