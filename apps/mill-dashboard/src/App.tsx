import { Building2, FileCheck2, LogOut, Menu, RefreshCw, RotateCcw, Settings, Users, X } from "lucide-react";
import { useState } from "react";

import SupplierDrawer from "./components/SupplierDrawer";
import ThemeToggle from "./components/ThemeToggle";
import PageState from "./components/PageState";
import CreateBatchDialog from "./components/CreateBatchDialog";
import { usesMockData } from "./data/dashboard";
import { useDashboardData } from "./hooks/useDashboardData";
import { useSupplierDetail } from "./hooks/useSupplierDetail";
import { useReviewQueue } from "./hooks/useReviewQueue";
import { useEvidencePacks } from "./hooks/useEvidencePacks";
import { useAuth } from "./hooks/useAuth";
import { useMill } from "./hooks/useMill";
import { useAdminMills } from "./hooks/useAdminMills";
import { DEMO_MILL_ID } from "./mocks/dashboard";
import EvidencePacksPage from "./pages/EvidencePacksPage";
import OverviewPage from "./pages/OverviewPage";
import RenewalsPage from "./pages/RenewalsPage";
import ReviewQueuePage from "./pages/ReviewQueuePage";
import SuppliersPage from "./pages/SuppliersPage";
import LoginPage from "./pages/LoginPage";
import SettingsPage from "./pages/SettingsPage";
import MillSelectorPage from "./pages/MillSelectorPage";
import type { Batch, MillDashboardSupplier, RenewalStatus, User, UUID } from "./types/api";

type PageId = "overview" | "suppliers" | "review" | "packs" | "renewals" | "settings";

const pageLabels: Record<PageId, string> = {
  overview: "Overview",
  suppliers: "Suppliers",
  review: "Review queue",
  packs: "Evidence packs",
  renewals: "Renewals",
  settings: "Settings",
};

const emptySuppliers: MillDashboardSupplier[] = [];
const emptyRenewals: RenewalStatus[] = [];
const emptyBatches: Batch[] = [];
const ADMIN_MILL_KEY = "tapak.admin.mill-id";

interface DashboardAppProps {
  user: User;
  millId: UUID;
  onLogout: () => void;
  onChangeMill?: () => void;
}

function DashboardApp({ user, millId, onLogout, onChangeMill }: DashboardAppProps) {
  const [menuOpen, setMenuOpen] = useState(false);
  const [activePage, setActivePage] = useState<PageId>("overview");
  const [selectedSupplierId, setSelectedSupplierId] = useState<UUID | null>(null);
  const [creatingBatch, setCreatingBatch] = useState(false);
  const { data, error, loading, retry, addBatch } = useDashboardData(millId);
  const millProfile = useMill(millId);
  const selectedSupplier = data?.suppliers.find((supplier) => supplier.household_id === selectedSupplierId) ?? null;
  const selectedRenewal = data?.renewals.find((renewal) => renewal.household_id === selectedSupplierId) ?? null;
  const supplierDetail = useSupplierDetail(selectedSupplier, selectedRenewal);
  const reviewQueue = useReviewQueue(
    activePage === "review" && Boolean(data),
    data?.suppliers ?? emptySuppliers,
    data?.renewals ?? emptyRenewals,
  );
  const evidencePacks = useEvidencePacks(
    activePage === "packs" && Boolean(data),
    data?.batches ?? emptyBatches,
  );

  const openPage = (page: PageId) => {
    setActivePage(page);
    setMenuOpen(false);
  };

  const renderPage = () => {
    if (loading) {
      return <PageState kind="loading" message="Preparing supplier and compliance records." />;
    }

    if (error) {
      return <PageState kind="error" message={error} onRetry={retry} />;
    }

    if (!data) {
      return <PageState kind="empty" message="No dashboard data is available for this mill." />;
    }

    switch (activePage) {
      case "settings":
        return <SettingsPage mill={millProfile.mill} loading={millProfile.loading} error={millProfile.error} onUpdateContact={millProfile.updateContact} />;
      case "suppliers":
        return <SuppliersPage suppliers={data.suppliers} onSelectSupplier={setSelectedSupplierId} />;
      case "review":
        return <ReviewQueuePage items={reviewQueue.items} loading={reviewQueue.loading} error={reviewQueue.error} onRetry={reviewQueue.retry} onSelectSupplier={setSelectedSupplierId} />;
      case "packs":
        return <EvidencePacksPage batches={data.batches} records={evidencePacks.records} loading={evidencePacks.loading} error={evidencePacks.pageError} onGenerate={evidencePacks.generate} onCreate={() => setCreatingBatch(true)} />;
      case "renewals":
        return <RenewalsPage suppliers={data.suppliers} renewals={data.renewals} />;
      default:
        return <OverviewPage millName={millProfile.mill?.name ?? "this mill"} suppliers={data.suppliers} renewals={data.renewals} batches={data.batches} usingMocks={usesMockData} onViewSuppliers={() => openPage("suppliers")} />;
    }
  };

  return (
    <div className="app-shell">
      <aside className={`sidebar${menuOpen ? " sidebar--open" : ""}`}>
        <div className="sidebar__header">
          <a className="brand" href="#" aria-label="TAPAK dashboard home">
            <span className="brand__mark">T</span>
            <span>TAPAK</span>
          </a>
          <button
            aria-label="Close navigation"
            className="icon-button sidebar__close"
            type="button"
            onClick={() => setMenuOpen(false)}
          >
            <X aria-hidden="true" />
          </button>
        </div>

        <nav className="navigation" aria-label="Main navigation">
          <p className="navigation__label">Workspace</p>
          <button className={`navigation__item${activePage === "overview" ? " navigation__item--active" : ""}`} type="button" onClick={() => openPage("overview")}>
            <RefreshCw aria-hidden="true" />
            Overview
          </button>
          <button className={`navigation__item${activePage === "suppliers" ? " navigation__item--active" : ""}`} type="button" onClick={() => openPage("suppliers")}>
            <Users aria-hidden="true" />
            Suppliers
          </button>
          <button className={`navigation__item${activePage === "review" ? " navigation__item--active" : ""}`} type="button" onClick={() => openPage("review")}>
            <FileCheck2 aria-hidden="true" />
            Review queue
          </button>
          <button className={`navigation__item${activePage === "packs" ? " navigation__item--active" : ""}`} type="button" onClick={() => openPage("packs")}>
            <FileCheck2 aria-hidden="true" />
            Evidence packs
          </button>
          <button className={`navigation__item${activePage === "renewals" ? " navigation__item--active" : ""}`} type="button" onClick={() => openPage("renewals")}>
            <RotateCcw aria-hidden="true" />
            Renewals
          </button>
          <button className={`navigation__item${activePage === "settings" ? " navigation__item--active" : ""}`} type="button" onClick={() => openPage("settings")}>
            <Settings aria-hidden="true" />
            Settings
          </button>
          {onChangeMill && <button className="navigation__item" type="button" onClick={onChangeMill}><Building2 aria-hidden="true" />Change mill</button>}
        </nav>

        <div className="sidebar__profile">
          <span className="avatar">{user.email.slice(0, 2).toUpperCase()}</span>
          <span>
            <strong>{millProfile.mill?.name ?? (user.role === "admin" ? "Admin account" : "Mill account")}</strong>
            <small>{user.email}</small>
          </span>
          <button className="icon-button" type="button" aria-label="Sign out" title="Sign out" onClick={onLogout}><LogOut aria-hidden="true" /></button>
        </div>
      </aside>

      {menuOpen && (
        <button
          aria-label="Close navigation"
          className="sidebar-backdrop"
          type="button"
          onClick={() => setMenuOpen(false)}
        />
      )}

      <div className="workspace">
        <header className="topbar">
          <div className="topbar__start">
            <button
              aria-label="Open navigation"
              className="icon-button menu-button"
              type="button"
              onClick={() => setMenuOpen(true)}
            >
              <Menu aria-hidden="true" />
            </button>
            <span className="breadcrumb">{millProfile.mill?.name ?? "Mill workspace"}</span>
            <span className="breadcrumb__separator">/</span>
            <strong>{pageLabels[activePage]}</strong>
          </div>
          <div className="topbar__actions">
            <ThemeToggle />
          </div>
        </header>

        <main className="page-content">{renderPage()}</main>
      </div>
      <SupplierDrawer
        detail={supplierDetail.detail}
        error={supplierDetail.error}
        loading={supplierDetail.loading}
        supplier={selectedSupplier}
        onClose={() => setSelectedSupplierId(null)}
      />
      <CreateBatchDialog
        open={creatingBatch}
        millId={millId}
        suppliers={data?.suppliers ?? emptySuppliers}
        renewals={data?.renewals ?? emptyRenewals}
        onClose={() => setCreatingBatch(false)}
        onCreated={addBatch}
      />
    </div>
  );
}

function App() {
  const auth = useAuth();
  const [adminMillId, setAdminMillId] = useState<UUID | null>(() => sessionStorage.getItem(ADMIN_MILL_KEY));
  const adminMills = useAdminMills(auth.user?.role === "admin");

  const selectAdminMill = (millId: UUID) => {
    sessionStorage.setItem(ADMIN_MILL_KEY, millId);
    setAdminMillId(millId);
  };

  const clearAdminMill = () => {
    sessionStorage.removeItem(ADMIN_MILL_KEY);
    setAdminMillId(null);
  };

  const signOut = () => {
    clearAdminMill();
    auth.signOut();
  };

  if (auth.loading) {
    return <main className="auth-page"><PageState kind="loading" message="Restoring your session." /></main>;
  }

  if (!auth.user) {
    return <LoginPage error={auth.error} submitting={auth.submitting} onSubmit={auth.signIn} />;
  }

  if (auth.user.role === "admin" && !adminMillId) {
    return <MillSelectorPage mills={adminMills.mills} loading={adminMills.loading} error={adminMills.error} onRetry={adminMills.retry} onSelect={selectAdminMill} onLogout={signOut} />;
  }

  const millId = auth.user.mill_id ?? adminMillId ?? (usesMockData ? DEMO_MILL_ID : null);

  if (!millId) {
    return (
      <main className="auth-page">
        <section className="auth-card">
          <div><p className="eyebrow">Admin account</p><h1>Select a mill</h1><p className="text-muted">Set VITE_MILL_ID to the mill you want to inspect. A mill selector will be added with the admin workspace.</p></div>
          <button className="button button--secondary" type="button" onClick={signOut}>Sign out</button>
        </section>
      </main>
    );
  }

  return <DashboardApp user={auth.user} millId={millId} onLogout={signOut} onChangeMill={auth.user.role === "admin" ? clearAdminMill : undefined} />;
}

export default App;
