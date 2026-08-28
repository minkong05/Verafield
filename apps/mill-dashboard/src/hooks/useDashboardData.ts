import { useCallback, useEffect, useState } from "react";

import { loadDashboardData, type DashboardData } from "../data/dashboard";
import type { UUID } from "../types/api";

interface DashboardDataState {
  data: DashboardData | null;
  error: string | null;
  loading: boolean;
  retry: () => void;
}

export function useDashboardData(millId: UUID): DashboardDataState {
  const [data, setData] = useState<DashboardData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [requestVersion, setRequestVersion] = useState(0);

  const retry = useCallback(() => setRequestVersion((version) => version + 1), []);

  useEffect(() => {
    let active = true;
    setLoading(true);
    setError(null);

    loadDashboardData(millId)
      .then((result) => {
        if (active) setData(result);
      })
      .catch((reason: unknown) => {
        if (active) {
          setData(null);
          setError(reason instanceof Error ? reason.message : "Unable to load dashboard data.");
        }
      })
      .finally(() => {
        if (active) setLoading(false);
      });

    return () => {
      active = false;
    };
  }, [millId, requestVersion]);

  return { data, error, loading, retry };
}
