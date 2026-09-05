import type { EvidencePack, UUID } from "../types/api";
import { apiRequest } from "./client";

export function getEvidencePack(millId: UUID, batchId: UUID): Promise<EvidencePack> {
  return apiRequest(`/mills/${millId}/batches/${batchId}/evidence-pack`);
}

export function generateEvidencePack(
  millId: UUID,
  batchId: UUID,
  generatedBy: string,
): Promise<EvidencePack> {
  return apiRequest(`/mills/${millId}/batches/${batchId}/evidence-pack`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ generated_by: generatedBy }),
  });
}
