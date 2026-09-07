import type { TokenResponse } from "../types/api";

const SESSION_KEY = "tapak.auth.session";
export const SESSION_EXPIRED_EVENT = "tapak:session-expired";

export interface AuthSession {
  accessToken: string;
  expiresAt: string;
}

export function getSession(): AuthSession | null {
  const stored = sessionStorage.getItem(SESSION_KEY);
  if (!stored) return null;

  try {
    const session = JSON.parse(stored) as AuthSession;
    if (!session.accessToken || new Date(session.expiresAt).getTime() <= Date.now()) {
      clearSession();
      return null;
    }
    return session;
  } catch {
    clearSession();
    return null;
  }
}

export function saveSession(token: TokenResponse): AuthSession {
  const session = { accessToken: token.access_token, expiresAt: token.expires_at };
  sessionStorage.setItem(SESSION_KEY, JSON.stringify(session));
  return session;
}

export function clearSession(): void {
  sessionStorage.removeItem(SESSION_KEY);
}

export function expireSession(): void {
  clearSession();
  window.dispatchEvent(new Event(SESSION_EXPIRED_EVENT));
}
