import type {
  DeforestationCheck,
  FieldVerificationCheck,
  GapAssessment,
  LandOwnershipAssessment,
  MillDashboardSupplier,
  NationalSystemsLookup,
  Plot,
  RenewalStatus,
  YieldLicenceCheck,
} from "./api";

export interface SupplierDetail {
  supplier: MillDashboardSupplier;
  email: string;
  postalAddress: string;
  gapAssessment: GapAssessment;
  landOwnership: LandOwnershipAssessment;
  plots: Plot[];
  deforestationChecks: DeforestationCheck[];
  fieldVerificationChecks: FieldVerificationCheck[];
  yieldLicenceCheck: YieldLicenceCheck;
  nationalSystems: NationalSystemsLookup;
  renewal: RenewalStatus | null;
}

export type ReviewPriority = "high" | "medium" | "low";

export interface ReviewItem {
  id: string;
  householdId: string;
  supplierName: string;
  district: string;
  category: string;
  summary: string;
  priority: ReviewPriority;
}

export type EvidencePackState = "ready" | "not_generated" | "blocked";
