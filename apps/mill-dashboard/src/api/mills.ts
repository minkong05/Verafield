import type { Mill, MillAdminUpdate, MillContactUpdate, MillCreateInput, UUID } from "../types/api";
import { apiRequest } from "./client";

export function getMill(millId: UUID): Promise<Mill> {
  return apiRequest(`/mills/${millId}`);
}

export function listMills(): Promise<Mill[]> {
  return apiRequest("/mills");
}

export function createMill(payload: MillCreateInput): Promise<Mill> {
  return apiRequest("/mills", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
}

export function updateMillAsAdmin(millId: UUID, payload: MillAdminUpdate): Promise<Mill> {
  return apiRequest(`/mills/${millId}`, { method: "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
}

export function updateMill(millId: UUID, payload: MillContactUpdate): Promise<Mill> {
  return apiRequest(`/mills/${millId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}
