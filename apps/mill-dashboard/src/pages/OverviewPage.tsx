import { ArrowRight, Clock3, PackageCheck, ShieldCheck, Snowflake, Users } from "lucide-react";

import { batches, dashboardSuppliers, renewalStatuses } from "../mocks/dashboard";
import type { MillDashboardStatus } from "../types/api";

const statusLabels: Record<MillDashboardStatus, string> = {
  cleared: "Cleared",
  pending: "Pending",
  frozen: "Frozen",
};

const formatMass = (value: string) =>
  new Intl.NumberFormat("en-MY", { maximumFractionDigits: 0 }).format(Number(value));

const formatDate = (value: string) =>
  new Intl.DateTimeFormat("en-MY", { day: "numeric", month: "short", year: "numeric" }).format(
    new Date(value),
  );

function OverviewPage() {
  const counts = dashboardSuppliers.reduce(
    (result, supplier) => {
      result[supplier.status] += 1;
      return result;
    },
    { cleared: 0, pending: 0, frozen: 0 },
  );

  const suppliersNeedingAttention = dashboardSuppliers.filter(
    (supplier) => supplier.status !== "cleared",
  );
  const lapsedRenewals = renewalStatuses.filter((renewal) => renewal.lapsed);

  return (
    <>
      <header className="page-heading">
        <div>
          <p className="eyebrow">Mill workspace</p>
          <h1>Overview</h1>
          <p className="text-muted">
            Supplier compliance and evidence preparation for Sungai Murni Mill.
          </p>
        </div>
        <span className="data-source-note">Development preview data</span>
      </header>

      <section className="overview-metrics" aria-label="Supplier compliance summary">
        <article className="metric-card">
          <span className="metric-card__icon">
            <Users aria-hidden="true" />
          </span>
          <div>
            <p>Total suppliers</p>
            <strong>{dashboardSuppliers.length}</strong>
          </div>
        </article>
        <article className="metric-card">
          <span className="metric-card__icon metric-card__icon--cleared">
            <ShieldCheck aria-hidden="true" />
          </span>
          <div>
            <p>Cleared</p>
            <strong>{counts.cleared}</strong>
          </div>
        </article>
        <article className="metric-card">
          <span className="metric-card__icon metric-card__icon--pending">
            <Clock3 aria-hidden="true" />
          </span>
          <div>
            <p>Pending</p>
            <strong>{counts.pending}</strong>
          </div>
        </article>
        <article className="metric-card">
          <span className="metric-card__icon metric-card__icon--frozen">
            <Snowflake aria-hidden="true" />
          </span>
          <div>
            <p>Frozen</p>
            <strong>{counts.frozen}</strong>
          </div>
        </article>
      </section>

      <div className="overview-layout">
        <section className="data-panel" aria-labelledby="attention-title">
          <header className="data-panel__header">
            <div>
              <h2 id="attention-title">Needs attention</h2>
              <p>Suppliers that are not currently cleared.</p>
            </div>
            <button className="text-button" type="button">
              View suppliers <ArrowRight aria-hidden="true" />
            </button>
          </header>
          <div className="table-scroll">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Supplier</th>
                  <th>District</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {suppliersNeedingAttention.map((supplier) => (
                  <tr key={supplier.household_id}>
                    <td className="data-table__primary">{supplier.name}</td>
                    <td>{supplier.district}</td>
                    <td>
                      <span className={`status status--${supplier.status}`}>
                        {statusLabels[supplier.status]}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        <aside className="overview-side">
          <section className="data-panel" aria-labelledby="renewal-title">
            <header className="data-panel__header">
              <div>
                <h2 id="renewal-title">Renewals</h2>
                <p>Annual reviews requiring follow-up.</p>
              </div>
            </header>
            {lapsedRenewals.length > 0 ? (
              <div className="compact-list">
                {lapsedRenewals.map((renewal) => (
                  <div className="compact-list__item" key={renewal.household_id}>
                    <div>
                      <strong>{renewal.name}</strong>
                      <span>{renewal.district}</span>
                    </div>
                    <span className="status status--frozen">Lapsed</span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="panel-empty">No lapsed renewals.</p>
            )}
          </section>

          <section className="data-panel" aria-labelledby="batch-title">
            <header className="data-panel__header">
              <div>
                <h2 id="batch-title">Recent batches</h2>
                <p>Latest evidence-pack inputs.</p>
              </div>
            </header>
            <div className="compact-list">
              {batches.map((batch) => (
                <div className="batch-row" key={batch.id}>
                  <span className="batch-row__icon">
                    <PackageCheck aria-hidden="true" />
                  </span>
                  <div>
                    <strong>{batch.trade_name}</strong>
                    <span>
                      {formatMass(batch.net_mass_kg)} kg · {batch.plots.length} plot ·{" "}
                      {formatDate(batch.created_at)}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </section>
        </aside>
      </div>
    </>
  );
}

export default OverviewPage;
