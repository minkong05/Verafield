import { changePassword } from "../api/auth";
import { createMill, getMill, listMills, updateMill, updateMillAsAdmin } from "../api/mills";
import type { Mill, MillAdminUpdate, MillContactUpdate, MillCreateInput, PasswordChangeRequest, UUID } from "../types/api";
import { usesMockData } from "./dashboard";

const demoMill: Mill = {
  id: "10000000-0000-4000-8000-000000000001",
  name: "Sungai Murni Mill",
  mpob_licence_number: "MPOB-MILL-1001",
  postal_address: "Sandakan, Sabah, Malaysia",
  email: "operations@sungaimurni.example",
  district: "Sandakan",
  state: "sabah",
  is_active: true,
  created_at: "2026-08-01T00:00:00Z",
  updated_at: "2026-08-01T00:00:00Z",
};

export function loadMill(millId: UUID): Promise<Mill> {
  return usesMockData ? Promise.resolve({ ...demoMill, id: millId }) : getMill(millId);
}

export function loadMills(): Promise<Mill[]> {
  return usesMockData ? Promise.resolve([demoMill]) : listMills();
}

export function registerMill(values: MillCreateInput): Promise<Mill> {
  if (!usesMockData) return createMill(values);
  const now = new Date().toISOString();
  return Promise.resolve({ id: crypto.randomUUID(), ...values, is_active: true, created_at: now, updated_at: now });
}

export function saveMillAsAdmin(mill: Mill, values: MillAdminUpdate): Promise<Mill> {
  return usesMockData
    ? Promise.resolve({ ...mill, ...values, updated_at: new Date().toISOString() })
    : updateMillAsAdmin(mill.id, values);
}

export function saveMillContact(mill: Mill, values: MillContactUpdate): Promise<Mill> {
  return usesMockData
    ? Promise.resolve({ ...mill, ...values, updated_at: new Date().toISOString() })
    : updateMill(mill.id, values);
}

export function savePassword(values: PasswordChangeRequest): Promise<void> {
  return usesMockData ? Promise.resolve() : changePassword(values);
}
