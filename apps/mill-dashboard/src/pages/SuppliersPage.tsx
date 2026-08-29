import { Search } from "lucide-react";
import { useMemo, useState } from "react";

import { supplierDetails } from "../mocks/dashboard";
import type { MillDashboardStatus, MillDashboardSupplier, UUID } from "../types/api";

interface SuppliersPageProps {
  suppliers: MillDashboardSupplier[];
  onSelectSupplier: (householdId: UUID) => void;
}

const statusLabels: Record<MillDashboardStatus, string> = {
  cleared: "Cleared",
  pending: "Pending",
  frozen: "Frozen",
};

function SuppliersPage({ suppliers: supplierRecords, onSelectSupplier }: SuppliersPageProps) {
  const [query, setQuery] = useState("");
  const [status, setStatus] = useState<MillDashboardStatus | "all">("all");

  const suppliers = useMemo(
    () =>
      supplierRecords.filter((supplier) => {
        const matchesQuery = `${supplier.name} ${supplier.district}`
          .toLowerCase()
          .includes(query.toLowerCase());
        return matchesQuery && (status === "all" || supplier.status === status);
      }),
    [query, status, supplierRecords],
  );

  return (
    <>
      <header className="page-heading">
        <div>
          <p className="eyebrow">Supplier registry</p>
          <h1>Suppliers</h1>
          <p className="text-muted">Households and plots currently linked to this mill.</p>
        </div>
      </header>

      <section className="data-panel">
        <header className="table-toolbar">
          <label className="table-search">
            <Search aria-hidden="true" />
            <span className="sr-only">Search suppliers</span>
            <input
              value={query}
              placeholder="Search name or district"
              onChange={(event) => setQuery(event.target.value)}
            />
          </label>
          <label>
            <span className="sr-only">Filter by status</span>
            <select value={status} onChange={(event) => setStatus(event.target.value as typeof status)}>
              <option value="all">All statuses</option>
              <option value="cleared">Cleared</option>
              <option value="pending">Pending</option>
              <option value="frozen">Frozen</option>
            </select>
          </label>
        </header>
        <div className="table-scroll">
          <table className="data-table data-table--interactive">
            <thead>
              <tr>
                <th>Supplier</th>
                <th>District</th>
                <th>MPOB licence</th>
                <th>Plots</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {suppliers.map((supplier) => {
                const detail = supplierDetails[supplier.household_id];
                return (
                  <tr key={supplier.household_id} onClick={() => onSelectSupplier(supplier.household_id)}>
                    <td className="data-table__primary">{supplier.name}</td>
                    <td>{supplier.district}</td>
                    <td>{detail?.nationalSystems?.mpob_licence_number ?? "—"}</td>
                    <td>{detail?.plots.length ?? "—"}</td>
                    <td>
                      <span className={`status status--${supplier.status}`}>
                        {statusLabels[supplier.status]}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
        {suppliers.length === 0 && <p className="panel-empty">No suppliers match the filters.</p>}
        <footer className="panel-footer">Showing {suppliers.length} suppliers</footer>
      </section>
    </>
  );
}

export default SuppliersPage;
