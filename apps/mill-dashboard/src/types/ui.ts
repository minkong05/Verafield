import type {
  DeforestationCheck,
  FieldVerificationCheck,
  GapAssessment,
  LandOwnershipAssessment,
  LabourDeclaration,
  MillDashboardSupplier,
  NationalSystemsLookup,
  Plot,
  RenewalStatus,
  YieldLicenceCheck,
  ConsentRecord,
} from "./api";

export interface SupplierDetail {
  supplier: MillDashboardSupplier;
  email: string | null;
  postalAddress: string | null;
  gapAssessment: GapAssessment | null;
  landOwnership: LandOwnershipAssessment | null;
  labourDeclaration?: LabourDeclaration | null;
  consent?: ConsentRecord | null;
  plots: Plot[];
  deforestationChecks: DeforestationCheck[];
  fieldVerificationChecks: FieldVerificationCheck[];
  yieldLicenceCheck: YieldLicenceCheck | null;
  nationalSystems: NationalSystemsLookup | null;
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
