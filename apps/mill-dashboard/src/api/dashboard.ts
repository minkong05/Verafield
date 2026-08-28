import type { Batch, MillDashboardSupplier, RenewalStatus, UUID } from "../types/api";
import { apiRequest } from "./client";

export function getMillDashboard(millId: UUID): Promise<MillDashboardSupplier[]> {
  return apiRequest(`/mills/${millId}/dashboard`);
}

export function getMillRenewalStatuses(millId: UUID): Promise<RenewalStatus[]> {
  return apiRequest(`/mills/${millId}/renewal-status`);
}

export function getMillBatches(millId: UUID): Promise<Batch[]> {
  return apiRequest(`/mills/${millId}/batches`);
}
