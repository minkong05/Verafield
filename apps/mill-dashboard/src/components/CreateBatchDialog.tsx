import { LoaderCircle, X } from "lucide-react";
import { useEffect, useState, type FormEvent } from "react";

import { createBatchRecord, loadPlotOptions, type PlotOption } from "../data/batches";
import type { Batch, BatchCreateInput, MillDashboardSupplier, RenewalStatus, UUID } from "../types/api";

interface CreateBatchDialogProps {
  open: boolean;
  millId: UUID;
  suppliers: MillDashboardSupplier[];
  renewals: RenewalStatus[];
  onClose: () => void;
  onCreated: (batch: Batch) => void;
}

const today = () => {
  const date = new Date();
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
};

function CreateBatchDialog({ open, millId, suppliers, renewals, onClose, onCreated }: CreateBatchDialogProps) {
  const [plots, setPlots] = useState<PlotOption[]>([]);
  const [loadingPlots, setLoadingPlots] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!open) return;
    let active = true;
    setLoadingPlots(true);
    setError(null);
    loadPlotOptions(suppliers, renewals)
      .then((result) => { if (active) setPlots(result); })
      .catch((reason: unknown) => { if (active) setError(reason instanceof Error ? reason.message : "Unable to load plots."); })
      .finally(() => { if (active) setLoadingPlots(false); });
    return () => { active = false; };
  }, [open, suppliers, renewals]);

  if (!open) return null;

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const values = new FormData(event.currentTarget);
    const payload: BatchCreateInput = {
      product_description: String(values.get("product_description")),
      trade_name: String(values.get("trade_name")),
      hs_code: String(values.get("hs_code")),
      net_mass_kg: String(values.get("net_mass_kg")),
      recipient_name: String(values.get("recipient_name")),
      recipient_postal_address: String(values.get("recipient_postal_address")),
      recipient_email: String(values.get("recipient_email")),
      created_by: String(values.get("created_by")),
      plots: [{ plot_id: String(values.get("plot_id")), harvest_date: String(values.get("harvest_date")) }],
    };

    setSubmitting(true);
    setError(null);
    try {
      const batch = await createBatchRecord(millId, payload);
      onCreated(batch);
      onClose();
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Unable to create batch.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <>
      <button className="drawer-backdrop" aria-label="Close create batch dialog" onClick={onClose} />
      <section className="batch-dialog" role="dialog" aria-modal="true" aria-labelledby="create-batch-title">
        <header className="drawer-header">
          <span>New shipment batch</span>
          <button className="icon-button" type="button" aria-label="Close create batch dialog" onClick={onClose}><X aria-hidden="true" /></button>
        </header>
        <form className="batch-form" onSubmit={submit}>
          <div className="batch-form__heading"><h2 id="create-batch-title">Create batch</h2><p>Record the product, recipient and source plot before generating evidence.</p></div>
          <fieldset><legend>Product</legend>
            <label><span>Product description</span><input name="product_description" defaultValue="Fresh fruit bunches" required /></label>
            <div className="form-row"><label><span>Trade name</span><input name="trade_name" defaultValue="Oil palm fruit" required /></label><label><span>HS code</span><input name="hs_code" defaultValue="120710" required /></label></div>
            <label><span>Net mass (kg)</span><input name="net_mass_kg" type="number" min="0.01" step="0.01" required /></label>
          </fieldset>
          <fieldset><legend>Recipient</legend>
            <label><span>Name</span><input name="recipient_name" required /></label>
            <label><span>Postal address</span><textarea name="recipient_postal_address" rows={2} required /></label>
            <label><span>Email</span><input name="recipient_email" type="email" required /></label>
          </fieldset>
          <fieldset><legend>Source</legend>
            <label><span>Plot</span><select name="plot_id" required disabled={loadingPlots || plots.length === 0}><option value="">{loadingPlots ? "Loading plots…" : plots.length ? "Select a plot" : "No plots available"}</option>{plots.map(({ plot, supplier }) => <option key={plot.id} value={plot.id}>{supplier.name} · {supplier.district} · {Number(plot.area_ha)} ha · {plot.id.slice(0, 8)}</option>)}</select></label>
            <label><span>Harvest date</span><input name="harvest_date" type="date" max={today()} defaultValue={today()} required /></label>
            <label><span>Created by</span><input name="created_by" defaultValue="Mill dashboard analyst" required /></label>
          </fieldset>
          {error && <p className="form-error" role="alert">{error}</p>}
          <footer className="batch-form__actions"><button className="button button--secondary" type="button" onClick={onClose}>Cancel</button><button className="button button--primary" type="submit" disabled={submitting || loadingPlots || plots.length === 0}>{submitting && <LoaderCircle className="page-state__spinner" aria-hidden="true" />}{submitting ? "Creating…" : "Create batch"}</button></footer>
        </form>
      </section>
    </>
  );
}

export default CreateBatchDialog;
