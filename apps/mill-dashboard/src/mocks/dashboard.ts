import type { Batch, MillDashboardSupplier, RenewalStatus, UUID } from "../types/api";
import type { EvidencePackState, ReviewItem, SupplierDetail } from "../types/ui";

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
  {
    id: "30000000-0000-4000-8000-000000000002",
    mill_id: DEMO_MILL_ID,
    product_description: "Fresh fruit bunches",
    trade_name: "Oil palm fruit",
    hs_code: "120710",
    net_mass_kg: "12100.00",
    recipient_name: "Meridian Oils BV",
    recipient_postal_address: "Rotterdam, Netherlands",
    recipient_email: "due-diligence@meridian.example",
    no_mixing_status: "single_source",
    created_by: "Aina Noor",
    created_at: "2026-08-23T11:20:00Z",
    plots: [],
  },
  {
    id: "30000000-0000-4000-8000-000000000003",
    mill_id: DEMO_MILL_ID,
    product_description: "Fresh fruit bunches",
    trade_name: "Oil palm fruit",
    hs_code: "120710",
    net_mass_kg: "22800.00",
    recipient_name: "Northshore Commodities GmbH",
    recipient_postal_address: "Hamburg, Germany",
    recipient_email: "compliance@northshore.example",
    no_mixing_status: "mixed_sources",
    created_by: "Aina Noor",
    created_at: "2026-08-19T07:10:00Z",
    plots: [],
  },
];

const categories = [
  "product_quantity",
  "geolocation",
  "land_ownership",
  "deforestation_proof",
  "labour_consent",
  "documentation_pack",
] as const;

export const supplierDetails = Object.fromEntries(
  dashboardSuppliers.map((supplier, supplierIndex): [string, SupplierDetail] => {
    const isFrozen = supplier.status === "frozen";
    const isPending = supplier.status === "pending";
    const plotId = `50000000-0000-4000-8000-00000000000${supplierIndex + 1}`;

    return [
      supplier.household_id,
      {
        supplier,
        email: `${supplier.name.toLowerCase().replace(" ", ".")}@example.com`,
        postalAddress: `${12 + supplierIndex}, ${supplier.district}, Malaysia`,
        gapAssessment: {
          id: `60000000-0000-4000-8000-00000000000${supplierIndex + 1}`,
          mill_id: DEMO_MILL_ID,
          household_id: supplier.household_id,
          assessed_by: "Aina Noor",
          assessed_at: "2026-08-18T09:30:00Z",
          items: categories.map((category, categoryIndex) => ({
            id: `61000000-0000-4000-8000-0000000000${supplierIndex}${categoryIndex}`,
            category,
            status:
              (isFrozen && category === "deforestation_proof") ||
              (isPending && category === "land_ownership")
                ? "needs_verification"
                : "present",
            notes:
              isPending && category === "land_ownership"
                ? "Tenancy evidence requires analyst confirmation."
                : null,
          })),
        },
        landOwnership: {
          id: `62000000-0000-4000-8000-00000000000${supplierIndex + 1}`,
          mill_id: DEMO_MILL_ID,
          household_id: supplier.household_id,
          state: supplier.district === "Miri" || supplier.district === "Bintulu" ? "sarawak" : "sabah",
          land_type: isPending ? "leased" : "native_title",
          rule_version: "1.0",
          status: isPending ? "needs_follow_up" : "cleared",
          assessed_by: "Aina Noor",
          assessed_at: "2026-08-18T10:00:00Z",
          documents_collected: isPending
            ? ["landlord_identity", "landlord_title"]
            : ["sabah_native_title"],
        },
        plots: [
          {
            id: plotId,
            mill_id: DEMO_MILL_ID,
            household_id: supplier.household_id,
            polygon: [
              [118.1, 5.8],
              [118.11, 5.8],
              [118.11, 5.81],
            ],
            centroid_lat: "5.805000",
            centroid_lon: "118.105000",
            area_ha: `${3 + supplierIndex}.2500`,
            collected_by: "Field Team 1",
            collected_at: "2026-08-16T08:15:00Z",
          },
        ],
        deforestationChecks: [
          {
            plot_id: plotId,
            status: isFrozen ? "needs_review" : "compliant",
            forest_loss_detected: false,
            review_inconclusive: isFrozen,
            reviewed_by: "GIS Review Team",
            reviewed_at: "2026-08-20T06:45:00Z",
          },
        ],
        fieldVerificationChecks: [
          {
            plot_id: plotId,
            checkin_mismatch: false,
            photo_mismatch: isFrozen,
            area_mismatch: false,
            status: isFrozen ? "needs_review" : "cleared",
            recorded_by: "Field Team 1",
            recorded_at: "2026-08-20T07:20:00Z",
          },
        ],
        yieldLicenceCheck: {
          household_id: supplier.household_id,
          mpob_licensed_area_ha: `${3 + supplierIndex}.5000`,
          declared_area_ha: `${3 + supplierIndex}.2500`,
          annual_output_kg: `${38000 + supplierIndex * 5000}.00`,
          regional_yield_benchmark_kg_per_ha: "11500.00",
          licence_mismatch: false,
          yield_mismatch: false,
          status: "cleared",
        },
        nationalSystems: {
          household_id: supplier.household_id,
          mpob_licence_number: `MPOB-${20481 + supplierIndex}`,
          sims_transaction_volume_kg: `${36000 + supplierIndex * 5000}.00`,
          geosawit_mapping_exists: true,
          geosawit_reference: `GS-${8800 + supplierIndex}`,
          emspo_certification_status: "Active",
          status: "cleared",
          looked_up_at: "2026-08-21T04:30:00Z",
        },
        renewal:
          renewalStatuses.find((renewal) => renewal.household_id === supplier.household_id) ?? null,
      },
    ];
  }),
) as Record<UUID, SupplierDetail>;

export const reviewItems: ReviewItem[] = [
  {
    id: "review-001",
    householdId: dashboardSuppliers[2].household_id,
    supplierName: dashboardSuppliers[2].name,
    district: dashboardSuppliers[2].district,
    category: "Field verification",
    summary: "Photo coordinates require review against the plot location.",
    priority: "high",
  },
  {
    id: "review-002",
    householdId: dashboardSuppliers[1].household_id,
    supplierName: dashboardSuppliers[1].name,
    district: dashboardSuppliers[1].district,
    category: "Land ownership",
    summary: "Leased-land documents need analyst follow-up.",
    priority: "medium",
  },
  {
    id: "review-003",
    householdId: dashboardSuppliers[2].household_id,
    supplierName: dashboardSuppliers[2].name,
    district: dashboardSuppliers[2].district,
    category: "Annual renewal",
    summary: "The current evidence pack has passed its renewal date.",
    priority: "high",
  },
];

export const evidencePackStates: Record<UUID, EvidencePackState> = {
  [batches[0].id]: "ready",
  [batches[1].id]: "not_generated",
  [batches[2].id]: "blocked",
};
