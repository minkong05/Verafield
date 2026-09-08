import { Plus } from "lucide-react";
import { useState, type FormEvent } from "react";

import type { MalaysiaState, Mill, MillAdminUpdate, MillCreateInput, UUID } from "../types/api";

interface AdminMillsPageProps {
  mills: Mill[];
  onCreate: (values: MillCreateInput) => Promise<void>;
  onUpdate: (mill: Mill, values: MillAdminUpdate) => Promise<void>;
  onOpen: (millId: UUID) => void;
}

function AdminMillsPage({ mills, onCreate, onUpdate, onOpen }: AdminMillsPageProps) {
  const [creating, setCreating] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const form = event.currentTarget;
    const values = new FormData(form);
    const payload: MillCreateInput = { name: String(values.get("name")), mpob_licence_number: String(values.get("mpob_licence_number")), postal_address: String(values.get("postal_address")), email: String(values.get("email")), district: String(values.get("district")), state: String(values.get("state")) as MalaysiaState };
    setSubmitting(true); setError(null);
    try { await onCreate(payload); form.reset(); setCreating(false); }
    catch (reason) { setError(reason instanceof Error ? reason.message : "Unable to register mill."); }
    finally { setSubmitting(false); }
  };

  const toggle = async (mill: Mill) => {
    setError(null);
    try { await onUpdate(mill, { is_active: !mill.is_active }); }
    catch (reason) { setError(reason instanceof Error ? reason.message : "Unable to update mill."); }
  };

  return <>
    <header className="page-heading"><div><p className="eyebrow">Administration</p><h1>Mills</h1><p className="text-muted">Register and manage customer mill accounts.</p></div><button className="button button--primary" type="button" onClick={() => setCreating((value) => !value)}><Plus aria-hidden="true" />Register mill</button></header>
    {creating && <section className="data-panel admin-create"><header><h2>New mill</h2><p>All identity fields are required by the registry.</p></header><form className="admin-form" onSubmit={submit}>
      <label><span>Name</span><input name="name" required /></label><label><span>MPOB licence</span><input name="mpob_licence_number" required /></label><label><span>Email</span><input name="email" type="email" required /></label><label><span>District</span><input name="district" required /></label><label className="admin-form__wide"><span>Postal address</span><textarea name="postal_address" rows={2} required /></label><label><span>State</span><select name="state" required><option value="sabah">Sabah</option><option value="sarawak">Sarawak</option></select></label>
      {error && <p className="form-error admin-form__wide" role="alert">{error}</p>}<div className="admin-form__actions admin-form__wide"><button className="button button--secondary" type="button" onClick={() => setCreating(false)}>Cancel</button><button className="button button--primary" disabled={submitting} type="submit">{submitting ? "Registering…" : "Register mill"}</button></div>
    </form></section>}
    {!creating && error && <p className="form-error" role="alert">{error}</p>}
    <section className="data-panel"><div className="table-scroll"><table className="data-table"><thead><tr><th>Mill</th><th>MPOB licence</th><th>Location</th><th>Status</th><th></th></tr></thead><tbody>{mills.map((mill) => <tr key={mill.id}><td className="data-table__primary">{mill.name}<small className="table-subtext">{mill.email}</small></td><td>{mill.mpob_licence_number}</td><td>{mill.district}, {mill.state}</td><td><span className={`status status--${mill.is_active ? "cleared" : "frozen"}`}>{mill.is_active ? "Active" : "Inactive"}</span></td><td className="admin-row-actions"><button className="button button--secondary" type="button" disabled={!mill.is_active} onClick={() => onOpen(mill.id)}>Open</button><button className="button button--secondary" type="button" onClick={() => toggle(mill)}>{mill.is_active ? "Deactivate" : "Activate"}</button></td></tr>)}</tbody></table></div></section>
  </>;
}

export default AdminMillsPage;
