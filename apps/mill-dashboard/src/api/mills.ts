import type { Mill, MillContactUpdate, UUID } from "../types/api";
import { apiRequest } from "./client";

export function getMill(millId: UUID): Promise<Mill> {
  return apiRequest(`/mills/${millId}`);
}

export function updateMill(millId: UUID, payload: MillContactUpdate): Promise<Mill> {
  return apiRequest(`/mills/${millId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}
