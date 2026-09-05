import { useEffect, useState } from "react";

import { generateEvidencePack, getEvidencePack } from "../api/evidencePacks";
import { ApiError } from "../api/client";
import { usesMockData } from "../data/dashboard";
import { evidencePackStates } from "../mocks/dashboard";
import type { Batch, EvidencePack, UUID } from "../types/api";
import type { EvidencePackState } from "../types/ui";

export interface EvidencePackRecord {
  state: EvidencePackState;
  pack: EvidencePack | null;
  busy: boolean;
  error: string | null;
}

type EvidencePackRecords = Record<UUID, EvidencePackRecord>;

const mockPack = (batch: Batch): EvidencePack => ({
  id: `demo-pack-${batch.id}`,
  mill_id: batch.mill_id,
  batch_id: batch.id,
  assembled_data: {
    product_description: batch.product_description,
    trade_name: batch.trade_name,
    hs_code: batch.hs_code,
    net_mass_kg: batch.net_mass_kg,
    recipient_name: batch.recipient_name,
    preview: true,
  },
  geojson: { type: "FeatureCollection", features: [] },
  generated_by: "Demo mill analyst",
  generated_at: new Date().toISOString(),
});

export function useEvidencePacks(enabled: boolean, batches: Batch[]) {
  const [records, setRecords] = useState<EvidencePackRecords>({});
  const [loading, setLoading] = useState(false);
  const [pageError, setPageError] = useState<string | null>(null);

  useEffect(() => {
    if (!enabled) return;
    let active = true;
    setLoading(true);
    setPageError(null);

    const load = async () => {
      if (usesMockData) {
        return Object.fromEntries(batches.map((batch) => {
          const state = evidencePackStates[batch.id] ?? "not_generated";
          return [batch.id, { state, pack: state === "ready" ? mockPack(batch) : null, busy: false, error: null }];
        })) as EvidencePackRecords;
      }

      const results = await Promise.all(batches.map(async (batch) => {
        try {
          const pack = await getEvidencePack(batch.mill_id, batch.id);
          return [batch.id, { state: "ready", pack, busy: false, error: null }] as const;
        } catch (error) {
          if (error instanceof ApiError && error.status === 404) {
            return [batch.id, { state: "not_generated", pack: null, busy: false, error: null }] as const;
          }
          throw error;
        }
      }));
      return Object.fromEntries(results) as EvidencePackRecords;
    };

    load()
      .then((result) => { if (active) setRecords(result); })
      .catch((reason: unknown) => { if (active) setPageError(reason instanceof Error ? reason.message : "Unable to load evidence packs."); })
      .finally(() => { if (active) setLoading(false); });

    return () => { active = false; };
  }, [enabled, batches]);

  const generate = async (batch: Batch) => {
    setRecords((current) => ({ ...current, [batch.id]: { ...(current[batch.id] ?? { state: "not_generated", pack: null }), busy: true, error: null } }));
    try {
      const pack = usesMockData ? mockPack(batch) : await generateEvidencePack(batch.mill_id, batch.id, "Mill dashboard analyst");
      setRecords((current) => ({ ...current, [batch.id]: { state: "ready", pack, busy: false, error: null } }));
    } catch (reason) {
      if (reason instanceof ApiError && reason.status === 409) {
        const pack = await getEvidencePack(batch.mill_id, batch.id);
        setRecords((current) => ({ ...current, [batch.id]: { state: "ready", pack, busy: false, error: null } }));
        return;
      }
      const blocked = reason instanceof ApiError && reason.status === 422;
      setRecords((current) => ({
        ...current,
        [batch.id]: {
          state: blocked ? "blocked" : "not_generated",
          pack: null,
          busy: false,
          error: reason instanceof Error ? reason.message : "Unable to generate evidence pack.",
        },
      }));
    }
  };

  return { records, loading, pageError, generate };
}
