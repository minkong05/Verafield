import { clearSession, saveSession } from "../auth/session";
import type { LoginRequest, PasswordChangeRequest, TokenResponse, User } from "../types/api";
import { apiRequest } from "./client";

export async function login(payload: LoginRequest): Promise<TokenResponse> {
  const token = await apiRequest<TokenResponse>("/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  saveSession(token);
  return token;
}

export function getCurrentUser(): Promise<User> {
  return apiRequest<User>("/auth/me");
}

export function changePassword(payload: PasswordChangeRequest): Promise<void> {
  return apiRequest<void>("/auth/change-password", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export function logout(): void {
  clearSession();
}
