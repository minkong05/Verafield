import { useEffect, useState } from "react";

import { getCurrentUser, login, logout } from "../api/auth";
import { getSession } from "../auth/session";
import { usesMockData } from "../data/dashboard";
import { DEMO_MILL_ID } from "../mocks/dashboard";
import type { LoginRequest, User } from "../types/api";

const demoUser: User = {
  id: "demo-user",
  email: "mill@example.com",
  role: "mill_user",
  mill_id: DEMO_MILL_ID,
  is_active: true,
  created_at: "2026-08-29T00:00:00Z",
  updated_at: "2026-08-29T00:00:00Z",
};

export function useAuth() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (usesMockData) {
      setUser(demoUser);
      setLoading(false);
      return;
    }

    if (!getSession()) {
      setLoading(false);
      return;
    }

    getCurrentUser()
      .then(setUser)
      .catch(() => logout())
      .finally(() => setLoading(false));
  }, []);

  const signIn = async (credentials: LoginRequest) => {
    setSubmitting(true);
    setError(null);
    try {
      if (usesMockData) {
        setUser({ ...demoUser, email: credentials.email });
        return;
      }
      await login(credentials);
      setUser(await getCurrentUser());
    } catch (reason) {
      logout();
      setError(reason instanceof Error ? reason.message : "Unable to sign in.");
    } finally {
      setSubmitting(false);
    }
  };

  const signOut = () => {
    logout();
    setUser(null);
    setError(null);
  };

  return { user, loading, submitting, error, signIn, signOut };
}
