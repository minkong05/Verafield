import { useEffect, useState } from "react";

import { loadMills, registerMill, saveMillAsAdmin } from "../data/mill";
import type { Mill, MillAdminUpdate, MillCreateInput } from "../types/api";

export function useAdminMills(enabled: boolean) {
  const [mills, setMills] = useState<Mill[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [requestVersion, setRequestVersion] = useState(0);

  useEffect(() => {
    if (!enabled) return;
    let active = true;
    setLoading(true); setError(null);
    loadMills()
      .then((result) => { if (active) setMills(result); })
      .catch((reason: unknown) => { if (active) setError(reason instanceof Error ? reason.message : "Unable to load mills."); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [enabled, requestVersion]);

  const create = async (values: MillCreateInput) => {
    const mill = await registerMill(values);
    setMills((current) => [...current, mill]);
  };

  const update = async (mill: Mill, values: MillAdminUpdate) => {
    const updated = await saveMillAsAdmin(mill, values);
    setMills((current) => current.map((item) => item.id === updated.id ? updated : item));
  };

  return { mills, loading, error, retry: () => setRequestVersion((version) => version + 1), create, update };
}
