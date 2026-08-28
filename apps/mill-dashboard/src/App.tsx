import { Bell, FileCheck2, Menu, RefreshCw, RotateCcw, Search, Users, X } from "lucide-react";
import { useState } from "react";

import SupplierDrawer from "./components/SupplierDrawer";
import ThemeToggle from "./components/ThemeToggle";
import { supplierDetails } from "./mocks/dashboard";
import EvidencePacksPage from "./pages/EvidencePacksPage";
import OverviewPage from "./pages/OverviewPage";
import RenewalsPage from "./pages/RenewalsPage";
import ReviewQueuePage from "./pages/ReviewQueuePage";
import SuppliersPage from "./pages/SuppliersPage";
import type { UUID } from "./types/api";

type PageId = "overview" | "suppliers" | "review" | "packs" | "renewals";

const pageLabels: Record<PageId, string> = {
  overview: "Overview",
  suppliers: "Suppliers",
  review: "Review queue",
  packs: "Evidence packs",
  renewals: "Renewals",
};

function App() {
  const [menuOpen, setMenuOpen] = useState(false);
  const [activePage, setActivePage] = useState<PageId>("overview");
  const [selectedSupplierId, setSelectedSupplierId] = useState<UUID | null>(null);

  const openPage = (page: PageId) => {
    setActivePage(page);
    setMenuOpen(false);
  };

  const renderPage = () => {
    switch (activePage) {
      case "suppliers":
        return <SuppliersPage onSelectSupplier={setSelectedSupplierId} />;
      case "review":
        return <ReviewQueuePage onSelectSupplier={setSelectedSupplierId} />;
      case "packs":
        return <EvidencePacksPage />;
      case "renewals":
        return <RenewalsPage />;
      default:
        return <OverviewPage />;
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
            <label className="topbar-search">
              <Search aria-hidden="true" />
              <span className="sr-only">Search</span>
              <input placeholder="Search" />
            </label>
            <ThemeToggle />
            <button aria-label="Notifications" className="icon-button" type="button">
              <Bell aria-hidden="true" />
            </button>
          </div>
        </header>

        <main className="page-content">{renderPage()}</main>
      </div>
      <SupplierDrawer
        detail={selectedSupplierId ? supplierDetails[selectedSupplierId] : null}
        onClose={() => setSelectedSupplierId(null)}
      />
    </div>
  );
}

export default App;
