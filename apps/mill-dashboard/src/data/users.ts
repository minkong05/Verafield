import { createUser, listUsers, setUserActive } from "../api/users";
import type { User, UserCreateInput } from "../types/api";
import { usesMockData } from "./dashboard";

const demoUsers: User[] = [{ id: "demo-admin", email: "admin@tapak.example", role: "admin", mill_id: null, is_active: true, created_at: "2026-09-01T00:00:00Z", updated_at: "2026-09-01T00:00:00Z" }];

export function loadUsers(): Promise<User[]> {
  return usesMockData ? Promise.resolve(demoUsers) : listUsers();
}

export function registerUser(values: UserCreateInput): Promise<User> {
  if (!usesMockData) return createUser(values);
  const now = new Date().toISOString();
  return Promise.resolve({ id: crypto.randomUUID(), email: values.email, role: values.role, mill_id: values.mill_id, is_active: true, created_at: now, updated_at: now });
}

export function updateUserActive(user: User, isActive: boolean): Promise<User> {
  return usesMockData ? Promise.resolve({ ...user, is_active: isActive, updated_at: new Date().toISOString() }) : setUserActive(user.id, isActive);
}
