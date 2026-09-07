import type { User, UserCreateInput, UUID } from "../types/api";
import { apiRequest } from "./client";

export function listUsers(millId?: UUID): Promise<User[]> {
  const query = millId ? `?mill_id=${encodeURIComponent(millId)}` : "";
  return apiRequest(`/users${query}`);
}

export function createUser(payload: UserCreateInput): Promise<User> {
  return apiRequest("/users", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
}

export function setUserActive(userId: UUID, isActive: boolean): Promise<User> {
  return apiRequest(`/users/${userId}`, { method: "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ is_active: isActive }) });
}
