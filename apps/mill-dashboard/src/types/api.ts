export type UUID = string;
export type DateTimeString = string;
export type DateString = string;
export type DecimalString = string;

export type MillDashboardStatus = "cleared" | "pending" | "frozen";
export type NoMixingStatus = "single_source" | "mixed_sources";

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
