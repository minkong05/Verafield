import { Download, FileArchive, Plus } from "lucide-react";

import { evidencePackStates } from "../mocks/dashboard";
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
}

function EvidencePacksPage({ batches }: EvidencePacksPageProps) {
  return (
    <>
      <header className="page-heading">
        <div>
          <p className="eyebrow">Buyer documentation</p>
          <h1>Evidence packs</h1>
          <p className="text-muted">Shipment batches and their Annex II evidence output.</p>
        </div>
        <button className="button button--primary" type="button"><Plus aria-hidden="true" /> Create batch</button>
      </header>

      <section className="data-panel">
        <div className="table-scroll">
          <table className="data-table">
            <thead><tr><th>Batch</th><th>Recipient</th><th>Net mass</th><th>Created</th><th>Pack status</th><th></th></tr></thead>
            <tbody>
              {batches.map((batch) => {
                const state = evidencePackStates[batch.id] ?? "not_generated";
                return (
                  <tr key={batch.id}>
                    <td><span className="batch-name"><FileArchive aria-hidden="true" /><span><strong>{batch.trade_name}</strong><small>{batch.id.slice(0, 8)}</small></span></span></td>
                    <td>{batch.recipient_name}</td>
                    <td>{Number(batch.net_mass_kg).toLocaleString()} kg</td>
                    <td>{formatDate(batch.created_at)}</td>
                    <td><span className={`status status--${stateClass[state]}`}>{stateLabels[state]}</span></td>
                    <td className="table-action"><button className="icon-button" type="button" aria-label={`Download ${batch.trade_name} evidence pack`} disabled={state !== "ready"}><Download aria-hidden="true" /></button></td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </section>
    </>
  );
}

export default EvidencePacksPage;
