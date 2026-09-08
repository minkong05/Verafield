import { useEffect, useState } from "react";

import { loadUsers, registerUser, updateUserActive } from "../data/users";
import type { User, UserCreateInput } from "../types/api";

export function useAdminUsers(enabled: boolean) {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [requestVersion, setRequestVersion] = useState(0);

  useEffect(() => {
    if (!enabled) return;
    let active = true;
    setLoading(true); setError(null);
    loadUsers().then((result) => { if (active) setUsers(result); }).catch((reason: unknown) => { if (active) setError(reason instanceof Error ? reason.message : "Unable to load users."); }).finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [enabled, requestVersion]);

  const create = async (values: UserCreateInput) => {
    const user = await registerUser(values);
    setUsers((current) => [...current, user]);
  };

  const toggle = async (user: User) => {
    const updated = await updateUserActive(user, !user.is_active);
    setUsers((current) => current.map((item) => item.id === updated.id ? updated : item));
  };

  return { users, loading, error, retry: () => setRequestVersion((value) => value + 1), create, toggle };
}
