import { reviewItems as mockReviewItems } from "../mocks/dashboard";
import type { MillDashboardSupplier, RenewalStatus } from "../types/api";
import type { ReviewItem, ReviewPriority, SupplierDetail } from "../types/ui";
import { usesMockData } from "./dashboard";
import { loadSupplierDetail } from "./supplierDetail";

function item(
  detail: SupplierDetail,
  key: string,
  category: string,
  summary: string,
  priority: ReviewPriority,
): ReviewItem {
  return {
    id: `${detail.supplier.household_id}-${key}`,
    householdId: detail.supplier.household_id,
    supplierName: detail.supplier.name,
    district: detail.supplier.district,
    category,
    summary,
    priority,
  };
}

export function deriveReviewItems(detail: SupplierDetail): ReviewItem[] {
  const items: ReviewItem[] = [];
  const add = (key: string, category: string, summary: string, priority: ReviewPriority) =>
    items.push(item(detail, key, category, summary, priority));

  if (!detail.gapAssessment) {
    add("gap-missing", "Evidence", "Gap assessment has not been collected", "medium");
  } else {
    detail.gapAssessment.items.forEach((gapItem) => {
      if (gapItem.status !== "present") {
        add(`gap-${gapItem.category}`, "Evidence", `${gapItem.category.replaceAll("_", " ")} is ${gapItem.status.replaceAll("_", " ")}`, "medium");
      }
    });
  }

  if (!detail.landOwnership) {
    add("land-missing", "Land", "Land ownership assessment is missing", "medium");
  } else if (detail.landOwnership.status !== "cleared") {
    add("land-status", "Land", `Land ownership is ${detail.landOwnership.status.replaceAll("_", " ")}`, detail.landOwnership.status === "failed" ? "high" : "medium");
  }

  if (!detail.labourDeclaration) add("labour-missing", "Labour", "Labour declaration is missing", "medium");
  if (!detail.consent) add("consent-missing", "Consent", "Consent record is missing", "medium");
  if (detail.labourDeclaration?.has_land_dispute) add("land-dispute", "Labour", "Household reported a land dispute", "high");
  if (detail.labourDeclaration && !detail.labourDeclaration.no_child_labour_confirmed) add("child-labour", "Labour", "No-child-labour declaration is not confirmed", "high");

  detail.plots.forEach((plot) => {
    const shortId = plot.id.slice(0, 8);
    const deforestation = detail.deforestationChecks.find((check) => check.plot_id === plot.id);
    const field = detail.fieldVerificationChecks.find((check) => check.plot_id === plot.id);
    if (!deforestation) add(`deforestation-${plot.id}`, "Deforestation", `Plot ${shortId} has no deforestation check`, "medium");
    else if (deforestation.status !== "compliant") add(`deforestation-${plot.id}`, "Deforestation", `Plot ${shortId} is ${deforestation.status.replaceAll("_", " ")}`, deforestation.status === "non_compliant" ? "high" : "medium");
    if (!field) add(`field-${plot.id}`, "Field verification", `Plot ${shortId} has no field verification`, "medium");
    else if (field.status === "needs_review") add(`field-${plot.id}`, "Field verification", `Plot ${shortId} has mismatched field signals`, "medium");
  });

  if (!detail.yieldLicenceCheck) add("yield-missing", "Yield and licence", "Yield and licence check is missing", "medium");
  else if (detail.yieldLicenceCheck.status === "needs_review") add("yield-review", "Yield and licence", "Yield or licence data requires review", "medium");

  if (detail.nationalSystems?.status === "needs_review") add("national-review", "National systems", "National systems lookup requires review", "medium");
  if (detail.renewal?.lapsed) add("renewal-lapsed", "Renewal", "Annual evidence renewal has lapsed", "high");

  return items;
}

export async function loadReviewQueue(
  suppliers: MillDashboardSupplier[],
  renewals: RenewalStatus[],
): Promise<ReviewItem[]> {
  if (usesMockData) return mockReviewItems;

  const details = await Promise.all(
    suppliers.map((supplier) =>
      loadSupplierDetail(
        supplier,
        renewals.find((renewal) => renewal.household_id === supplier.household_id) ?? null,
      ),
    ),
  );

  const priorityOrder: Record<ReviewPriority, number> = { high: 0, medium: 1, low: 2 };
  return details.flatMap(deriveReviewItems).sort((a, b) => priorityOrder[a.priority] - priorityOrder[b.priority]);
}
