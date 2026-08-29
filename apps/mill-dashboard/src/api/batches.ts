import type { Batch, BatchCreateInput, UUID } from "../types/api";
import { apiRequest } from "./client";

export function createBatch(millId: UUID, payload: BatchCreateInput): Promise<Batch> {
  return apiRequest(`/mills/${millId}/batches`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}
