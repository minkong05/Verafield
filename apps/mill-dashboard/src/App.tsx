import { Bell, FileCheck2, Menu, RefreshCw, RotateCcw, Search, Users, X } from "lucide-react";
import { useState } from "react";

import ThemeToggle from "./components/ThemeToggle";

function App() {
  const [menuOpen, setMenuOpen] = useState(false);

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
          <a className="navigation__item navigation__item--active" href="#overview">
            <RefreshCw aria-hidden="true" />
            Overview
          </a>
          <a className="navigation__item" href="#suppliers">
            <Users aria-hidden="true" />
            Suppliers
          </a>
          <a className="navigation__item" href="#review">
            <FileCheck2 aria-hidden="true" />
            Review queue
          </a>
          <a className="navigation__item" href="#packs">
            <FileCheck2 aria-hidden="true" />
            Evidence packs
          </a>
          <a className="navigation__item" href="#renewals">
            <RotateCcw aria-hidden="true" />
            Renewals
          </a>
        </nav>

        <div className="sidebar__profile">
          <span className="avatar">AN</span>
          <span>
            <strong>--</strong>
            <small>Compliance analyst</small>
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
            <strong>Overview</strong>
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

        <main className="page-content" id="overview">
          <header className="page-heading">
            <div>
              <p className="eyebrow">Mill workspace</p>
              <h1>Overview</h1>
              <p className="text-muted">
                Supplier compliance and evidence preparation for Sungai Murni Mill.
              </p>
            </div>
          </header>

          <section className="content-placeholder" aria-labelledby="workspace-ready">
            <div>
              <h2 id="workspace-ready">Workspace structure ready</h2>
              <p className="text-muted">
                Supplier data and backend status results will be added in the next stage.
              </p>
            </div>
            <div className="foundation-row" aria-label="Compliance status styles">
              <span className="status status--cleared">Cleared</span>
              <span className="status status--pending">Pending</span>
              <span className="status status--frozen">Frozen</span>
            </div>
          </section>
        </main>
      </div>
    </div>
  );
}

export default App;
