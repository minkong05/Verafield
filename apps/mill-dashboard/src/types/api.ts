export type UUID = string;
export type DateTimeString = string;
export type DateString = string;
export type DecimalString = string;

export type MillDashboardStatus = "cleared" | "pending" | "frozen";
export type NoMixingStatus = "single_source" | "mixed_sources";
export type GapStatus = "present" | "missing" | "needs_verification";
export type EvidenceCategory =
  | "product_quantity"
  | "geolocation"
  | "land_ownership"
  | "deforestation_proof"
  | "labour_consent"
  | "documentation_pack";
export type FieldVerificationStatus = "cleared" | "needs_review";
export type DeforestationStatus = "compliant" | "non_compliant" | "needs_review";
export type LandOwnershipStatus = "cleared" | "failed" | "needs_follow_up";
export type MalaysiaState = "sabah" | "sarawak";

export interface MillDashboardSupplier {
  household_id: UUID;
  mill_id: UUID;
  name: string;
  district: string;
  status: MillDashboardStatus;
}

export interface RenewalStatus {
  household_id: UUID;
  mill_id: UUID;
  name: string;
  district: string;
  last_evidence_pack_generated_at: DateTimeString | null;
  renewal_due_at: DateTimeString | null;
  lapsed: boolean;
}

export interface BatchPlot {
  id: UUID;
  mill_id: UUID;
  batch_id: UUID;
  plot_id: UUID;
  harvest_date: DateString;
}

export interface Batch {
  id: UUID;
  mill_id: UUID;
  product_description: string;
  trade_name: string;
  hs_code: string;
  net_mass_kg: DecimalString;
  recipient_name: string;
  recipient_postal_address: string;
  recipient_email: string;
  no_mixing_status: NoMixingStatus;
  created_by: string;
  created_at: DateTimeString;
  plots: BatchPlot[];
}

export interface ApiErrorBody {
  detail?: string;
}

export interface GapAssessmentItem {
  id: UUID;
  category: EvidenceCategory;
  status: GapStatus;
  notes: string | null;
}

export interface GapAssessment {
  id: UUID;
  mill_id: UUID;
  household_id: UUID;
  assessed_by: string;
  assessed_at: DateTimeString;
  items: GapAssessmentItem[];
}

export interface LandOwnershipAssessment {
  id: UUID;
  mill_id: UUID;
  household_id: UUID;
  state: MalaysiaState;
  land_type: string;
  rule_version: string;
  status: LandOwnershipStatus;
  assessed_by: string;
  assessed_at: DateTimeString;
  documents_collected: string[];
}

export interface Plot {
  id: UUID;
  mill_id: UUID;
  household_id: UUID;
  polygon: number[][];
  centroid_lat: DecimalString;
  centroid_lon: DecimalString;
  area_ha: DecimalString;
  collected_by: string;
  collected_at: DateTimeString;
}

export interface DeforestationCheck {
  plot_id: UUID;
  status: DeforestationStatus;
  forest_loss_detected: boolean;
  review_inconclusive: boolean;
  reviewed_by: string;
  reviewed_at: DateTimeString;
}

export interface FieldVerificationCheck {
  plot_id: UUID;
  checkin_mismatch: boolean;
  photo_mismatch: boolean;
  area_mismatch: boolean;
  status: FieldVerificationStatus;
  recorded_by: string;
  recorded_at: DateTimeString;
}

export interface YieldLicenceCheck {
  household_id: UUID;
  mpob_licensed_area_ha: DecimalString;
  declared_area_ha: DecimalString;
  annual_output_kg: DecimalString;
  regional_yield_benchmark_kg_per_ha: DecimalString;
  licence_mismatch: boolean;
  yield_mismatch: boolean;
  status: FieldVerificationStatus;
}

export interface NationalSystemsLookup {
  household_id: UUID;
  mpob_licence_number: string;
  sims_transaction_volume_kg: DecimalString;
  geosawit_mapping_exists: boolean;
  geosawit_reference: string | null;
  emspo_certification_status: string;
  status: FieldVerificationStatus;
  looked_up_at: DateTimeString;
}
