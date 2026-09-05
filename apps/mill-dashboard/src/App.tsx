import { FileCheck2, Menu, RefreshCw, RotateCcw, Users, X } from "lucide-react";
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
import { DEMO_MILL_ID } from "./mocks/dashboard";
import EvidencePacksPage from "./pages/EvidencePacksPage";
import OverviewPage from "./pages/OverviewPage";
import RenewalsPage from "./pages/RenewalsPage";
import ReviewQueuePage from "./pages/ReviewQueuePage";
import SuppliersPage from "./pages/SuppliersPage";
import type { Batch, MillDashboardSupplier, RenewalStatus, UUID } from "./types/api";

type PageId = "overview" | "suppliers" | "review" | "packs" | "renewals";

const pageLabels: Record<PageId, string> = {
  overview: "Overview",
  suppliers: "Suppliers",
  review: "Review queue",
  packs: "Evidence packs",
  renewals: "Renewals",
};

const emptySuppliers: MillDashboardSupplier[] = [];
const emptyRenewals: RenewalStatus[] = [];
const emptyBatches: Batch[] = [];

function App() {
  const [menuOpen, setMenuOpen] = useState(false);
  const [activePage, setActivePage] = useState<PageId>("overview");
  const [selectedSupplierId, setSelectedSupplierId] = useState<UUID | null>(null);
  const [creatingBatch, setCreatingBatch] = useState(false);
  const millId = import.meta.env.VITE_MILL_ID ?? DEMO_MILL_ID;
  const { data, error, loading, retry, addBatch } = useDashboardData(millId);
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
      case "suppliers":
        return <SuppliersPage suppliers={data.suppliers} onSelectSupplier={setSelectedSupplierId} />;
      case "review":
        return <ReviewQueuePage items={reviewQueue.items} loading={reviewQueue.loading} error={reviewQueue.error} onRetry={reviewQueue.retry} onSelectSupplier={setSelectedSupplierId} />;
      case "packs":
        return <EvidencePacksPage batches={data.batches} records={evidencePacks.records} loading={evidencePacks.loading} error={evidencePacks.pageError} onGenerate={evidencePacks.generate} onCreate={() => setCreatingBatch(true)} />;
      case "renewals":
        return <RenewalsPage suppliers={data.suppliers} renewals={data.renewals} />;
      default:
        return <OverviewPage suppliers={data.suppliers} renewals={data.renewals} batches={data.batches} usingMocks={usesMockData} onViewSuppliers={() => openPage("suppliers")} />;
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
        </nav>

        <div className="sidebar__profile">
          <span className="avatar">SM</span>
          <span>
            <strong>Sungai Murni</strong>
            <small>Mill account</small>
          </span>
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
            <span className="breadcrumb">Sungai Murni Mill</span>
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

export default App;
