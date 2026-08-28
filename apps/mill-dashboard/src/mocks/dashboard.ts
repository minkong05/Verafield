import type { Batch, MillDashboardSupplier, RenewalStatus, UUID } from "../types/api";

export const DEMO_MILL_ID: UUID = "10000000-0000-4000-8000-000000000001";

export const dashboardSuppliers: MillDashboardSupplier[] = [
  {
    household_id: "20000000-0000-4000-8000-000000000001",
    mill_id: DEMO_MILL_ID,
    name: "Azlan Rahman",
    district: "Sandakan",
    status: "cleared",
  },
  {
    household_id: "20000000-0000-4000-8000-000000000002",
    mill_id: DEMO_MILL_ID,
    name: "Siti Liyana",
    district: "Miri",
    status: "pending",
  },
  {
    household_id: "20000000-0000-4000-8000-000000000003",
    mill_id: DEMO_MILL_ID,
    name: "Jamal Matusin",
    district: "Lahad Datu",
    status: "frozen",
  },
  {
    household_id: "20000000-0000-4000-8000-000000000004",
    mill_id: DEMO_MILL_ID,
    name: "Nurul Latifah",
    district: "Bintulu",
    status: "cleared",
  },
];

export const renewalStatuses: RenewalStatus[] = [
  {
    household_id: dashboardSuppliers[0].household_id,
    mill_id: DEMO_MILL_ID,
    name: dashboardSuppliers[0].name,
    district: dashboardSuppliers[0].district,
    last_evidence_pack_generated_at: "2026-07-18T09:30:00Z",
    renewal_due_at: "2027-07-18T09:30:00Z",
    lapsed: false,
  },
  {
    household_id: dashboardSuppliers[2].household_id,
    mill_id: DEMO_MILL_ID,
    name: dashboardSuppliers[2].name,
    district: dashboardSuppliers[2].district,
    last_evidence_pack_generated_at: "2025-08-14T10:15:00Z",
    renewal_due_at: "2026-08-14T10:15:00Z",
    lapsed: true,
  },
];

export const batches: Batch[] = [
  {
    id: "30000000-0000-4000-8000-000000000001",
    mill_id: DEMO_MILL_ID,
    product_description: "Fresh fruit bunches",
    trade_name: "Oil palm fruit",
    hs_code: "120710",
    net_mass_kg: "18500.00",
    recipient_name: "Northshore Commodities GmbH",
    recipient_postal_address: "Hamburg, Germany",
    recipient_email: "compliance@northshore.example",
    no_mixing_status: "single_source",
    created_by: "Aina Noor",
    created_at: "2026-08-27T08:45:00Z",
    plots: [
      {
        id: "40000000-0000-4000-8000-000000000001",
        mill_id: DEMO_MILL_ID,
        batch_id: "30000000-0000-4000-8000-000000000001",
        plot_id: "50000000-0000-4000-8000-000000000001",
        harvest_date: "2026-08-26",
      },
    ],
  },
];
