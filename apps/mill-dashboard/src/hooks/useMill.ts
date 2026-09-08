import { useEffect, useState } from "react";

import { loadMill, saveMillContact } from "../data/mill";
import type { Mill, MillContactUpdate, UUID } from "../types/api";

export function useMill(millId: UUID) {
  const [mill, setMill] = useState<Mill | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    setLoading(true);
    setError(null);
    loadMill(millId)
      .then((result) => { if (active) setMill(result); })
      .catch((reason: unknown) => { if (active) setError(reason instanceof Error ? reason.message : "Unable to load mill profile."); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [millId]);

  const updateContact = async (values: MillContactUpdate) => {
    if (!mill) throw new Error("Mill profile is not available.");
    const updated = await saveMillContact(mill, values);
    setMill(updated);
  };

  return { mill, loading, error, updateContact };
}
