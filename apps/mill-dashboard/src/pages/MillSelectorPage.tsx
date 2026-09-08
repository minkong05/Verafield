import { ArrowRight, Building2, LogOut } from "lucide-react";

import PageState from "../components/PageState";
import ThemeToggle from "../components/ThemeToggle";
import type { Mill, UUID } from "../types/api";

interface MillSelectorPageProps {
  mills: Mill[];
  loading: boolean;
  error: string | null;
  onRetry: () => void;
  onSelect: (millId: UUID) => void;
  onLogout: () => void;
}

function MillSelectorPage({ mills, loading, error, onRetry, onSelect, onLogout }: MillSelectorPageProps) {
  return <main className="selector-page">
    <header className="auth-page__header"><a className="brand" href="#"><span className="brand__mark">T</span><span>TAPAK</span></a><div className="selector-actions"><ThemeToggle /><button className="icon-button" type="button" aria-label="Sign out" onClick={onLogout}><LogOut aria-hidden="true" /></button></div></header>
    <section className="selector-content"><div className="selector-heading"><p className="eyebrow">Admin workspace</p><h1>Select a mill</h1><p className="text-muted">Choose the mill workspace you want to inspect.</p></div>
      {loading ? <PageState kind="loading" message="Loading registered mills." /> : error ? <PageState kind="error" message={error} onRetry={onRetry} /> : mills.length === 0 ? <PageState kind="empty" message="No mills have been registered." /> :
        <div className="mill-list">{mills.map((mill) => <button className="mill-option" type="button" key={mill.id} disabled={!mill.is_active} onClick={() => onSelect(mill.id)}><span className="mill-option__icon"><Building2 aria-hidden="true" /></span><span><strong>{mill.name}</strong><small>{mill.district}, {mill.state} · {mill.mpob_licence_number}</small></span><span className={`status status--${mill.is_active ? "cleared" : "frozen"}`}>{mill.is_active ? "Active" : "Inactive"}</span><ArrowRight aria-hidden="true" /></button>)}</div>}
    </section>
  </main>;
}

export default MillSelectorPage;
