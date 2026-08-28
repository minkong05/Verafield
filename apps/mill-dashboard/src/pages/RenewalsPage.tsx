import { CalendarClock } from "lucide-react";

import { dashboardSuppliers, renewalStatuses } from "../mocks/dashboard";

const formatDate = (value: string | null) =>
  value
    ? new Intl.DateTimeFormat("en-MY", { day: "numeric", month: "short", year: "numeric" }).format(new Date(value))
    : "Not issued";

function RenewalsPage() {
  const records = dashboardSuppliers.map((supplier) => ({
    supplier,
    renewal: renewalStatuses.find((item) => item.household_id === supplier.household_id) ?? null,
  }));

  return (
    <>
      <header className="page-heading">
        <div>
          <p className="eyebrow">Annual review</p>
          <h1>Renewals</h1>
          <p className="text-muted">Evidence-pack validity and annual re-verification status.</p>
        </div>
      </header>

      <section className="data-panel">
        <div className="table-scroll">
          <table className="data-table">
            <thead><tr><th>Supplier</th><th>District</th><th>Last pack</th><th>Renewal due</th><th>Status</th></tr></thead>
            <tbody>
              {records.map(({ supplier, renewal }) => (
                <tr key={supplier.household_id}>
                  <td><span className="renewal-name"><CalendarClock aria-hidden="true" /><strong>{supplier.name}</strong></span></td>
                  <td>{supplier.district}</td>
                  <td>{formatDate(renewal?.last_evidence_pack_generated_at ?? null)}</td>
                  <td>{formatDate(renewal?.renewal_due_at ?? null)}</td>
                  <td>
                    {renewal?.lapsed ? <span className="status status--frozen">Lapsed</span> : renewal ? <span className="status status--cleared">Current</span> : <span className="status status--pending">Not issued</span>}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </>
  );
}

export default RenewalsPage;
