import { createBatch } from "../api/batches";
import type { Batch, BatchCreateInput, MillDashboardSupplier, Plot, RenewalStatus, UUID } from "../types/api";
import { usesMockData } from "./dashboard";
import { loadSupplierDetail } from "./supplierDetail";

export interface PlotOption {
  plot: Plot;
  supplier: MillDashboardSupplier;
}

export async function loadPlotOptions(
  suppliers: MillDashboardSupplier[],
  renewals: RenewalStatus[],
): Promise<PlotOption[]> {
  const details = await Promise.all(suppliers.map((supplier) =>
    loadSupplierDetail(supplier, renewals.find((renewal) => renewal.household_id === supplier.household_id) ?? null),
  ));
  return details.flatMap((detail) => detail.plots.map((plot) => ({ plot, supplier: detail.supplier })));
}

export async function createBatchRecord(millId: UUID, payload: BatchCreateInput): Promise<Batch> {
  if (!usesMockData) return createBatch(millId, payload);
  const id = crypto.randomUUID();
  return {
    id,
    mill_id: millId,
    ...payload,
    no_mixing_status: "single_source",
    created_at: new Date().toISOString(),
    plots: payload.plots.map((plot, index) => ({
      id: `${id}-${index}`,
      mill_id: millId,
      batch_id: id,
      ...plot,
    })),
  };
}
