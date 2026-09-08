import { useState, type FormEvent } from "react";

import { savePassword } from "../data/mill";
import type { Mill, MillContactUpdate } from "../types/api";

interface SettingsPageProps {
  mill: Mill | null;
  loading: boolean;
  error: string | null;
  onUpdateContact: (values: MillContactUpdate) => Promise<void>;
}

function SettingsPage({ mill, loading, error: loadError, onUpdateContact }: SettingsPageProps) {
  const [profileStatus, setProfileStatus] = useState<string | null>(null);
  const [passwordStatus, setPasswordStatus] = useState<string | null>(null);
  const [savingProfile, setSavingProfile] = useState(false);
  const [savingPassword, setSavingPassword] = useState(false);

  if (loading) return <p className="panel-empty">Loading mill account…</p>;
  if (loadError || !mill) return <p className="form-error" role="alert">{loadError ?? "Mill account is unavailable."}</p>;

  const submitProfile = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const values = new FormData(event.currentTarget);
    setSavingProfile(true); setProfileStatus(null);
    try {
      await onUpdateContact({ postal_address: String(values.get("postal_address")), email: String(values.get("email")), district: String(values.get("district")) });
      setProfileStatus("Contact details saved.");
    } catch (reason) {
      setProfileStatus(reason instanceof Error ? reason.message : "Unable to save contact details.");
    } finally { setSavingProfile(false); }
  };

  const submitPassword = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const form = event.currentTarget;
    const values = new FormData(form);
    const nextPassword = String(values.get("new_password"));
    if (nextPassword !== String(values.get("confirm_password"))) { setPasswordStatus("New passwords do not match."); return; }
    setSavingPassword(true); setPasswordStatus(null);
    try {
      await savePassword({ current_password: String(values.get("current_password")), new_password: nextPassword });
      form.reset(); setPasswordStatus("Password changed.");
    } catch (reason) {
      setPasswordStatus(reason instanceof Error ? reason.message : "Unable to change password.");
    } finally { setSavingPassword(false); }
  };

  return <>
    <header className="page-heading"><div><p className="eyebrow">Account</p><h1>Settings</h1><p className="text-muted">Mill identity, contact details and account security.</p></div></header>
    <div className="settings-layout">
      <section className="data-panel settings-panel"><header><h2>Mill profile</h2><p>Identity fields are managed by a TAPAK administrator.</p></header>
        <dl className="settings-summary"><div><dt>Name</dt><dd>{mill.name}</dd></div><div><dt>MPOB licence</dt><dd>{mill.mpob_licence_number}</dd></div><div><dt>State</dt><dd>{mill.state.replace(/^./, (value) => value.toUpperCase())}</dd></div></dl>
        <form className="settings-form" onSubmit={submitProfile}>
          <label><span>Postal address</span><textarea name="postal_address" rows={3} defaultValue={mill.postal_address} required /></label>
          <label><span>Contact email</span><input name="email" type="email" defaultValue={mill.email} required /></label>
          <label><span>District</span><input name="district" defaultValue={mill.district} required /></label>
          {profileStatus && <p className="form-message" role="status">{profileStatus}</p>}
          <button className="button button--primary" type="submit" disabled={savingProfile}>{savingProfile ? "Saving…" : "Save changes"}</button>
        </form>
      </section>
      <section className="data-panel settings-panel"><header><h2>Change password</h2><p>Use at least 12 characters.</p></header>
        <form className="settings-form" onSubmit={submitPassword}>
          <label><span>Current password</span><input name="current_password" type="password" autoComplete="current-password" required /></label>
          <label><span>New password</span><input name="new_password" type="password" minLength={12} autoComplete="new-password" required /></label>
          <label><span>Confirm new password</span><input name="confirm_password" type="password" minLength={12} autoComplete="new-password" required /></label>
          {passwordStatus && <p className="form-message" role="status">{passwordStatus}</p>}
          <button className="button button--primary" type="submit" disabled={savingPassword}>{savingPassword ? "Changing…" : "Change password"}</button>
        </form>
      </section>
    </div>
  </>;
}

export default SettingsPage;
