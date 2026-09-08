import { Plus } from "lucide-react";
import { useState, type FormEvent } from "react";

import PageState from "../components/PageState";
import type { Mill, User, UserCreateInput, UserRole, UUID } from "../types/api";

interface AdminUsersPageProps {
  currentUserId: UUID;
  users: User[];
  mills: Mill[];
  loading: boolean;
  error: string | null;
  onRetry: () => void;
  onCreate: (values: UserCreateInput) => Promise<void>;
  onToggle: (user: User) => Promise<void>;
}

function AdminUsersPage({ currentUserId, users, mills, loading, error: loadError, onRetry, onCreate, onToggle }: AdminUsersPageProps) {
  const [creating, setCreating] = useState(false);
  const [role, setRole] = useState<UserRole>("mill_user");
  const [submitting, setSubmitting] = useState(false);
  const [actionError, setActionError] = useState<string | null>(null);

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const form = event.currentTarget;
    const values = new FormData(form);
    setSubmitting(true); setActionError(null);
    try {
      await onCreate({ email: String(values.get("email")), password: String(values.get("password")), role, mill_id: role === "mill_user" ? String(values.get("mill_id")) : null });
      form.reset(); setRole("mill_user"); setCreating(false);
    } catch (reason) { setActionError(reason instanceof Error ? reason.message : "Unable to create user."); }
    finally { setSubmitting(false); }
  };

  const toggle = async (user: User) => {
    setActionError(null);
    try { await onToggle(user); }
    catch (reason) { setActionError(reason instanceof Error ? reason.message : "Unable to update user."); }
  };

  const millName = (millId: UUID | null) => millId ? mills.find((mill) => mill.id === millId)?.name ?? millId.slice(0, 8) : "TAPAK";

  return <>
    <header className="page-heading"><div><p className="eyebrow">Administration</p><h1>Users</h1><p className="text-muted">Create and revoke TAPAK admin and mill accounts.</p></div><button className="button button--primary" type="button" onClick={() => setCreating((value) => !value)}><Plus aria-hidden="true" />Create user</button></header>
    {creating && <section className="data-panel admin-create"><header><h2>New user</h2><p>Role and mill assignment cannot be changed after creation.</p></header><form className="admin-form" onSubmit={submit}>
      <label><span>Email</span><input name="email" type="email" required /></label><label><span>Password</span><input name="password" type="password" minLength={12} required /></label>
      <label><span>Role</span><select name="role" value={role} onChange={(event) => setRole(event.target.value as UserRole)}><option value="mill_user">Mill user</option><option value="admin">Admin</option></select></label>
      {role === "mill_user" && <label><span>Mill</span><select name="mill_id" required><option value="">Select a mill</option>{mills.filter((mill) => mill.is_active).map((mill) => <option key={mill.id} value={mill.id}>{mill.name}</option>)}</select></label>}
      {actionError && <p className="form-error admin-form__wide" role="alert">{actionError}</p>}<div className="admin-form__actions admin-form__wide"><button className="button button--secondary" type="button" onClick={() => setCreating(false)}>Cancel</button><button className="button button--primary" type="submit" disabled={submitting}>{submitting ? "Creating…" : "Create user"}</button></div>
    </form></section>}
    {!creating && actionError && <p className="form-error" role="alert">{actionError}</p>}
    {loading ? <PageState kind="loading" message="Loading user accounts." /> : loadError ? <PageState kind="error" message={loadError} onRetry={onRetry} /> : users.length === 0 ? <PageState kind="empty" message="No user accounts found." /> :
      <section className="data-panel"><div className="table-scroll"><table className="data-table"><thead><tr><th>User</th><th>Role</th><th>Workspace</th><th>Status</th><th></th></tr></thead><tbody>{users.map((user) => <tr key={user.id}><td className="data-table__primary">{user.email}{user.id === currentUserId && <small className="table-subtext">Current account</small>}</td><td>{user.role === "mill_user" ? "Mill user" : "Admin"}</td><td>{millName(user.mill_id)}</td><td><span className={`status status--${user.is_active ? "cleared" : "frozen"}`}>{user.is_active ? "Active" : "Inactive"}</span></td><td className="admin-row-actions"><button className="button button--secondary" type="button" disabled={user.id === currentUserId} title={user.id === currentUserId ? "You cannot deactivate your current session here." : undefined} onClick={() => toggle(user)}>{user.is_active ? "Deactivate" : "Activate"}</button></td></tr>)}</tbody></table></div></section>}
  </>;
}

export default AdminUsersPage;
