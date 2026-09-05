import { useEffect, useState } from "react";

import { loadReviewQueue } from "../data/reviewQueue";
import type { MillDashboardSupplier, RenewalStatus } from "../types/api";
import type { ReviewItem } from "../types/ui";

export function useReviewQueue(
  enabled: boolean,
  suppliers: MillDashboardSupplier[],
  renewals: RenewalStatus[],
) {
  const [items, setItems] = useState<ReviewItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [requestVersion, setRequestVersion] = useState(0);

  useEffect(() => {
    if (!enabled) return;
    let active = true;
    setLoading(true);
    setError(null);

    loadReviewQueue(suppliers, renewals)
      .then((result) => { if (active) setItems(result); })
      .catch((reason: unknown) => {
        if (active) setError(reason instanceof Error ? reason.message : "Unable to build review queue.");
      })
      .finally(() => { if (active) setLoading(false); });

    return () => { active = false; };
  }, [enabled, suppliers, renewals, requestVersion]);

  return { items, loading, error, retry: () => setRequestVersion((version) => version + 1) };
}
