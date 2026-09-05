import { useEffect, useState } from "react";

import { loadSupplierDetail } from "../data/supplierDetail";
import type { MillDashboardSupplier, RenewalStatus } from "../types/api";
import type { SupplierDetail } from "../types/ui";

export function useSupplierDetail(
  supplier: MillDashboardSupplier | null,
  renewal: RenewalStatus | null,
) {
  const [detail, setDetail] = useState<SupplierDetail | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    let active = true;
    setDetail(null);
    setError(null);

    if (!supplier) {
      setLoading(false);
      return () => { active = false; };
    }

    setLoading(true);
    loadSupplierDetail(supplier, renewal)
      .then((result) => { if (active) setDetail(result); })
      .catch((reason: unknown) => {
        if (active) setError(reason instanceof Error ? reason.message : "Unable to load supplier details.");
      })
      .finally(() => { if (active) setLoading(false); });

    return () => { active = false; };
  }, [supplier, renewal]);

  return { detail, error, loading };
}
