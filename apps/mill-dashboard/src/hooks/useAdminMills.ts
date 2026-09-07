import { useEffect, useState } from "react";

import { loadMills } from "../data/mill";
import type { Mill } from "../types/api";

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

  return { mills, loading, error, retry: () => setRequestVersion((version) => version + 1) };
}
