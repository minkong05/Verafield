import { Download, FileArchive, FilePlus2, LoaderCircle, Plus } from "lucide-react";

import PageState from "../components/PageState";
import type { EvidencePackRecord } from "../hooks/useEvidencePacks";
import type { Batch } from "../types/api";
import type { EvidencePackState } from "../types/ui";

const stateLabels: Record<EvidencePackState, string> = {
  ready: "Ready",
  not_generated: "Not generated",
  blocked: "Blocked",
};

const stateClass: Record<EvidencePackState, string> = {
  ready: "cleared",
  not_generated: "pending",
  blocked: "frozen",
};

const formatDate = (value: string) =>
  new Intl.DateTimeFormat("en-MY", { day: "numeric", month: "short", year: "numeric" }).format(new Date(value));

interface EvidencePacksPageProps {
  batches: Batch[];
  records: Record<string, EvidencePackRecord>;
  loading: boolean;
  error: string | null;
  onGenerate: (batch: Batch) => void;
  onCreate: () => void;
}

function downloadPack(batch: Batch, record: EvidencePackRecord) {
  if (!record.pack) return;
  const blob = new Blob([JSON.stringify(record.pack, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `evidence-pack-${batch.id}.json`;
  link.click();
  URL.revokeObjectURL(url);
}

function EvidencePacksPage({ batches, records, loading, error, onGenerate, onCreate }: EvidencePacksPageProps) {
  return (
    <>
      <header className="page-heading">
        <div>
          <p className="eyebrow">Buyer documentation</p>
          <h1>Evidence packs</h1>
          <p className="text-muted">Shipment batches and their Annex II evidence output.</p>
        </div>
        <button className="button button--primary" type="button" onClick={onCreate}><Plus aria-hidden="true" /> Create batch</button>
      </header>

      <section className="data-panel">
        {loading ? <PageState kind="loading" message="Checking evidence pack status for each batch." /> : error ? <PageState kind="error" message={error} /> : batches.length === 0 ? <PageState kind="empty" message="Create a shipment batch before generating an evidence pack." /> :
        <div className="table-scroll">
          <table className="data-table">
            <thead><tr><th>Batch</th><th>Recipient</th><th>Net mass</th><th>Created</th><th>Pack status</th><th></th></tr></thead>
            <tbody>
              {batches.map((batch) => {
                const record = records[batch.id] ?? { state: "not_generated", pack: null, busy: false, error: null };
                const state = record.state;
                return (
                  <tr key={batch.id}>
                    <td><span className="batch-name"><FileArchive aria-hidden="true" /><span><strong>{batch.trade_name}</strong><small>{batch.id.slice(0, 8)}</small></span></span></td>
                    <td>{batch.recipient_name}</td>
                    <td>{Number(batch.net_mass_kg).toLocaleString()} kg</td>
                    <td>{formatDate(batch.created_at)}</td>
                    <td><span className={`status status--${stateClass[state]}`} title={record.error ?? undefined}>{stateLabels[state]}</span></td>
                    <td className="pack-action">
                      {state === "ready" ? <button className="button button--secondary" type="button" onClick={() => downloadPack(batch, record)}><Download aria-hidden="true" /> Download</button> :
                        <button className="button button--secondary" type="button" disabled={record.busy || state === "blocked"} title={record.error ?? undefined} onClick={() => onGenerate(batch)}>
                          {record.busy ? <LoaderCircle className="page-state__spinner" aria-hidden="true" /> : <FilePlus2 aria-hidden="true" />} {record.busy ? "Generating" : state === "blocked" ? "Blocked" : "Generate"}
                        </button>}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>}
      </section>
    </>
  );
}

export default EvidencePacksPage;
